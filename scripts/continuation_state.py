#!/usr/bin/env python3
"""Pure, read-only continuation-state assessment and JSON CLI."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping

DIGEST = re.compile(r"^[0-9a-f]{64}$")
DISPOSITIONS = {
    "continue", "complete", "blocked", "invalid_state", "stale", "revoked",
    "expired", "budget_exhausted", "unknown", "duplicate_replay",
    "concurrent_or_ambiguous", "authority_expansion", "reconcile",
}


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    return value


def canonical_json(value: Any) -> bytes:
    """Return the repository's canonical UTF-8 JSON encoding."""
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Assessment:
    disposition: str
    admissible: bool
    state_id: str | None
    idempotency_key: str | None
    diagnostics: tuple[Diagnostic, ...] = ()
    _next_action_json: str | None = None
    observed_evidence: tuple[str, ...] = ()
    renewal: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_schema": 1,
            "disposition": self.disposition,
            "admissible": self.admissible,
            "state_id": self.state_id,
            "idempotency_key": self.idempotency_key,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "next_action": self.next_action,
            "observed_evidence": list(self.observed_evidence),
            "renewal": _plain(self.renewal),
        }

    @property
    def action_json(self) -> str | None:
        return self._next_action_json

    @property
    def next_action(self) -> Mapping[str, Any] | None:
        return None if self._next_action_json is None else json.loads(self._next_action_json)


def _diag(code: str, path: str, reason: str) -> Diagnostic:
    return Diagnostic(code, path, reason)


def _timestamp(value: Any, path: str, errors: list[Diagnostic]) -> datetime | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
        errors.append(_diag("invalid_timestamp", path, "must be an RFC3339 string"))
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError
        return parsed.astimezone(timezone.utc)
    except ValueError:
        errors.append(_diag("invalid_timestamp", path, "must be an RFC3339 timestamp"))
        return None


def _obj(value: Any, path: str, errors: list[Diagnostic]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(_diag("invalid_type", path, "must be an object"))
        return {}
    return value


def _digest(value: Any, path: str, errors: list[Diagnostic]) -> str | None:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        errors.append(_diag("invalid_digest", path, "must be a lowercase SHA-256 digest"))
        return None
    return value


def _int(value: Any, path: str, errors: list[Diagnostic]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(_diag("invalid_integer", path, "must be an integer (boolean is not valid)"))
        return None
    return value


def _same(a: Mapping[str, Any], b: Mapping[str, Any], key: str,
          errors: list[Diagnostic], label: str = "mismatch") -> None:
    if key in a and key in b and a[key] != b[key]:
        errors.append(_diag(label, f"$.{key}", f"state and supplied records disagree for {key}"))


def _parse_as_of(value: datetime | str) -> datetime | None:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else None
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
        except ValueError:
            return None
    return None


def _assess(state: Mapping[str, Any], observation: Mapping[str, Any],
           grant: Mapping[str, Any], as_of: datetime | str) -> Assessment:
    """Assess supplied state/evidence/grant without side effects."""
    errors: list[Diagnostic] = []
    state = _obj(state, "$.state", errors)
    observation = _obj(observation, "$.observation", errors)
    grant = _obj(grant, "$.grant", errors)
    now = _parse_as_of(as_of)
    if now is None:
        errors.append(_diag("invalid_as_of", "$.as_of", "must be timezone-aware RFC3339"))

    state_id = state.get("state_id") if isinstance(state.get("state_id"), str) else None
    if state_id is not None:
        _digest(state_id, "$.state_id", errors)
        without_id = dict(state)
        without_id.pop("state_id", None)
        try:
            identity_matches = digest(without_id) == state_id
        except (TypeError, ValueError, OverflowError):
            identity_matches = False
            errors.append(_diag("invalid_json_value", "$.state", "state contains a noncanonical JSON value"))
        if not identity_matches:
            errors.append(_diag("state_identity_mismatch", "$.state_id", "does not match canonical state"))
    else:
        errors.append(_diag("missing_state_id", "$.state_id", "required"))

    if type(state.get("schema")) is not int or state.get("schema") != 1:
        errors.append(_diag("unsupported_schema", "$.schema", "only schema version 1 is supported"))
    status = _obj(state.get("status"), "$.status", errors)
    phase = status.get("phase")
    terminal = status.get("terminal")
    if not isinstance(terminal, bool):
        errors.append(_diag("invalid_terminal", "$.status.terminal", "must be boolean"))
    action = state.get("next_action")
    if not terminal and action is None:
        errors.append(_diag("missing_next_action", "$.next_action", "resumable state requires a next action"))
    if action is not None and (not isinstance(action, Mapping) or action.get("kind") not in {"run", "renew", "reconcile"} or not isinstance(action.get("owner"), str) or not action.get("owner") or not isinstance(action.get("action_digest"), str)):
        errors.append(_diag("invalid_next_action", "$.next_action", "must be null or a nonempty action object"))
    if terminal is True and action is not None:
        errors.append(_diag("terminal_next_action", "$.next_action", "terminal state cannot have next action"))
    for key in ("campaign_id", "source_run_id", "repository_identity", "source_commit", "objective_digest",
                "module_digest", "bundle_digest", "policy_digest"):
        if key.endswith("digest"):
            _digest(state.get(key), f"$.{key}", errors)
        elif not isinstance(state.get(key), str) or not state[key]:
            errors.append(_diag("missing_identity", f"$.{key}", "required non-empty identity"))
    if not isinstance(state.get("source_commit"), str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", state.get("source_commit", "")):
        errors.append(_diag("invalid_source_commit", "$.source_commit", "must be an exact Git commit identity"))
    _digest(state.get("predecessor_state_id"), "$.predecessor_state_id", errors)
    if phase not in {"issued", "running", "checkpointed", "renewing", "completed", "stopped", "blocked", "unknown"}:
        errors.append(_diag("invalid_phase", "$.status.phase", "unsupported lifecycle phase"))
    epoch = _int(state.get("epoch"), "$.epoch", errors)
    if epoch is not None and epoch < 0:
        errors.append(_diag("negative_epoch", "$.epoch", "must not be negative"))
    created = _timestamp(state.get("created_at"), "$.created_at", errors)
    updated = _timestamp(state.get("updated_at"), "$.updated_at", errors)
    if updated and now and updated > now:
        errors.append(_diag("future_state", "$.updated_at", "state is newer than the assessment time"))
    if created and updated and updated < created:
        errors.append(_diag("timestamp_regression", "$.updated_at", "before created_at"))

    budget = _obj(state.get("budget"), "$.budget", errors)
    limit = _int(budget.get("batch_limit"), "$.budget.batch_limit", errors)
    consumed = _int(budget.get("consumed"), "$.budget.consumed", errors)
    remaining = _int(budget.get("remaining"), "$.budget.remaining", errors)
    total = _int(budget.get("total_ceiling"), "$.budget.total_ceiling", errors)
    total_consumed = _int(budget.get("total_consumed"), "$.budget.total_consumed", errors)
    if None not in (limit, consumed, remaining) and (limit < 0 or consumed < 0 or remaining < 0 or remaining != limit - consumed):
        errors.append(_diag("budget_arithmetic", "$.budget", "remaining must equal batch_limit minus consumed"))
    if None not in (consumed, total) and (total < 0 or consumed > total):
        errors.append(_diag("budget_ceiling", "$.budget", "consumed exceeds total ceiling"))
    if None not in (total_consumed, total) and (total_consumed < 0 or total_consumed > total):
        errors.append(_diag("budget_ceiling", "$.budget.total_consumed", "total consumed exceeds total ceiling"))

    required_observation = ("campaign_id", "epoch", "source_run_id", "repository_identity", "source_commit",
                            "objective_digest", "module_digest", "bundle_digest", "policy_digest",
                            "action_digest", "attempt_status", "current_state_id", "evidence_refs")
    for key in required_observation:
        if key not in observation:
            errors.append(_diag("missing_observation", f"$.observation.{key}", "current controller observation is required"))
    for key in ("campaign_id", "source_run_id", "repository_identity", "source_commit", "objective_digest",
                "module_digest", "bundle_digest", "policy_digest"):
        _same(state, observation, key, errors)
    if epoch is not None and observation.get("epoch") != epoch:
        errors.append(_diag("epoch_mismatch", "$.observation.epoch", "does not match state epoch"))
    if observation.get("attempt_status") not in {"ready", "running", "completed", "failed", "unknown", "interrupted", "reconciled"}:
        errors.append(_diag("invalid_attempt_status", "$.observation.attempt_status", "unsupported controller attempt status"))
    if not isinstance(observation.get("current_state_id"), str) or not DIGEST.fullmatch(observation.get("current_state_id", "")):
        errors.append(_diag("invalid_observation_state_id", "$.observation.current_state_id", "must be a state digest"))
    if not isinstance(observation.get("evidence_refs"), list) or not observation.get("evidence_refs"):
        errors.append(_diag("missing_observation_evidence", "$.observation.evidence_refs", "controller evidence references are required"))
    if action is not None and isinstance(action, Mapping):
        action_digest = action.get("action_digest") or action.get("digest")
        if action_digest is not None:
            _digest(action_digest, "$.next_action.action_digest", errors)
            if observation.get("action_digest") != action_digest:
                errors.append(_diag("action_mismatch", "$.observation.action_digest", "does not match next action"))

    delegation = _obj(state.get("delegation"), "$.delegation", errors)
    if not DIGEST.fullmatch(delegation.get("grant_id", "")):
        errors.append(_diag("missing_delegation_grant", "$.delegation.grant_id", "delegation must bind an exact grant identity"))
    if grant.get("grant_id") is not None and delegation.get("grant_id") not in (None, grant.get("grant_id")):
        errors.append(_diag("grant_identity_mismatch", "$.delegation.grant_id", "does not match supplied grant"))
    owner = _obj(state.get("owner"), "$.owner", errors)
    if isinstance(action, Mapping) and action.get("owner") not in (None, owner.get("id")):
        errors.append(_diag("owner_mismatch", "$.next_action.owner", "next action has another owner"))

    for key in ("grant_id", "campaign_id", "owner", "objective_digest", "repository_identity", "policy_digest", "expires_at", "revoked", "renewal_allowed", "authority", "budget_caps"):
        if key not in grant:
            errors.append(_diag("missing_grant", f"$.grant.{key}", "trusted current grant field is required"))
    grant_id = grant.get("grant_id")
    _digest(grant_id, "$.grant.grant_id", errors)
    if grant.get("campaign_id") != state.get("campaign_id"):
        errors.append(_diag("grant_scope_mismatch", "$.grant.campaign_id", "grant is for another campaign"))
    expiry = _timestamp(grant.get("expires_at"), "$.grant.expires_at", errors)
    revoked = grant.get("revoked")
    if not isinstance(revoked, bool):
        errors.append(_diag("invalid_revocation", "$.grant.revoked", "must be boolean"))
    if not isinstance(grant.get("renewal_allowed"), bool):
        errors.append(_diag("invalid_renewal_policy", "$.grant.renewal_allowed", "must be boolean"))
    if not isinstance(grant.get("authority"), Mapping):
        errors.append(_diag("invalid_authority", "$.grant.authority", "must be an object"))
    if grant.get("owner") != state.get("owner", {}).get("id"):
        errors.append(_diag("grant_scope_mismatch", "$.grant.owner", "grant owner differs from state"))
    for key in ("objective_digest", "repository_identity", "policy_digest"):
        if grant.get(key) != state.get(key):
            errors.append(_diag("grant_scope_mismatch", f"$.grant.{key}", "grant binding differs from state"))
    caps = _obj(grant.get("budget_caps"), "$.grant.budget_caps", errors)
    for key in ("batch_limit", "total_ceiling"):
        cap = _int(caps.get(key), f"$.grant.budget_caps.{key}", errors)
        if cap is not None and isinstance(budget.get(key), int) and not isinstance(budget.get(key), bool) and budget[key] > cap:
            errors.append(_diag("budget_scope_expansion", f"$.budget.{key}", "state budget exceeds grant cap"))
    observed = observation.get("observed_state") or observation.get("status")
    evidence = observation.get("evidence_refs", ())
    evidence_refs = tuple(evidence) if isinstance(evidence, list) and all(isinstance(x, str) for x in evidence) else ()
    try:
        key = digest({"campaign_id": state.get("campaign_id"), "epoch": epoch, "next_action": action}) if epoch is not None else None
    except (TypeError, ValueError, OverflowError):
        key = None
        errors.append(_diag("invalid_json_value", "$.next_action", "contains a noncanonical JSON value"))

    requested_authority = observation.get("requested_authority")
    expansion = isinstance(requested_authority, Mapping) and requested_authority != state.get("authority")
    if isinstance(grant.get("authority"), Mapping) and grant["authority"] != state.get("authority"):
        expansion = True
    if errors:
        disposition = "invalid_state"
    elif expansion:
        disposition = "authority_expansion"
    elif revoked:
        disposition = "revoked"
    elif expiry and now and now >= expiry:
        disposition = "expired"
    elif status.get("terminal") is True or phase in {"completed", "stopped"}:
        disposition = "complete" if phase == "completed" else "blocked"
    elif total_consumed is not None and total is not None and total_consumed >= total:
        disposition = "budget_exhausted"
    elif remaining == 0 and grant.get("renewal_allowed") is not True:
        disposition = "budget_exhausted"
    elif remaining == 0 and observation.get("checkpoint_verified") is not True:
        disposition = "budget_exhausted"
    elif observation.get("ambiguous") is True or observation.get("concurrent") is True:
        disposition = "concurrent_or_ambiguous"
    elif phase == "blocked":
        disposition = "blocked"
    elif phase == "unknown" or status.get("reason") == "unknown":
        disposition = "unknown"
    elif observation.get("attempt_status") in {"unknown", "interrupted"} or observed == "unknown":
        disposition = "unknown"
    elif observation.get("attempt_status") in {"running", "failed"}:
        disposition = "reconcile"
    elif observation.get("duplicate") is True or observation.get("attempt_status") == "completed":
        disposition = "duplicate_replay"
    elif observation.get("current_state_id") not in (None, state_id):
        disposition = "stale"
    else:
        disposition = "continue"
    diagnostics = list(errors)
    if expansion:
        diagnostics.append(_diag("authority_expansion", "$.observation.requested_authority", "requested envelope differs from state authority"))
    renewal = {"eligible": True, "proposed_batch_limit": min(limit, total - total_consumed), "total_consumed": total_consumed, "total_ceiling": total} if disposition == "continue" and remaining == 0 else None
    action_json = None
    if disposition == "continue" and action is not None:
        try:
            action_json = canonical_json(action).decode("utf-8")
        except (TypeError, ValueError, OverflowError):
            diagnostics.append(_diag("invalid_json_value", "$.next_action", "contains a noncanonical JSON value"))
            disposition = "invalid_state"
    return Assessment(disposition, disposition == "continue", state_id, key,
                      tuple(sorted(diagnostics, key=lambda d: (d.path, d.code, d.reason))),
                      action_json, evidence_refs, renewal)


STATE_FIELDS = frozenset("schema state_id campaign_id epoch source_run_id repository_identity source_commit predecessor_state_id objective_digest module_digest bundle_digest policy_digest owner authority delegation budget next_action status evidence_refs created_at updated_at".split())
IDENTITIES = frozenset("campaign_id source_run_id repository_identity source_commit objective_digest module_digest bundle_digest policy_digest".split())
BUDGET_FIELDS = frozenset("batch_limit consumed remaining total_consumed total_ceiling".split())
OBS_REQUIRED = IDENTITIES | {"epoch", "action_digest", "attempt_status", "current_state_id", "evidence_refs", "budget", "predecessor_state_id"}
OBS_OPTIONAL = frozenset("checkpoint_verified ambiguous concurrent duplicate requested_authority observed_state status".split())
GRANT_FIELDS = frozenset("grant_id campaign_id owner objective_digest repository_identity policy_digest expires_at revoked renewal_allowed authority budget_caps decision_class".split())


def _shape(value: Any, required: set | frozenset, optional: set | frozenset = frozenset()) -> bool:
    return isinstance(value, dict) and required <= value.keys() <= required | optional


def assess(state: Any, observation: Any, grant: Any, as_of: datetime | str) -> Assessment:
    """Assess JSON snapshots; malformed inputs are deterministic refusals.

    Observations and grants must be supplied independently by the trusted owner.
    Budget and predecessor observations prevent a proposed state from resetting
    recorded consumption. This function cannot authenticate those observations.
    """
    try:
        state, observation, grant = json.loads(canonical_json([state, observation, grant]))
        checks = (
            (_shape(state, STATE_FIELDS), "state"),
            (_shape(observation, OBS_REQUIRED, OBS_OPTIONAL), "observation"),
            (_shape(grant, GRANT_FIELDS), "grant"),
        )
        bad = tuple(_diag("invalid_shape", path, "Missing or unknown contract fields.") for valid, path in checks if not valid)
        if bad:
            return Assessment("invalid_state", False, None, None, bad)
        owner, budget, status, action = state["owner"], state["budget"], state["status"], state["next_action"]
        checks = (
            (_shape(owner, {"kind", "id"}) and all(isinstance(v, str) and bool(v.strip()) for v in owner.values()), "state.owner"),
            (_shape(budget, BUDGET_FIELDS) and all(type(v) is int and v >= 0 for v in budget.values()), "state.budget"),
            (_shape(observation["budget"], BUDGET_FIELDS) and all(type(v) is int and v >= 0 for v in observation["budget"].values()), "observation.budget"),
            (_shape(status, {"phase", "terminal"}, {"reason"}) and isinstance(status["phase"], str) and type(status["terminal"]) is bool, "state.status"),
            (_shape(state["delegation"], {"grant_id", "decision_class"}) and state["delegation"]["decision_class"] == "same-envelope-continuation", "state.delegation"),
            (isinstance(state["authority"], dict) and bool(state["authority"]), "state.authority"),
            (action is None or (_shape(action, {"kind", "owner", "action_digest"}) and all(isinstance(v, str) and bool(v) for v in action.values())), "state.next_action"),
            (all(isinstance(state[k], str) and bool(state[k]) for k in IDENTITIES), "state.identities"),
            (type(observation["epoch"]) is int and isinstance(observation["attempt_status"], str), "observation.attempt"),
            (isinstance(observation["current_state_id"], str), "observation.current_state_id"),
            (all(isinstance(v, list) and bool(v) and all(isinstance(x, str) and bool(x.strip()) for x in v) for v in (state["evidence_refs"], observation["evidence_refs"])), "evidence_refs"),
            (_shape(grant["budget_caps"], {"batch_limit", "total_ceiling"}) and all(type(v) is int and v > 0 for v in grant["budget_caps"].values()), "grant.budget_caps"),
            (grant["decision_class"] == "same-envelope-continuation", "grant.decision_class"),
            (all(type(observation[k]) is bool for k in ("checkpoint_verified", "ambiguous", "concurrent", "duplicate") if k in observation), "observation.flags"),
            ("requested_authority" not in observation or isinstance(observation["requested_authority"], dict), "observation.requested_authority"),
            (all(isinstance(observation[k], str) for k in ("observed_state", "status") if k in observation), "observation.status"),
            ("reason" not in status or isinstance(status["reason"], str), "state.status.reason"),
        )
        bad = tuple(_diag("invalid_shape", path, "Value does not match the v1 contract.") for valid, path in checks if not valid)
        if bad:
            return Assessment("invalid_state", False, state.get("state_id"), None, bad)
        if budget != observation["budget"] or state["predecessor_state_id"] != observation["predecessor_state_id"]:
            return Assessment("invalid_state", False, state.get("state_id"), None, (_diag("observation_mismatch", "observation", "Recorded budget or predecessor differs from proposed state."),))
        if budget["total_consumed"] < budget["consumed"] or budget["batch_limit"] == 0:
            return Assessment("invalid_state", False, state.get("state_id"), None, (_diag("budget_arithmetic", "state.budget", "Total consumption cannot be below batch consumption; batch must be positive."),))
        if (status["phase"] in {"completed", "stopped"}) != status["terminal"]:
            return Assessment("invalid_state", False, state.get("state_id"), None, (_diag("terminal_mismatch", "state.status", "Terminal flag and phase disagree."),))
        if isinstance(as_of, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", as_of):
            return Assessment("invalid_state", False, state.get("state_id"), None, (_diag("invalid_as_of", "as_of", "Expected RFC3339 timestamp."),))
        return _assess(state, observation, grant, as_of)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        return Assessment("invalid_state", False, None, None, (_diag("invalid_json", "$", str(exc)),))


def _load(path: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--observation", required=True)
    parser.add_argument("--grant", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = assess(_load(args.state), _load(args.observation), _load(args.grant), args.as_of)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"assessment_schema": 1, "disposition": "invalid_state",
                          "admissible": False, "diagnostics": [{"code": "input_error", "path": "$", "reason": str(exc)}]}, sort_keys=True))
        return 2
    print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0 if result.admissible else 1


if __name__ == "__main__":
    raise SystemExit(main())
