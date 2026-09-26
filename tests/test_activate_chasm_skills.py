from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from activate_chasm_skills import apply, prepare


def bundle_at(root: Path, skills: dict[str, str], references: dict[str, str] | None = None) -> Path:
    for name, body in skills.items():
        skill = root / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(body)
    for name, body in (references or {}).items():
        item = root / "references" / name
        item.parent.mkdir(parents=True, exist_ok=True)
        item.write_text(body)
    return root


def fixture(tmp_path: Path, runtime: str = "codex") -> tuple[Path, Path, Path]:
    home = tmp_path / "home"
    snapshot_root = tmp_path / "snapshots"
    bundle = bundle_at(tmp_path / "bundle", {"new-skill": "new bundle skill\n"}, {"guide.md": "new ref\n"})
    return home, snapshot_root, bundle


def active_link(home: Path, runtime: str) -> Path:
    if runtime == "codex":
        return home / ".codex/skills/host-synced"
    return home / ".pi/agent/skills/host-synced"


def seed_snapshot(home: Path, root: Path, runtime: str, skills: dict[str, str],
                  refs: dict[str, str] | None = None) -> Path:
    digest = "a" * 64
    snapshot = root / runtime / digest
    for name, body in skills.items():
        folder = snapshot / "skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(body)
    for name, body in (refs or {}).items():
        file = snapshot / "references" / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(body)
    link = active_link(home, runtime)
    link.parent.mkdir(parents=True)
    link.symlink_to(snapshot / "skills")
    return snapshot


class ActivateChasmSkillsTests(unittest.TestCase):
  def test_dry_run_does_not_mutate_and_apply_composes_then_reports_rollback(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path)
      old = seed_snapshot(home, snapshots, "codex", {"keep-me": "old\n", "new-skill": "old skill\n"},
                          {"prior.md": "prior ref\n"})
      # The replacement must remove stale files and a second manifest.
      stale = old / "skills/new-skill/stale.txt"
      stale.write_text("stale\n")
      (old / "skills/new-skill/skill.md").write_text("second manifest\n")
      plan = prepare("codex", bundle, home, snapshots)
      self.assertEqual(active_link(home, "codex").resolve(), old / "skills")
      self.assertFalse((snapshots / "codex" / plan["digest"]).exists())

      final, rollback, archive = apply(plan)
      self.assertEqual(rollback, old / "skills")
      self.assertIsNone(archive)
      self.assertEqual(active_link(home, "codex").resolve(), final / "skills")
      self.assertEqual((final / "skills/keep-me/SKILL.md").read_text(), "old\n")
      self.assertEqual((final / "skills/new-skill/SKILL.md").read_text(), "new bundle skill\n")
      self.assertFalse((final / "skills/new-skill/stale.txt").exists())
      self.assertFalse((final / "skills/new-skill/skill.md").exists())
      self.assertEqual((final / "references/prior.md").read_text(), "prior ref\n")
      self.assertEqual((final / "references/guide.md").read_text(), "new ref\n")
      self.assertEqual((old / "skills/keep-me/SKILL.md").read_text(), "old\n")


  def test_pi_archives_broken_links_and_duplicate_names_but_keeps_unique_entries(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path, "pi")
      old = seed_snapshot(home, snapshots, "pi", {"old-skill": "old\n"})
      root = home / ".pi/agent/skills"
      duplicate = root / "new-skill"
      duplicate.mkdir()
      (duplicate / "SKILL.md").write_text("legacy duplicate\n")
      unique = root / "pi-only"
      unique.mkdir()
      (unique / "SKILL.md").write_text("unique\n")
      broken = root / "gone-skill"
      broken.symlink_to(home / "deleted-source")

      plan = prepare("pi", bundle, home, snapshots)
      self.assertEqual(set(plan["archive_candidates"]), {duplicate, broken})
      final, rollback, archive = apply(plan)
      self.assertEqual(rollback, old / "skills")
      self.assertIsNotNone(archive)
      self.assertEqual((archive / "new-skill/SKILL.md").read_text(), "legacy duplicate\n")
      self.assertTrue((archive / "gone-skill").is_symlink())
      self.assertFalse(duplicate.exists())
      self.assertFalse(os.path.lexists(broken))
      self.assertEqual((unique / "SKILL.md").read_text(), "unique\n")
      self.assertEqual(active_link(home, "pi").resolve(), final / "skills")


  def test_rejects_nonmanaged_active_link(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path)
      link = active_link(home, "codex")
      link.parent.mkdir(parents=True)
      outside = tmp_path / "outside"
      outside.mkdir()
      link.symlink_to(outside)
      with self.assertRaisesRegex(ValueError, "outside managed snapshot"):
          prepare("codex", bundle, home, snapshots)


  def test_rejects_invalid_bundle_skill_name_or_manifest(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path)
      (bundle / "skills/new-skill/SKILL.md").unlink()
      (bundle / "skills/new-skill/README.md").write_text("not a skill manifest")
      with self.assertRaisesRegex(ValueError, "exactly one SKILL.md"):
          prepare("codex", bundle, home, snapshots)


  def test_rejects_bundle_symlink_escape(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path)
      outside = tmp_path / "outside.md"
      outside.write_text("outside")
      (bundle / "skills/new-skill/outside.md").symlink_to(outside)
      with self.assertRaisesRegex(ValueError, "symlinks are not allowed"):
          prepare("codex", bundle, home, snapshots)


  def test_reactivation_is_idempotent(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path)
      first_plan = prepare("codex", bundle, home, snapshots)
      first, _, _ = apply(first_plan)
      second_plan = prepare("codex", bundle, home, snapshots)
      self.assertEqual(second_plan["digest"], first.name)
      second, rollback, _ = apply(second_plan)
      self.assertEqual(second, first)
      self.assertEqual(rollback, first / "skills")

  def test_refuses_corrupt_existing_hashed_snapshot(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      tmp_path = Path(temporary)
      home, snapshots, bundle = fixture(tmp_path)
      plan = prepare("codex", bundle, home, snapshots)
      occupied = snapshots / "codex" / plan["digest"]
      (occupied / "skills").mkdir(parents=True)
      (occupied / "skills/corrupt").write_text("wrong content")
      with self.assertRaisesRegex(ValueError, "does not match its digest"):
          apply(plan)


if __name__ == "__main__":
    unittest.main()
