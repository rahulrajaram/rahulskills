import subprocess
import tempfile
import unittest
from pathlib import Path


class BackupRootTests(unittest.TestCase):
    def test_fixed_clock_allocations_are_unique(self) -> None:
        script = Path(__file__).resolve().parent / "stitch-skills.sh"
        with tempfile.TemporaryDirectory() as raw_dir:
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    """
                    source "$1"
                    date() { printf '20260101T000000Z\\n'; }
                    first="$(new_backup_root "$2" build)"
                    second="$(new_backup_root "$2" build)"
                    printf '%s\\n%s\\n' "$first" "$second"
                    """,
                    "bash",
                    str(script),
                    raw_dir,
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            first, second = map(Path, result.stdout.splitlines())
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())


if __name__ == "__main__":
    unittest.main()
