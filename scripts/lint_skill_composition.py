#!/usr/bin/env python3
"""Composition linter for the skill contract registry, recipes, and catalog edges.

Deterministic, stdlib-only. Mirrors the required structure of
capabilities/contracts/skill-contract.schema.json; the schema file remains the
canonical shape for external tooling. Exit 1 on any error; warnings go to
stderr without failing the run.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "capabilities" / "contracts"
RECIPES_DIR = ROOT / "capabilities" / "recipes"
CATALOG = ROOT / "capabilities" / "skills.toml"

DIGEST = re.compile(r"^[0-9a-f]{64}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ROLE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
PORT = re.compile(r"^[a-z0-9_]+$")

REQUIRED_TOP = [
    "contract_schema", "unit", "inputs", "outputs", "preconditions",
    "failures", "effects", "determinism", "resources", "authority",
    "evidence", "compatibility",
]
INPUT_CLASSES = {"artifact", "observation", "claim", "human_decision"}
OUTPUT_CLASSES = {"claim", "diagnostic", "controller_evidence", "rendering"}
CARDINALITY = {"one", "zero-or-one", "many"}
FAILURE_TYPES = {"invalid_input", "denied_effect", "conclusive_failure",
                 "timeout", "cancellation", "unknown"}
EFFECT_KINDS = {"filesystem", "process", "network", "credential", "model",
                "external_state", "install", "git", "release", "deployment", "none"}
EFFECT_MODES = {"read", "write", "execute"}
OVERLAP_KINDS = {"alias", "router", "composer", "producer-consumer", "shared-backend"}
BREAKING = ["effect", "authority", "confinement", "resource", "recovery", "output_meaning"]


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def lint_contract(path: Path, errors: list[str], warnings: list[str]) -> tuple[str, dict]:
    doc = load_json(path)
    name = path.name
    for key in REQUIRED_TOP:
        if key not in doc:
            errors.append(f"{name}: missing required key '{key}'")
    unit = doc.get("unit", {})
    for key in ("phase_id", "skill", "semantic_version", "guidance_digest"):
        if not unit.get(key):
            errors.append(f"{name}: unit.{key} missing")
    phase_id = unit.get("phase_id", "")
    if phase_id and not SLUG.fullmatch(phase_id):
        errors.append(f"{name}: unit.phase_id must be a kebab-case slug")
    if unit.get("semantic_version") and not SEMVER.fullmatch(unit["semantic_version"]):
        errors.append(f"{name}: unit.semantic_version must be semver")
    digest = unit.get("guidance_digest", "")
    if digest and not DIGEST.fullmatch(digest):
        errors.append(f"{name}: unit.guidance_digest must be lowercase sha256")
    skill = unit.get("skill", "")
    guidance = ROOT / "skills" / skill / "SKILL.md"
    if skill and guidance.is_file():
        actual = hashlib.sha256(guidance.read_bytes()).hexdigest()
        if digest and digest != actual:
            errors.append(
                f"{name}: guidance digest is stale (declared {digest[:12]}, "
                f"actual {actual[:12]} for skills/{skill}/SKILL.md)"
            )
    elif skill:
        errors.append(f"{name}: no skills/{skill}/SKILL.md for declared unit.skill")

    ports = {"inputs": INPUT_CLASSES, "outputs": OUTPUT_CLASSES}
    for section, classes in ports.items():
        items = doc.get(section, [])
        if not isinstance(items, list) or not items:
            errors.append(f"{name}: {section} must be a non-empty array")
            continue
        for item in items:
            if not PORT.fullmatch(item.get("name", "")):
                errors.append(f"{name}: {section} port name invalid: {item.get('name')!r}")
            if item.get("epistemic_class") not in classes:
                errors.append(
                    f"{name}: {section}[{item.get('name')}].epistemic_class "
                    f"{item.get('epistemic_class')!r} not in {sorted(classes)}"
                )
            if "required" in item and not isinstance(item["required"], bool):
                errors.append(f"{name}: {section}[{item.get('name')}].required must be boolean")

    failures = doc.get("failures", [])
    if not failures:
        errors.append(f"{name}: failures must be a non-empty array")
    for item in failures:
        if item.get("failure_type") not in FAILURE_TYPES:
            errors.append(f"{name}: failures.failure_type {item.get('failure_type')!r} invalid")
        if not isinstance(item.get("retryable"), bool):
            errors.append(f"{name}: failures[{item.get('failure_type')}].retryable must be boolean")

    for item in doc.get("effects", []):
        if item.get("kind") not in EFFECT_KINDS:
            errors.append(f"{name}: effects.kind {item.get('kind')!r} invalid")
        if item.get("mode") not in EFFECT_MODES:
            errors.append(f"{name}: effects.mode {item.get('mode')!r} invalid")

    determinism = doc.get("determinism", {})
    if determinism.get("status") not in {"pure", "effectful"}:
        errors.append(f"{name}: determinism.status must be 'pure' or 'effectful'")

    authority = doc.get("authority", {})
    if authority.get("attenuate_only") is not True:
        errors.append(f"{name}: authority.attenuate_only must be true (invariant)")

    compatibility = doc.get("compatibility", {})
    if compatibility.get("breaking_widenings") != BREAKING:
        errors.append(f"{name}: compatibility.breaking_widenings must be exactly {BREAKING}")

    resources = doc.get("resources", {})
    if not isinstance(resources, dict):
        errors.append(f"{name}: resources must be an object")

    return phase_id, doc


def lint_recipe(path: Path, contracts: dict[str, dict], skills: set[str],
                errors: list[str], warnings: list[str]) -> None:
    doc = load_json(path)
    name = path.name
    for key in ("recipe_schema", "name", "runtime_profile", "entry",
                "required_roles", "edges", "completeness_checks"):
        if key not in doc:
            errors.append(f"{name}: missing required key '{key}'")

    contracted_phases = set(contracts)
    roles = {}
    for role in doc.get("required_roles", []):
        rid = role.get("role", "")
        if not ROLE_ID.fullmatch(rid):
            errors.append(f"{name}: role id invalid: {rid!r}")
        roles[rid] = role
        for target in role.get("resolve_to", []) + role.get("alternatives", []):
            if target in contracted_phases:
                continue
            if target in skills:
                if not role.get("optional"):
                    errors.append(
                        f"{name}: role '{rid}' resolves to '{target}' which has no "
                        f"contract; non-optional roles must resolve to registered phases"
                    )
                else:
                    warnings.append(
                        f"{name}: role '{rid}' target '{target}' has no contract yet "
                        f"(optional role tolerated)"
                    )
            else:
                errors.append(f"{name}: role '{rid}' resolves to unknown skill/phase '{target}'")

    for edge in doc.get("edges", []):
        for endpoint in (edge.get("from", ""), edge.get("to", "")):
            if endpoint not in contracted_phases and endpoint not in roles and endpoint not in skills:
                errors.append(f"{name}: edge endpoint '{endpoint}' is not a role, phase, or skill")
        src = contracts.get(edge.get("from"))
        if src:
            outputs = {item["name"] for item in src.get("outputs", [])}
            if edge.get("output") not in outputs:
                errors.append(
                    f"{name}: edge output '{edge.get('output')}' is not an output of "
                    f"phase '{edge.get('from')}'"
                )
        dst = contracts.get(edge.get("to"))
        if dst:
            inputs = {item["name"] for item in dst.get("inputs", [])}
            if edge.get("input") not in inputs:
                errors.append(
                    f"{name}: edge input '{edge.get('input')}' is not an input of "
                    f"phase '{edge.get('to')}'"
                )


def lint_catalog(skills: dict, errors: list[str], warnings: list[str]) -> None:
    names = set(skills)
    declared: dict[str, set[str]] = {n: set(v.get("overlaps", [])) for n, v in skills.items()}
    for name, targets in sorted(declared.items()):
        if not targets:
            continue
        if "overlap_kind" not in skills[name]:
            errors.append(f"skills.{name}: declares overlaps without overlap_kind")
        elif skills[name]["overlap_kind"] not in OVERLAP_KINDS:
            errors.append(
                f"skills.{name}: overlap_kind {skills[name]['overlap_kind']!r} "
                f"not in {sorted(OVERLAP_KINDS)}"
            )
        per_pair = skills[name].get("overlap_kinds", {})
        if not isinstance(per_pair, dict):
            errors.append(f"skills.{name}: overlap_kinds must be a table")
        else:
            unknown_keys = sorted(set(per_pair) - targets)
            if unknown_keys:
                errors.append(
                    f"skills.{name}: overlap_kinds names non-overlapped skills: "
                    f"{', '.join(unknown_keys)}"
                )
            for target, kind in sorted(per_pair.items()):
                if kind not in OVERLAP_KINDS:
                    errors.append(
                        f"skills.{name}: overlap_kinds.{target} kind {kind!r} "
                        f"not in {sorted(OVERLAP_KINDS)}"
                    )
        for target in sorted(targets):
            if target not in names:
                errors.append(f"skills.{name}: overlaps unknown skill '{target}'")
            elif name not in declared.get(target, set()):
                errors.append(
                    f"skills.{name}: overlaps '{target}' but the reverse edge is missing "
                    f"(add '{name}' to skills.{target}.overlaps)"
                )
    for name, entry in sorted(skills.items()):
        for target in entry.get("routes_to", []):
            if target not in names:
                errors.append(f"skills.{name}: routes_to unknown skill '{target}'")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    contracts: dict[str, dict] = {}
    contract_files = sorted(CONTRACTS_DIR.glob("*.contract.json"))
    for path in contract_files:
        phase_id, doc = lint_contract(path, errors, warnings)
        if phase_id:
            if phase_id in contracts:
                errors.append(f"{path.name}: duplicate phase_id '{phase_id}'")
            contracts[phase_id] = doc

    with CATALOG.open("rb") as handle:
        catalog = tomllib.load(handle)
    skills = catalog.get("skills", {})

    for path in sorted(RECIPES_DIR.glob("*.recipe.json")):
        lint_recipe(path, contracts, set(skills), errors, warnings)

    lint_catalog(skills, errors, warnings)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if errors:
        print("Skill composition lint failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Skill composition is consistent: {len(contract_files)} contracts, "
        f"{len(list(RECIPES_DIR.glob('*.recipe.json')))} recipes, "
        f"{len(skills)} catalog entries checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
