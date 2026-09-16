import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("learning_ingest", ROOT / "scripts" / "learning_ingest.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["learning_ingest"] = MODULE
SPEC.loader.exec_module(MODULE)
ingest, digest = MODULE.ingest, MODULE.digest


def context(**changes):
    value = {"campaign_id": "camp-1", "epoch": 1, "run_id": "run-1",
             "source_commit": "a" * 40, "policy_digest": "b" * 64}
    value.update(changes)
    return value


def record(finding="A concrete observed finding.", **changes):
    value = {"record_schema": 1, "finding": finding, "source_skill": "check-antipatterns",
             "evidence_refs": ["report.json#finding-1"],
             "disposition": {"status": "recorded", "target": None}}
    value.update(changes)
    return value


class LearningIngestTests(unittest.TestCase):
    def test_order_independent_and_idempotent(self):
        first, second = record("first"), record("second")
        a = ingest([first, second, first], context())
        b = ingest([second, first], context())
        self.assertTrue(a.accepted)
        self.assertEqual(a.document_json, b.document_json)
        self.assertEqual(len(a.document["entries"]), 2)
        self.assertTrue(all(e["epistemic_class"] == "claim" for e in a.document["entries"]))

    def test_previous_snapshot_is_merged_without_mutation(self):
        original = [record()]
        prior = ingest(original, context()).document
        result = ingest([record("new")], context(), prior)
        self.assertTrue(result.accepted)
        self.assertEqual(len(result.document["entries"]), 2)
        self.assertEqual(original, [record()])

    def test_provenance_conflict_refuses_atomically(self):
        prior = ingest([record()], context()).document
        result = ingest([record("new")], context(epoch=2), prior)
        self.assertFalse(result.accepted)
        self.assertIsNone(result.document)
        self.assertEqual(result.diagnostics[0].code, "provenance_conflict")

    def test_tampered_previous_digest_refuses(self):
        prior = ingest([record()], context()).document
        prior["digest"] = "f" * 64
        result = ingest([record("new")], context(), prior)
        self.assertFalse(result.accepted)
        self.assertTrue(any(i.code == "invalid_previous" for i in result.diagnostics))

    def test_invalid_record_makes_mixed_batch_atomic(self):
        result = ingest([record(), {"record_schema": 1}], context())
        self.assertFalse(result.accepted)
        self.assertIsNone(result.document)
        self.assertTrue(any(i.path == "records[1]" for i in result.diagnostics))

    def test_result_document_is_snapshot(self):
        source = record()
        result = ingest([source], context())
        source["finding"] = "mutated after ingestion"
        source["evidence_refs"].append("new-ref")
        self.assertEqual(result.document["entries"][0]["record"]["finding"], "A concrete observed finding.")
        self.assertEqual(result.document["entries"][0]["record"]["evidence_refs"], ["report.json#finding-1"])

    def test_cli_rejects_duplicate_keys_and_emits_strict_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = root / "records.json"
            ctx = root / "context.json"
            records.write_text(json.dumps([record()]), encoding="utf-8")
            ctx.write_text(json.dumps(context()), encoding="utf-8")
            command = [sys.executable, str(ROOT / "scripts/learning_ingest.py"), "--records", str(records), "--context", str(ctx)]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["accepted"], True)
            records.write_text('[{"record_schema":1,"record_schema":1}]', encoding="utf-8")
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["accepted"], False)


if __name__ == "__main__":
    unittest.main()
