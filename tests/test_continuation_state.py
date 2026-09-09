import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("continuation_state", ROOT / "scripts" / "continuation_state.py")
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules["continuation_state"] = _MODULE
_SPEC.loader.exec_module(_MODULE)
assess, digest = _MODULE.assess, _MODULE.digest


def fixture_state(**changes):
    state = {
        "schema": 1, "campaign_id": "camp-1", "epoch": 1, "source_run_id": "run-1",
        "repository_identity": "repo@abc", "source_commit": "f" * 40, "predecessor_state_id": "0" * 64, "objective_digest": "a" * 64,
        "module_digest": "b" * 64, "bundle_digest": "c" * 64, "policy_digest": "d" * 64,
        "owner": {"kind": "workflow", "id": "owner-1"},
        "authority": {"envelope_class": "local-read", "effect_ceiling": ["none"]},
        "delegation": {"grant_id": "1" * 64, "decision_class": "same-envelope-continuation"},
        "budget": {"batch_limit": 4, "consumed": 0, "remaining": 4, "total_consumed": 0, "total_ceiling": 8},
        "next_action": {"kind": "run", "owner": "owner-1", "action_digest": "e" * 64},
        "status": {"phase": "running", "terminal": False}, "evidence_refs": ["obs-1"],
        "created_at": "2026-09-08T20:00:00Z", "updated_at": "2026-09-08T20:01:00Z",
    }
    state.update(changes)
    state["state_id"] = digest({k: v for k, v in state.items() if k != "state_id"})
    return state


def fixture_observation(**changes):
    value = {"campaign_id": "camp-1", "epoch": 1, "source_run_id": "run-1",
             "repository_identity": "repo@abc", "source_commit": "f" * 40, "objective_digest": "a" * 64,
             "module_digest": "b" * 64, "bundle_digest": "c" * 64, "policy_digest": "d" * 64,
             "action_digest": "e" * 64, "attempt_status": "ready",
             "evidence_refs": ["obs-1"], "current_state_id": fixture_state()["state_id"], "budget": fixture_state()["budget"], "predecessor_state_id": "0" * 64}
    value.update(changes)
    return value


def fixture_grant(**changes):
    value = {"grant_id": "1" * 64, "campaign_id": "camp-1", "owner": "owner-1", "objective_digest": "a" * 64, "repository_identity": "repo@abc", "policy_digest": "d" * 64, "expires_at": "2026-09-08T22:00:00Z",
             "revoked": False, "renewal_allowed": False,
             "authority": {"envelope_class": "local-read", "effect_ceiling": ["none"]}, "budget_caps": {"batch_limit": 4, "total_ceiling": 8},
             "decision_class": "same-envelope-continuation"}
    value.update(changes)
    return value


class ContinuationStateTests(unittest.TestCase):
    def test_valid_assessment_is_deterministic_and_admissible(self):
        args = (fixture_state(), fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z")
        first, second = assess(*args), assess(*args)
        self.assertEqual(first, second)
        self.assertEqual(first.disposition, "continue")
        self.assertTrue(first.admissible)
        self.assertIsNotNone(first.idempotency_key)

    def test_identity_tampering_is_invalid(self):
        state = fixture_state()
        state["updated_at"] = "2026-09-08T20:02:00Z"
        result = assess(state, fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z")
        self.assertEqual(result.disposition, "invalid_state")
        self.assertTrue(any(d.code == "state_identity_mismatch" for d in result.diagnostics))

    def test_budget_and_time_refusals(self):
        exhausted = fixture_state(budget={"batch_limit": 4, "consumed": 4, "remaining": 0, "total_consumed": 4, "total_ceiling": 4})
        self.assertEqual(assess(exhausted, fixture_observation(current_state_id=exhausted["state_id"], budget=exhausted["budget"]), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "budget_exhausted")
        self.assertEqual(assess(fixture_state(), fixture_observation(), fixture_grant(), "2026-09-08T23:00:00Z").disposition, "expired")
        self.assertEqual(assess(fixture_state(), fixture_observation(), fixture_grant(revoked=True), "2026-09-08T21:00:00Z").disposition, "revoked")

    def test_terminal_and_unknown_never_admit(self):
        terminal = fixture_state(status={"phase": "completed", "terminal": True}, next_action=None)
        self.assertEqual(assess(terminal, fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "complete")
        unknown = assess(fixture_state(), fixture_observation(attempt_status="unknown"), fixture_grant(), "2026-09-08T21:00:00Z")
        self.assertEqual(unknown.disposition, "unknown")
        self.assertFalse(unknown.admissible)

    def test_duplicate_and_ambiguous_are_refusals(self):
        duplicate = assess(fixture_state(), fixture_observation(duplicate=True), fixture_grant(), "2026-09-08T21:00:00Z")
        ambiguous = assess(fixture_state(), fixture_observation(ambiguous=True), fixture_grant(), "2026-09-08T21:00:00Z")
        self.assertEqual(duplicate.disposition, "duplicate_replay")
        self.assertEqual(ambiguous.disposition, "concurrent_or_ambiguous")

    def test_bool_budget_is_invalid(self):
        state = fixture_state(budget={"batch_limit": True, "consumed": 0, "remaining": 1, "total_ceiling": 2})
        self.assertEqual(assess(state, fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "invalid_state")

    def test_renewal_requires_budget_and_checkpoint_gate(self):
        state = fixture_state(budget={"batch_limit": 2, "consumed": 2, "remaining": 0, "total_consumed": 2, "total_ceiling": 3})
        grant = fixture_grant(renewal_allowed=True, budget_caps={"batch_limit": 2, "total_ceiling": 3})
        self.assertEqual(assess(state, fixture_observation(checkpoint_verified=True, current_state_id=state["state_id"], budget=state["budget"]), grant, "2026-09-08T21:00:00Z").disposition, "continue")
        self.assertIsNotNone(assess(state, fixture_observation(checkpoint_verified=True, current_state_id=state["state_id"], budget=state["budget"]), grant, "2026-09-08T21:00:00Z").renewal)
        self.assertEqual(assess(state, fixture_observation(current_state_id=state["state_id"], budget=state["budget"]), grant, "2026-09-08T21:00:00Z").disposition, "budget_exhausted")
        self.assertEqual(assess(state, fixture_observation(checkpoint_verified=True, current_state_id=state["state_id"], budget=state["budget"]), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "budget_exhausted")
        renewed = fixture_state(budget={"batch_limit": 2, "consumed": 0, "remaining": 2, "total_consumed": 3, "total_ceiling": 3})
        self.assertEqual(assess(renewed, fixture_observation(current_state_id=renewed["state_id"], budget=renewed["budget"]), grant, "2026-09-08T21:00:00Z").disposition, "budget_exhausted")

    def test_stale_running_and_blocked_are_explicit(self):
        self.assertEqual(assess(fixture_state(), fixture_observation(current_state_id="f" * 64), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "stale")
        self.assertEqual(assess(fixture_state(), fixture_observation(attempt_status="running"), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "reconcile")
        blocked = fixture_state(status={"phase": "blocked", "terminal": False})
        self.assertEqual(assess(blocked, fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "blocked")

    def test_missing_bindings_and_malformed_values_refuse(self):
        state, observation, grant = fixture_state(), fixture_observation(), fixture_grant()
        for value, key in ((observation, "current_state_id"), (grant, "authority"), (grant, "budget_caps")):
            altered = copy.deepcopy(value)
            altered.pop(key, None)
            args = (state, altered, grant) if value is observation else (state, observation, altered)
            self.assertEqual(assess(*args, "2026-09-08T21:00:00Z").disposition, "invalid_state")
        malformed = fixture_state(source_commit=42)
        self.assertEqual(assess(malformed, observation, grant, "2026-09-08T21:00:00Z").disposition, "invalid_state")
        malformed = fixture_state(status={"phase": [], "terminal": False})
        self.assertEqual(assess(malformed, observation, grant, "2026-09-08T21:00:00Z").disposition, "invalid_state")

    def test_action_snapshot_is_json_backed(self):
        result = assess(fixture_state(), fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z")
        action = result.next_action
        action["kind"] = "mutated"
        self.assertEqual(result.next_action["kind"], "run")
        self.assertEqual(json.loads(result.action_json), result.next_action)

    def test_all_required_bindings_and_unknown_fields_fail_closed(self):
        base = (fixture_state(), fixture_observation(), fixture_grant())
        for position, original in enumerate(base):
            for key in original:
                with self.subTest(position=position, missing=key):
                    values = copy.deepcopy(base)
                    values[position].pop(key)
                    self.assertFalse(assess(*values, "2026-09-08T21:00:00Z").admissible)
        for position in range(3):
            values = copy.deepcopy(base)
            values[position]["invented_permission"] = True
            self.assertEqual(assess(*values, "2026-09-08T21:00:00Z").disposition, "invalid_state")

    def test_malformed_json_values_never_admit_or_raise(self):
        for value in (None, [], 42, True, "bad", float("nan"), {"bad": float("inf")}):
            for position in range(3):
                with self.subTest(position=position, value=repr(value)):
                    args = [fixture_state(), fixture_observation(), fixture_grant()]
                    args[position] = value
                    self.assertEqual(assess(*args, "2026-09-08T21:00:00Z").disposition, "invalid_state")

    def test_optional_status_fields_obey_the_declared_schema(self):
        for field in ("status", "observed_state"):
            result = assess(fixture_state(), fixture_observation(**{field: []}), fixture_grant(), "2026-09-08T21:00:00Z")
            self.assertEqual(result.disposition, "invalid_state")
        state = fixture_state(status={"phase": "running", "terminal": False, "reason": []})
        self.assertEqual(assess(state, fixture_observation(), fixture_grant(), "2026-09-08T21:00:00Z").disposition, "invalid_state")

    def test_proposed_budget_cannot_reset_controller_consumption(self):
        observation = fixture_observation(budget={**fixture_state()["budget"], "total_consumed": 2})
        result = assess(fixture_state(), observation, fixture_grant(), "2026-09-08T21:00:00Z")
        self.assertEqual(result.disposition, "invalid_state")
        self.assertIn("observation_mismatch", [d.code for d in result.diagnostics])

    def test_expanding_authority_and_future_timestamp_refuse(self):
        result = assess(fixture_state(), fixture_observation(requested_authority={"network": True}), fixture_grant(), "2026-09-08T21:00:00Z")
        self.assertEqual(result.disposition, "authority_expansion")
        self.assertEqual(assess(fixture_state(), fixture_observation(), fixture_grant(), "2026-09-08T19:00:00Z").disposition, "invalid_state")

    def test_cli_is_read_only_and_machine_json(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for name, value in (("state", fixture_state()), ("observation", fixture_observation()), ("grant", fixture_grant())):
                path = Path(directory) / f"{name}.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                paths.append(str(path))
            command = [sys.executable, str(ROOT / "scripts/continuation_state.py"), "--state", paths[0], "--observation", paths[1], "--grant", paths[2], "--as-of", "2026-09-08T21:00:00Z"]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["disposition"], "continue")


if __name__ == "__main__":
    unittest.main()
