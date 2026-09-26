import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import skill_profiles


class SkillProfileTests(unittest.TestCase):
    def test_bundle_includes_linked_repo_resources_and_excludes_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (root / "references").mkdir()
            (skill / "SKILL.md").write_text("[guide](../../references/guide.md)\nexample references/never.md\n")
            (skill / "run.sh").write_text("#!/bin/sh\necho ok\n")
            (skill / "run.sh").chmod(0o755)
            (skill / "__pycache__").mkdir()
            (skill / "__pycache__" / "x.pyc").write_bytes(b"cache")
            (root / "references" / "guide.md").write_text("guide")
            output = Path(tmp) / "bundle"
            report = skill_profiles.bundle(root, output, "pi", ("demo",), ("references/guide.md",))
            self.assertIn("references/guide.md", report["files"])
            self.assertEqual((output / "skills/demo/SKILL.md").read_text().splitlines()[0], "[guide](../../references/guide.md)")
            self.assertTrue((output / "skills/demo/run.sh").stat().st_mode & 0o111)
            self.assertFalse((output / "skills/demo/__pycache__").exists())
            self.assertFalse(report["findings"])

    def test_bundle_reports_host_only_symlink_without_copying_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("demo")
            outside = Path(tmp) / "outside.txt"
            outside.write_text("private")
            (skill / "private.txt").symlink_to(outside)
            output = Path(tmp) / "bundle"
            with self.assertRaisesRegex(ValueError, "reject symlinks"):
                skill_profiles.bundle(root, output, "codex", ("demo",))
            self.assertFalse((output / "skills/demo/private.txt").exists())

    def test_bundle_rejects_missing_payload_and_source_nested_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("demo")
            with self.assertRaisesRegex(ValueError, "Missing portable payload"):
                skill_profiles.bundle(root, Path(tmp) / "out", "pi", ("demo",), ("references/nope.md",))
            with self.assertRaisesRegex(ValueError, "outside the source"):
                skill_profiles.bundle(root, root / "out", "pi", ("demo",))

    def test_bundle_rejects_symlink_ancestor_in_declared_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("[payload](../../references/link/file.txt)")
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "file.txt").write_text("secret")
            (root / "references").mkdir()
            (root / "references" / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                skill_profiles.bundle(root, Path(tmp) / "out", "pi", ("demo",), ("references/link/file.txt",))

    def test_profiles_keep_design_optional_and_runtime_exclusions(self):
        root = skill_profiles.ROOT
        core = skill_profiles.select(root, "codex", [], [])
        design = skill_profiles.select(root, "codex", ["design"], [])
        self.assertNotIn("figma", core)
        self.assertNotIn("figma-implement-design", core)
        self.assertNotIn("tui-web-design-orchestrator", core)
        self.assertIn("figma", design)
        self.assertNotIn("skill-creator", core)  # Codex owns this runtime skill.

    def test_chasm_profiles_are_additive_and_keep_host_defaults(self):
        root = skill_profiles.ROOT
        for runtime in ("pi", "codex", "claude", "opencode"):
            core = skill_profiles.select(root, runtime, [], [])
            guest = skill_profiles.select(root, runtime, ["chasm-development"], [])
            admin = skill_profiles.select(root, runtime, ["chasm-admin"], [])
            self.assertEqual(set(guest) - set(core), {"new-worktree-feature", "worktree-salvage"})
            self.assertEqual(admin, ("chasm-migrate",))
            self.assertNotIn("chasm-migrate", core)
            self.assertNotIn("new-worktree-feature", core)
            self.assertNotIn("worktree-salvage", core)
        self.assertEqual(skill_profiles.select(root, "pi", [], []), skill_profiles.select(root, "pi", ["core"], []))

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

    def test_dual_runtime_bundle_migration_keeps_unmanaged_and_shared_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            common = Path(tmp) / "common-bundle"
            pi_only = Path(tmp) / "pi-bundle"
            for name in ("alpha", "beta"):
                (common / "skills" / name).mkdir(parents=True)
                (common / "skills" / name / "SKILL.md").write_text(f"{name}\n")
            (common / "references").mkdir()
            (common / "references" / "shared.md").write_text("shared")
            (pi_only / "skills" / "skill-creator").mkdir(parents=True)
            (pi_only / "skills" / "skill-creator" / "SKILL.md").write_text("creator")
            (pi_only / "references").mkdir()
            (pi_only / "references" / "contract.md").write_text("contract")
            agents = Path(tmp) / "guest" / ".agents"
            pi = Path(tmp) / "guest" / ".pi" / "agent"
            unmanaged = agents / "skills" / "local-only"
            unmanaged.mkdir(parents=True)
            (unmanaged / "SKILL.md").write_text("keep")
            common_names = ("alpha", "beta")
            common_changes = skill_profiles.migration(root, common, agents, common_names)
            skill_profiles.apply(root, common, agents, common_changes)
            pi_changes = skill_profiles.migration(root, pi_only, pi, ("skill-creator",))
            skill_profiles.apply(root, pi_only, pi, pi_changes)
            self.assertEqual((agents / "skills/alpha/SKILL.md").read_text(), "alpha\n")
            self.assertEqual((agents / "references/shared.md").read_text(), "shared")
            self.assertEqual((pi / "skills/skill-creator/SKILL.md").read_text(), "creator")
            self.assertEqual((unmanaged / "SKILL.md").read_text(), "keep")

    def test_real_chasm_profiles_have_unique_guest_layout_and_conflict_preview(self):
        root = skill_profiles.ROOT
        common_names = skill_profiles.select(root, "codex", ["chasm-development"], [])
        # Codex owns skill-creator; pi-defects-harvester declares runtimes = ["pi"].
        pi_names = ("pi-defects-harvester", "skill-creator")
        self.assertEqual(len(set(common_names) | set(pi_names)), 61)
        self.assertIn("agent-stall-triage", common_names)
        self.assertEqual(set(common_names) & set(pi_names), set())
        for runtime in ("pi", "codex", "claude", "opencode"):
            selected = set(skill_profiles.select(root, runtime, ["chasm-development"], []))
            self.assertTrue(set(common_names) <= selected | {"skill-creator"})
            self.assertIn("new-worktree-feature", selected)
            self.assertIn("worktree-salvage", selected)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            common_bundle = base / "common"
            pi_bundle = base / "pi-only"
            skill_profiles.bundle(root, common_bundle, "codex", common_names,
                                  skill_profiles.declared_payloads(root, common_names))
            skill_profiles.bundle(root, pi_bundle, "pi", pi_names,
                                  skill_profiles.declared_payloads(root, pi_names))
            agents = base / ".agents"
            pi_home = base / ".pi" / "agent"
            unmanaged = agents / "skills" / "local-only"
            unmanaged.mkdir(parents=True)
            (unmanaged / "SKILL.md").write_text("keep")
            changes = skill_profiles.migration(root, common_bundle, agents, common_names)
            self.assertFalse(any(change.action == "blocked" for change in changes))
            skill_profiles.apply(root, common_bundle, agents, changes)
            pi_changes = skill_profiles.migration(root, pi_bundle, pi_home, pi_names)
            skill_profiles.apply(root, pi_bundle, pi_home, pi_changes)
            self.assertTrue((agents / "skills/new-worktree-feature/SKILL.md").is_file())
            self.assertTrue((pi_home / "skills/skill-creator/SKILL.md").is_file())
            self.assertEqual((unmanaged / "SKILL.md").read_text(), "keep")
            conflict = pi_home / "skills/skill-creator/SKILL.md"
            conflict.write_text("user copy")
            blocked = skill_profiles.migration(root, pi_bundle, pi_home, pi_names)
            self.assertTrue(any(change.action == "blocked" for change in blocked))

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


class RuntimeSupportTests(unittest.TestCase):
    @staticmethod
    def _fixture(root: Path, catalog: str, exclusions: dict[str, str] | None = None) -> None:
        for name in ("alpha", "pionly", "init"):
            (root / "skills" / name).mkdir(parents=True)
            (root / "skills" / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
        (root / "capabilities").mkdir()
        (root / "capabilities/install-profiles.toml").write_text(
            'default = "core"\n[profiles]\ncore = ["alpha", "pionly", "init"]\n')
        (root / "capabilities/skills.toml").write_text(catalog)
        (root / "runtime-exclusions").mkdir()
        for runtime, text in (exclusions or {}).items():
            (root / "runtime-exclusions" / f"{runtime}.txt").write_text(text)

    def test_runtimes_field_gates_selection_per_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root, '[skills.pionly]\nruntimes = ["pi"]\n')
            self.assertIn("pionly", skill_profiles.select(root, "pi", [], []))
            for runtime in ("claude", "codex", "opencode"):
                self.assertNotIn("pionly", skill_profiles.select(root, runtime, [], []))
                self.assertIn("alpha", skill_profiles.select(root, runtime, [], []))
            # Explicit selection cannot install an unsupported runtime copy.
            self.assertEqual(skill_profiles.select(root, "claude", [], ["pionly"]), ())

    def test_invalid_runtimes_fail_closed(self):
        for catalog in ('[skills.pionly]\nruntimes = ["vscode"]\n',
                        '[skills.pionly]\nruntimes = []\n',
                        '[skills.pionly]\nruntimes = "pi"\n',
                        '[skills.pionly.modes.x]\nruntimes = ["nope"]\n'):
            with self.subTest(catalog=catalog), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self._fixture(root, catalog)
                with self.assertRaisesRegex(ValueError, "runtime"):
                    skill_profiles.select(root, "pi", [], [])

    def test_claude_exclusions_block_builtin_names_only_for_claude(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root, "", {"claude": "# built-ins\ninit\n"})
            self.assertNotIn("init", skill_profiles.select(root, "claude", [], []))
            self.assertIn("init", skill_profiles.select(root, "codex", [], []))

    def test_real_catalog_runtimes(self):
        root = skill_profiles.ROOT
        support = skill_profiles.runtime_support(root)
        self.assertEqual(support["pi-defects-harvester"], frozenset({"pi"}))
        self.assertIn("pi-defects-harvester", skill_profiles.select(root, "pi", [], []))
        for runtime in ("claude", "codex", "opencode"):
            self.assertNotIn("pi-defects-harvester", skill_profiles.select(root, runtime, [], []))

    def test_real_claude_exclusions_do_not_shadow_package_skills(self):
        root = skill_profiles.ROOT
        builtins = skill_profiles.exclusions(root, "claude") - skill_profiles.exclusions(root, "__none__")
        self.assertTrue({"init", "review", "security-review", "simplify", "loop"} <= builtins)
        packaged = {path.name for path in (root / "skills").iterdir() if path.is_dir()}
        self.assertEqual(builtins & packaged, set(), "package skill collides with a Claude built-in")


class LedgerAdoptionTests(unittest.TestCase):
    def _install(self, tmp: Path, adopt: bool = False):
        root = tmp / "checkout"
        source = tmp / "assembled"
        destination = tmp / "runtime"
        (source / "skills" / "demo").mkdir(parents=True, exist_ok=True)
        (source / "skills" / "demo" / "SKILL.md").write_text("v1")
        changes = skill_profiles.migration(root, source, destination, ("demo",), adopt_source=adopt)
        skill_profiles.apply(root, source, destination, changes, adopt_source=adopt)
        return source, destination

    def test_foreign_ledger_is_refused_by_default_and_adopted_explicitly(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            source, destination = self._install(tmp)
            (source / "skills" / "demo" / "SKILL.md").write_text("v2")
            worktree = tmp / "worktree"
            with self.assertRaisesRegex(ValueError, "another source.*--adopt-source"):
                skill_profiles.migration(worktree, source, destination, ("demo",))
            changes = skill_profiles.migration(worktree, source, destination, ("demo",), adopt_source=True)
            self.assertEqual([c.action for c in changes if c.path == "skills/demo"], ["update"])
            skill_profiles.apply(worktree, source, destination, changes, adopt_source=True)
            ledger = json.loads((destination / skill_profiles.LEDGER).read_text())
            self.assertEqual(ledger["source"], str(worktree.resolve()))
            self.assertEqual((destination / "skills/demo/SKILL.md").read_text(), "v2")
            # Re-rooted: no flag needed from the adopting checkout any more.
            skill_profiles.migration(worktree, source, destination, ("demo",))

    def test_adoption_still_preserves_user_modified_entries(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            source, destination = self._install(tmp)
            (destination / "skills/demo/SKILL.md").write_text("user edit")
            changes = skill_profiles.migration(tmp / "worktree", source, destination, ("demo",), adopt_source=True)
            self.assertEqual([c.action for c in changes if c.path == "skills/demo"], ["blocked"])

    def test_unsupported_ledger_version_is_refused_even_when_adopting(self):
        with tempfile.TemporaryDirectory() as raw:
            destination = Path(raw)
            (destination / skill_profiles.LEDGER).write_text(json.dumps({"version": 9, "source": "/x", "entries": {}}))
            with self.assertRaisesRegex(ValueError, "version"):
                skill_profiles.load_ownership(destination, Path(raw) / "root", adopt_source=True)


if __name__ == "__main__":
    unittest.main()
