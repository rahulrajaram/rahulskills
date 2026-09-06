"""Execute the documented library transaction with disposable fault injection."""

import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


DOCUMENT = (Path(__file__).parent / "skills/install-commithooks/SKILL.md").read_text()
SECTION = DOCUMENT.split("### Step 3:", 1)[1].split("### Step 4:", 1)[0]
TRANSACTION = re.search(r"```bash\n(.*?)\n```", SECTION, re.DOTALL).group(1)
MOCKS = r"""
realpath() {
  [[ "$FAULT" != resolve ]] || return 19
  command realpath "$@"
}
mktemp() {
  if [[ "$FAULT" == stage && "$*" == *'.lib-stage.'* ]]; then return 19; fi
  if [[ "$FAULT" == allocation && "$*" == *'commithooks-backups/'* ]]; then return 19; fi
  command mktemp "$@"
}
cp() {
  printf 'copy\n' >> "$TRACE"
  [[ "$FAULT" != copy ]] || return 19
  command cp "$@"
}
mkdir() {
  [[ "$FAULT" != mkdir ]] || return 19
  command mkdir "$@"
}
mv() {
  local source="${@: -2:1}"
  local destination="${@: -1}"
  if [[ "$source" == "$GIT_DIR/lib" ]]; then
    printf 'backup\n' >> "$TRACE"
    [[ "$FAULT" != backup ]] || return 19
  elif [[ "$source" == *'/.lib-stage.'* ]]; then
    printf 'publish\n' >> "$TRACE"
    [[ "$FAULT" != publish && "$FAULT" != rollback ]] || return 19
    if [[ "$FAULT" == collision ]]; then
      command mkdir "$destination"
      printf 'concurrent owner\n' > "$destination/concurrent.txt"
    fi
  else
    printf 'restore\n' >> "$TRACE"
    [[ "$FAULT" != rollback ]] || return 19
  fi
  command mv "$@"
}
"""


class LibraryTransactionTests(unittest.TestCase):
    def run_transaction(self, root, fault):
        git_dir = root / "git-metadata"
        (git_dir / "lib").mkdir(parents=True)
        (git_dir / "lib/old.txt").write_text("old library")
        source = root / "source"
        (source / "lib").mkdir(parents=True)
        if fault != "source":
            (source / "lib/common.sh").write_text("# complete new library\n")
        configured_git_dir = git_dir
        if fault == "symlink":
            configured_git_dir = root / "git-link"
            configured_git_dir.symlink_to(git_dir, target_is_directory=True)
        trace = root / "operations.log"
        result = subprocess.run(
            # The conditional call also suppresses inherited errexit. Every
            # failure must be handled explicitly by the documented transaction.
            [
                "bash",
                "-c",
                MOCKS
                + "\ninstall_example() {\n"
                + TRANSACTION
                + "\n}\nif install_example; then exit 0; else exit $?; fi",
            ],
            env={
                **os.environ,
                "GIT_DIR": str(configured_git_dir),
                "SOURCE": str(source),
                "FAULT": fault,
                "TRACE": str(trace),
            },
            capture_output=True,
            text=True,
            timeout=10,
        )
        return git_dir, result, trace.read_text().splitlines() if trace.exists() else []

    def test_prerequisite_failures_preserve_the_live_library(self):
        for fault in (
            "resolve",
            "symlink",
            "source",
            "stage",
            "copy",
            "mkdir",
            "allocation",
            "backup",
        ):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as raw_dir:
                git_dir, result, operations = self.run_transaction(Path(raw_dir), fault)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual("old library", (git_dir / "lib/old.txt").read_text())
                self.assertNotIn("publish", operations)
                self.assertFalse((git_dir / "lib/common.sh").exists())

    def test_success_publishes_complete_library_and_keeps_backup(self):
        with tempfile.TemporaryDirectory() as raw_dir:
            git_dir, result, operations = self.run_transaction(Path(raw_dir), "none")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(["copy", "backup", "publish"], operations)
            self.assertTrue((git_dir / "lib/common.sh").is_file())
            self.assertEqual(
                1, len(tuple(git_dir.glob("commithooks-backups/*/lib/old.txt")))
            )
            self.assertFalse((git_dir / "lib/old.txt").exists())

    def test_publication_failure_restores_old_library(self):
        with tempfile.TemporaryDirectory() as raw_dir:
            git_dir, result, operations = self.run_transaction(Path(raw_dir), "publish")
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("restore", operations[-1])
            self.assertTrue((git_dir / "lib/old.txt").is_file())
            self.assertEqual(1, len(tuple(git_dir.glob(".lib-stage.*/common.sh"))))

    def test_rollback_failure_keeps_both_recoverable_trees(self):
        with tempfile.TemporaryDirectory() as raw_dir:
            git_dir, result, _ = self.run_transaction(Path(raw_dir), "rollback")
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Restore failed", result.stderr)
            self.assertEqual(
                1, len(tuple(git_dir.glob("commithooks-backups/*/lib/old.txt")))
            )
            self.assertEqual(1, len(tuple(git_dir.glob(".lib-stage.*/common.sh"))))

    def test_publication_never_nests_in_a_concurrently_created_target(self):
        with tempfile.TemporaryDirectory() as raw_dir:
            git_dir, result, _ = self.run_transaction(Path(raw_dir), "collision")
            self.assertNotEqual(0, result.returncode)
            self.assertTrue((git_dir / "lib/concurrent.txt").is_file())
            self.assertEqual([], list((git_dir / "lib").glob(".lib-stage.*")))
            self.assertEqual(
                1, len(tuple(git_dir.glob("commithooks-backups/*/lib/old.txt")))
            )


if __name__ == "__main__":
    unittest.main()
