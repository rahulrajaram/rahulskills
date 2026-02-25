#!/usr/bin/env python3
"""Sync vision -> plan -> tranches across projects.

Examples:
  python3 vision-plan-tranche-sync.py --project-root . [--apply]
  python3 vision-plan-tranche-sync.py --path . --only-plan --apply
  python3 vision-plan-tranche-sync.py --project-root . --only-tranches --apply
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PLAN_HEADER_RE = re.compile(
    r"^\s*(\d+)\.\s*(I\d+)\s+`([^`]+)`:\s*(complete|incomplete|blocked)\.\s*tranche_group=([^\s#]+)"
)

VISION_CANDIDATES = ["VISION.md", "Vision.md", "vision.md"]

VISION_SECTION_RE = re.compile(r"^\s*#{1,6}\s+(.*)$")
SECTION_PRIORITY_RE = re.compile(
    r"(vision|roadmap|plan|plan\s+of\s+record|backlog|next|upcoming|milestone|next\s+work|todo)",
    re.IGNORECASE,
)
BULLET_RE = re.compile(r"^\s*[-*]\s*(?:\[[ xX]?\]\s*)?(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+[\.|)]\s+(.*)$")

TRANCHE_KEY_RE = re.compile(r"^\s*key\s*=\s*\"(I\d+)\"\s*$")
TRANCHE_GROUP_RE = re.compile(r"^\s*group\s*=\s*\"([^\"]+)\"\s*$")
TRANCHE_STATUS_RE = re.compile(r"^\s*status\s*=\s*\"([^\"]+)\"\s*$")
TRANCHE_SUMMARY_RE = re.compile(r"^\s*summary\s*=\s*\"(.*)\"\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--path", default=".")
    p.add_argument("--project-root", default=None)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--only-plan", action="store_true")
    p.add_argument("--only-tranches", action="store_true")
    p.add_argument("--force-principal-architect", action="store_true")

    p.add_argument("--vision-file", default=None)
    p.add_argument("--plan-file", default="IMPLEMENTATION_PLAN.md")
    p.add_argument("--tranches-file", default=".yarli/tranches.toml")
    return p.parse_args()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9 ]", " ", value)).strip().lower()


def resolve_path(project_root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else project_root / candidate


def find_file(base: Path, names: List[str]) -> Optional[Path]:
    for name in names:
        candidate = base / name
        if candidate.is_file():
            return candidate
    return None


def parse_implementation_plan(path: Path) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        match = PLAN_HEADER_RE.match(line)
        if not match:
            i += 1
            continue

        entry: Dict[str, str] = {
            "ordinal": match.group(1),
            "key": match.group(2),
            "title": match.group(3).strip(),
            "status": match.group(4),
            "group": match.group(5),
        }

        j = i + 1
        while j < len(lines) and not PLAN_HEADER_RE.match(lines[j]):
            j += 1

        entries.append(entry)
        i = j

    return entries


def split_plan_text_for_insertion(lines: List[str]) -> Tuple[int, int]:
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Next Work Tranches":
            start = i
            break
    if start is None:
        raise ValueError("Could not find '## Next Work Tranches' section")

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") and j > start + 1:
            end = j
            break
    return start + 1, end


def parse_vision_items(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_scope = False
    items: List[str] = []

    for line in lines:
        header = VISION_SECTION_RE.match(line)
        if header:
            in_scope = bool(SECTION_PRIORITY_RE.search(header.group(1)))
            continue

        if not in_scope:
            continue

        bullet = BULLET_RE.match(line)
        if bullet:
            text = bullet.group(1).strip()
            if text:
                items.append(text)
            continue

        numbered = NUMBERED_RE.match(line)
        if numbered and in_scope:
            text = numbered.group(1).strip()
            if text:
                items.append(text)

    # Keep unique while preserving order.
    deduped: List[str] = []
    seen = set()
    for text in items:
        key = normalize_text(text)
        if key and key not in seen:
            deduped.append(text)
            seen.add(key)

    return deduped


def max_key(entries: List[Dict[str, str]]) -> int:
    values = [int(e["key"][1:]) for e in entries if e["key"].startswith("I")]
    return max(values) if values else 0


def max_ordinal(entries: List[Dict[str, str]]) -> int:
    ordinals = [int(e["ordinal"]) for e in entries if e.get("ordinal", "0").isdigit()]
    return max(ordinals) if ordinals else 0


def guess_group(text: str) -> str:
    t = text.lower()
    if re.search(r"\b(read|write|edit|patch|file|filesystem|glob|index)\b", t):
        return "tool-io"
    if re.search(r"\b(shell|command|bash|run|process|exec)\b", t):
        return "tool-shell"
    if re.search(r"\b(router|model|provider|anthropic|openai|kimi)\b", t):
        return "multi-model"
    if re.search(r"\b(sandbox|security|permission|policy|safe|deny|allow)\b", t):
        return "permission-mode"
    if re.search(r"\b(lsp|symbol|search|repo|ast|reflector)\b", t):
        return "tool-search-ui"
    return "cross-cutting"


def find_principal_architect(paths: List[Path]) -> List[Path]:
    candidates: List[Path] = []
    for base in paths:
        if not base.exists():
            continue
        for item in base.glob("**/*.md"):
            if item.is_file() and (
                re.search(r"principal[-_ ]?architect", item.name, re.IGNORECASE)
                or ("architect" in item.stem.lower() and "principal" in item.stem.lower())
            ):
                candidates.append(item)

    uniq = []
    seen = set()
    for item in candidates:
        p = str(item)
        if p not in seen:
            uniq.append(item)
            seen.add(p)
    return uniq


def sync_plan(
    plan_path: Path,
    vision_items: List[str],
    existing_plan_entries: List[Dict[str, str]],
    source_name: str,
    apply_changes: bool,
) -> Tuple[int, List[str]]:
    existing_titles = {normalize_text(e["title"]) for e in existing_plan_entries}
    next_ordinal = max_ordinal(existing_plan_entries) + 1
    next_key = max_key(existing_plan_entries) + 1

    proposals: List[Dict[str, str]] = []
    for item in vision_items:
        if normalize_text(item) in existing_titles:
            continue

        proposals.append(
            {
                "ordinal": str(next_ordinal),
                "key": f"I{next_key:03d}",
                "title": item,
                "status": "incomplete",
                "group": guess_group(item),
                "source": source_name,
            }
        )
        next_ordinal += 1
        next_key += 1

    if not proposals:
        return 0, []

    lines = plan_path.read_text(encoding="utf-8").splitlines()
    _, end = split_plan_text_for_insertion(lines)

    insert: List[str] = []
    for proposal in proposals:
        insert.extend(
            [
                f"{proposal['ordinal']}. {proposal['key']} {proposal['title']}: {proposal['status']}. tranche_group={proposal['group']}",
                "    Scope:",
                f"1. From {proposal['source']}: {proposal['title']}",
                "    Exit criteria:",
                "1. Implement this tranche and add verification evidence when complete.",
                "",
            ]
        )

    if lines and lines[-1].strip() != "":
        lines.append("")
    lines[end:end] = insert

    if apply_changes:
        plan_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return len(proposals), [p["title"] for p in proposals]


def parse_toml_tranches(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []

    entries: List[Dict[str, str]] = []
    current: Dict[str, str] = {}

    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip().startswith("[[tranches]]"):
            if current:
                entries.append(current)
            current = {}
            continue

        key_match = TRANCHE_KEY_RE.match(raw)
        if key_match:
            current["key"] = key_match.group(1)
            continue

        group_match = TRANCHE_GROUP_RE.match(raw)
        if group_match:
            current["group"] = group_match.group(1)
            continue

        status_match = TRANCHE_STATUS_RE.match(raw)
        if status_match:
            current["status"] = status_match.group(1)
            continue

        summary_match = TRANCHE_SUMMARY_RE.match(raw)
        if summary_match:
            current["summary"] = summary_match.group(1)
            continue

    if current:
        entries.append(current)

    return entries


def sync_tranches(
    plan_entries: List[Dict[str, str]],
    tranches_path: Path,
    apply_changes: bool,
) -> Tuple[int, List[str]]:
    existing_entries = parse_toml_tranches(tranches_path)
    existing_keys = {e["key"] for e in existing_entries if "key" in e}

    open_plan_entries = [e for e in plan_entries if e["status"] in {"incomplete", "blocked"}]
    to_add = [e for e in open_plan_entries if e["key"] not in existing_keys]

    if not to_add:
        return 0, []

    blocks: List[str] = []
    for e in to_add:
        blocks.extend(
            [
                "",
                "[[tranches]]",
                f'key = "{e["key"]}"',
                f'summary = {json.dumps(e["title"])}',
                f'status = "{e["status"]}"',
                f'group = "{e["group"]}"',
            ]
        )

    if apply_changes:
        if tranches_path.exists():
            base = tranches_path.read_text(encoding="utf-8").rstrip()
        else:
            base = "version = 1\n"
        base = (base + "\n") if base else ""
        tranches_path.write_text(base + "\n".join(blocks).lstrip("\n") + "\n", encoding="utf-8")

    return len(to_add), [e["key"] for e in to_add]


def principal_architect_paths(project_root: Path) -> List[Path]:
    candidates = [
        project_root / ".claude" / "agents",
        project_root / ".claude",
        Path.home() / ".claude" / "agents",
        Path.home() / ".agents" / "agents",
        project_root / "agents",
    ]
    return find_principal_architect(candidates)


def run() -> int:
    args = parse_args()
    project_root = Path(args.project_root or args.path).expanduser().resolve()

    if args.only_plan and args.only_tranches:
        raise SystemExit("Cannot combine --only-plan with --only-tranches")

    if not project_root.exists():
        raise SystemExit(f"Project path does not exist: {project_root}")

    plan_path = resolve_path(project_root, args.plan_file)
    if not plan_path.is_file():
        raise SystemExit(f"Missing plan file: {plan_path}")

    tranches_path = resolve_path(project_root, args.tranches_file)

    if args.vision_file:
        vision_path = resolve_path(project_root, args.vision_file)
        if not vision_path.is_file():
            vision_path = None
    else:
        vision_path = find_file(project_root, VISION_CANDIDATES)

    plan_entries = parse_implementation_plan(plan_path)

    if not args.only_tranches:
        if vision_path:
            vision_items = parse_vision_items(vision_path)
            plan_added, plan_titles = sync_plan(
                plan_path,
                vision_items,
                plan_entries,
                source_name=vision_path.name,
                apply_changes=args.apply,
            )
            print(f"vision_file={vision_path}")
            print(f"plan_sync_count={plan_added}")
            if plan_added:
                print("plan_sync_added=\n" + "\n".join(f"- {t}" for t in plan_titles))
                if args.apply:
                    plan_entries = parse_implementation_plan(plan_path)
            else:
                print("plan_sync_added=none")
        else:
            candidates = principal_architect_paths(project_root)
            print("vision_file=none")
            if candidates:
                print("principal_architect_candidates=\n" + "\n".join(f"- {p}" for p in candidates))
                if not args.force_principal_architect:
                    print("principal_architect_action=invoke_first_then_continue")
                else:
                    print("principal_architect_action=required_and_blocked")
                    return 2
            elif args.force_principal_architect:
                print("principal_architect_action=required_and_missing")
                return 2
            else:
                print("principal_architect_action=missing")

    if not args.only_plan:
        tranche_count, added_keys = sync_tranches(plan_entries, tranches_path, args.apply)
        print(f"tranche_sync_count={tranche_count}")
        if tranche_count:
            print("tranche_sync_added=\n" + "\n".join(f"- {k}" for k in added_keys))
        else:
            print("tranche_sync_added=none")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
