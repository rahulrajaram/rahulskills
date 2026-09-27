"""Keep checked-in Chasm instructions in sync with their source overlays."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import render_chasm_instructions as renderer


class RenderChasmInstructionsTests(unittest.TestCase):
    def test_rendered_files_match_sources_and_runtime_overlays(self):
        policy = renderer.POLICY.read_text(encoding="utf-8")
        self.assertEqual(set(renderer.RUNTIME_OVERLAYS), {"codex", "pi", "claude"})

        for runtime, (filename, _) in renderer.RUNTIMES.items():
            with self.subTest(runtime=runtime):
                rendered = renderer.render(runtime, policy)
                output = renderer.OUTPUT / f"{runtime}-{filename}"
                self.assertEqual(output.read_text(encoding="utf-8"), rendered)

                overlays = renderer.RUNTIME_OVERLAYS.get(runtime, ())
                self.assertEqual(rendered.count("<!-- BEGIN ORCHESTRATOR MODEL"), len(overlays))
                self.assertEqual(rendered.count("<!-- END ORCHESTRATOR MODEL -->"), len(overlays))
                for path in overlays:
                    self.assertTrue(path.is_file(), path)
                    block = path.read_text(encoding="utf-8").strip()
                    self.assertEqual(rendered.count(block), 1)
                    if runtime == "pi":
                        self.assertLess(rendered.index(block), rendered.index(policy.rstrip()))
                    else:
                        self.assertGreater(rendered.index(block), rendered.index(policy.rstrip()))


if __name__ == "__main__":
    unittest.main()
