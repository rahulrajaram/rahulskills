import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]


class CompletionTests(unittest.TestCase):
    def run_task(self, base, *arguments):
        env = dict(os.environ, OW_CONTINUATION_DIR=str(base / "state"))
        return subprocess.run([sys.executable, str(ROOT / "bin/ow-run"), *arguments],
                              env=env, capture_output=True, text=True, timeout=10)

    def test_exit_log_and_recipient_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            log = base / "logs/task.log"
            result = self.run_task(base, "sample", "--log", str(log), "--target-pid", str(os.getpid()),
                                   "--target-session", "ses_example", "--", sys.executable,
                                   "-c", "print('result'); raise SystemExit(7)")
            self.assertEqual(result.returncode, 7)
            record = json.loads(next((base / "state").glob("*.json")).read_text())
            self.assertEqual(record["exit_code"], 7)
            self.assertEqual(record["target_session"], "ses_example")
            self.assertEqual(record["target_pid"], os.getpid())
            self.assertEqual(log.read_text(), "result\n")
            self.assertEqual(next((base / "state").glob("*.json")).stat().st_mode & 0o777, 0o600)

    def test_bad_log_does_not_erase_child_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = self.run_task(base, "sample", "--log", str(base), "--", sys.executable, "-c", "pass")
            self.assertEqual(result.returncode, 0)
            record = json.loads(next((base / "state").glob("*.json")).read_text())
            self.assertTrue(record["log_warning"])
            self.assertIsNone(record["log"])

    def test_signal_exit_preserves_signal_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = self.run_task(base, "signal", "--", sys.executable,
                                   "-c", "import os,signal; os.kill(os.getpid(), signal.SIGTERM)")
            self.assertEqual(result.returncode, 143)
            record = json.loads(next((base / "state").glob("*.json")).read_text())
            self.assertEqual(record["exit_code"], -15)
            self.assertEqual(record["signal"], "signal 15")

    def test_missing_command_still_records_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = self.run_task(base, "sample", "--", str(base / "absent"))
            self.assertEqual(result.returncode, 127)
            self.assertEqual(json.loads(next((base / "state").glob("*.json")).read_text())["exit_code"], 127)

    def test_invalid_options_do_not_start_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for header in [("--log",), ("--target-pid", "invalid"), ("--target-pid", "-1")]:
                result = self.run_task(base, "sample", *header, "--", sys.executable, "-c", "raise Exception('ran')")
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((base / "state").exists())

    def test_preflight_does_not_overwrite_fixed_probe_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "state").mkdir()
            probe = base / "state/.ow-write-probe"
            probe.write_text("existing")
            self.assertEqual(self.run_task(base, "sample", "--", sys.executable, "-c", "pass").returncode, 0)
            self.assertEqual(probe.read_text(), "existing")


class ChildInspectorTests(unittest.TestCase):
    def test_pid_matching_is_exact(self):
        loader = SourceFileLoader("ow_child_test", str(ROOT / "bin/ow-child"))
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
        loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "plugin.log"
            log.write_text("time pid=12 tracking session=correct\ntime pid=123 tracking session=wrong\n")
            module.CONTINUATION_LOG = log
            self.assertEqual(module.session_for_pid("12"), "correct")

    def test_reads_fixture_database_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "store?#.db"
            with sqlite3.connect(db) as conn:
                conn.executescript("CREATE TABLE session(id, directory, time_updated); CREATE TABLE todo(session_id, content, status, position); CREATE TABLE part(session_id, time_created, data);")
                conn.execute("INSERT INTO session VALUES (?, ?, ?)", ("ses_demo", tmp, 0))
                conn.execute("INSERT INTO todo VALUES (?, ?, ?, ?)", ("ses_demo", "Inspect fixture", "pending", 0))
            original = hashlib.sha256(db.read_bytes()).hexdigest()
            result = subprocess.run([sys.executable, str(ROOT / "bin/ow-child"), "--session", "ses_demo", "--db", str(db)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Inspect fixture", result.stdout)
            self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(), original)


if __name__ == "__main__":
    unittest.main()
