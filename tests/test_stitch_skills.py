import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class StitchFixtureTests(unittest.TestCase):
    def test_isolated_assembly_is_fresh_and_default_omits_design_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "assembled"
            subprocess.run([str(ROOT / "stitch-skills.sh"), "assemble", "--output", str(output)],
                           cwd=ROOT, check=True, stdout=subprocess.PIPE, text=True)
            self.assertTrue((output / "codex" / "references").is_dir())
            self.assertFalse((output / "codex" / "skills" / "figma").exists())
            self.assertFalse((output / "codex" / "skills" / "tui-web-design-orchestrator").exists())


if __name__ == "__main__":
    unittest.main()
