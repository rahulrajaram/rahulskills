"""Claude runtime coverage for scripts/activate_chasm_skills.py."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from activate_chasm_skills import CLAUDE_LEDGER, apply, main, prepare


def write_bundle(root: Path, skills: dict[str, str], references: dict[str, str] | None = None) -> Path:
    for name, body in skills.items():
        (root / "skills" / name).mkdir(parents=True, exist_ok=True)
        (root / "skills" / name / "SKILL.md").write_text(body)
    for name, body in (references or {}).items():
        (root / "references").mkdir(parents=True, exist_ok=True)
        (root / "references" / name).write_text(body)
    return root


class ClaudeActivationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.snapshots = self.tmp / "snapshots"
        self.config = self.home / ".claude"
        env = mock.patch.dict(os.environ, {}, clear=False)
        env.start()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)
        self.addCleanup(env.stop)
        self.addCleanup(self._tmp.cleanup)

    def activate(self, bundle: Path, **kwargs):
        return apply(prepare("claude", bundle, self.home, self.snapshots, **kwargs))

    def test_projects_real_copies_directly_under_claude_skills(self) -> None:
        bundle = write_bundle(self.tmp / "b1", {"demo": "v1\n"}, {"guide.md": "ref\n"})
        final, rollback, archive = self.activate(bundle)
        self.assertIsNone(rollback)
        self.assertIsNone(archive)
        skill = self.config / "skills/demo"
        self.assertTrue(skill.is_dir() and not skill.is_symlink())
        self.assertEqual((skill / "SKILL.md").read_text(), "v1\n")
        # ../../references links from a skill resolve lexically and physically.
        self.assertEqual((skill / "../../references/guide.md").read_text(), "ref\n")
        self.assertFalse(os.path.lexists(self.config / "skills/host-synced"))
        self.assertEqual((self.snapshots / "claude/active").resolve(), final / "skills")
        ledger = json.loads((self.config / CLAUDE_LEDGER).read_text())
        self.assertEqual(set(ledger["entries"]), {"skills/demo", "references/guide.md"})

    def test_user_skills_are_preserved_and_name_collisions_refuse_without_writes(self) -> None:
        mine = self.config / "skills/my-own"
        mine.mkdir(parents=True)
        (mine / "SKILL.md").write_text("user skill\n")
        clash = self.config / "skills/demo"
        clash.mkdir()
        (clash / "SKILL.md").write_text("user demo\n")
        bundle = write_bundle(self.tmp / "b1", {"demo": "v1\n", "other": "o\n"})
        plan = prepare("claude", bundle, self.home, self.snapshots)
        self.assertIn(("skills/demo", "blocked"), [(k, a) for k, a, _ in plan["projection"]])
        with self.assertRaisesRegex(ValueError, "skills/demo"):
            apply(plan)
        self.assertEqual((clash / "SKILL.md").read_text(), "user demo\n")
        self.assertFalse((self.config / "skills/other").exists())
        self.assertFalse(os.path.lexists(self.snapshots / "claude/active"))
        clash_backup = self.tmp / "moved-demo"
        clash.rename(clash_backup)
        self.activate(bundle)
        self.assertEqual((mine / "SKILL.md").read_text(), "user skill\n")
        self.assertNotIn("skills/my-own", json.loads((self.config / CLAUDE_LEDGER).read_text())["entries"])

    def test_updates_owned_entries_but_refuses_local_edits(self) -> None:
        self.activate(write_bundle(self.tmp / "b1", {"demo": "v1\n", "keep": "k\n"}))
        (self.config / "skills/demo/stale.txt").write_text("x")  # local edit
        with self.assertRaisesRegex(ValueError, "skills/demo"):
            prepare_and_apply = prepare("claude", write_bundle(self.tmp / "b2", {"demo": "v2\n"}),
                                        self.home, self.snapshots)
            apply(prepare_and_apply)
        self.assertEqual((self.config / "skills/demo/SKILL.md").read_text(), "v1\n")
        (self.config / "skills/demo/stale.txt").unlink()
        final, rollback, _ = self.activate(self.tmp / "b2")
        self.assertIsNotNone(rollback)
        self.assertEqual((self.config / "skills/demo/SKILL.md").read_text(), "v2\n")
        # The prior generation's other skills are composed forward.
        self.assertEqual((self.config / "skills/keep/SKILL.md").read_text(), "k\n")
        second = prepare("claude", self.tmp / "b2", self.home, self.snapshots)
        self.assertTrue(all(action == "unchanged" for _, action, _ in second["projection"]))
        self.assertEqual(apply(second)[0], final)

    def test_claude_config_dir_env_and_flag(self) -> None:
        bundle = write_bundle(self.tmp / "b1", {"demo": "v1\n"})
        env_config = self.tmp / "env-claude"
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(env_config)}):
            self.activate(bundle)
        self.assertTrue((env_config / "skills/demo/SKILL.md").is_file())
        self.assertFalse(self.config.exists())
        flag_config = self.tmp / "flag-claude"
        code = main(["--runtime", "claude", "--bundle", str(bundle), "--home", str(self.home),
                     "--snapshot-root", str(self.snapshots), "--claude-config-dir", str(flag_config), "--apply"])
        self.assertEqual(code, 0)
        self.assertTrue((flag_config / "skills/demo/SKILL.md").is_file())

    def test_refuses_symlinked_discovery_root(self) -> None:
        elsewhere = self.tmp / "elsewhere"
        elsewhere.mkdir()
        self.config.mkdir()
        (self.config / "skills").symlink_to(elsewhere)
        with self.assertRaisesRegex(ValueError, "real directory"):
            prepare("claude", write_bundle(self.tmp / "b1", {"demo": "v1\n"}), self.home, self.snapshots)


if __name__ == "__main__":
    unittest.main()
