import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import composition_lock


ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "composition-lock"
DIGEST = "a" * 64


def contract(phase, input_card="one", output_class="artifact", schema=DIGEST):
    return {
        "unit": {"phase_id": phase, "semantic_version": "1.0.0"},
        "inputs": [{"name": "value", "epistemic_class": "artifact", "required": True,
                    "cardinality": input_card, "schema_digest": schema}],
        "outputs": [{"name": "value", "epistemic_class": output_class,
                     "cardinality": "one", "schema_digest": schema}],
    }


class CompositionLockTests(unittest.TestCase):
    def test_create_is_deterministic_and_checks_actual_files(self):
        args = (FIXTURE / "recipe.json", FIXTURE / "catalog.toml", FIXTURE,
                FIXTURE / "schema.json")
        first, second = composition_lock.create_lock(*args), composition_lock.create_lock(*args)
        self.assertTrue(first.ok, first.issues)
        self.assertEqual(first.value, second.value)
        self.assertEqual(first.value["lock_digest"], composition_lock.sha256_json({k: v for k, v in first.value.items() if k != "lock_digest"}))

    def test_check_and_diff_report_identity_changes(self):
        args = (FIXTURE / "recipe.json", FIXTURE / "catalog.toml", FIXTURE,
                FIXTURE / "schema.json")
        lock = composition_lock.create_lock(*args).value
        self.assertTrue(composition_lock.check_lock(lock, lock).ok)
        changed = json.loads(json.dumps(lock))
        changed["recipe"]["digest"] = "b" * 64
        changed.pop("lock_digest")
        changed["lock_digest"] = composition_lock.sha256_json(changed)
        result = composition_lock.check_lock(lock, changed)
        self.assertFalse(result.ok)
        self.assertIn("identity_mismatch", {item.code for item in result.issues})
        report = composition_lock.diff_lock(lock, changed)
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["changes"][0]["path"], "recipe")

    def test_missing_schema_is_review_required(self):
        contracts = {"a": contract("a", schema=None), "b": contract("b", schema=None)}
        recipe = {"edges": [{"from": "a", "output": "value", "to": "b", "input": "value"}], "required_roles": []}
        result = composition_lock.build_lock(recipe, {}, contracts, {"a": "a" * 64, "b": "b" * 64}, DIGEST, DIGEST, DIGEST)
        self.assertFalse(result.ok)
        self.assertIn("review_required", {item.code for item in result.issues})

    def test_cardinality_and_epistemic_mismatch_refuse(self):
        contracts = {"a": contract("a", output_class="diagnostic"), "b": contract("b", input_card="one")}
        contracts["a"]["outputs"][0]["cardinality"] = "many"
        edge = {"from": "a", "output": "value", "to": "b", "input": "value"}
        issues = composition_lock.validate_edge(edge, contracts)
        self.assertIn("cardinality_mismatch", {item.code for item in issues})
        self.assertIn("epistemic_mismatch", {item.code for item in issues})

    def test_only_explicit_bounded_lifecycle_cycle_is_admitted(self):
        contracts = {"a": contract("a")}
        pins = {"a": DIGEST}
        edge = {"from": "a", "output": "value", "to": "a", "input": "value",
                "kind": "lifecycle_backedge", "termination": {"max_epochs": 3, "proof": "epoch limit"}}
        recipe = {"edges": [edge], "required_roles": []}
        self.assertTrue(composition_lock.build_lock(recipe, {}, contracts, pins, DIGEST, DIGEST, DIGEST).ok)
        edge.pop("kind"); edge.pop("termination")
        refused = composition_lock.build_lock(recipe, {}, contracts, pins, DIGEST, DIGEST, DIGEST)
        self.assertIn("unbounded_cycle", {item.code for item in refused.issues})

    def test_malformed_edge_returns_diagnostic(self):
        result = composition_lock.build_lock({"edges": [None], "required_roles": []}, {}, {}, {}, DIGEST, DIGEST, DIGEST)
        self.assertFalse(result.ok)
        self.assertEqual(result.issues[0].code, "malformed_edge")

    def test_malformed_role_and_selected_roles_are_diagnostics(self):
        recipe = {"edges": [], "required_roles": [None], "selected_roles": [3]}
        result = composition_lock.build_lock(recipe, {}, {}, {}, DIGEST, DIGEST, DIGEST)
        codes = {item.code for item in result.issues}
        self.assertIn("malformed_role", codes)
        self.assertIn("malformed_recipe", codes)

    def test_fake_verified_adapter_does_not_enable_schema_migration(self):
        contracts = {"a": contract("a", schema=DIGEST), "b": contract("b", schema="b" * 64)}
        edge = {"from": "a", "output": "value", "to": "b", "input": "value",
                "producer_contract_digest": DIGEST, "consumer_contract_digest": DIGEST,
                "producer_schema_digest": DIGEST, "consumer_schema_digest": "b" * 64,
                "adapter_digest": DIGEST, "adapter_binding": {"digest": DIGEST, "verified": True}}
        self.assertIn("review_required", {item.code for item in composition_lock.validate_edge(edge, contracts)})

    def test_optional_unselected_edge_is_recorded_inactive(self):
        contracts = {"a": contract("a"), "b": contract("b")}
        recipe = {"required_roles": [{"role": "optional", "optional": True, "resolve_to": ["b"]}],
                  "selected_roles": [], "edges": [{"from": "a", "output": "value", "to": "b", "input": "value"}]}
        result = composition_lock.build_lock(recipe, {}, contracts, {"a": DIGEST, "b": DIGEST}, DIGEST, DIGEST, DIGEST)
        self.assertTrue(result.ok, result.issues)
        self.assertEqual(len(result.value["edges"]), 0)
        self.assertEqual(len(result.value["inactive_edges"]), 1)

    def test_cycle_detection_is_independent_of_edge_order(self):
        contracts = {name: contract(name) for name in ("a", "b", "c")}
        pins = {name: DIGEST for name in contracts}
        edges = [{"from": "b", "output": "value", "to": "c", "input": "value"},
                 {"from": "c", "output": "value", "to": "a", "input": "value"},
                 {"from": "a", "output": "value", "to": "b", "input": "value"}]
        result = composition_lock.build_lock({"edges": edges, "required_roles": []}, {}, contracts, pins, DIGEST, DIGEST, DIGEST)
        self.assertIn("unbounded_cycle", {item.code for item in result.issues})

    def test_required_role_cannot_be_deselected_and_unknown_selection_refuses(self):
        recipe = {"required_roles": [{"role": "required", "resolve_to": ["a"]}],
                  "selected_roles": ["unknown"], "edges": []}
        result = composition_lock.build_lock(recipe, {}, {"a": contract("a")}, {"a": DIGEST}, DIGEST, DIGEST, DIGEST)
        codes = {item.code for item in result.issues}
        self.assertIn("unknown_selected_role", codes)

    def test_recomputed_lock_with_extra_top_level_field_is_rejected(self):
        args = (FIXTURE / "recipe.json", FIXTURE / "catalog.toml", FIXTURE, FIXTURE / "schema.json")
        lock = composition_lock.create_lock(*args).value
        changed = json.loads(json.dumps(lock)); changed["authority"] = {"ceiling": "wider"}
        changed["lock_digest"] = composition_lock.sha256_json({k: v for k, v in changed.items() if k != "lock_digest"})
        result = composition_lock.check_lock(lock, changed)
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
