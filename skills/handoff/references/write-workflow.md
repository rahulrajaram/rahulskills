# Write workflow

Use this reference only when `handoff` was invoked without an argument. The
outcome is a coherent repository commit followed by an untracked continuation
artifact that records the exact post-commit state.

## 1. Capture repository state

Run:

```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git status --short
git log --oneline -n 10
```

If the repository contains `scripts/build_handoff_snapshot.py`, also run:

```bash
python scripts/build_handoff_snapshot.py --repo .
```

If multiple repositories or worktrees could own the handoff, resolve that real
ambiguity before committing.

## 2. Reconcile canonical plan documents

Look for `IMPLEMENTATION_PLAN.md` and `PROMPT.md` at the repository root first.
If absent there, search for the canonical files the project treats as primary.

- Mark work complete only when it is actually done.
- Move incomplete work into prioritized, actionable open items.
- Remove stale claims that imply unfinished work is complete.
- Do not invent completed work.

If neither document exists, skip this step and record their absence.

## 3. Commit the coherent workspace

Invoke the shared `commit` skill after reconciling documentation. Its policy
discovery, file triage, secret checks, explicit-path staging, and verification
rules are authoritative. Never use `git add .` or `git add -A`.

If canonical handoff documents are classified as REVIEW or SKIP, follow the
commit skill's normal resolution instead of force-adding or silently omitting
them. Record a no-op if there is nothing to commit. Afterward, verify
`git status --short`; reconcile or report every unexplained change before
writing the continuation artifact.

## 4. Gather continuation context

Review the full conversation and repository evidence for:

1. Concrete work completed, including files and behavior.
2. Work not started or only partly complete.
3. Design decisions, tradeoffs, rejected options, and validated conclusions.
4. Discussion context that prevents rediscovery in the next shell.
5. Known risks, blockers, missing dependencies, and failing checks.
6. The first commands and highest-priority action for the next shell.

Discussion and reasoning are first-class handoff content even when no code was
written.

## 5. Write `NEXT_SHELL_PROMPT.md`

Read [next-shell-prompt-template.md](next-shell-prompt-template.md) and fill it
with exact facts. Write the result to `<REPO_ROOT>/NEXT_SHELL_PROMPT.md` only
after the coherent workspace commit so it records the actual final HEAD.

Replace an existing untracked artifact atomically and do not print it to
stdout. If the file is tracked, treat it as project-owned state and ask before
replacing it. Keep the resulting artifact untracked and never add it to the
index, `.gitignore`, or `.git/info/exclude` as a side effect of this workflow.

## 6. Verify and report

Verify that the artifact:

- exists at the repository root;
- contains no unresolved angle-bracket placeholders;
- records the actual post-commit HEAD; and
- leaves no unexplained working-tree changes other than the expected untracked
  `NEXT_SHELL_PROMPT.md`.

Return the commit hash and message (or no-op), canonical document status, the
absolute artifact path, `$handoff extract`, and `$handoff print`. Also give Pi's
equivalents: `/skill:handoff extract` and `/skill:handoff print`. Do not include
the handoff document contents in the response.
