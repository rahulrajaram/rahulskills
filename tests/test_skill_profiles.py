import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import skill_profiles


class SkillProfileTests(unittest.TestCase):
    def test_profiles_keep_design_optional_and_runtime_exclusions(self):
        root = skill_profiles.ROOT
        core = skill_profiles.select(root, "codex", [], [])
        design = skill_profiles.select(root, "codex", ["design"], [])
        self.assertNotIn("figma", core)
        self.assertNotIn("figma-implement-design", core)
        self.assertNotIn("tui-web-design-orchestrator", core)
        self.assertIn("figma", design)
        self.assertNotIn("skill-creator", core)  # Codex owns this runtime skill.

    def test_individual_selection_is_narrow_and_all_is_union(self):
        root = skill_profiles.ROOT
        one = skill_profiles.select(root, "claude", [], ["figma"])
        everything = skill_profiles.select(root, "claude", ["all"], [])
        self.assertEqual(one, ("figma",))
        self.assertIn("figma-implement-design", everything)
        self.assertIn("tui-web-design-orchestrator", everything)

    def test_preview_preserves_unmanaged_and_explicitly_removes_owned(self):
        root = skill_profiles.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "runtime"
            source = Path(tmp) / "source"
            (source / "skills" / "demo").mkdir(parents=True)
            (source / "skills" / "demo" / "SKILL.md").write_text("demo")
            (destination / "skills").mkdir(parents=True)
            (destination / "skills" / "unmanaged").mkdir()
            names = ("demo",)
            changes = skill_profiles.migration(root, source, destination, names)
            self.assertEqual(changes[0].action, "add")
            self.assertTrue(any(c.path == "skills/unmanaged" and c.action == "retain" for c in changes))

            managed = destination / "skills" / "old"
            managed.mkdir()
            ledger = {"version": 1, "source": str(root.resolve()),
                      "entries": {"skills/old": skill_profiles.fingerprint(managed)}}
            (destination / skill_profiles.LEDGER).write_text(json.dumps(ledger))
            removal = skill_profiles.migration(root, source, destination, names, remove=("old",))
            self.assertTrue(any(c.path == "skills/old" and c.action == "remove" for c in removal))

    def test_apply_rolls_back_when_ownership_commit_fails(self):
        root = skill_profiles.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            destination = Path(tmp) / "runtime"
            origin = destination / "skills" / "demo"
            origin.mkdir(parents=True)
            (origin / "SKILL.md").write_text("old")
            (source / "skills" / "demo").mkdir(parents=True)
            (source / "skills" / "demo" / "SKILL.md").write_text("new")
            ledger = {"version": 1, "source": str(root.resolve()),
                      "entries": {"skills/demo": skill_profiles.fingerprint(origin)}}
            ledger_path = destination / skill_profiles.LEDGER
            ledger_path.write_text(json.dumps(ledger))
            ledger_before = ledger_path.read_bytes()
            changes = skill_profiles.migration(root, source, destination, ("demo",))
            with mock.patch.object(skill_profiles, "write_ownership", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    skill_profiles.apply(root, source, destination, changes)
            self.assertEqual((origin / "SKILL.md").read_text(), "old")
            self.assertEqual(ledger_path.read_bytes(), ledger_before)
            self.assertFalse(any(destination.glob("skill-backups/migration-stage-*")))

    def test_apply_copy_failure_leaves_user_entry_and_no_stage(self):
        root = skill_profiles.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            destination = Path(tmp) / "runtime"
            origin = destination / "skills" / "demo"
            origin.mkdir(parents=True)
            (origin / "SKILL.md").write_text("old")
            (source / "skills" / "demo").mkdir(parents=True)
            (source / "skills" / "demo" / "SKILL.md").write_text("new")
            ledger = {"version": 1, "source": str(root.resolve()),
                      "entries": {"skills/demo": skill_profiles.fingerprint(origin)}}
            (destination / skill_profiles.LEDGER).write_text(json.dumps(ledger))
            changes = skill_profiles.migration(root, source, destination, ("demo",))
            with mock.patch.object(skill_profiles.shutil, "copytree", side_effect=OSError("copy failed")):
                with self.assertRaises(OSError):
                    skill_profiles.apply(root, source, destination, changes)
            self.assertEqual((origin / "SKILL.md").read_text(), "old")
            self.assertFalse(any(destination.glob("skill-backups/migration-stage-*")))


if __name__ == "__main__":
    unittest.main()
