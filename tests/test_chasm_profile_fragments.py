import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import skill_profiles as profiles


class ChasmFragmentTests(unittest.TestCase):
    def fixture(self, base):
        root = base / "source"
        manifest = root / "skills/demo/SKILL.md"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("---\nname: demo\ndescription: Demo\n---\nOriginal body.\n")
        fragments = root / "profiles/chasm-development/skills/demo"
        fragments.mkdir(parents=True)
        return root, manifest, fragments

    def test_prepend_and_replacement_preserve_source_and_hash_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, source, fragments = self.fixture(base)
            original = source.read_bytes()
            (fragments / "prepend.md").write_text("Guest guidance.")
            (fragments / "replace.toml").write_text('[[replacements]]\nfind="Original body."\nreplace="Guest body."\n')
            output = base / "out"
            report = profiles.bundle(root, output, "pi", ("demo",), profiles=("chasm-development",))
            actual = (output / "skills/demo/SKILL.md").read_bytes()
            self.assertIn(b"Guest guidance.", actual)
            self.assertIn(b"Guest body.", actual)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(report["sha256"]["skills/demo/SKILL.md"], hashlib.sha256(actual).hexdigest())
            profiles.bundle(root, base / "plain", "pi", ("demo",))
            self.assertEqual((base / "plain/skills/demo/SKILL.md").read_bytes(), original)

    def test_composed_links_still_require_declared_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, _, fragments = self.fixture(base)
            (root / "references").mkdir()
            (root / "references/guide.md").write_text("guide")
            (fragments / "prepend.md").write_text("[guide](../../references/guide.md)")
            with self.assertRaisesRegex(ValueError, "unlisted_reference"):
                profiles.bundle(root, base / "bad", "pi", ("demo",), profiles=("chasm-development",))
            self.assertFalse((base / "bad").exists())
            profiles.bundle(root, base / "good", "pi", ("demo",), ("references/guide.md",), profiles=("chasm-development",))
            self.assertTrue((base / "good/references/guide.md").is_file())

    def test_override_conflict_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, source, fragments = self.fixture(base)
            (fragments / "SKILL.md").write_bytes(source.read_bytes())
            (fragments / "prepend.md").write_text("extra")
            with self.assertRaisesRegex(ValueError, "both"):
                profiles.bundle(root, base / "out", "pi", ("demo",), profiles=("chasm-development",))
            (fragments / "prepend.md").unlink()
            (fragments / "SKILL.md").unlink()
            (fragments / "SKILL.md").symlink_to(source)
            with self.assertRaisesRegex(ValueError, "symlink"):
                profiles.bundle(root, base / "out", "pi", ("demo",), profiles=("chasm-development",))

    def test_complete_override_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, source, fragments = self.fixture(base)
            original = source.read_bytes()
            replacement = original.replace(b"Original body.", b"Guest body.")
            (fragments / "SKILL.md").write_bytes(replacement)
            first = profiles.bundle(root, base / "one", "pi", ("demo",), profiles=("chasm-development",))
            second = profiles.bundle(root, base / "two", "pi", ("demo",), profiles=("chasm-development",))
            self.assertEqual(first, second)
            self.assertEqual((base / "one/skills/demo/SKILL.md").read_bytes(), replacement)
            self.assertEqual(source.read_bytes(), original)

    def test_replacement_drift_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, _, fragments = self.fixture(base)
            (fragments / "replace.toml").write_text('[[replacements]]\nfind="Missing text"\nreplace="New"\n')
            with self.assertRaisesRegex(ValueError, "exactly one match"):
                profiles.bundle(root, base / "out", "pi", ("demo",), profiles=("chasm-development",))
            self.assertFalse((base / "out").exists())


if __name__ == "__main__":
    unittest.main()
