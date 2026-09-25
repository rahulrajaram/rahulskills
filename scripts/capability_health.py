#!/usr/bin/env python3
"""Report whether declared skill dependencies are available in this session."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import tomllib
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO / "capabilities/skills.toml"


def load_manifest(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def evaluate(
    manifest: dict[str, object], loaded_mcps: set[str], selected_modes: dict[str, str] | None = None
) -> dict[str, object]:
    results: dict[str, object] = {}
    skills = manifest.get("skills", {})
    if not isinstance(skills, dict):
        raise ValueError("manifest 'skills' must be a table")
    for name, raw in sorted(skills.items()):
        config = raw if isinstance(raw, dict) else {}
        selected_mode = (selected_modes or {}).get(name)
        if selected_mode:
            mode = config.get("modes", {}).get(selected_mode)
            if isinstance(mode, dict):
                config = {**config, **mode}
        commands = [str(item) for item in config.get("commands", [])]
        required_commands = [str(item) for item in config.get("required_commands", commands)]
        optional_commands = [str(item) for item in config.get("optional_commands", [])]
        mcps = [str(item) for item in config.get("mcps", [])]
        optional_mcps = [str(item) for item in config.get("optional_mcps", [])]
        platforms = [str(item).lower() for item in config.get("platforms", [])]
        missing_commands = [command for command in required_commands if shutil.which(command) is None]
        missing_optional_commands = [command for command in optional_commands if shutil.which(command) is None]
        missing_mcps = [mcp for mcp in mcps if mcp not in loaded_mcps]
        missing_optional_mcps = [mcp for mcp in optional_mcps if mcp not in loaded_mcps]
        current_platform = platform.system().lower()
        missing_platforms = platforms if platforms and current_platform not in platforms else []
        results[name] = {
            "available": not missing_commands and not missing_mcps and not missing_platforms,
            "missing_commands": missing_commands,
            "required_commands": required_commands,
            "optional_commands": optional_commands,
            "missing_optional_commands": missing_optional_commands,
            "missing_mcps": missing_mcps,
            "required_mcps": mcps,
            "optional_mcps": optional_mcps,
            "missing_optional_mcps": missing_optional_mcps,
            "missing_platforms": missing_platforms,
            "platforms": platforms,
            "degraded": bool(missing_optional_commands or missing_optional_mcps),
            "effect": config.get("effect", "unknown"),
            "effects": config.get("effects", [config.get("effect", "unknown")]),
            "approval_boundaries": config.get("approval_boundaries", []),
            "layer": config.get("layer", "workflow"),
            "overlaps": config.get("overlaps", []),
            "modes": config.get("modes", {}),
            "selected_mode": selected_mode,
            "host_only": bool(config.get("host_only", False)),
            "portable": not bool(config.get("host_only", False)),
            "mcp_evidence": {mcp: mcp in loaded_mcps for mcp in (*mcps, *optional_mcps)},
        }
    mcp_results = {
        name: {
            "loaded": name in loaded_mcps,
            "role": config.get("role", "unknown"),
            "effects": config.get("effects", []),
            "health_tool": config.get("health_tool"),
            "conflicts": config.get("conflicts", []),
        }
        for name, config in sorted(manifest.get("mcps", {}).items())
    }
    return {
        "schema_version": manifest.get("schema_version", 1),
        "skills": results,
        "mcps": mcp_results,
    }


def admission(
    report: dict[str, object], *, target: str = "chasm", runtime: str = "host",
    observation: dict[str, object] | None = None,
) -> dict[str, object]:
    """Render a read-only guest admission report from declared metadata.

    Without an observation payload this reports static metadata only. Supplied
    command/MCP/platform observations are scoped to that payload and never
    inferred from the caller's host.
    """
    skills = report.get("skills", {})
    observation = observation or {}
    observed = bool(observation)
    observed_commands = set(str(item) for item in observation.get("commands", []))
    observed_mcps = set(str(item) for item in observation.get("mcps", []))
    observed_platform = str(observation.get("platform", ""))
    mcp_health = observation.get("mcp_health", {})
    entries = []
    for name, item in sorted(skills.items()):
        observed_missing_commands = [command for command in item["required_commands"] if command not in observed_commands] if observed else []
        platforms = item.get("platforms", [])
        required_mcps = item.get("required_mcps", [])
        observed_missing_mcps = [mcp for mcp in required_mcps if mcp not in observed_mcps] if observed else []
        platform_missing = bool(platforms and observed_platform.lower() not in platforms) if observed else False
        mcp_verified = bool(required_mcps) and isinstance(mcp_health, dict) and all(
            mcp_health.get(mcp) is True for mcp in required_mcps
        )
        required_ready = observed and not observed_missing_commands and not observed_missing_mcps and not platform_missing
        prerequisites_ready = required_ready and (not required_mcps or mcp_verified) and not item["host_only"]
        entries.append({
            "name": name,
            "target": target,
            "runtime": runtime,
            "command_observation": "supplied observation" if observed else "none",
            "static_ready": not item["host_only"],
            "declared_prerequisites_ready": prerequisites_ready if observed else None,
            "admissible": prerequisites_ready if observed else (False if item["host_only"] else None),
            "host_only": item["host_only"],
            "platforms": platforms,
            "required_commands": item["required_commands"],
            "caller_missing_required_commands": item["missing_commands"],
            "required_mcps": required_mcps,
            "caller_missing_required_mcps": item["missing_mcps"],
            "optional_commands": item["optional_commands"],
            "caller_missing_optional_commands": item["missing_optional_commands"],
            "optional_mcps": item["optional_mcps"],
            "caller_missing_optional_mcps": item["missing_optional_mcps"],
            "caller_degraded": item["degraded"] or bool(item["missing_commands"]),
            "caller_loaded_mcps": [name for name, loaded in item["mcp_evidence"].items() if loaded],
            "caller_missing_mcps": [name for name, loaded in item["mcp_evidence"].items() if not loaded],
            "mcp_functionality_verified": mcp_verified,
            "observed_missing_required_commands": observed_missing_commands,
            "observed_missing_required_mcps": observed_missing_mcps,
            "observed_platform": observed_platform or None,
            "observed_degraded": bool(observed_missing_commands or observed_missing_mcps or platform_missing),
        })
    return {
        "schema_version": 1,
        "target": target,
        "runtime": runtime,
        "observed": observed,
        "observation_scope": observation.get("scope") if observed else None,
        "evidence_limits": "Command presence is prerequisite evidence, not proof that a skill's workflow succeeds. MCP health is supplied evidence, not a probe performed by this report.",
        "skills": entries,
    }


def undeclared_source_skills(manifest: dict[str, object], skills_root: Path) -> list[str]:
    declared = set(manifest.get("skills", {}))
    source = {path.parent.name for path in skills_root.glob("*/SKILL.md")}
    return sorted(source - declared)


def undeclared_mcp_dependencies(manifest: dict[str, object]) -> list[str]:
    declared = set(manifest.get("mcps", {}))
    referenced = {
        str(mcp)
        for config in manifest.get("skills", {}).values()
        if isinstance(config, dict)
        for key in ("mcps", "optional_mcps")
        for mcp in config.get(key, [])
    }
    return sorted(referenced - declared)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--mcp", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--portable", action="store_true", help="Include a Chasm/guest admission report")
    parser.add_argument("--target", default="chasm")
    parser.add_argument("--runtime", choices=("host", "codex", "pi", "claude", "opencode"), default="host")
    parser.add_argument("--observation-file", type=Path, help="JSON guest observation: commands, mcps, platform, scope")
    parser.add_argument("--mode", action="append", default=[], metavar="SKILL=MODE")
    args = parser.parse_args()
    env_mcps = os.environ.get("LOADED_MCP_NAMESPACES", "").split(",")
    modes = dict(item.split("=", 1) for item in args.mode if "=" in item)
    report = evaluate(load_manifest(args.manifest), set(args.mcp) | set(filter(None, env_mcps)), modes)
    report["undeclared_source_skills"] = undeclared_source_skills(
        load_manifest(args.manifest), REPO / "skills"
    )
    report["undeclared_mcp_dependencies"] = undeclared_mcp_dependencies(
        load_manifest(args.manifest)
    )
    if args.portable:
        if args.observation_file:
            try:
                observation = json.loads(args.observation_file.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                parser.error(f"invalid observation file: {exc}")
            if not isinstance(observation, dict):
                parser.error("observation file must contain a JSON object")
        else:
            observation = None
        report["admission"] = admission(report, target=args.target, runtime=args.runtime, observation=observation)
    unavailable = [name for name, item in report["skills"].items() if not item["available"]]
    missing_mcps = [name for name, item in report["mcps"].items() if not item["loaded"]]
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"skill capabilities: {len(report['skills'])} declared, {len(unavailable)} unavailable")
        for name in unavailable:
            item = report["skills"][name]
            reasons = (
                item["missing_commands"]
                + [f"mcp:{mcp}" for mcp in item["missing_mcps"]]
                + [f"platform:{name}" for name in item["missing_platforms"]]
            )
            print(f"UNAVAILABLE {name}: {', '.join(reasons)}")
        for name in report["undeclared_source_skills"]:
            print(f"UNDECLARED {name}")
        for name in report["undeclared_mcp_dependencies"]:
            print(f"UNDECLARED MCP {name}")
        print(f"MCP capabilities: {len(report['mcps'])} declared, {len(missing_mcps)} not loaded")
        for name in missing_mcps:
            print(f"MCP NOT LOADED {name}")
        if args.portable:
            entries = report["admission"]["skills"]
            ready = [item for item in entries if item["admissible"] is True]
            blocked = [item for item in entries if item["admissible"] is False]
            unknown = [item for item in entries if item["admissible"] is None]
            print(
                f"Portable admission ({args.target}/{args.runtime}): "
                f"{len(ready)} ready, {len(blocked)} blocked, {len(unknown)} unknown"
            )
            for item in blocked:
                reasons = item["observed_missing_required_commands"] + item["observed_missing_required_mcps"]
                if item["host_only"]:
                    reasons.append("host-only capability")
                if item["platforms"] and (item["observed_platform"] or "").lower() not in item["platforms"]:
                    reasons.append("platform mismatch or unverified")
                if item["required_mcps"] and not item["mcp_functionality_verified"]:
                    reasons.append("required MCP health unverified")
                print(f"PORTABLE BLOCKED {item['name']} (target): {', '.join(reasons)}")
            for item in unknown:
                print(f"PORTABLE UNKNOWN {item['name']} (target): no supplied guest observation")
            for item in entries:
                if item["caller_degraded"]:
                    print(
                        f"PORTABLE CALLER {item['name']}: "
                        f"missing required commands={item['caller_missing_required_commands']} "
                        f"mcps={item['caller_missing_required_mcps']}"
                    )
    portable_failures = [
        item["name"]
        for item in report.get("admission", {}).get("skills", [])
        if item["admissible"] is not True
    ]
    strict_failures = portable_failures if args.portable else (
        unavailable
        + report["undeclared_source_skills"]
        + report["undeclared_mcp_dependencies"]
    )
    return int(args.strict and bool(strict_failures))


if __name__ == "__main__":
    raise SystemExit(main())
