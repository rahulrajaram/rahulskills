import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import bind_qualification_source

SOURCE_MARKER = bind_qualification_source.SOURCE_MARKER
bind_source = bind_qualification_source.bind_source


class SourceBindingTests(unittest.TestCase):
    def template(self):
        return {"actions": [{"command": {"argv": ["python3", "runner.py", "--source-commit", SOURCE_MARKER]}}]}

    def test_exact_substitution_preserves_template(self):
        template = self.template()
        original = copy.deepcopy(template)
        result = bind_source(template, "a" * 40)
        self.assertIsNone(result.error)
        self.assertEqual(json.loads(result.module_json)["actions"][0]["command"]["argv"][-1], "a" * 40)
        self.assertEqual(template, original)

    def test_rebinding_and_symbolic_revision_refuse(self):
        self.assertIsNotNone(bind_source(self.template(), "HEAD").error)
        bound = bind_source(self.template(), "a" * 40)
        self.assertIsNotNone(bind_source(json.loads(bound.module_json), "b" * 40).error)

    def test_marker_cannot_change_another_argument(self):
        template = self.template()
        template["actions"][0]["command"]["argv"] += [SOURCE_MARKER]
        self.assertIsNotNone(bind_source(template, "a" * 40).error)
