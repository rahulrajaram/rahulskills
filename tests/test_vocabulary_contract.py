"""Offline response validation: no backend calls or vocabulary writes."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


VALIDATOR = (Path(__file__).resolve().parents[1] /
             "skills/yore-vocabulary-llm-filter/scripts/validate.jq")


def entry(term="Yore", **changes):
    return dict(term=term, verdict="keep", category="project-name",
                reason="Ambiguous pronunciation") | changes


class VocabularyContractTests(unittest.TestCase):
    def validate(self, expected, response, *, raw=False):
        with tempfile.TemporaryDirectory() as directory:
            candidates = Path(directory) / "expected.json"
            result = Path(directory) / "response.json"
            candidates.write_text(json.dumps(expected), encoding="utf-8")
            result.write_text(response if raw else json.dumps(response), encoding="utf-8")
            return subprocess.run(
                ["jq", "-e", "-s", "--slurpfile", "expected", str(candidates),
                 "-f", str(VALIDATOR), str(result)],
                text=True, capture_output=True,
            )

    def assert_valid(self, expected, response):
        result = self.validate(expected, response)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "true")

    def assert_invalid(self, expected, response, **kwargs):
        result = self.validate(expected, response, **kwargs)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_valid_nonempty_and_all_enums(self):
        categories = ["acronym", "project-name", "proper-noun", "jargon",
                      "phonetically-clear", "compound-clear", "stemming-artifact", "other"]
        for verdict in ["keep", "drop", "review", "artifact"]:
            for category in categories:
                with self.subTest(verdict=verdict, category=category):
                    self.assert_valid(["Yore"], {"terms": [entry(verdict=verdict, category=category)]})

    def test_coverage_accepts_order_changes_and_preserves_unicode(self):
        self.assert_valid(["Yore", "éclair"], {"terms": [entry("éclair"), entry()]})

    def test_missing_unknown_duplicate_and_case_changed_terms(self):
        for terms in [[], [entry("Other")], [entry(), entry()], [entry("yore")]]:
            with self.subTest(terms=terms):
                self.assert_invalid(["Yore"], {"terms": terms})
        self.assert_invalid(["Yore", "Lisp"], {"terms": [entry()]})
        self.assert_invalid(["Yore"], {"terms": [entry(), entry("Other")]})

    def test_empty_input_is_intentional(self):
        self.assert_valid([], {"terms": []})
        self.assert_invalid([], {"terms": [entry()]})

    def test_invalid_candidate_arrays(self):
        for candidates in [["Yore", "Yore"], [""], ["  "], [None], [1], {}, "Yore"]:
            with self.subTest(candidates=candidates):
                self.assert_invalid(candidates, {"terms": []})

    def test_invalid_verdict_category_and_reason(self):
        for field, value in [("verdict", "KEEP"), ("verdict", None), ("verdict", []),
                             ("category", "unknown"), ("category", 1), ("category", []),
                             ("reason", ""), ("reason", " \n"), ("reason", None),
                             ("term", ""), ("term", 2)]:
            with self.subTest(field=field, value=value):
                self.assert_invalid(["Yore"], {"terms": [entry(**{field: value})]})

    def test_missing_and_extra_fields(self):
        for field in entry():
            incomplete = entry()
            del incomplete[field]
            self.assert_invalid(["Yore"], {"terms": [incomplete]})
        self.assert_invalid(["Yore"], {"terms": [entry(extra=True)]})
        self.assert_invalid(["Yore"], {"terms": [entry()], "extra": True})

    def test_wrong_container_shapes(self):
        for response in [None, [], "data", {}, {"terms": None}, {"terms": {}},
                         {"terms": [None]}, {"terms": ["Yore"]}]:
            with self.subTest(response=response):
                self.assert_invalid(["Yore"], response)

    def test_fences_partial_and_multiple_documents_rejected(self):
        valid = json.dumps({"terms": [entry()]})
        for response in ["", "```json\n" + valid + "\n```", valid[:-1], valid + "\n" + valid]:
            with self.subTest(response=response):
                self.assert_invalid(["Yore"], response, raw=True)


if __name__ == "__main__":
    unittest.main()
