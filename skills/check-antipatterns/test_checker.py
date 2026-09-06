import json
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
