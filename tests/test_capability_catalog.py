import unittest
import tempfile
import json
import subprocess
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

    def test_portable_admission_separates_required_and_optional_gaps(self):
        manifest = {
            "schema_version": 1,
            "skills": {
                "demo": {"commands": ["required"], "optional_commands": ["optional"]},
                "host": {"host_only": True},
            },
            "mcps": {},
        }
        def missing(command):
            return "/bin/" + command if command == "required" else None
        with mock.patch.object(capability_health.shutil, "which", side_effect=missing):
            report = capability_health.evaluate(manifest, set())
        admission = capability_health.admission(report)
        demo = next(item for item in admission["skills"] if item["name"] == "demo")
        host = next(item for item in admission["skills"] if item["name"] == "host")
        self.assertIsNone(demo["admissible"])
        self.assertEqual(demo["caller_missing_optional_commands"], ["optional"])
        self.assertFalse(host["admissible"])
        self.assertFalse(demo["mcp_functionality_verified"])
        self.assertIsNone(demo["declared_prerequisites_ready"])
        observed = capability_health.admission(
            report,
            runtime="pi",
            observation={"scope": "guest", "commands": ["required"], "mcps": [], "platform": "linux"},
        )
        observed_demo = next(item for item in observed["skills"] if item["name"] == "demo")
        self.assertTrue(observed_demo["declared_prerequisites_ready"])
        self.assertEqual(observed["observation_scope"], "guest")

    def test_unhealthy_required_mcp_is_not_functionally_ready(self):
        manifest = {"schema_version": 1, "skills": {"demo": {"mcps": ["demo_mcp"]}},
                    "mcps": {"demo_mcp": {}}}
        report = capability_health.evaluate(manifest, set())
        admission = capability_health.admission(
            report,
            observation={"scope": "guest", "mcps": ["demo_mcp"], "mcp_health": {"demo_mcp": False}},
        )
        demo = admission["skills"][0]
        self.assertFalse(demo["declared_prerequisites_ready"])
        self.assertFalse(demo["admissible"])
        self.assertFalse(demo["mcp_functionality_verified"])

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

    def test_portable_cli_strict_requires_guest_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "skills.toml"
            manifest.write_text('[skills.demo]\ncommands = ["python"]\n\n[mcps]\n')
            script = ROOT / "scripts" / "capability_health.py"

            def run(observation=None):
                observation_path = root / "observation.json"
                args = [sys.executable, str(script), "--manifest", str(manifest), "--portable", "--strict", "--json"]
                if observation is not None:
                    observation_path.write_text(json.dumps(observation))
                    args.extend(["--observation-file", str(observation_path)])
                return subprocess.run(args, capture_output=True, text=True, check=False)

            unknown = run()
            self.assertNotEqual(unknown.returncode, 0)
            self.assertIsNone(json.loads(unknown.stdout)["admission"]["skills"][0]["admissible"])
            blocked = run({"scope": "guest", "commands": [], "mcps": [], "platform": "linux"})
            self.assertNotEqual(blocked.returncode, 0)
            self.assertFalse(json.loads(blocked.stdout)["admission"]["skills"][0]["admissible"])
            ready = run({"scope": "guest", "commands": ["python"], "mcps": [], "platform": "linux"})
            self.assertEqual(ready.returncode, 0)
            self.assertTrue(json.loads(ready.stdout)["admission"]["skills"][0]["admissible"])

    def test_portable_non_json_reports_admission_counts_and_malformed_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "skills.toml"
            manifest.write_text('[skills.demo]\ncommands = ["python"]\n\n[mcps]\n')
            script = ROOT / "scripts" / "capability_health.py"
            observation = root / "observation.json"
            observation.write_text(json.dumps({"scope": "guest", "commands": ["python"], "mcps": [], "platform": "linux"}))
            ready = subprocess.run(
                [sys.executable, str(script), "--manifest", str(manifest), "--portable", "--observation-file", str(observation)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(ready.returncode, 0)
            self.assertIn("Portable admission (chasm/host): 1 ready, 0 blocked, 0 unknown", ready.stdout)
            observation.write_text("[]")
            malformed = subprocess.run(
                [sys.executable, str(script), "--manifest", str(manifest), "--portable", "--observation-file", str(observation)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(malformed.returncode, 2)
            self.assertIn("observation file must contain a JSON object", malformed.stderr)


if __name__ == "__main__":
    unittest.main()
