#!/usr/bin/env python3
"""Render Chasm's shared development policy for the supported agent runtimes."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "profiles/chasm-development/instructions/policy.md"
RUNTIME_NOTES = {
    "pi": ROOT / "profiles/chasm-development/instructions/pi-runtime.md",
    "claude": ROOT / "profiles/chasm-development/instructions/claude-runtime.md",
}
RUNTIME_OVERLAYS = {
    "codex": (ROOT / "profiles/chasm-development/instructions/overlays/codex-orchestration.md",),
    "pi": (ROOT / "profiles/chasm-development/instructions/overlays/pi-worker.md",),
    "claude": (ROOT / "profiles/chasm-development/instructions/overlays/claude-orchestrator.md",),
}
OUTPUT = ROOT / "profiles/chasm-development/instructions/rendered"

RUNTIMES = {
    "codex": (
        "AGENTS.md",
        "Install as the Codex global instruction file for the active Codex home. "
        "A workspace-level file is not a substitute for global instructions "
        "when a repository is nested below that workspace.",
    ),
    "pi": (
        "AGENTS.md",
        "Install in Pi's active agent directory, merging with its existing global "
        "instructions and preserving any explicitly configured agent directory.",
    ),
    "claude": (
        "CLAUDE.md",
        "Prepare for Claude's existing global instruction layer; install only "
        "when Claude is present and its active configuration is confirmed.",
    ),
    "opencode": (
        "instructions-candidate.md",
        "Content candidate only. Inspect the installed OpenCode version and its "
        "actual global-instruction configuration before choosing a destination.",
    ),
}


def render(runtime: str, policy: str) -> str:
    """Render the shared policy without installer notes in agent context."""
    note = RUNTIME_NOTES.get(runtime)
    runtime_text = note.read_text(encoding="utf-8").rstrip() if note else ""
    overlays = "\n\n".join(
        path.read_text(encoding="utf-8").strip()
        for path in RUNTIME_OVERLAYS.get(runtime, ())
    )
    body = policy.rstrip()
    if runtime_text:
        body += "\n\n" + runtime_text
    rendered = (
        f"<!-- Generated from profiles/chasm-development/instructions/policy.md; "
        f"edit the source, then rerender. -->\n"
        f"# Chasm development instructions ({runtime})\n\n"
        f"{body}\n"
    )
    if runtime == "pi":
        return f"{overlays}\n\n{rendered}" if overlays else rendered
    return f"{rendered.rstrip()}\n\n{overlays}\n" if overlays else rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=(*RUNTIMES, "all"), default="all")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    policy = POLICY.read_text(encoding="utf-8")
    selected = RUNTIMES if args.runtime == "all" else {args.runtime: RUNTIMES[args.runtime]}
    args.output.mkdir(parents=True, exist_ok=True)
    for runtime, (filename, _) in selected.items():
        path = args.output / f"{runtime}-{filename}"
        path.write_text(render(runtime, policy), encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
