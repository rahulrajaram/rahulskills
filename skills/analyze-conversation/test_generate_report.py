import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_report
import session_discovery
from analyzer import analyze_conversation, detect_hardcoded_values, print_anti_patterns
from patterns import find_retry_without_diagnosis, is_normal_retry_command


def message(role, text):
    return {"type": role, "message": {"content": [{"type": "text", "text": text}]}}


def command(text):
    return {"type": "assistant", "message": {"content": [{"name": "Bash", "input": {"command": text}}]}}


def boundary(prefix, limit):
    return prefix + "x" * (limit - len(prefix) - 26) + " https://u:SYNTHETIC_TAIL" + "z" * 40 + "@host.invalid"


def synthetic_url(userinfo, scheme="https"):
    return f"{scheme}://{userinfo}@host.invalid"


def write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )


RUNTIME_ENV = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "PI_CODING_AGENT_DIR")
_saved_env = {}


def setUpModule() -> None:
    # Keep report output and discovery hermetic even inside a configured runtime.
    import os

    for name in RUNTIME_ENV:
        if name in os.environ:
            _saved_env[name] = os.environ.pop(name)


def tearDownModule() -> None:
    import os

    os.environ.update(_saved_env)


class CodexNormalizationTests(unittest.TestCase):
    def test_console_evidence_and_ip_context_keep_full_source_boundaries(self) -> None:
        source = 'PASSWORD="' + "x" * 100 + "SYNTHETIC_TAIL 192.0.2.1 " + "x" * 100 + '"'
        findings = detect_hardcoded_values(source)
        self.assertEqual(2, len(findings))
        self.assertNotIn("192.0.2.1", json.dumps(findings))
        self.assertNotIn("SYNTHETIC_TAIL", json.dumps(findings))

    def test_saved_reports_redact_before_each_lossy_transformation(self) -> None:
        cases = (
            ([message("user", boundary("do it ", 220))], "User Signals"),
            (
                [message("user", boundary("you have seemingly stopped ", 220))],
                "User Signals",
            ),
            (
                [
                    message("assistant", "Should I do it?"),
                    message("user", boundary("do it ", 220)),
                ],
                "Assistant Routing Questions",
            ),
            (
                [message("assistant", boundary("Should I do it? ", 220))],
                "Low-Confidence Question Candidates",
            ),
            ([command(boundary("deploy ", 100))] * 2, "1. Command:"),
            ([command(boundary("deploy ", 80))] * 3, "Repeated 3x"),
            ([message("user", "Inspect only"), message("assistant", "I will also create " + synthetic_url("u:SYNTHETIC_TAIL.more"))], "Expansion:"),
            ([message("assistant", "export URL=" + synthetic_url("u:SYNTHETIC_TAIL:1234", "http"))], "Value:"),
            ([message("assistant", r'PASSWORD="prefix\"SYNTHETIC_TAIL"')], "Credential assignment detected"),
            ([command("env 'PASSWORD=prefix SYNTHETIC_TAIL' deploy")] * 3, "Repeated 3x"),
        )
        for messages, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as raw_dir:
                root = Path(raw_dir)
                transcript = root / "synthetic.jsonl"
                write_jsonl(transcript, messages)
                with contextlib.redirect_stdout(io.StringIO()):
                    report = Path(generate_report.generate_markdown_report(str(transcript), root))
                text = report.read_text()
                self.assertIn(expected, text)
                self.assertIn("[REDACTED]", text)
                self.assertNotIn("SYNTHETIC_TAIL", text)

    def test_redaction_does_not_merge_distinct_raw_commands(self) -> None:
        commands = [command("deploy --token first-value"), command("deploy --token second-value")]
        self.assertEqual([], find_retry_without_diagnosis(commands))
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "synthetic.jsonl"
            write_jsonl(transcript, commands)
            stats = analyze_conversation(str(transcript))
            self.assertEqual(2, len(stats.repeated_commands))
            self.assertEqual([1, 1], list(stats.repeated_commands.values()))

    def test_completed_stderr_is_redacted_before_normalization_truncates_it(self) -> None:
        result = generate_report._normalize_completed_item({
            "payload": {"item": {"type": "CommandExecution", "command": "deploy",
                "stderr": "error " + "x" * 230 + " https://u:SYNTHETIC_TAIL" + "z" * 300 + "@host.invalid"}}
        })
        self.assertNotIn("SYNTHETIC_TAIL", json.dumps(result))
        self.assertIn("[REDACTED]", json.dumps(result))
    def test_candidates_preserve_authority_and_redact_before_excerpting(self) -> None:
        # Userinfo crosses the 80-character command and 300-character context
        # limits; redacting only the final report would miss the truncated @.
        secret = "userinfo-sensitive-" + "z" * 400
        command = "deploy https://user:" + secret + "@host.invalid"
        text = 'password="fixture"; let me also add the requested tests. https://user:' + secret + '@host.invalid'
        events = [
            {"type": "user", "message": {"content": "Implement the fix and all necessary tests; continue autonomously."}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}},
            *[
                {"type": "assistant", "message": {"content": [{"name": "Bash", "input": {"command": command}}]}}
                for _ in range(3)
            ],
        ]
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            transcript = root / "candidates.jsonl"
            write_jsonl(transcript, events)
            with patch.dict("os.environ", {"HOME": str(root)}):
                output = Path(generate_report.generate_markdown_report(transcript))
            report = output.read_text(encoding="utf-8")
        self.assertIn("Heuristic Candidates", report)
        self.assertIn("prior authorization", report)
        self.assertIn("current authority or safety violation", report)
        self.assertIn("Continue necessary authorized work", report)
        self.assertIn("Evidence:", report)
        self.assertNotIn("userinfo-sensitive", report)
        self.assertIn("[REDACTED]", report)
        for unsupported in (
            "Universal Rules Violated", "Always read from K8s secrets",
            "base64 -d", "without asking user", "Stop and ask before expanding",
            "Build metrics dashboard", "Would have prevented",
        ):
            self.assertNotIn(unsupported, report)

    def test_environment_credential_reference_does_not_require_kubernetes(self) -> None:
        from patterns import find_credential_antipatterns
        messages = [{"type": "assistant", "message": {"content": "export DB_PASSWORD=$APP_PASSWORD"}}]
        self.assertEqual([], find_credential_antipatterns(messages))

    def test_report_redacts_transcript_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            transcript = root / "credential-test.jsonl"
            write_jsonl(
                transcript,
                [
                    {
                        "timestamp": "2026-01-01T00:00:00Z",
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        'export DATABASE_PASSWORD="actual-password"\n'
                                        "Authorization: Bearer actual-token\n"
                                        "service://actual-user:actual-pass@host.invalid/path\n"
                                        '{"api_key": "actual-json-key"}\n'
                                        "deploy --token actual-flag-token"
                                    ),
                                }
                            ]
                        },
                    }
                ],
            )

            with patch.dict("os.environ", {"HOME": str(root)}):
                output = Path(generate_report.generate_markdown_report(transcript))
            report = output.read_text(encoding="utf-8")

            self.assertNotIn("actual-password", report)
            self.assertNotIn("actual-token", report)
            self.assertNotIn("actual-user:actual-pass", report)
            self.assertNotIn("actual-json-key", report)
            self.assertNotIn("actual-flag-token", report)
            self.assertIn("[REDACTED]", report)

    def test_governed_test_repetition_and_file_reads_are_not_blind_retries(
        self,
    ) -> None:
        self.assertTrue(
            is_normal_retry_command(
                "overwatch run --profile generic -- cargo test --offline"
            )
        )
        self.assertTrue(
            is_normal_retry_command(
                "overwatch run --profile generic -- cargo clippy --offline"
            )
        )
        self.assertTrue(is_normal_retry_command("sed -n '1,220p' SKILL.md"))
        self.assertTrue(
            generate_report.is_normal_dev_command(
                "overwatch run --profile generic -- cargo test --offline"
            )
        )
        self.assertTrue(
            generate_report.is_normal_dev_command(
                "python -m unittest discover -s tests -v"
            )
        )

    def test_unittest_reruns_are_normal_test_cycles(self) -> None:
        command = "python -m unittest discover -s tests -v"
        messages = [
            {
                "type": "assistant",
                "message": {
                    "content": [{"name": "Bash", "input": {"command": command}}]
                },
            },
            {
                "type": "assistant",
                "message": {
                    "content": [{"name": "Bash", "input": {"command": command}}]
                },
            },
        ]

        self.assertEqual([], find_retry_without_diagnosis(messages))

    def test_current_item_stream_captures_commands_files_tools_and_humans(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            transcript = root / "rollout-test.jsonl"
            write_jsonl(
                transcript,
                [
                    {
                        "timestamp": "2026-01-01T00:00:00Z",
                        "type": "session_meta",
                        "payload": {"cwd": str(root)},
                    },
                    {
                        "timestamp": "2026-01-01T00:00:00.500Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "duplicate"}],
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:01Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "item_completed",
                            "item": {
                                "type": "UserMessage",
                                "content": [{"type": "text", "text": "Build it"}],
                            },
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:02Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "item_completed",
                            "item": {
                                "type": "AgentMessage",
                                "content": [{"type": "Text", "text": "Working"}],
                            },
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:03Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "item_completed",
                            "item": {
                                "type": "CommandExecution",
                                "id": "exec-1",
                                "command": ["/bin/zsh", "-lc", "git status --short"],
                                "source": "unified_exec",
                                "duration": {"secs": 1, "nanos": 500_000_000},
                                "exit_code": 0,
                                "status": "completed",
                                "stderr": "",
                                "parsed_cmd": [
                                    {"type": "read", "path": "/tmp/input.txt"}
                                ],
                            },
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:04Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "item_completed",
                            "item": {
                                "type": "FileChange",
                                "changes": {
                                    "/tmp/new.txt": {"type": "add"},
                                    "/tmp/old.txt": {"type": "update"},
                                },
                            },
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:05Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "item_completed",
                            "item": {
                                "type": "McpToolCall",
                                "server": "example",
                                "tool": "lookup",
                                "arguments": {"id": "one"},
                            },
                        },
                    },
                ],
            )

            normalized = generate_report.normalize_codex_conversation(str(transcript))
            self.addCleanup(Path(normalized).unlink, missing_ok=True)
            stats = analyze_conversation(normalized)

            self.assertEqual(stats.user_messages, ["Build it"])
            self.assertEqual(len(stats.bash_commands), 1)
            self.assertEqual(stats.bash_commands[0]["command"], "git status --short")
            self.assertEqual(stats.command_duration_seconds, 1.5)
            self.assertEqual(stats.file_reads, ["/tmp/input.txt"])
            self.assertEqual(stats.file_writes, ["/tmp/new.txt"])
            self.assertEqual(len(stats.file_edits), 1)
            self.assertEqual(stats.tool_calls["mcp__example__lookup"], 1)

            with patch.object(generate_report.Path, "home", return_value=root):
                report = Path(generate_report.generate_markdown_report(str(transcript)))
            self.assertEqual(report.parent, root / ".codex" / "retrospectives")
            text = report.read_text(encoding="utf-8")
            self.assertIn("**Shell Commands**: 1", text)
            self.assertIn("**Cumulative Shell Runtime**: 2s", text)
            self.assertIn("**Observed Transcript Span**: 4s", text)

    def test_legacy_response_stream_still_normalizes_exec_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "rollout-legacy.jsonl"
            write_jsonl(
                transcript,
                [
                    {
                        "timestamp": "2026-01-01T00:00:00Z",
                        "type": "session_meta",
                        "payload": {},
                    },
                    {
                        "timestamp": "2026-01-01T00:00:01Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Inspect"}],
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:02Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "git status"}),
                        },
                    },
                ],
            )

            normalized = generate_report.normalize_codex_conversation(str(transcript))
            self.addCleanup(Path(normalized).unlink, missing_ok=True)
            stats = analyze_conversation(normalized)

            self.assertEqual(stats.user_messages, ["Inspect"])
            self.assertEqual(len(stats.bash_commands), 1)
            self.assertEqual(stats.bash_commands[0]["command"], "git status")


def claude_record(role, content, cwd, **extra):
    return {
        "type": role,
        "sessionId": "synthetic-session",
        "cwd": cwd,
        "isSidechain": False,
        "timestamp": extra.pop("timestamp", "2026-01-01T00:00:00Z"),
        "message": {"role": role, "content": content},
        **extra,
    }


def claude_bash(command, cwd, tool_id="t1", **extra):
    return claude_record(
        "assistant",
        [{"type": "tool_use", "id": tool_id, "name": "Bash", "input": {"command": command}}],
        cwd,
        **extra,
    )


def claude_result(text, cwd, tool_id="t1", is_error=False, **extra):
    return claude_record(
        "user",
        [{"type": "tool_result", "tool_use_id": tool_id, "content": text, "is_error": is_error}],
        cwd,
        **extra,
    )


class ClaudeDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.config = self.root / "claude-config"
        self.cwd = "/srv/example/my_proj.x"
        self.project = self.config / "projects" / "-srv-example-my-proj-x"
        self.project.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def transcript(self, name, mtime):
        import os

        path = self.project / f"{name}.jsonl"
        write_jsonl(path, [claude_record("user", "hi", self.cwd)])
        os.utime(path, (mtime, mtime))
        return path

    def test_slugs_follow_runtime_layouts(self) -> None:
        self.assertEqual("-srv-example-my-proj-x", session_discovery.claude_slug(self.cwd))
        self.assertEqual("--srv-example-my_proj.x--", session_discovery.pi_slug(self.cwd))

    def test_runtime_detection_order(self) -> None:
        detect = session_discovery.detect_runtime
        self.assertEqual("claude", detect({"CLAUDECODE": "1", "CODEX_SANDBOX": "x"}))
        self.assertEqual("claude", detect({"CLAUDE_CODE_SESSION_ID": "abc"}))
        self.assertEqual("codex", detect({"CODEX_SANDBOX": "seatbelt"}))
        self.assertIsNone(detect({"CODEX_HOME": "/somewhere"}))
        self.assertEqual("pi", detect({"PI_CODING_AGENT": "true"}))
        self.assertIsNone(detect({}))

    def test_session_id_env_wins_over_newest_transcript(self) -> None:
        older = self.transcript("older", 1_000)
        self.transcript("newer", 2_000)
        env = {"CLAUDECODE": "1", "CLAUDE_CONFIG_DIR": str(self.config), "CLAUDE_CODE_SESSION_ID": "older"}
        found = session_discovery.current_session(None, self.cwd, env)
        self.assertEqual(("claude", older), (found.runtime, found.path))

    def test_newest_slug_transcript_without_session_id(self) -> None:
        self.transcript("older", 1_000)
        newer = self.transcript("newer", 2_000)
        (self.project / "newer" / "subagents").mkdir(parents=True)
        write_jsonl(self.project / "newer" / "subagents" / "agent-x.jsonl", [])
        env = {"CLAUDECODE": "1", "CLAUDE_CONFIG_DIR": str(self.config)}
        self.assertEqual(newer, session_discovery.current_session(None, self.cwd, env).path)
        self.assertEqual(
            newer,
            Path(generate_report.find_current_conversation_file("claude", self.cwd, env)),
        )

    def test_missing_session_lists_candidates_without_guessing(self) -> None:
        env = {"CLAUDE_CONFIG_DIR": str(self.config), "HOME": str(self.root)}
        other = self.config / "projects" / "-elsewhere"
        other.mkdir()
        write_jsonl(other / "s.jsonl", [claude_record("user", "hi", "/elsewhere")])
        with self.assertRaises(session_discovery.SessionNotFound) as raised:
            session_discovery.current_session("claude", self.cwd, env)
        self.assertEqual((), raised.exception.candidates)
        with patch.dict("os.environ", env), self.assertRaises(FileNotFoundError):
            generate_report.find_current_conversation_file("claude", self.cwd, env)

    def test_find_by_id_is_exact_for_claude(self) -> None:
        target = self.transcript("abc", 1_000)
        self.transcript("abcd", 2_000)
        env = {"CLAUDE_CONFIG_DIR": str(self.config), "HOME": str(self.root)}
        with patch.dict("os.environ", env):
            self.assertEqual(str(target), generate_report.find_conversation_file("abc", "claude"))
            with self.assertRaises(FileNotFoundError):
                generate_report.find_conversation_file("missing", "claude")


class ClaudeParsingTests(unittest.TestCase):
    def test_claude_transcript_normalizes_turns_results_and_project_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            project = root / "my_proj.x"  # the lossy slug decode would miss this path
            project.mkdir()
            (project / "AGENTS.md").write_text("synthetic", encoding="utf-8")
            cwd = str(project)
            session_dir = root / "projects" / session_discovery.claude_slug(cwd)
            session_dir.mkdir(parents=True)
            transcript = session_dir / "synthetic-session.jsonl"
            write_jsonl(
                transcript,
                [
                    {"type": "permission-mode", "sessionId": "synthetic-session"},
                    claude_record("user", "Run the build", cwd, timestamp="2026-01-01T00:00:00Z"),
                    claude_record(
                        "user", "<skill body>", cwd, isMeta=True, timestamp="2026-01-01T00:00:01Z"
                    ),
                    claude_bash("make build", cwd, timestamp="2026-01-01T00:00:02Z"),
                    claude_result(
                        "make: *** failed", cwd, is_error=True, timestamp="2026-01-01T00:00:03Z"
                    ),
                    claude_record(
                        "assistant",
                        [{"type": "text", "text": "The build failed."}],
                        cwd,
                        timestamp="2026-01-01T00:00:04Z",
                    ),
                ],
            )

            normalized, runtime, _ = generate_report.normalize_runtime_conversation(str(transcript))
            try:
                self.assertEqual("claude", runtime)
                stats = analyze_conversation(normalized)
            finally:
                Path(normalized).unlink()
            self.assertEqual(1, stats.total_turns)
            self.assertEqual(["Run the build"], stats.user_messages)
            self.assertEqual(["make build"], [c["command"] for c in stats.bash_commands])
            self.assertEqual(1, len(stats.errors))

            self.assertEqual(project, session_discovery.transcript_cwd(transcript))
            self.assertTrue(generate_report.check_project_context(str(transcript))["has_agents_md"])

            with contextlib.redirect_stdout(io.StringIO()):
                report = Path(generate_report.generate_markdown_report(str(transcript), root / "out"))
            text = report.read_text(encoding="utf-8")
            self.assertEqual("synthetic-session_retrospective.md", report.name)
            self.assertIn("Claude Code JSONL normalized", text)
            self.assertIn("**Shell Commands**: 1", text)

    def test_include_subagents_merges_actions_but_not_parent_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            cwd = "/synthetic/project"
            transcript = root / "main-session.jsonl"
            write_jsonl(
                transcript,
                [
                    claude_record("user", "Delegate it", cwd, timestamp="2026-01-01T00:00:00Z"),
                    claude_bash("git status", cwd, timestamp="2026-01-01T00:00:05Z"),
                ],
            )
            subagents = root / "main-session" / "subagents"
            subagents.mkdir(parents=True)
            write_jsonl(
                subagents / "agent-a1.jsonl",
                [
                    claude_record(
                        "user", "Worker prompt", cwd, isSidechain=True, timestamp="2026-01-01T00:00:01Z"
                    ),
                    claude_bash("pytest -q", cwd, "s1", isSidechain=True, timestamp="2026-01-01T00:00:02Z"),
                    claude_result("ok", cwd, "s1", isSidechain=True, timestamp="2026-01-01T00:00:03Z"),
                ],
            )

            for include, commands in ((False, ["git status"]), (True, ["pytest -q", "git status"])):
                with self.subTest(include=include):
                    normalized, _, paths = generate_report.normalize_runtime_conversation(
                        str(transcript), include_subagents=include
                    )
                    try:
                        stats = analyze_conversation(normalized)
                    finally:
                        Path(normalized).unlink()
                    self.assertEqual(len(paths), 1 if include else 0)
                    self.assertEqual(["Delegate it"], stats.user_messages)
                    self.assertEqual(commands, [c["command"] for c in stats.bash_commands])

    def test_cli_current_claude_session_writes_under_config_dir(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            cwd = "/synthetic/project"
            config = root / "claude-config"
            session_dir = config / "projects" / session_discovery.claude_slug(cwd)
            session_dir.mkdir(parents=True)
            write_jsonl(
                session_dir / "cli-session.jsonl",
                [claude_record("user", "Inspect", cwd), claude_bash("git status", cwd)],
            )
            env = {"CLAUDECODE": "1", "CLAUDE_CONFIG_DIR": str(config), "HOME": str(root)}
            with patch.dict("os.environ", env), patch("os.getcwd", return_value=cwd), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(0, generate_report.main(["--current", "--runtime", "claude"]))
            self.assertTrue((config / "retrospectives" / "cli-session_retrospective.md").is_file())
            self.assertIn("runtime: claude", out.getvalue())

    def test_empty_claude_conversation_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "meta-only.jsonl"
            write_jsonl(transcript, [claude_record("user", "x", "/p", isMeta=True)])
            with self.assertRaises(ValueError):
                generate_report.normalize_runtime_conversation(str(transcript))


class PiParsingTests(unittest.TestCase):
    def test_pi_session_maps_tools_results_and_header_cwd(self) -> None:
        records = [
            {"type": "session", "version": 3, "id": "s", "timestamp": "t0", "cwd": "/synthetic/pi"},
            {"type": "model_change", "id": "m"},
            {"type": "message", "timestamp": "t1", "message": {"role": "user", "content": [{"type": "text", "text": "Fix it"}]}},
            {
                "type": "message",
                "timestamp": "t2",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "hidden"},
                        {"type": "toolCall", "id": "c1", "name": "bash", "arguments": {"command": "make", "timeout": 5}},
                        {"type": "toolCall", "id": "c2", "name": "edit", "arguments": {"path": "a.py", "edits": []}},
                    ],
                },
            },
            {
                "type": "message",
                "timestamp": "t3",
                "message": {"role": "toolResult", "toolCallId": "c1", "toolName": "bash", "isError": True, "content": [{"type": "text", "text": "failed"}]},
            },
        ]
        self.assertEqual("pi", session_discovery.detect_format(records))
        messages = session_discovery.normalize_pi_records(records)
        self.assertEqual(["user", "assistant", "assistant"], [m["type"] for m in messages])
        tools = messages[1]["message"]["content"]
        self.assertEqual(("Bash", {"command": "make", "description": ""}), (tools[0]["name"], tools[0]["input"]))
        self.assertEqual(("Edit", {"file_path": "a.py"}), (tools[1]["name"], tools[1]["input"]))
        self.assertTrue(messages[2]["message"]["content"][0]["is_error"])
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "pi.jsonl"
            write_jsonl(transcript, records)
            self.assertEqual(Path("/synthetic/pi"), session_discovery.transcript_cwd(transcript))


if __name__ == "__main__":
    unittest.main()
