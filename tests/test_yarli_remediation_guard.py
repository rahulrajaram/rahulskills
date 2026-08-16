from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "yarli-execution-loop"
    / "scripts"
    / "yarli-remediate-stale-runs.sh"
)
BASH = "/bin/bash"


def write_fake_yarli(tmp_path: Path, updated: str) -> dict[str, str]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    missing_workspace = tmp_path / "missing-workspace"
    yarli = fake_bin / "yarli"
    yarli.write_text(
        f"""#!/bin/bash
if [[ "$1 $2" == "run list" ]]; then
  printf 'RUN ID STATE\\n------ -----\\nrun-1 RunActive\\n'
elif [[ "$1 $2" == "run status" ]]; then
  printf 'State: RunActive\\nUpdated: {updated}\\nworkspace_dir: {missing_workspace}\\n'
else
  exit 2
fi
""",
        encoding="utf-8",
    )
    yarli.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    return env


class YarliRemediationGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_fix_requires_explicit_confirmation(self) -> None:
        result = subprocess.run(
            [BASH, str(SCRIPT), str(self.root), "--fix"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--fix requires --confirmed", result.stderr)

    def test_default_mode_is_read_only(self) -> None:
        result = subprocess.run(
            [BASH, str(SCRIPT), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
            env={"PATH": ""},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "yarli unavailable")

    def test_unknown_update_age_is_not_treated_as_stale(self) -> None:
        result = subprocess.run(
            [BASH, str(SCRIPT), str(self.root), "--min-age-seconds", "1"],
            check=False,
            capture_output=True,
            text=True,
            env=write_fake_yarli(self.root, "not-a-timestamp"),
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("stale_runs_detected: 0", result.stdout)

    def test_old_missing_workspace_is_detected(self) -> None:
        result = subprocess.run(
            [BASH, str(SCRIPT), str(self.root), "--min-age-seconds", "1"],
            check=False,
            capture_output=True,
            text=True,
            env=write_fake_yarli(self.root, "2000-01-01 00:00:00"),
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("stale_run_detected: run_id=run-1", result.stdout)
        self.assertIn("stale_runs_detected: 1", result.stdout)
