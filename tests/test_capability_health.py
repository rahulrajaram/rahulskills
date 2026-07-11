from pathlib import Path
import importlib.util
import sys


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "capability_health.py"
SPEC = importlib.util.spec_from_file_location("capability_health", MODULE_PATH)
assert SPEC and SPEC.loader
capability_health = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = capability_health
SPEC.loader.exec_module(capability_health)


def test_evaluate_reports_missing_commands_and_mcps(monkeypatch) -> None:
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
    monkeypatch.setattr(
        capability_health.shutil,
        "which",
        lambda command: f"/bin/{command}" if command == "present" else None,
    )

    report = capability_health.evaluate(manifest, {"ready"})

    assert report["skills"]["demo"]["available"] is False
    assert report["skills"]["demo"]["missing_commands"] == ["absent"]
    assert report["skills"]["demo"]["missing_mcps"] == ["missing"]


def test_loads_repository_manifest() -> None:
    manifest = capability_health.load_manifest(capability_health.DEFAULT_MANIFEST)
    assert manifest["schema_version"] == 1
    assert "figma" in manifest["skills"]
    assert set(manifest["mcps"]) == {
        "cultivar",
        "gptqueue_shared",
        "haake_memory",
        "selfimprovemeta",
    }


def test_repository_manifest_covers_every_source_skill() -> None:
    manifest = capability_health.load_manifest(capability_health.DEFAULT_MANIFEST)
    assert capability_health.undeclared_source_skills(
        manifest, capability_health.REPO / "skills"
    ) == []
