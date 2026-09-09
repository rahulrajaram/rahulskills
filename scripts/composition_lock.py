#!/usr/bin/env python3
"""Content addressed composition locks and typed edge admission.

The module is deliberately stdlib-only.  File loading and CLI output are the
thin effect boundary; lock construction, edge checking, and reports are pure
functions over JSON values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = 1
PORT_CLASSES = {
    "artifact", "observation", "claim", "human_decision",
    "diagnostic", "controller_evidence", "rendering",
}
CARDINALITIES = {"one", "zero-or-one", "many"}
BREAKING_DIMENSIONS = {
    "effect", "authority", "confinement", "resource", "recovery", "output_meaning",
}
_REVIEW = "review_required"


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


class FrozenDict(dict):
    """JSON-compatible immutable mapping used inside Result values."""
    def _blocked(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError("immutable composition result")
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _blocked
    __ior__ = _blocked

    def __deepcopy__(self, memo: dict[int, Any]) -> "FrozenDict":
        return self


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return FrozenDict({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class Result:
    ok: bool
    value: Any = None
    issues: tuple[Issue, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _freeze(self.value))

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "value": self.value,
                "issues": [item.as_dict() for item in self.issues]}


def canonical_json(value: Any) -> bytes:
    """Return the repository's canonical UTF-8 JSON representation."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate object key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ValueError(f"non-finite JSON number: {value}")


def load_json(path: Path) -> Result:
    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=_strict_pairs,
                           parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return Result(False, issues=(Issue("invalid_json", str(path), str(exc)),))
    return Result(True, value)


def file_digest(path: Path) -> Result:
    try:
        return Result(True, sha256_bytes(path.read_bytes()))
    except (OSError, IOError) as exc:
        return Result(False, issues=(Issue("missing_file", str(path), str(exc)),))


def _issue(code: str, path: str, message: str) -> Issue:
    return Issue(code, path, message)


def _port(contract: Mapping[str, Any], section: str, name: str) -> Mapping[str, Any] | None:
    return next((p for p in contract.get(section, []) if p.get("name") == name), None)


def _schema_for(edge: Mapping[str, Any], producer: Mapping[str, Any], consumer: Mapping[str, Any]) -> tuple[Any, Any]:
    producer_port = _port(producer, "outputs", edge.get("output", edge.get("output_port", "")) or "")
    consumer_port = _port(consumer, "inputs", edge.get("input", edge.get("input_port", "")) or "")
    return (
        producer_port.get("schema_digest") if producer_port else None,
        consumer_port.get("schema_digest") if consumer_port else None,
    )


def _cardinality_compatible(producer: str, consumer: str) -> bool:
    # A consumer accepting many accepts one; optionality is safe only when the
    # producer can omit its value.  No other structural assignability is inferred.
    return ((producer == consumer) or
            (consumer == "zero-or-one" and producer in {"one", "zero-or-one"}) or
            (consumer == "many" and producer in {"one", "zero-or-one"}) or
            (producer == "zero-or-one" and consumer == "many"))


def _epistemic_compatible(producer: str, consumer: str) -> bool:
    # Classes are intentionally conservative.  Diagnostic/controller evidence
    # are not silently promoted to claims or human decisions.
    return producer == consumer or (producer == "claim" and consumer == "artifact")


def validate_edge(edge: Mapping[str, Any], contracts: Mapping[str, Mapping[str, Any]]) -> tuple[Issue, ...]:
    if not isinstance(edge, Mapping):
        return (_issue("malformed_edge", "edge", "edge must be an object"),)
    issues: list[Issue] = []
    src_name, dst_name = edge.get("from", edge.get("from_phase")), edge.get("to", edge.get("to_phase"))
    src, dst = contracts.get(src_name), contracts.get(dst_name)
    base = f"edges[{edge.get('_index', '?')}]"
    if src is None:
        issues.append(_issue("missing_endpoint", base + ".from", f"unknown phase {src_name!r}"))
    if dst is None:
        issues.append(_issue("missing_endpoint", base + ".to", f"unknown phase {dst_name!r}"))
    if src is None or dst is None:
        return tuple(issues)
    output, input_ = edge.get("output", edge.get("output_port")), edge.get("input", edge.get("input_port"))
    producer, consumer = _port(src, "outputs", output), _port(dst, "inputs", input_)
    if producer is None:
        issues.append(_issue("missing_port", base + ".output", f"{src_name}.{output} is not declared"))
    if consumer is None:
        issues.append(_issue("missing_port", base + ".input", f"{dst_name}.{input_} is not declared"))
    if producer is None or consumer is None:
        return tuple(issues)
    ps, cs = _schema_for(edge, src, dst)
    if not ps or not cs or not edge.get("producer_schema_digest") or not edge.get("consumer_schema_digest"):
        issues.append(_issue(_REVIEW, base + ".schema", "typed edge requires producer and consumer schema digests"))
    if edge.get("producer_schema_digest") and edge.get("producer_schema_digest") != ps:
        issues.append(_issue("schema_mismatch", base + ".producer_schema_digest", "edge pin differs from producer port schema"))
    if edge.get("consumer_schema_digest") and edge.get("consumer_schema_digest") != cs:
        issues.append(_issue("schema_mismatch", base + ".consumer_schema_digest", "edge pin differs from consumer port schema"))
    if ps and cs and ps != cs:
        issues.append(_issue(_REVIEW, base + ".schema", "schema migration is unsupported; review is required"))
    pc, cc = producer.get("cardinality"), consumer.get("cardinality")
    if pc not in CARDINALITIES or cc not in CARDINALITIES:
        issues.append(_issue("invalid_cardinality", base + ".cardinality", "ports must declare a supported cardinality"))
    elif not _cardinality_compatible(pc, cc):
        issues.append(_issue("cardinality_mismatch", base + ".cardinality", f"producer {pc!r} cannot feed consumer {cc!r}"))
    pe, ce = producer.get("epistemic_class"), consumer.get("epistemic_class")
    if pe not in PORT_CLASSES or ce not in PORT_CLASSES or not _epistemic_compatible(pe, ce):
        issues.append(_issue("epistemic_mismatch", base + ".epistemic_class", f"{pe!r} cannot feed {ce!r}"))
    declared = edge.get("producer_contract_digest"), edge.get("consumer_contract_digest")
    if not declared[0] or not declared[1]:
        issues.append(_issue(_REVIEW, base + ".contract", "edge must pin both contract identities"))
    return tuple(issues)


def _load_contracts(directory: Path) -> Result:
    contracts: dict[str, Mapping[str, Any]] = {}
    digests: dict[str, str] = {}
    issues: list[Issue] = []
    for path in sorted(directory.glob("*.contract.json")):
        loaded, digest = load_json(path), file_digest(path)
        issues.extend(loaded.issues); issues.extend(digest.issues)
        if not loaded.ok or not digest.ok or not isinstance(loaded.value, dict):
            continue
        phase = loaded.value.get("unit", {}).get("phase_id")
        if not phase:
            issues.append(_issue("invalid_contract", str(path), "unit.phase_id is required"))
            continue
        contracts[phase] = loaded.value
        digests[phase] = digest.value
    return Result(not issues, {"contracts": contracts, "digests": digests}, tuple(issues))


def build_lock(recipe: Mapping[str, Any], catalog: Mapping[str, Any], contracts: Mapping[str, Mapping[str, Any]],
               pins: Mapping[str, str], recipe_digest: str, catalog_digest: str,
               schema_digest: str, tool_version: str = "composition-lock/1") -> Result:
    edges: list[dict[str, Any]] = []
    issues: list[Issue] = []
    if not isinstance(recipe, Mapping) or not isinstance(catalog, Mapping) or not isinstance(contracts, Mapping):
        return Result(False, issues=(_issue("malformed_input", "composition", "recipe, catalog, and contracts must be objects"),))
    edges_input = recipe.get("edges", [])
    if not isinstance(edges_input, Sequence) or isinstance(edges_input, (str, bytes)):
        return Result(False, issues=(_issue("malformed_recipe", "edges", "recipe.edges must be an array"),))
    roles_raw = recipe.get("required_roles", [])
    selected_raw = recipe.get("selected_roles")
    selected_set_early = (set(selected_raw) if isinstance(selected_raw, Sequence) and not isinstance(selected_raw, (str, bytes))
                          and all(isinstance(item, str) for item in selected_raw) else None)
    def role_targets(role: Mapping[str, Any]) -> tuple[str, ...]:
        values: list[str] = []
        for field in ("resolve_to", "alternatives"):
            raw = role.get(field, ())
            if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
                return ()
            values.extend(item for item in raw if isinstance(item, str))
        return tuple(values)
    optional_targets = {target for role in roles_raw if isinstance(role, Mapping) and role.get("optional") and
                        role.get("role") not in (selected_set_early or set())
                        for target in role_targets(role)} if isinstance(roles_raw, Sequence) else set()
    for index, original in enumerate(edges_input):
        if not isinstance(original, Mapping):
            issues.append(_issue("malformed_edge", f"edges[{index}]", "edge must be an object"))
            continue
        edge = dict(original); edge.pop("active", None); edge["_index"] = index
        endpoints = {edge.get("from", edge.get("from_phase")), edge.get("to", edge.get("to_phase"))}
        if selected_set_early is not None and endpoints.intersection(optional_targets):
            edge["active"] = False
        edge["producer_contract_digest"] = edge.get("producer_contract_digest") or pins.get(edge.get("from", edge.get("from_phase")))
        edge["consumer_contract_digest"] = edge.get("consumer_contract_digest") or pins.get(edge.get("to", edge.get("to_phase")))
        source = contracts.get(edge.get("from", edge.get("from_phase"))); target = contracts.get(edge.get("to", edge.get("to_phase")))
        if isinstance(source, Mapping):
            port = _port(source, "outputs", edge.get("output", edge.get("output_port", "")))
            if port and "producer_schema_digest" not in edge: edge["producer_schema_digest"] = port.get("schema_digest")
        if isinstance(target, Mapping):
            port = _port(target, "inputs", edge.get("input", edge.get("input_port", "")))
            if port and "consumer_schema_digest" not in edge: edge["consumer_schema_digest"] = port.get("schema_digest")
        if edge.get("active", True):
            issues.extend(validate_edge(edge, contracts))
        source_id = edge.get("from", edge.get("from_phase")); target_id = edge.get("to", edge.get("to_phase"))
        if edge.get("producer_contract_digest") != pins.get(source_id):
            issues.append(_issue("contract_mismatch", f"edges[{index}].producer_contract_digest", "producer digest is not the current contract identity"))
        if edge.get("consumer_contract_digest") != pins.get(target_id):
            issues.append(_issue("contract_mismatch", f"edges[{index}].consumer_contract_digest", "consumer digest is not the current contract identity"))
        edge.pop("_index", None)
        edges.append(edge)
    # A cycle is a lifecycle construct only when every edge in that cycle is
    # explicitly bounded.  Recipe notes never imply this permission.
    adjacency: dict[str, list[tuple[str, Mapping[str, Any]]]] = {}
    for edge in edges:
        if edge.get("active") is False:
            continue
        source = edge.get("from", edge.get("from_phase")); target = edge.get("to", edge.get("to_phase"))
        adjacency.setdefault(source, []).append((target, edge))
    # Validated lifecycle backedges are removed; every remaining active edge
    # must form a DAG. This makes detection independent of edge ordering.
    def bounded_backedge(edge: Mapping[str, Any]) -> bool:
        termination = edge.get("termination")
        return (edge.get("kind") == "lifecycle_backedge" and isinstance(termination, Mapping) and
                isinstance(termination.get("max_epochs"), int) and not isinstance(termination.get("max_epochs"), bool) and
                termination["max_epochs"] > 0 and isinstance(termination.get("proof"), str) and bool(termination["proof"].strip()))
    for node, arcs in adjacency.items():
        for _, edge in arcs:
            if edge.get("kind") == "lifecycle_backedge" and not bounded_backedge(edge):
                issues.append(_issue("unbounded_cycle", "edges", "lifecycle backedge requires positive max_epochs and proof"))
    adjacency = {node: [(target, edge) for target, edge in arcs
                        if not bounded_backedge(edge)]
                 for node, arcs in adjacency.items()}
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(node: str) -> bool:
        if node in visiting: return True
        if node in visited or node not in adjacency: return False
        visiting.add(node)
        found = any(visit(target) for target, _ in adjacency[node])
        visiting.remove(node); visited.add(node)
        return found
    if any(visit(node) for node in sorted(adjacency)):
        issues.append(_issue("unbounded_cycle", "edges", "active composition graph must be acyclic after lifecycle backedges are removed"))
    roles_input = recipe.get("required_roles", [])
    if not isinstance(roles_input, Sequence) or isinstance(roles_input, (str, bytes)):
        issues.append(_issue("malformed_recipe", "required_roles", "recipe.required_roles must be an array")); roles_input = []
    for index, role in enumerate(roles_input):
        if not isinstance(role, Mapping) or not isinstance(role.get("role"), str):
            issues.append(_issue("malformed_role", f"required_roles[{index}]", "role must be an object with a string role"))
    roles = sorted((r for r in roles_input if isinstance(r, Mapping)), key=lambda x: x.get("role", ""))
    phase_names = set(contracts)
    catalog_skills = catalog.get("skills", {}) if isinstance(catalog, Mapping) else {}
    catalog_names = set(catalog_skills) if isinstance(catalog_skills, Mapping) else set()
    selected = recipe.get("selected_roles")
    if selected is not None and (not isinstance(selected, Sequence) or isinstance(selected, (str, bytes)) or
                                 any(not isinstance(item, str) for item in selected)):
        issues.append(_issue("malformed_recipe", "selected_roles", "selected_roles must be an array of strings"))
        selected = None
    selected_set = set(selected) if selected is not None else None
    role_by_name = {r.get("role"): r for r in roles}
    if selected_set is not None:
        for name in sorted(selected_set):
            if name not in role_by_name:
                issues.append(_issue("unknown_selected_role", "selected_roles", f"unknown selected role {name!r}"))
    active_targets = set()
    if selected_set is None:
        active_targets = {target for role in roles for target in role_targets(role)}
    else:
        for role_name in selected_set:
            role = role_by_name.get(role_name)
            if role:
                active_targets.update(role_targets(role))
    for index, role in enumerate(roles):
        targets = role_targets(role)
        if any(field in role and (not isinstance(role.get(field), Sequence) or isinstance(role.get(field), (str, bytes)) or
                                  not role.get(field) or any(not isinstance(item, str) for item in role.get(field, ())))
               for field in ("resolve_to", "alternatives")):
            issues.append(_issue("malformed_role", f"roles[{index}]", "role targets must be arrays of strings"))
        if len(targets) != len(set(targets)) or any(not target for target in targets):
            issues.append(_issue("malformed_role", f"roles[{index}]", "role targets must be unique and non-empty"))
        for target in targets:
            active_role = not role.get("optional") or selected_set is None or role.get("role") in selected_set
            if active_role and target not in phase_names:
                issues.append(_issue("unresolved_role", f"roles[{index}]", f"active role target {target!r} has no contract"))
            if active_role and target in phase_names:
                skill = contracts[target].get("unit", {}).get("skill")
                if skill and skill not in catalog_names:
                    issues.append(_issue("unbound_catalog_skill", f"roles[{index}]", f"contract skill {skill!r} is absent from catalog"))
    inactive_edges: list[dict[str, Any]] = []
    for edge in edges:
        endpoints = {edge.get("from", edge.get("from_phase")), edge.get("to", edge.get("to_phase"))}
        inactive = selected_set is not None and any(
            role.get("role") not in selected_set and role.get("optional") and
            endpoints.intersection(set(role.get("resolve_to", []))) for role in roles
        )
        edge["active"] = not inactive
        if inactive:
            inactive_edges.append(edge)
    lock_body = {
        "lock_schema": SCHEMA_VERSION, "tool_version": tool_version,
        "recipe": {"name": recipe.get("name"), "digest": recipe_digest},
        "catalog": {"digest": catalog_digest}, "schema": {"digest": schema_digest},
        "contracts": [{"phase_id": phase, "digest": pins[phase],
                       "semantic_version": contracts[phase].get("unit", {}).get("semantic_version")}
                      for phase in sorted(pins)],
        "roles": roles, "selected_roles": sorted(selected_set) if selected_set is not None else None,
        "edges": [edge for edge in edges if edge.get("active")], "inactive_edges": inactive_edges,
    }
    lock = dict(lock_body); lock["lock_digest"] = sha256_json(lock_body)
    return Result(not issues, lock, tuple(sorted(issues, key=lambda i: (i.path, i.code))))


def create_lock(recipe_path: Path, catalog_path: Path, contracts_dir: Path, schema_path: Path,
                tool_version: str = "composition-lock/1") -> Result:
    recipe, schema = load_json(recipe_path), load_json(schema_path)
    try:
        catalog = Result(True, tomllib.loads(catalog_path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        catalog = Result(False, issues=(Issue("invalid_catalog", str(catalog_path), str(exc)),))
    loaded = _load_contracts(contracts_dir)
    issues = list(recipe.issues + catalog.issues + schema.issues + loaded.issues)
    if issues:
        return Result(False, issues=tuple(issues))
    for phase, document in loaded.value["contracts"].items():
        for section in ("inputs", "outputs"):
            ports = document.get(section, ())
            if not isinstance(ports, Sequence) or isinstance(ports, (str, bytes)):
                continue
            for index, port in enumerate(ports):
                if not isinstance(port, Mapping) or not port.get("schema_path"):
                    continue
                path = (contracts_dir / port["schema_path"]).resolve()
                digest = file_digest(path)
                issues.extend(digest.issues)
                if digest.ok and digest.value != port.get("schema_digest"):
                    issues.append(_issue("schema_mismatch", f"{phase}.{section}[{index}]", "schema_digest does not match schema_path bytes"))
    if issues:
        return Result(False, issues=tuple(issues))
    digests = [file_digest(path) for path in (recipe_path, catalog_path, schema_path)]
    issues.extend(issue for item in digests for issue in item.issues)
    if issues:
        return Result(False, issues=tuple(issues))
    return build_lock(recipe.value, catalog.value, loaded.value["contracts"], loaded.value["digests"],
                      digests[0].value, digests[1].value, digests[2].value, tool_version)


def check_lock(lock: Mapping[str, Any], current: Mapping[str, Any]) -> Result:
    issues: list[Issue] = []
    if not isinstance(lock, Mapping) or not isinstance(current, Mapping):
        return Result(False, issues=(_issue("malformed_lock", "lock", "lock and current must be objects"),))
    required = {"lock_schema", "lock_digest", "tool_version", "recipe", "catalog", "schema", "contracts", "roles", "edges", "selected_roles", "inactive_edges"}
    for key in sorted(required - set(lock)):
        issues.append(_issue("malformed_lock", key, "required lock field is missing"))
    if lock.get("lock_schema") != SCHEMA_VERSION:
        issues.append(_issue("unsupported_lock_schema", "lock_schema", "unsupported lock schema"))
    body = dict(lock); actual = body.pop("lock_digest", None)
    if actual != sha256_json(body):
        issues.append(_issue("stale_lock", "lock_digest", "lock digest does not match its content"))
    issues.extend(_identity_differences(lock, current))
    if isinstance(current, Mapping):
        current_body = dict(current); current_digest = current_body.pop("lock_digest", None)
        if current_digest != sha256_json(current_body):
            issues.append(_issue("stale_current", "current.lock_digest", "current composition digest does not match its content"))
        if lock.get("tool_version") != current.get("tool_version"):
            issues.append(_issue("tool_version_mismatch", "tool_version", "lock was created by a different tool version"))
    return Result(not issues, current, tuple(sorted(issues, key=lambda i: (i.path, i.code))))


def _identity_differences(old: Mapping[str, Any], new: Mapping[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    for key in sorted(set(old) | set(new)):
        if key == "lock_digest":
            continue
        if key not in old or key not in new or canonical_json(old.get(key)) != canonical_json(new.get(key)):
            issues.append(_issue("identity_mismatch", key, "pinned composition identity changed"))
    return issues


def diff_lock(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    for dimension in sorted(set(previous) | set(current) | BREAKING_DIMENSIONS):
        if dimension == "lock_digest":
            continue
        before, after = previous.get(dimension), current.get(dimension)
        if (dimension not in previous and dimension not in current) or (dimension in previous and dimension in current and canonical_json(before) == canonical_json(after)):
            continue
        kind = "breaking" if dimension in {"recipe", "catalog", "schema", "contracts", "roles", "edges"} else "changed"
        changes.append({"path": dimension, "kind": kind, "before": before, "after": after})
    return {"schema": 1, "status": "unchanged" if not changes else "review_required",
            "changes": changes}


# Descriptive aliases keep the functional API discoverable without adding a
# second implementation surface.
create_composition_lock = create_lock
validate_lock = check_lock


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("create"); make.add_argument("--recipe", type=Path, required=True); make.add_argument("--catalog", type=Path, required=True); make.add_argument("--contracts", type=Path, required=True); make.add_argument("--schema", type=Path, required=True); make.add_argument("--output", type=Path); make.add_argument("--tool-version", default="composition-lock/1")
    chk = sub.add_parser("check"); chk.add_argument("--lock", type=Path, required=True); chk.add_argument("--current", type=Path, required=True)
    dif = sub.add_parser("diff"); dif.add_argument("--lock", type=Path, required=True); dif.add_argument("--current", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "create":
        result = create_lock(args.recipe, args.catalog, args.contracts, args.schema, args.tool_version)
        if result.ok and args.output:
            args.output.write_bytes(canonical_json(result.value) + b"\n")
        print(json.dumps(result.as_dict(), sort_keys=True, ensure_ascii=False))
        return 0 if result.ok else 1
    left, right = load_json(args.lock), load_json(args.current)
    if not left.ok or not right.ok:
        result = Result(False, issues=left.issues + right.issues)
    elif args.command == "check":
        result = check_lock(left.value, right.value)
    else:
        result = Result(True, diff_lock(left.value, right.value))
    print(json.dumps(result.as_dict(), sort_keys=True, ensure_ascii=False))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
