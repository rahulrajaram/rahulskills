#!/usr/bin/env python3
"""Validate learning claims and prepare deterministic retrospective input.

Pure ingestion never promotes findings, authenticates actors, or changes a run.
The CLI reads bounded JSON and writes one result to stdout; it performs no writes.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


MAX_BYTES = 1_048_576
MAX_RECORDS = 10_000
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
CONTEXT_KEYS = frozenset({"campaign_id", "epoch", "run_id", "source_commit", "policy_digest"})
RECORD_REQUIRED = frozenset({"record_schema", "finding", "source_skill", "evidence_refs", "disposition"})
RECORD_KEYS = RECORD_REQUIRED | {"rule_id", "promotion_contract"}
STATUSES = frozenset({"recorded", "promoted", "routed", "dismissed"})


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    reason: str


@dataclass(frozen=True)
class IngestionResult:
    accepted: bool
    document_json: str | None
    diagnostics: tuple[Issue, ...] = ()

    @property
    def document(self) -> dict[str, Any] | None:
        return json.loads(self.document_json) if self.document_json is not None else None

    def to_dict(self) -> dict[str, Any]:
        return {"accepted": self.accepted, "document": self.document,
                "diagnostics": [asdict(issue) for issue in self.diagnostics]}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _issue(condition: bool, code: str, path: str, reason: str) -> tuple[Issue, ...]:
    return () if condition else (Issue(code, path, reason),)


def _context_errors(value: Any) -> tuple[Issue, ...]:
    if not isinstance(value, dict):
        return (Issue("invalid_context", "context", "Expected an object."),)
    return (
        _issue(set(value) == CONTEXT_KEYS, "invalid_context", "context", "Context fields must match the v1 contract.")
        + _issue(bool(SLUG.fullmatch(value.get("campaign_id", ""))) if isinstance(value.get("campaign_id"), str) else False,
                 "invalid_context", "context.campaign_id", "Expected a nonempty slug.")
        + _issue(type(value.get("epoch")) is int and value["epoch"] >= 1,
                 "invalid_context", "context.epoch", "Expected a positive integer, not a boolean.")
        + _issue(_text(value.get("run_id")), "invalid_context", "context.run_id", "Expected a run identity.")
        + _issue(bool(COMMIT.fullmatch(value.get("source_commit", ""))) if isinstance(value.get("source_commit"), str) else False,
                 "invalid_context", "context.source_commit", "Expected an exact Git commit digest.")
        + _issue(bool(SHA256.fullmatch(value.get("policy_digest", ""))) if isinstance(value.get("policy_digest"), str) else False,
                 "invalid_context", "context.policy_digest", "Expected a SHA256 digest.")
    )


def _record_errors(value: Any, path: str) -> tuple[Issue, ...]:
    if not isinstance(value, dict):
        return (Issue("invalid_record", path, "Expected a learning-record object."),)
    disposition = value.get("disposition")
    refs = value.get("evidence_refs")
    rule = value.get("rule_id")
    return (
        _issue(RECORD_REQUIRED <= set(value) <= RECORD_KEYS, "invalid_record", path, "Missing or unknown learning-record fields.")
        + _issue(type(value.get("record_schema")) is int and value["record_schema"] == 1,
                 "invalid_record", path + ".record_schema", "Only record_schema 1 is supported.")
        + _issue(_text(value.get("finding")), "invalid_record", path + ".finding", "Expected a nonempty finding.")
        + _issue(isinstance(value.get("source_skill"), str) and bool(SLUG.fullmatch(value["source_skill"])),
                 "invalid_record", path + ".source_skill", "Expected a skill slug.")
        + _issue(isinstance(refs, list) and bool(refs) and all(_text(ref) for ref in refs),
                 "invalid_record", path + ".evidence_refs", "Expected nonempty evidence references; they are references, not verified evidence.")
        + _issue(rule is None or (isinstance(rule, str) and bool(re.fullmatch(r"DIAG-[0-9]{3}", rule))),
                 "invalid_record", path + ".rule_id", "Expected null or DIAG-NNN.")
        + _issue("promotion_contract" not in value or _text(value["promotion_contract"]),
                 "invalid_record", path + ".promotion_contract", "A supplied promotion contract must be nonempty.")
        + _issue(isinstance(disposition, dict) and {"status"} <= set(disposition) <= {"status", "target"}
                 and isinstance(disposition.get("status"), str) and disposition["status"] in STATUSES
                 and (disposition.get("target") is None or isinstance(disposition["target"], str)),
                 "invalid_record", path + ".disposition", "Invalid disposition; existing promotion labels remain source claims only.")
    )


def _entry(record: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    record_digest = digest(record)
    return {"entry_id": digest({"context": context, "record_digest": record_digest}),
            "record_digest": record_digest, "epistemic_class": "claim", "record": record}


def _prior_records(previous: Any, context: dict[str, Any]) -> tuple[tuple[dict[str, Any], ...], tuple[Issue, ...]]:
    if previous is None:
        return (), ()
    fields = {"schema_version", "kind", "context", "entries", "digest"}
    if not isinstance(previous, dict) or set(previous) != fields:
        return (), (Issue("invalid_previous", "previous", "Expected a complete retrospective-learning-input document."),)
    if previous["context"] != context:
        return (), (Issue("provenance_conflict", "previous.context", "Prior ingestion belongs to different run/epoch/source/policy context."),)
    if (type(previous["schema_version"]) is not int or previous["schema_version"] != 1
            or previous["kind"] != "retrospective-learning-input"
            or not isinstance(previous["entries"], list) or len(previous["entries"]) > MAX_RECORDS):
        return (), (Issue("invalid_previous", "previous", "Unsupported or malformed ingestion document."),)
    body = {key: value for key, value in previous.items() if key != "digest"}
    if previous["digest"] != digest(body):
        return (), (Issue("invalid_previous", "previous.digest", "Ingestion document digest does not match its content."),)
    errors = tuple(issue for index, item in enumerate(previous["entries"])
                   for issue in _record_errors(item.get("record") if isinstance(item, dict) else None,
                                               f"previous.entries[{index}].record"))
    if errors:
        return (), errors
    entries = previous["entries"]
    records = tuple(item["record"] for item in entries)
    expected = sorted((_entry(record, context) for record in records), key=lambda item: item["record_digest"])
    if entries != expected or len({item["record_digest"] for item in entries}) != len(entries):
        return (), (Issue("invalid_previous", "previous.entries", "Entries are changed, duplicated, unordered, or carry an unsupported evidence class."),)
    return records, ()


def ingest(records: Any, context: Any, previous: Any = None) -> IngestionResult:
    """Return atomic retrospective input or diagnostics; never mutate inputs."""
    try:
        # Freeze a JSON snapshot so callers cannot mutate retained result values.
        records, context, previous = json.loads(canonical_json([records, context, previous]))
        errors = _context_errors(context)
        if not isinstance(records, list) or len(records) > MAX_RECORDS:
            errors += (Issue("invalid_records", "records", "Expected a bounded array of learning records."),)
        else:
            errors += tuple(issue for index, record in enumerate(records)
                            for issue in _record_errors(record, f"records[{index}]"))
        if errors:
            return IngestionResult(False, None, errors)
        prior, errors = _prior_records(previous, context)
        if errors:
            return IngestionResult(False, None, errors)
        unique = {digest(record): record for record in (*prior, *records)}
        if len(unique) > MAX_RECORDS:
            return IngestionResult(False, None, (Issue("too_many_records", "records", "Merged batch exceeds record bound."),))
        body = {"schema_version": 1, "kind": "retrospective-learning-input", "context": context,
                "entries": [_entry(unique[key], context) for key in sorted(unique)]}
        return IngestionResult(True, canonical_json({**body, "digest": digest(body)}))
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        return IngestionResult(False, None, (Issue("invalid_json", "$", str(exc)),))


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = tuple(key for key, _ in pairs)
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate JSON object key.")
    return dict(pairs)


def _bad_constant(value: str) -> None:
    raise ValueError(f"Nonfinite JSON number: {value}")


def read_json(path: str) -> Any:
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Input exceeds the one MiB byte bound.")
    return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_bad_constant)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--previous")
    args = parser.parse_args(argv)
    try:
        result = ingest(read_json(args.records), read_json(args.context),
                        read_json(args.previous) if args.previous else None)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        result = IngestionResult(False, None, (Issue("input_error", "$", str(exc)),))
    print(canonical_json(result.to_dict()))
    return 0 if result.accepted else 2


if __name__ == "__main__":
    sys.exit(main())
