"""Execute the documented Bash recipes only in disposable Git repositories.

Requires Python 3, Bash, Git and an already installed git-filter-repo.
Run: python -m unittest discover -s tests -p test_history_rewrite_recipes.py -v
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def bash_recipe(path):
    return re.findall(r"```bash\n(.*?)```", (ROOT / path).read_text(), re.S)[0]


class HistoryRecipes(unittest.TestCase):
    def test_scoped_rewrites_and_recovery(self):
        for dependency in ("git", "bash", "git-filter-repo"):
            self.assertIsNotNone(shutil.which(dependency), f"Missing {dependency}; do not install implicitly")
        for mode in ("messages", "cleaner"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix="history-recipe-") as temporary:
                root = Path(temporary)
                repo = root / "repo"
                repo.mkdir()
                env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
                # Ignore caller repository/index/namespace overrides in the disposable fixture.
                for key in tuple(env):
                    if key.startswith("GIT_") and key not in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"):
                        del env[key]

                def git(*args, cwd=repo):
                    return subprocess.check_output(["git", *args], cwd=cwd, env=env)

                git("init", "--template=", "-b", "selected")
                git("config", "user.name", "Fixture")
                git("config", "user.email", "fixture@example.invalid")
                (repo / "retained.txt").write_text("BLOCKED_TEXT was here\nWHITELIST stays\n")
                (repo / "purged.txt").write_text("BLOCKED_TEXT obsolete\n")
                git("add", ".")
                git("commit", "-m", "EXACT OLD MESSAGE")
                original_first = git("rev-parse", "HEAD").strip().decode()
                (repo / "retained.txt").write_text("current version is clean\nWHITELIST stays\n")
                git("rm", "purged.txt")
                git("commit", "-am", f"retain hash {original_first}")
                original_head = git("rev-parse", "HEAD").strip().decode()
                git("branch", "unselected")
                git("tag", "private-original")
                before_refs = git("for-each-ref", "--format=%(refname) %(objectname)")
                before_reflog = git("reflog", "show", "--format=%H", "refs/heads/selected").splitlines()

                setup = bash_recipe("references/history-rewrite-safety.md")
                setup = setup.replace("refs/heads/REVIEWED_BRANCH", "refs/heads/selected")
                setup = setup.replace("backup_parent=/ABSOLUTE/PRIVATE/BACKUP/DIRECTORY", 'backup_parent="$FIXTURE_BACKUP_PARENT"')
                if mode == "messages":
                    rewrite = bash_recipe("skills/rewrite-commit-messages/SKILL.md")
                    rewrite = rewrite.replace("FULL_ORIGINAL_COMMIT_ID", original_first)
                    prepare = ""
                else:
                    rewrite = bash_recipe("skills/reference-cleaner/SKILL.md")
                    rewrite = rewrite.replace("REVIEWED/PURGED/PATH", "purged.txt")
                    prepare = """printf '%s\\n' 'literal:BLOCKED_TEXT==>CLEANED_TEXT' > "$backup_dir/reviewed-replacements.txt"
printf '%s\\n' 'commit.message = commit.message' > "$backup_dir/reviewed-message-callback.py"
"""
                result = subprocess.run(["bash", "-c", setup + "\n" + prepare + rewrite],
                                        cwd=repo, env=dict(env, FIXTURE_BACKUP_PARENT=str(root)),
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                backup = next(root.glob("history-rewrite.*"))
                recovery = backup / "recovery.git"
                self.assertEqual(git("rev-parse", "refs/heads/selected", cwd=recovery).strip().decode(), original_head)
                git("bundle", "verify", str(backup / "original.bundle"))
                self.assertEqual((backup / "refs-before").read_bytes(), before_refs)
                for ref in ("refs/heads/unselected", "refs/tags/private-original"):
                    self.assertEqual(git("rev-parse", ref).strip().decode(), original_head)
                self.assertTrue(set(before_reflog).issubset(set(git("reflog", "show", "--format=%H", "refs/heads/selected").splitlines())))
                self.assertEqual(git("status", "--porcelain"), b"")
                self.assertEqual(git("rev-list", "--count", "selected"), b"2\n")
                mapping = dict(line.split() for line in (repo / ".git/filter-repo/commit-map").read_text().splitlines()[1:])
                self.assertIn(original_first, mapping)
                self.assertIn(original_head, mapping)
                for old in (original_first, original_head):
                    new = mapping[old]
                    old_raw = git("cat-file", "commit", old, cwd=recovery)
                    new_raw = git("cat-file", "commit", new)
                    old_headers, old_message = old_raw.split(b"\n\n", 1)
                    new_headers, new_message = new_raw.split(b"\n\n", 1)
                    expected_message = b"EXACT NEW MESSAGE\n" if mode == "messages" and old == original_first else old_message
                    self.assertEqual(new_message, expected_message)
                    old_parents = [line[7:].decode() for line in old_headers.splitlines() if line.startswith(b"parent ")]
                    new_parents = [line[7:].decode() for line in new_headers.splitlines() if line.startswith(b"parent ")]
                    self.assertEqual(new_parents, [mapping.get(parent, parent) for parent in old_parents])
                    metadata = lambda headers: [line for line in headers.splitlines() if not line.startswith((b"tree ", b"parent "))]
                    self.assertEqual(metadata(old_headers), metadata(new_headers))
                    if mode == "messages":
                        self.assertEqual(git("rev-parse", old + "^{tree}", cwd=recovery), git("rev-parse", new + "^{tree}"))
                    else:
                        old_blob = git("show", old + ":retained.txt", cwd=recovery)
                        self.assertEqual(git("show", new + ":retained.txt"), old_blob.replace(b"BLOCKED_TEXT", b"CLEANED_TEXT"))
                        for entry in git("ls-tree", "-r", "-z", "--full-tree", new).split(b"\0"):
                            if not entry:
                                continue
                            meta, path = entry.split(b"\t", 1)
                            self.assertNotEqual(path, b"purged.txt")
                            self.assertNotIn(b"BLOCKED_TEXT", path)
                            _, kind, oid = meta.split()
                            if kind == b"blob":
                                self.assertNotIn(b"BLOCKED_TEXT", git("cat-file", "blob", oid.decode()))
                # The term exists only in an old retained-file version and the independent original.
                self.assertIn(b"BLOCKED_TEXT", git("show", original_first + ":retained.txt", cwd=recovery))


if __name__ == "__main__":
    unittest.main()
