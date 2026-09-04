import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_report
from analyzer import analyze_conversation
from patterns import find_retry_without_diagnosis, is_normal_retry_command


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
