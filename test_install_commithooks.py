"""Check that the documented commithooks installer retains its transaction guards."""

from pathlib import Path
import re
import unittest


DOCUMENT = (Path(__file__).parent / "skills/install-commithooks/SKILL.md").read_text()


class LibraryTransactionDocumentationTests(unittest.TestCase):
    def test_documented_installer_stages_and_recovers_library(self):
        match = re.search(r"```python\n(.*?)\n```", DOCUMENT, re.DOTALL)
        self.assertIsNotNone(match)
        installer = match.group(1)
        for fragment in (
            "tempfile.mkdtemp(prefix=\".lib-stage-\", dir=git_dir)",
            "shutil.copytree(commithooks / \"lib\", stage",
            "lib_dst.rename(backup)",
            "stage.rename(lib_dst)",
            "backup.rename(lib_dst)",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, installer)

    def test_documented_installer_checks_routing_and_custom_dispatchers(self):
        self.assertIn("core.hooksPath", DOCUMENT)
        self.assertIn("Preserving custom dispatcher", DOCUMENT)
        self.assertIn("Preserving custom hooks directory", DOCUMENT)


if __name__ == "__main__":
    unittest.main()
