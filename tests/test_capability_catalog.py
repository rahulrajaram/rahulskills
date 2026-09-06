import unittest
import tempfile
from pathlib import Path
import sys
import tomllib
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import audit_catalog
import capability_health


ROOT = Path(__file__).parents[1]


class CapabilityCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "capabilities/skills.toml").open("rb") as stream:
            cls.manifest = tomllib.load(stream)

    def test_optional_tools_do_not_make_mode_unavailable(self):
        def missing(command):
            return None if command == "overwatch" else "/usr/bin/" + command
        with mock.patch.object(capability_health.shutil, "which", side_effect=missing):
            report = capability_health.evaluate(self.manifest, set())
        self.assertTrue(report["skills"]["test"]["available"])
        self.assertIn("overwatch", report["skills"]["test"]["missing_optional_commands"])
        self.assertEqual(report["skills"]["check-antipatterns"]["missing_commands"], [])
        self.assertIn("transcript", report["skills"]["check-antipatterns"]["modes"])

    def test_catalog_report_exposes_inventory_and_nonsemantic_limits(self):
        report = audit_catalog.audit([ROOT / "skills"], 400, ROOT / "skills")
        self.assertTrue(report["inventory"])
        self.assertIn("metadata_defaults", report)
        self.assertFalse(report["semantic_proof"])

    def test_inventory_classifies_canonical_generated_and_archive_lowercase_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            canonical = base / "skills" / "one"
            generated = base / "build" / "codex" / "skills" / "two"
            archived = base / "archives" / "old"
            for path, filename in ((canonical, "SKILL.md"), (generated, "SKILL.md"), (archived, "skill.md")):
                path.mkdir(parents=True)
                (path / filename).write_text("---\nname: %s\ndescription: x\n---\n" % path.name)
            (canonical / "ref.md").write_text("reference")
            (canonical / "SKILL.md").write_text("---\nname: one\ndescription: x\n---\n[ref](ref.md)\n")
            report = audit_catalog.audit([canonical.parent, generated.parent, archived.parent], 400, canonical.parent)
            kinds = {item["root_kind"] for item in report["inventory"]}
            self.assertEqual(kinds, {"canonical", "generated", "archive"})
            self.assertEqual(report["summary"]["broken_references"], 0)


if __name__ == "__main__":
    unittest.main()
