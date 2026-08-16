from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "capability_health.py"
SPEC = importlib.util.spec_from_file_location("capability_health", MODULE_PATH)
assert SPEC and SPEC.loader
capability_health = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = capability_health
SPEC.loader.exec_module(capability_health)


class CapabilityHealthTests(unittest.TestCase):
    def test_evaluate_reports_missing_commands_and_mcps(self) -> None:
        manifest = {
            "schema_version": 1,
            "skills": {
                "demo": {
                    "commands": ["present", "absent"],
                    "mcps": ["ready", "missing"],
                    "effect": "readonly",
                }
            },
        }
        resolver = lambda command: f"/bin/{command}" if command == "present" else None

        with patch.object(capability_health.shutil, "which", resolver):
            report = capability_health.evaluate(manifest, {"ready"})

        self.assertFalse(report["skills"]["demo"]["available"])
        self.assertEqual(report["skills"]["demo"]["missing_commands"], ["absent"])
        self.assertEqual(report["skills"]["demo"]["missing_mcps"], ["missing"])
        self.assertEqual(report["skills"]["demo"]["effects"], ["readonly"])
        self.assertEqual(report["skills"]["demo"]["approval_boundaries"], [])

    def test_loads_repository_manifest(self) -> None:
        manifest = capability_health.load_manifest(capability_health.DEFAULT_MANIFEST)
        self.assertEqual(manifest["schema_version"], 2)
        self.assertIn("figma", manifest["skills"])
        self.assertEqual(
            set(manifest["mcps"]),
            {
                "cultivar",
                "figma",
                "gptqueue_shared",
                "haake_memory",
                "image_gen",
                "openai_docs",
                "selfimprovemeta",
            },
        )

    def test_repository_manifest_covers_every_source_skill(self) -> None:
        manifest = capability_health.load_manifest(capability_health.DEFAULT_MANIFEST)
        self.assertEqual(
            capability_health.undeclared_source_skills(
                manifest, capability_health.REPO / "skills"
            ),
            [],
        )

    def test_optional_mcp_degrades_without_making_skill_unavailable(self) -> None:
        manifest = capability_health.load_manifest(capability_health.DEFAULT_MANIFEST)
        report = capability_health.evaluate(manifest, set())
        openai_docs = report["skills"]["openai-docs"]

        self.assertTrue(openai_docs["available"])
        self.assertTrue(openai_docs["degraded"])
        self.assertEqual(openai_docs["missing_optional_mcps"], ["openai_docs"])

    def test_repository_manifest_declares_every_mcp_dependency(self) -> None:
        manifest = capability_health.load_manifest(capability_health.DEFAULT_MANIFEST)
        self.assertEqual(capability_health.undeclared_mcp_dependencies(manifest), [])
