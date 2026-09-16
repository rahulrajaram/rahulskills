#!/usr/bin/env python3
"""Validate negative claims in a handoff draft against the filesystem.

Stale-claim class (f-2030): a handoff asserted that R-001 exit-condition
evidence was still missing while the digest-covered artifacts had existed for
hours. Before publishing, every negative claim ("missing", "not done", ...)
about evidence or a named path should resolve:

- CONFIRMED  — the claim names a path that does not exist (consistent);
- SUSPECT    — the claim says missing, but the named path EXISTS (the stale
               class; publishing this is the failure mode);
- UNRESOLVED — an evidence/artifact claim with no resolvable path; the author
               should attach the evidence path or rewrite the claim as
               "unverified".

Usage:
    python3 validate_handoff_claims.py NEXT_SHELL_PROMPT.md [--repo ROOT]
        [--json] [--strict]

Exit codes: 0 clean or advisory-only; 2 SUSPECT findings, or any UNRESOLVED
when --strict; 1 usage or read error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ABSENCE_MARKERS = (
    "missing",
    "not done",
    "not yet",
    "absent",
    "does not exist",
    "no evidence",
    "not created",
    "not started",
    "not closed",
    "still needs",
    "unfinished",
    "has not",
    "have not",
    "without evidence",
)

EVIDENCE_ANCHORS = (
    "evidence",
    "artifact",
    "proof",
    "receipt",
    "report",
    "closure",
)

BACKTICK_TOKEN = re.compile(r"`([^`\n]+)`")
PATH_TOKEN = re.compile(
    r"(?<![\w@.+-])((?:/|[\w@.+-]+/)[\w@.+-/]*[\w@.+-]|[\w@.+-]+\.(?:md|json|jsonl|txt|log|csv|yml|yaml|py|sh|rs|toml))"
)
ABS_PATH = re.compile(r"/(?:[\w@.+-]+/)+[\w@.+-]+")
BULLET_START = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


@dataclass
class Claim:
    line: int
    status: str
    claim_text: str
    path: str | None
    detail: str


def _blocks(lines: list[str]) -> list[tuple[int, str]]:
    """Group lines into claim-sized blocks.

    A block ends at a blank line or when the next line starts a new bullet
    or numbered item, so one oversized bullet list cannot pull unrelated
    paths into another claim's scope.
    """
    blocks: list[tuple[int, str]] = []
    current: list[str] = []
    start = 0
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            if current:
                blocks.append((start, " ".join(current)))
                current = []
            continue
        if current and (BULLET_START.match(line) or BULLET_START.match(current[0])):
            blocks.append((start, " ".join(current)))
            current = []
        if not current:
            start = number
        current.append(stripped)
    if current:
        blocks.append((start, " ".join(current)))
    return blocks


def _classify_token(token: str) -> tuple[str, str] | None:
    """Classify a token as ('concrete'|'dir_ish', token) or None."""
    token = token.strip().rstrip(".,;:")
    if not token or token.startswith("-") or len(token) < 3:
        return None
    if re.search(r"\.(?:md|json|jsonl|txt|log|csv|yml|yaml|py|sh|rs|toml)$", token):
        return ("concrete", token)
    if token.count("/") >= 2 or (token.startswith("/") and "/" in token[1:]):
        return ("dir_ish", token)
    if "/" in token:
        return ("dir_ish", token)
    return None


def _candidate_paths(block: str) -> tuple[list[str], list[str]]:
    """Return (concrete, dir_ish) path candidates from a claim block.

    Concrete candidates carry a file extension and support a CONFIRMED
    verdict when absent. Dir-ish slash tokens (for example
    "full-suite/Clippy") commonly come from prose; when absent they do not
    prove the claim consistent, so the block stays UNRESOLVED.
    """
    concrete: list[str] = []
    dir_ish: list[str] = []
    seen: set[str] = set()
    raw_tokens = (
        BACKTICK_TOKEN.findall(block) + PATH_TOKEN.findall(block) + ABS_PATH.findall(block)
    )
    for raw in raw_tokens:
        classified = _classify_token(raw)
        if classified is None:
            continue
        kind, token = classified
        if token in seen:
            continue
        seen.add(token)
        (concrete if kind == "concrete" else dir_ish).append(token)
    return concrete, dir_ish


def _resolve(candidate: str, repo: Path, cwd: Path) -> Path | None:
    path = Path(candidate).expanduser()
    if path.is_absolute():
        return path if path.exists() else None
    for root in (repo, cwd):
        probe = root / candidate
        if probe.exists():
            return probe
    return None


def _manifest_note(path: Path) -> str:
    """Report whether a nearby SHA256SUMS manifest mentions this file."""
    for parent in [path.parent, path.parent.parent]:
        manifest = parent / "SHA256SUMS"
        if manifest.is_file():
            try:
                if path.name in manifest.read_text(errors="replace"):
                    return f"covered by {manifest}"
            except OSError:
                continue
    return "no manifest coverage found"


def find_claims(text: str, repo: Path, cwd: Path) -> list[Claim]:
    claims: list[Claim] = []
    for line_number, block in _blocks(text.splitlines()):
        lowered = block.lower()
        marker = next((m for m in ABSENCE_MARKERS if m in lowered), None)
        if marker is None:
            continue
        candidates, dir_ish = _candidate_paths(block)
        anchor = next((a for a in EVIDENCE_ANCHORS if a in lowered), None)
        if not candidates and not dir_ish and anchor is None:
            continue  # not an evidence/artifact claim (e.g. guardrail prose)
        resolved = None
        for candidate in (*candidates, *dir_ish):
            found = _resolve(candidate, repo, cwd)
            if found is not None:
                resolved = found
                break
        if resolved is not None:
            size = resolved.stat().st_size
            claims.append(
                Claim(
                    line_number,
                    "SUSPECT",
                    block[:200],
                    str(resolved),
                    f"claimed missing but exists ({size} bytes; {_manifest_note(resolved)})",
                )
            )
        elif candidates:
            claims.append(
                Claim(
                    line_number,
                    "CONFIRMED",
                    block[:200],
                    candidates[0],
                    "named path does not exist (claim consistent)",
                )
            )
        else:
            claims.append(
                Claim(
                    line_number,
                    "UNRESOLVED",
                    block[:200],
                    None,
                    "evidence/artifact claim with no resolvable path; attach the "
                    "evidence path or rewrite as unverified",
                )
            )
    return claims


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validate_handoff_claims")
    parser.add_argument("handoff", help="Handoff markdown path")
    parser.add_argument("--repo", default=".", help="Repository root for relative paths")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also fail (exit 2) on UNRESOLVED evidence claims",
    )
    args = parser.parse_args(argv)

    handoff = Path(args.handoff)
    try:
        text = handoff.read_text(encoding="utf-8")
    except OSError as error:
        print(f"validate_handoff_claims: cannot read {handoff}: {error}", file=sys.stderr)
        return 1
    repo = Path(args.repo).resolve()
    claims = find_claims(text, repo, Path.cwd())

    if args.json:
        print(json.dumps([asdict(claim) for claim in claims], indent=2))
    else:
        if not claims:
            print("No negative evidence claims found.")
        for claim in claims:
            print(f"{claim.status}: line {claim.line} — {claim.detail}")
            print(f"    {claim.claim_text}")

    suspects = [c for c in claims if c.status == "SUSPECT"]
    unresolved = [c for c in claims if c.status == "UNRESOLVED"]
    if suspects:
        print(
            f"validate_handoff_claims: {len(suspects)} SUSPECT claim(s) — "
            "a reported-missing artifact exists; resolve or rewrite before publishing.",
            file=sys.stderr,
        )
        return 2
    if unresolved and args.strict:
        print(
            f"validate_handoff_claims: {len(unresolved)} UNRESOLVED evidence "
            "claim(s) under --strict; attach paths or mark unverified.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
