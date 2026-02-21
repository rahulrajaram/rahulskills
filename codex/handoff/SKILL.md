---
name: handoff
description: "Commit current workspace state, reconcile handoff docs, and generate a next-shell continuation prompt. Use when the user asks for /handoff, asks to wrap up work, asks to continue from a new shell, or needs an accurate session handoff. Execute three outcomes in order: (1) commit all current changes, (2) update canonical IMPLEMENTATION_PLAN.md and PROMPT.md if present so status claims are accurate, and (3) produce a detailed copy-paste prompt for the next shell."
---

# Handoff

Use this workflow whenever a user wants a clean, accurate shell handoff.

## Workflow
1. Capture repo state.
Run `python scripts/build_handoff_snapshot.py --repo .` to collect branch, HEAD, status, and doc presence.
Run `git status --short` and `git log --oneline -n 10` if more detail is needed.

2. Commit all current changes.
Run `git add -A`.
Run `git commit -m "<handoff message>"`.
If commit fails because there is nothing to commit, report that explicitly.
If commit fails for another reason, report the exact blocker and stop.

3. Update canonical plan docs when they exist.
Look for `IMPLEMENTATION_PLAN.md` and `PROMPT.md` at repo root first.
If not found at root, search the repo and pick the canonical file that the project already treats as primary.
Update these files to match reality:
- Mark completed work only when it is actually done.
- Move unfinished work to open items.
- Remove stale claims that imply work is done when it is not.
- Keep remaining work prioritized and actionable.
Do not invent completed work.

4. Produce next-shell prompt.
Use `references/next-shell-prompt-template.md`.
Fill it with exact facts from this shell:
- What was completed.
- What remains (ordered).
- What commands should be run first.
- Known failures, risks, and pending validations.
- Commit hash, branch, and touched files.

5. Return handoff package.
Return:
- Commit result (hash + message, or no-op).
- Updated plan/prompt files.
- Final copy-paste prompt for the new shell.

## Guardrails
- Preserve user intent and existing project conventions.
- Prefer factual, verifiable statements over narrative.
- Keep prompt content specific enough that a new shell can continue without re-discovery.
- If there are multiple repos/worktrees, confirm which repo to hand off before committing.
