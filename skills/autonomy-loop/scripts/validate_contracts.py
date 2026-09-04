#!/usr/bin/env python3
"""Validate cross-skill autonomy contract invariants without dependencies."""

from __future__ import annotations

import json
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_SKILLS = SKILL_DIR.parent
AUTONOMY = SKILL_DIR / "SKILL.md"
EXECUTOR = REPO_SKILLS / "autonomous-execution-contract" / "SKILL.md"
CHECKPOINT_SCHEMA = SKILL_DIR / "references" / "checkpoint-event.schema.json"


def require(text: str, fragments: tuple[str, ...], source: Path) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        joined = "\n  - ".join(missing)
        raise SystemExit(f"{source}: missing required contract text:\n  - {joined}")


def reject(text: str, fragments: tuple[str, ...], source: Path) -> None:
    present = [fragment for fragment in fragments if fragment in text]
    if present:
        joined = "\n  - ".join(present)
        raise SystemExit(f"{source}: contradictory legacy text remains:\n  - {joined}")


def validate_schema(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    expected = {
        "epic_id",
        "objective_digest",
        "authority_digest",
        "event_kind",
        "status",
        "source",
        "proof_receipt",
        "budgets",
        "token_usage",
        "failure_evidence",
        "next_ready_actions",
    }
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise SystemExit(f"{path}: checkpoint schema must use JSON Schema 2020-12")
    if not expected <= required:
        raise SystemExit(
            f"{path}: missing required fields: {sorted(expected - required)}"
        )
    max_frontier = schema["properties"]["next_ready_actions"].get("maxItems")
    if max_frontier != 5:
        raise SystemExit(
            f"{path}: ready frontier must be capped at 5, got {max_frontier!r}"
        )
    event_kinds = set(schema["properties"]["event_kind"].get("enum", []))
    lifecycle_kinds = {
        "patch_completed",
        "slice_completed",
        "tranche_completed",
        "commit_created",
        "milestone_completed",
    }
    if not lifecycle_kinds <= event_kinds:
        raise SystemExit(
            f"{path}: missing lifecycle event kinds: {sorted(lifecycle_kinds - event_kinds)}"
        )
    source_required = set(schema["properties"]["source"].get("required", []))
    identity_fields = {
        "tree",
        "dependency_digest",
        "toolchain",
        "feature_set_digest",
        "command_manifest_digest",
        "environment_digest",
        "frozen_artifact_digests",
    }
    if not identity_fields <= source_required:
        raise SystemExit(
            f"{path}: source identity is incomplete: {sorted(identity_fields - source_required)}"
        )


def main() -> None:
    autonomy = AUTONOMY.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")

    require(
        autonomy,
        (
            "ranked ready frontier of at most 5 tasks",
            "### Budget Precedence",
            "## Compiled Epic Contract",
            "## Proof Schedule And Receipts",
            "Append a checkpoint event after every commit, expensive proof run",
            "A slice need not equal a commit.",
        ),
        AUTONOMY,
    )
    require(
        executor,
        (
            "## Budget Precedence",
            "## Checkpoint And Receipt Minimum",
            "availability alone never grants delegation authority.",
            "Run milestone/global proof only when the inherited proof schedule says it is",
            "a patch, slice,\n   checkpoint, commit, and milestone are distinct events.",
        ),
        EXECUTOR,
    )
    reject(
        autonomy,
        (
            "Generate or refresh the next 10 candidate tasks.",
            "Re-rank the next 10 candidate tasks against the active epic.",
        ),
        AUTONOMY,
    )
    reject(
        executor,
        (
            "If unspecified and sub-agent tooling is available, prefer `sub-agents`",
            "Run the contract's proof target when focused checks pass.",
            "Update the checkpoint state when progress is material",
        ),
        EXECUTOR,
    )
    validate_schema(CHECKPOINT_SCHEMA)
    print("PASS: autonomy-loop and autonomous-execution-contract are congruent")


if __name__ == "__main__":
    main()
