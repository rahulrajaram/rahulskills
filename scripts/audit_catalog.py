#!/usr/bin/env python3
"""Audit resolved skill roots for collisions, bloat, and portability hazards."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
PERSONAL_PATH = re.compile(r"/home/(?!username/)[^/\s]+|~/Documents")


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    path: str
    lines: int
    sha256: str
    description: str


def parse_manifest(path: Path) -> SkillDefinition:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    metadata: dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t")):
                key, value = line.split(":", 1)
                metadata[key] = value.strip().strip('"')
    return SkillDefinition(
        name=metadata.get("name", path.parent.name),
        path=str(path),
        lines=text.count("\n") + 1,
        sha256=hashlib.sha256(text.encode()).hexdigest(),
        description=metadata.get("description", ""),
    )


def manifests(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.glob("*/SKILL.md")
        if path.parent.name != ".system"
    )


def audit(roots: list[Path], line_budget: int) -> dict[str, object]:
    definitions = [parse_manifest(path) for root in roots for path in manifests(root)]
    by_name: dict[str, list[SkillDefinition]] = {}
    for definition in definitions:
        by_name.setdefault(definition.name, []).append(definition)

    collisions = {
        name: [asdict(item) for item in items]
        for name, items in sorted(by_name.items())
        if len(items) > 1 and len({item.sha256 for item in items}) > 1
    }
    oversized = [asdict(item) for item in definitions if item.lines > line_budget]
    personal_paths = []
    for definition in definitions:
        text = Path(definition.path).read_text(encoding="utf-8")
        if PERSONAL_PATH.search(text):
            personal_paths.append(definition.path)

    return {
        "summary": {
            "roots": [str(root) for root in roots],
            "definitions": len(definitions),
            "unique_names": len(by_name),
            "divergent_collisions": len(collisions),
            "oversized": len(oversized),
            "personal_paths": len(personal_paths),
        },
        "collisions": collisions,
        "oversized": oversized,
        "personal_paths": personal_paths,
    }


def default_roots() -> list[Path]:
    home = Path(os.environ.get("HOME", Path.home()))
    return [
        home / ".agents/skills",
        home / ".codex/skills",
        home / ".codex/skills/.system",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", type=Path, dest="roots")
    parser.add_argument("--line-budget", type=int, default=400)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = audit(args.roots or default_roots(), args.line_budget)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "skill catalog: "
            f"{summary['definitions']} definitions, {summary['unique_names']} unique, "
            f"{summary['divergent_collisions']} collisions, "
            f"{summary['oversized']} oversized, {summary['personal_paths']} personal paths"
        )
        for name, items in report["collisions"].items():
            print(f"COLLISION {name}: " + ", ".join(item["path"] for item in items))
    return int(args.strict and bool(report["collisions"]))


if __name__ == "__main__":
    raise SystemExit(main())
