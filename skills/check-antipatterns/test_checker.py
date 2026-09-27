import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import checker


def write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )


def completed(timestamp: str, item: dict) -> dict:
    return {
        "timestamp": timestamp,
        "type": "event_msg",
        "payload": {"type": "item_completed", "item": item},
    }


class CodexNormalizationTests(unittest.TestCase):
    def test_current_stream_normalizes_messages_and_commands_once(self) -> None:
        events = [
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "duplicate"}],
                },
            },
            completed(
                "2026-01-01T00:00:01Z",
                {
                    "type": "UserMessage",
                    "content": [{"type": "text", "text": "Inspect it"}],
                },
            ),
            completed(
                "2026-01-01T00:00:02Z",
                {
                    "type": "CommandExecution",
                    "command": ["/bin/zsh", "-lc", "command -v rg"],
                },
            ),
        ]

        data = checker.normalize_events(events)

        self.assertEqual("codex-item-completed", data.source_format)
        self.assertEqual(2, len(data.messages))
        self.assertEqual(
            ((1, "command -v rg"),),
            checker.extract_bash_commands(data.messages),
        )
        self.assertEqual((), checker.check_tool_discovery(data.messages * 25))

    def test_legacy_stream_normalizes_exec_command(self) -> None:
        data = checker.normalize_events(
            [
                {
                    "timestamp": "2026-01-01T00:00:01Z",
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "git status"}),
                    },
                }
            ]
        )

        self.assertEqual(
            ((0, "git status"),), checker.extract_bash_commands(data.messages)
        )


class HeuristicTests(unittest.TestCase):
    def test_assignment_forms_keep_positive_and_negative_cases_distinct(self):
        positives = (
            "PASSWORD=synthetic-value", "PASSWORD=synthetic-value; deploy",
            "export DB_PASSWORD=synthetic-value", "DB_PASSWORD=synthetic-value deploy",
            "API_KEY_PROD=synthetic-value deploy", "env DB_PASSWORD=synthetic-value deploy",
            "env 'PASSWORD=synthetic value' deploy", 'env "DB_PASSWORD=synthetic value" deploy',
            "env -- 'API_KEY_PROD=synthetic value' deploy", "sudo -u root env 'PASSWORD=synthetic value' deploy",
            "/usr/bin/env 'PASSWORD=synthetic value' deploy", "sudo -u root DB_PASSWORD=synthetic-value deploy",
            "export 'DB_PASSWORD=synthetic-value'", "readonly SERVICE_API_KEY=synthetic-value",
        )
        negatives = (
            "echo PASSWORD=synthetic-value", "rg -n 'PASSWORD=' .", "TOKENIZER_OPTIONS=normal deploy",
            "MAX_TOKENS=100 deploy", "'PASSWORD=synthetic-value' deploy",
            "env printf '%s' 'PASSWORD=synthetic value'", "/usr/bin/env printf '%s' 'PASSWORD=synthetic value'",
            "env -u PASSWORD=synthetic-value deploy", "sudo -p PASSWORD=synthetic-value deploy",
            "printf '%s\\n' ';' export PASSWORD=synthetic-value",
        )
        for expected, commands in ((1, positives), (0, negatives)):
            for command in commands:
                with self.subTest(command=command):
                    messages = (checker._message("", "assistant", [{"name": "Bash", "input": {"command": command}}]),)
                    self.assertEqual(expected, len(checker.check_credential_usage(messages)))

    def test_quoted_and_escaped_operators_remain_arguments(self):
        for command in ("printf '%s\\n' ';' rm -rf /tmp/example", "printf '%s\\n' \\; rm -rf /tmp/example", "printf '%s\\n' '&&' rm -rf /tmp/example", "printf '%s\\n' '|' rm -rf /tmp/example", "printf '%s\\n' '\n' rm -rf /tmp/example", "echo safe # rm -rf /tmp/example"):
            with self.subTest(command=command):
                messages = (checker._message("", "assistant", [{"name": "Bash", "input": {"command": command}}]),)
                self.assertEqual((), checker.check_destructive_command_safety(messages))

    def test_real_operators_still_expose_subsequent_commands(self):
        for operator in (";", "&&", "||", "|", "\n"):
            command = f"echo safe {operator} rm -rf /tmp/example"
            messages = (checker._message("", "assistant", [{"name": "Bash", "input": {"command": command}}]),)
            self.assertEqual(1, len(checker.check_destructive_command_safety(messages)))

    def test_report_redacts_escaped_and_concatenated_values(self):
        for source in (r'PASSWORD="prefix\"SYNTHETIC_TAIL"', 'PASSWORD="prefix"SYNTHETIC_TAIL'):
            finding = checker.Finding("TEST_FINDING", "LOW", "1", source, "Inspect.")
            report = checker.generate_report((finding,), (), {"universal_rules": []})
            self.assertNotIn("SYNTHETIC_TAIL", report)
            self.assertIn("[REDACTED]", report)

    def test_high_candidate_does_not_create_stop_authority(self) -> None:
        findings = (checker.Finding(
            "MISSING_PREFLIGHT", "HIGH", "2", "pytest integration", "Review preflight."
        ),)
        report = checker.generate_report(findings, (), checker.load_rules())
        self.assertIn("CANDIDATES", report)
        self.assertIn("Evidence: pytest integration", report)
        self.assertIn("Continue authorized work", report)
        self.assertIn("current authority or safety violation", report)
        self.assertNotIn("Stop the affected action until", report)

    def test_secret_read_neither_proves_authorization_nor_exempts_assignment(self) -> None:
        messages = tuple(
            checker._message("", "assistant", [{"name": "Bash", "input": {"command": command}}])
            for command in (
                "kubectl get secret example | base64 -d",
                "API_KEY=fixture deploy",
            )
        )
        findings = checker.check_credential_usage(messages)
        self.assertEqual(1, len(findings))
        self.assertFalse(any(
            practice.kind == "CREDENTIAL_FROM_SECRET"
            for practice in checker.identify_good_practices(messages)
        ))
        report = checker.generate_report(findings, checker.identify_good_practices(messages), checker.load_rules())
        self.assertNotIn("Used an authorized secret read", report)
        self.assertIn("placeholder", report)

    def test_destructive_home_target_is_high_severity(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": 'rm -rf "$HOME"'}}],
            ),
        )

        findings = checker.check_destructive_command_safety(messages)

        self.assertEqual(1, len(findings))
        self.assertEqual("HIGH", findings[0].severity)
        self.assertIn("exact target", findings[0].suggestion.lower())

    def test_quoted_search_for_rm_is_not_treated_as_execution(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": "rg -n 'rm -rf' ."}}],
            ),
        )

        self.assertEqual((), checker.check_destructive_command_safety(messages))

    def test_quoted_search_for_rmtree_is_not_treated_as_execution(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": "rg -n 'shutil.rmtree' ."}}],
            ),
        )

        self.assertEqual((), checker.check_destructive_command_safety(messages))

    def test_python_rmtree_execution_is_detected(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [
                    {
                        "name": "Bash",
                        "input": {
                            "command": "python3 -c 'import shutil; shutil.rmtree(\"tmp\")'"
                        },
                    }
                ],
            ),
        )

        self.assertEqual(1, len(checker.check_destructive_command_safety(messages)))

    def test_sudo_options_do_not_hide_recursive_remove(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [
                    {
                        "name": "Bash",
                        "input": {"command": "sudo -u root rm -rf /tmp/example"},
                    }
                ],
            ),
        )

        self.assertEqual(1, len(checker.check_destructive_command_safety(messages)))

    def test_credential_value_is_redacted(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": "API_KEY=supersecret deploy"}}],
            ),
        )

        findings = checker.check_credential_usage(messages)

        self.assertEqual(1, len(findings))
        self.assertNotIn("supersecret", findings[0].command)
        self.assertIn("redacted", findings[0].command.lower())

    def test_credential_pattern_search_is_not_an_assignment(self) -> None:
        messages = (
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": "rg -n 'PASSWORD\\s*=' ."}}],
            ),
        )

        self.assertEqual((), checker.check_credential_usage(messages))

    def test_normal_test_cycle_is_not_a_blind_retry(self) -> None:
        command = {"name": "Bash", "input": {"command": "python3 -m unittest -v"}}
        messages = (
            checker._message("", "assistant", [command]),
            checker._message("", "assistant", [command]),
        )

        self.assertEqual((), checker.check_retry_without_diagnosis(messages))

    def test_report_labels_score_as_bounded_heuristic(self) -> None:
        report = checker.generate_report((), (), {"universal_rules": []})

        self.assertIn("Heuristic signal score", report)
        self.assertIn("not proof of policy compliance", report)
        self.assertNotIn("COMPLIANCE SCORE", report)

    def test_report_redacts_every_transcript_evidence_form(self) -> None:
        secret_values = (
            "assignment-secret",
            "mapping-secret",
            "flag-secret",
            "header-secret",
            "url-secret",
        )
        evidence = " ".join(
            (
                "API_TOKEN=assignment-secret",
                "'password': 'mapping-secret'",
                "--api-key flag-secret",
                "Authorization: Bearer header-secret",
                "https://" + "user:url-secret" + "@example.test/path",
            )
        )
        finding = checker.Finding(
            "TEST_FINDING",
            "LOW",
            "1",
            evidence,
            "Inspect the evidence.",
        )

        report = checker.generate_report((finding,), (), {"universal_rules": []})

        for secret in secret_values:
            self.assertNotIn(secret, report)
        self.assertGreaterEqual(report.count("[REDACTED]"), len(secret_values))

    def test_report_redacts_before_truncating_detector_evidence(self) -> None:
        secret = "late-url-secret"
        command = "deploy " + "x" * 120 + " https://" + f"user:{secret}" + "@host.test"
        tool_call = {"name": "Bash", "input": {"command": command}}
        messages = (
            checker._message("", "assistant", [tool_call]),
            checker._message("", "assistant", [tool_call]),
        )

        findings = checker.check_retry_without_diagnosis(messages)
        report = checker.generate_report(findings, (), {"universal_rules": []})

        self.assertEqual(1, len(findings))
        self.assertNotIn(secret, report)
        self.assertIn("[REDACTED]", report)


class FileLoadingTests(unittest.TestCase):
    def test_read_conversation_reports_invalid_line(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            path = Path(raw_dir) / "conversation.jsonl"
            path.write_text("{}\nnot-json\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "line 2"):
                checker.read_conversation(path)


class IdleWithPendingWorkTests(unittest.TestCase):
    def test_probe_then_yield_is_flagged(self) -> None:
        messages = (
            checker._message("", "user", [{"type": "text", "text": "go"}]),
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": "overwatch status abc-123"}}],
            ),
        )
        findings = checker.check_idle_with_pending_work(messages)
        self.assertEqual(1, len(findings))
        self.assertEqual("IDLE_WITH_PENDING_WORK", findings[0].kind)

    def test_blocking_follow_wait_is_accepted(self) -> None:
        messages = (
            checker._message("", "user", [{"type": "text", "text": "go"}]),
            checker._message(
                "",
                "assistant",
                [
                    {
                        "name": "Bash",
                        "input": {
                            "command": "overwatch events abc-123 --follow --json"
                        },
                    }
                ],
            ),
        )
        self.assertEqual((), checker.check_idle_with_pending_work(messages))

    def test_wait_after_probe_is_accepted(self) -> None:
        messages = (
            checker._message("", "user", [{"type": "text", "text": "go"}]),
            checker._message(
                "",
                "assistant",
                [{"name": "Bash", "input": {"command": "overwatch status abc-123"}}],
            ),
            checker._message(
                "",
                "assistant",
                [
                    {
                        "name": "overwatch_overwatch_run",
                        "input": {"command": ["x"], "wait": True},
                    }
                ],
            ),
        )
        self.assertEqual((), checker.check_idle_with_pending_work(messages))

    def test_score_counts_six_checks(self) -> None:
        self.assertEqual(6, len(checker.IMPLEMENTED_CHECKS))
        finding = checker.Finding("IDLE_WITH_PENDING_WORK", "MEDIUM", "1", "x", "y")
        self.assertEqual(83, checker.heuristic_signal_score((finding,)))


CWD = "/synthetic/my_proj.x"


def claude(role, content, **extra):
    return {
        "type": role,
        "sessionId": "synthetic-session",
        "cwd": CWD,
        "isSidechain": False,
        "timestamp": extra.pop("timestamp", "2026-01-01T00:00:00Z"),
        "message": {"role": role, "content": content},
        **extra,
    }


def claude_bash(command, tool_id):
    return claude(
        "assistant",
        [{"type": "tool_use", "id": tool_id, "name": "Bash", "input": {"command": command}}],
    )


def claude_result(tool_id, text="ok", is_error=False):
    return claude(
        "user",
        [{"type": "tool_result", "tool_use_id": tool_id, "content": text, "is_error": is_error}],
    )


class ClaudeTranscriptTests(unittest.TestCase):
    def test_claude_records_normalize_without_counting_tool_results_as_turns(self) -> None:
        events = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "synthetic-session"},
            claude("user", "Deploy the service"),
            claude("user", "<injected skill body>", isMeta=True),
            claude("assistant", [{"type": "thinking", "thinking": "plan"}]),
            claude_bash("make deploy", "t1"),
            claude_result("t1", "make: *** failed", is_error=True),
            claude_bash("make deploy", "t2"),
            claude_result("t2"),
        ]
        data = checker.normalize_events(events)
        self.assertEqual(("claude-message", "observed"), (data.source_format, data.coverage))
        self.assertEqual(
            ["user"], [m["type"] for m in data.messages if m["type"] == "user"]
        )
        self.assertEqual(
            ("make deploy", "make deploy"),
            tuple(command for _, command in checker.extract_bash_commands(data.messages)),
        )
        findings, _ = checker.analyze(data)
        self.assertIn("RETRY_WITHOUT_DIAGNOSIS", {finding.kind for finding in findings})

    def test_tool_result_does_not_end_turn_after_status_probe(self) -> None:
        followed_by_wait = [
            claude("user", "go"),
            claude_bash("overwatch status abc-123", "t1"),
            claude_result("t1", "running"),
            claude_bash("overwatch events abc-123 --follow --json", "t2"),
            claude_result("t2", "done"),
        ]
        data = checker.normalize_events(followed_by_wait)
        self.assertEqual((), checker.check_idle_with_pending_work(data.messages))

        yielded = [*followed_by_wait[:3], claude("user", "are you done?")]
        data = checker.normalize_events(yielded)
        self.assertEqual(
            ["IDLE_WITH_PENDING_WORK"],
            [f.kind for f in checker.check_idle_with_pending_work(data.messages)],
        )

    def test_meta_only_claude_transcript_is_unsupported_coverage(self) -> None:
        data = checker.normalize_events([claude("user", "x", isMeta=True)])
        self.assertEqual(("claude-message", "unsupported"), (data.source_format, data.coverage))

    def test_include_subagents_merges_worker_actions(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "main.jsonl"
            write_jsonl(transcript, [claude("user", "delegate"), claude_bash("git status", "m1")])
            subagents = Path(raw_dir) / "main" / "subagents"
            subagents.mkdir(parents=True)
            write_jsonl(
                subagents / "agent-a.jsonl",
                [claude("user", "worker prompt", isSidechain=True), claude_bash("rm -rf ~", "s1")],
            )
            plain = checker.read_conversation(transcript)
            merged = checker.read_conversation(transcript, include_subagents=True)
        self.assertEqual("claude-message", plain.source_format)
        self.assertEqual("claude-message+1-subagents", merged.source_format)
        self.assertEqual(1, sum(1 for m in merged.messages if m["type"] == "user"))
        self.assertIn(
            "DESTRUCTIVE_OPERATION_WITHOUT_EXACT_GUARD",
            {f.kind for f in checker.analyze(merged)[0]},
        )

    def test_cli_discovers_current_claude_session(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            config = Path(raw_dir) / "claude-config"
            project = config / "projects" / "-synthetic-my-proj-x"
            project.mkdir(parents=True)
            write_jsonl(project / "live.jsonl", [claude("user", "go"), claude_bash("git status", "t1")])
            env = {
                "CLAUDECODE": "1",
                "CLAUDE_CONFIG_DIR": str(config),
                "CLAUDE_CODE_SESSION_ID": "live",
                "HOME": raw_dir,
            }
            with patch.dict(os.environ, env), patch("os.getcwd", return_value=CWD), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(0, checker.main([]))
            self.assertIn(f"Transcript: {project / 'live.jsonl'} (current claude session)", out.getvalue())

            empty = {**env, "CLAUDE_CODE_SESSION_ID": "", "CLAUDE_CONFIG_DIR": str(Path(raw_dir) / "none")}
            with patch.dict(os.environ, empty), patch("os.getcwd", return_value=CWD), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(2, checker.main(["--runtime", "claude"]))
            self.assertIn("No current session transcript identified", out.getvalue())


class PiTranscriptTests(unittest.TestCase):
    def test_pi_session_normalizes_tool_calls(self) -> None:
        events = [
            {"type": "session", "version": 3, "id": "s", "cwd": CWD},
            {"type": "message", "message": {"role": "user", "content": [{"type": "text", "text": "go"}]}},
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "toolCall", "id": "c", "name": "bash", "arguments": {"command": "command -v rg"}}],
                },
            },
            {"type": "message", "message": {"role": "toolResult", "toolCallId": "c", "content": [{"type": "text", "text": "/bin/rg"}]}},
        ]
        data = checker.normalize_events(events)
        self.assertEqual(("pi-message", "observed"), (data.source_format, data.coverage))
        self.assertEqual(((1, "command -v rg"),), checker.extract_bash_commands(data.messages))


class SharedModuleTests(unittest.TestCase):
    def test_session_discovery_matches_sibling_skill_copy(self) -> None:
        here = Path(__file__).resolve().parent / "session_discovery.py"
        sibling = here.parents[1] / "analyze-conversation" / "session_discovery.py"
        if not sibling.exists():
            self.skipTest("analyze-conversation is not installed beside this skill")
        self.assertEqual(sibling.read_bytes(), here.read_bytes())


if __name__ == "__main__":
    unittest.main()
