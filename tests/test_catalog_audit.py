from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest


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


class CatalogAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_audit_reports_only_divergent_name_collisions(self) -> None:
        first = self.root / "first"
        second = self.root / "second"
        write_skill(first, "one", "shared")
        write_skill(second, "two", "shared", "different")
        write_skill(first, "solo", "solo")

        report = audit_catalog.audit([first, second], line_budget=400)

        self.assertEqual(list(report["collisions"]), ["shared"])
        self.assertEqual(report["summary"]["unique_names"], 2)

    def test_audit_reports_size_and_personal_paths(self) -> None:
        root = self.root / "skills"
        write_skill(root, "large", "large", "/home/example/tool\n" * 10)

        report = audit_catalog.audit([root], line_budget=5)

        self.assertEqual(report["summary"]["oversized"], 1)
        self.assertEqual(report["summary"]["personal_paths"], 1)
