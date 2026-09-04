import json
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_report
from analyzer import analyze_conversation, print_anti_patterns, detect_hardcoded_values
from patterns import find_retry_without_diagnosis, is_normal_retry_command


def message(role, text):
    return {"type": role, "message": {"content": [{"type": "text", "text": text}]}}


def command(text):
    return {
        "type": "assistant",
        "message": {"content": [{"name": "Bash", "input": {"command": text}}]},
    }


def boundary(prefix, limit):
    return (
        prefix
        + "x" * (limit - len(prefix) - 26)
        + " https://u:SYNTHETIC_TAIL"
        + "z" * 40
        + "@host.invalid"
    )


def synthetic_url(userinfo, scheme="https"):
    return f"{scheme}://{userinfo}@host.invalid"


class ReportEvidenceTests(unittest.TestCase):
    def test_saved_reports_redact_before_each_lossy_transformation(self):
        cases = (
            ([message("user", boundary("do it ", 220))], "User Signals"),
            (
                [message("assistant", boundary("Should I do it? ", 220))],
                "Assistant Routing Questions",
            ),
            ([command(boundary("deploy ", 100))] * 2, "1. Command:"),
            ([command(boundary("deploy ", 80))] * 3, "Repeated 3x"),
            (
                [
                    message("user", "Inspect only"),
                    message(
                        "assistant",
                        "I will also create " + synthetic_url("u:SYNTHETIC_TAIL.more"),
                    ),
                ],
                "Expansion:",
            ),
            (
                [
                    message(
                        "assistant",
                        "export URL=" + synthetic_url("u:SYNTHETIC_TAIL:1234", "http"),
                    )
                ],
                "Value:",
            ),
            (
                [message("assistant", r'PASSWORD="prefix\"SYNTHETIC_TAIL"')],
                "Credential assignment detected",
            ),
            (
                [command("env 'PASSWORD=prefix SYNTHETIC_TAIL' deploy")] * 3,
                "Repeated 3x",
            ),
        )
        for messages, expected in cases:
            with self.subTest(
                expected=expected
            ), tempfile.TemporaryDirectory() as raw_dir:
                root = Path(raw_dir)
                transcript = root / "synthetic.jsonl"
                write_jsonl(transcript, messages)
                with contextlib.redirect_stdout(io.StringIO()):
                    report = Path(
                        generate_report.generate_markdown_report(str(transcript), root)
                    )
                text = report.read_text()
                self.assertIn(expected, text)
                self.assertIn("[REDACTED]", text)
                self.assertNotIn("SYNTHETIC_TAIL", text)

    def test_console_evidence_and_ip_context_keep_full_source_boundaries(self):
        source = (
            'PASSWORD="' + "x" * 100 + "SYNTHETIC_TAIL 192.0.2.1 " + "x" * 100 + '"'
        )
        findings = detect_hardcoded_values(source)
        self.assertEqual(2, len(findings))
        self.assertNotIn("192.0.2.1", json.dumps(findings))
        self.assertNotIn("SYNTHETIC_TAIL", json.dumps(findings))
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "synthetic.jsonl"
            error = (
                "error "
                + "x" * 230
                + " https://u:SYNTHETIC_TAIL"
                + "z" * 300
                + "@host.invalid"
            )
            write_jsonl(
                transcript,
                [
                    message("assistant", source),
                    {
                        "type": "assistant",
                        "message": {
                            "content": [{"type": "tool_result", "content": error}]
                        },
                    },
                ],
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                print_anti_patterns(analyze_conversation(str(transcript)))
            self.assertIn("ERRORS ENCOUNTERED", output.getvalue())
            self.assertIn("[REDACTED]", output.getvalue())
            self.assertNotIn("SYNTHETIC_TAIL", output.getvalue())

    def test_redaction_does_not_merge_distinct_raw_commands(self):
        commands = [
            command("deploy --token first-value"),
            command("deploy --token second-value"),
        ]
        self.assertEqual([], find_retry_without_diagnosis(commands))
        with tempfile.TemporaryDirectory() as raw_dir:
            transcript = Path(raw_dir) / "synthetic.jsonl"
            write_jsonl(transcript, commands)
            stats = analyze_conversation(str(transcript))
            self.assertEqual(2, len(stats.repeated_commands))
            self.assertEqual([1, 1], list(stats.repeated_commands.values()))

    def test_completed_stderr_is_redacted_before_normalization_truncates_it(self):
        result = generate_report._normalize_completed_item(
            {
                "payload": {
                    "item": {
                        "type": "CommandExecution",
                        "command": "deploy",
                        "stderr": boundary("error ", 2000),
                    }
                }
            }
        )
        self.assertNotIn("SYNTHETIC_TAIL", json.dumps(result))
        self.assertIn("[REDACTED]", json.dumps(result))


def write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )


class CodexNormalizationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
