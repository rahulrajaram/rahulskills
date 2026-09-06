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
            "missing_optional_mcps": missing_optional_mcps,
            "missing_platforms": missing_platforms,
            "degraded": bool(missing_optional_commands or missing_optional_mcps),
            "effect": config.get("effect", "unknown"),
            "effects": config.get("effects", [config.get("effect", "unknown")]),
            "approval_boundaries": config.get("approval_boundaries", []),
            "layer": config.get("layer", "workflow"),
            "overlaps": config.get("overlaps", []),
            "modes": config.get("modes", {}),
            "selected_mode": selected_mode,
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
    strict_failures = (
        unavailable
        + report["undeclared_source_skills"]
        + report["undeclared_mcp_dependencies"]
    )
    return int(args.strict and bool(strict_failures))


if __name__ == "__main__":
    raise SystemExit(main())
