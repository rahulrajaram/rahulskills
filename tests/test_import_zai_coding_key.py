import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from import_zai_coding_key import install_key


class ImportZaiCodingKeyTests(unittest.TestCase):
    def test_preserves_existing_auth_and_sets_private_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            agent = Path(temp) / "agent"
            agent.mkdir()
            auth = agent / "auth.json"
            auth.write_text('{"other": {"type": "api_key", "key": "existing"}}')
            auth.chmod(0o600)
            install_key(agent, "private-test-key")
            data = json.loads(auth.read_text())
            self.assertEqual(data["other"]["key"], "existing")
            self.assertEqual(data["zai"], {"type": "api_key", "key": "private-test-key"})
            self.assertEqual(auth.stat().st_mode & 0o777, 0o600)

    def test_rejects_symlink_ancestor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "real/agent").mkdir(parents=True)
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlinked"):
                install_key(root / "alias/agent", "synthetic-test-key")
            self.assertFalse((root / "real/agent/auth.json").exists())

    def test_rejects_existing_key_and_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            agent = Path(temp) / "agent"
            agent.mkdir()
            install_key(agent, "first-key")
            with self.assertRaisesRegex(ValueError, "already exists"):
                install_key(agent, "second-key")
            auth = agent / "auth.json"
            auth.rename(agent / "saved.json")
            auth.symlink_to(agent / "saved.json")
            with self.assertRaisesRegex(ValueError, "symlinked"):
                install_key(agent, "second-key")


if __name__ == "__main__":
    unittest.main()
