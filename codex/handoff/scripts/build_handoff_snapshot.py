#!/usr/bin/env python3
"""Build a concise Markdown snapshot for shell handoff."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def _find_candidates(root: Path, name: str) -> list[str]:
    matches: list[str] = []
    for base, dirs, files in os.walk(root):
        if ".git" in dirs:
            dirs.remove(".git")
        if name in files:
            rel = Path(base, name).relative_to(root)
            matches.append(str(rel))
    return sorted(matches)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate handoff snapshot markdown")
    parser.add_argument("--repo", default=".", help="Path inside target git repo")
    parser.add_argument("--max-commits", type=int, default=10, help="Number of recent commits")
    args = parser.parse_args()

    repo_hint = Path(args.repo).resolve()
    repo_root = Path(_run(["git", "rev-parse", "--show-toplevel"], repo_hint))
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    head = _run(["git", "rev-parse", "HEAD"], repo_root)
    status = _run(["git", "status", "--short"], repo_root)
    commits = _run(["git", "log", f"-n{args.max_commits}", "--oneline"], repo_root)

    root_plan = repo_root / "IMPLEMENTATION_PLAN.md"
    root_prompt = repo_root / "PROMPT.md"

    plan_candidates = _find_candidates(repo_root, "IMPLEMENTATION_PLAN.md")
    prompt_candidates = _find_candidates(repo_root, "PROMPT.md")

    print("# Handoff Snapshot")
    print()
    print(f"- Repo root: `{repo_root}`")
    print(f"- Branch: `{branch}`")
    print(f"- HEAD: `{head}`")
    print()

    print("## Working Tree")
    if status:
        print("```text")
        print(status)
        print("```")
    else:
        print("Working tree is clean.")
    print()

    print("## Recent Commits")
    print("```text")
    print(commits)
    print("```")
    print()

    print("## Canonical Docs")
    print(f"- Root IMPLEMENTATION_PLAN.md: {'present' if root_plan.exists() else 'missing'}")
    print(f"- Root PROMPT.md: {'present' if root_prompt.exists() else 'missing'}")
    print(f"- IMPLEMENTATION_PLAN.md candidates: {plan_candidates if plan_candidates else 'none'}")
    print(f"- PROMPT.md candidates: {prompt_candidates if prompt_candidates else 'none'}")
    print()

    print("## Notes")
    print("- Use this snapshot to build the next-shell prompt and doc updates.")
    print("- Verify completed claims before marking them done in plan docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
