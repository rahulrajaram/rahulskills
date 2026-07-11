from pathlib import Path
import importlib.util
import sys


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "audit_catalog.py"
SPEC = importlib.util.spec_from_file_location("audit_catalog", MODULE_PATH)
assert SPEC and SPEC.loader
audit_catalog = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit_catalog
SPEC.loader.exec_module(audit_catalog)


def write_skill(root: Path, directory: str, name: str, body: str = "body") -> None:
    path = root / directory / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f'---\nname: {name}\ndescription: "test"\nargument-hint: ""\n---\n{body}\n',
        encoding="utf-8",
    )


def test_audit_reports_only_divergent_name_collisions(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_skill(first, "one", "shared")
    write_skill(second, "two", "shared", "different")
    write_skill(first, "solo", "solo")

    report = audit_catalog.audit([first, second], line_budget=400)

    assert list(report["collisions"]) == ["shared"]
    assert report["summary"]["unique_names"] == 2


def test_audit_reports_size_and_personal_paths(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    write_skill(root, "large", "large", "/home/example/tool\n" * 10)

    report = audit_catalog.audit([root], line_budget=5)

    assert report["summary"]["oversized"] == 1
    assert report["summary"]["personal_paths"] == 1
