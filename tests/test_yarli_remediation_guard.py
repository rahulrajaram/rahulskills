from __future__ import annotations

from pathlib import Path
import subprocess


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "yarli-execution-loop"
    / "scripts"
    / "yarli-remediate-stale-runs.sh"
)
BASH = "/bin/bash"


def test_fix_requires_explicit_confirmation(tmp_path: Path) -> None:
    result = subprocess.run(
        [BASH, str(SCRIPT), str(tmp_path), "--fix"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--fix requires --confirmed" in result.stderr


def test_default_mode_is_read_only(tmp_path: Path) -> None:
    result = subprocess.run(
        [BASH, str(SCRIPT), str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": ""},
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "yarli unavailable"
