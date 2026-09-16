import tempfile
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tests import larger_move_qualification as runner


class LargerMoveQualificationRunnerTests(unittest.TestCase):
    def test_main_writes_only_declared_report_to_configured_output(self):
        report = {"schema_version": 1, "passed": True, "epoch": 1}
        with tempfile.TemporaryDirectory() as directory, patch.object(
            runner, "qualify", return_value=(report, 0)
        ), patch.dict(runner.os.environ, {"METABUILDER_OUTPUT_DIR": directory}, clear=False):
            self.assertEqual(runner.main(["--epoch", "1", "--campaign-id", "campaign", "--run-id", "run", "--policy-digest", "a" * 64, "--source-commit", "b" * 40]), 0)
            output = Path(directory) / "qualification.json"
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)
            self.assertEqual(list(Path(directory).iterdir()), [output])

    def test_main_preserves_failure_status_and_report(self):
        report = {"schema_version": 1, "passed": False, "epoch": 1, "failure": "fixture"}
        with tempfile.TemporaryDirectory() as directory, patch.object(
            runner, "qualify", return_value=(report, 1)
        ), patch.dict(runner.os.environ, {"METABUILDER_OUTPUT_DIR": directory}, clear=False):
            self.assertEqual(runner.main(["--epoch", "1", "--campaign-id", "campaign", "--run-id", "run", "--policy-digest", "a" * 64, "--source-commit", "b" * 40]), 1)
            self.assertIn('"passed": false', (Path(directory) / "qualification.json").read_text())
            self.assertIn('"failure": "fixture"', (Path(directory) / "qualification.json").read_text())

    def test_run_suites_retains_a_failing_suite(self):
        class FailingSuite:
            def run(self, result):
                result.testsRun += 1
                result.failures.append((self, "expected"))

        fake_module = SimpleNamespace()
        with patch.object(runner, "SUITE_MODULES", ("fake.suite",)), patch.object(
            runner.importlib, "import_module", return_value=fake_module
        ), patch.object(
            runner.unittest.TestLoader, "loadTestsFromModule", return_value=FailingSuite()
        ):
            result = runner._run_suites()
        self.assertFalse(result["passed"])
        self.assertEqual(result["tests_run"], 1)
        self.assertEqual(result["modules"][0]["status"], "failed")
        self.assertEqual(result["modules"][0]["failures"], 1)

    def test_rejected_learning_ingestion_fails_qualification(self):
        rejected = {"accepted": False, "diagnostics": [{"code": "invalid_record"}]}
        with patch.object(runner, "_run_suites", return_value={"passed": True}), patch.object(
            runner, "_learning_result", return_value=rejected
        ):
            report, status = runner.qualify(1, "campaign", "run", "a" * 64, "b" * 40)
        self.assertEqual(status, 1)
        self.assertEqual(report["learning_ingestion"]["status"], "failed")

    def test_invalid_source_commit_is_rejected_by_ingestion(self):
        with patch.object(runner, "_run_suites", return_value={"passed": True}):
            report, status = runner.qualify(1, "campaign", "run", "a" * 64, "z" * 40)
        self.assertEqual(status, 1)
        self.assertEqual(report["learning_ingestion"]["status"], "failed")

    def test_empty_suite_is_failed(self):
        class EmptySuite:
            def run(self, result):
                return None

        with patch.object(runner, "SUITE_MODULES", ("fake.empty",)), patch.object(
            runner.importlib, "import_module", return_value=SimpleNamespace()
        ), patch.object(runner.unittest.TestLoader, "loadTestsFromModule", return_value=EmptySuite()):
            result = runner._run_suites()
        self.assertFalse(result["passed"])
        self.assertEqual(result["modules"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
