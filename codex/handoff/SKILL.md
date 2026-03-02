---
name: handoff
description: "Commit current workspace state, reconcile handoff docs, and generate a next-shell continuation prompt. Use when the user asks for /handoff, asks to wrap up work, asks to continue from a new shell, or needs an accurate session handoff. Execute three outcomes in order: (1) commit all current changes, (2) update canonical IMPLEMENTATION_PLAN.md and PROMPT.md if present so status claims are accurate, and (3) produce a detailed copy-paste prompt for the next shell."
---

# Handoff

Use this workflow whenever a user wants a clean, accurate shell handoff.

## Workflow

### Step 1: Capture repo state

Run these commands to collect context:
```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git status --short
git log --oneline -n 10
```

If the repo contains `scripts/build_handoff_snapshot.py`, run it:
```bash
python scripts/build_handoff_snapshot.py --repo .
```
Otherwise, the git commands above are sufficient.

### Step 2: Commit all current changes

Run `git add -A` then `git commit -m "handoff: <summary>"`.
- If commit fails because there is nothing to commit, report that explicitly.
- If commit fails for another reason, report the exact blocker and stop.

### Step 3: Update canonical plan docs when they exist

Look for `IMPLEMENTATION_PLAN.md` and `PROMPT.md` at repo root first.
If not found at root, search the repo and pick the canonical file that the project already treats as primary.
Update these files to match reality:
- Mark completed work only when it is actually done.
- Move unfinished work to open items.
- Remove stale claims that imply work is done when it is not.
- Keep remaining work prioritized and actionable.
Do not invent completed work.

If neither file exists, skip this step and note their absence.

### Step 4: Gather session context for the prompt

Before writing the prompt, review the full conversation to extract:

1. **Completed work** — concrete changes made (files, features, fixes)
2. **Remaining work** — tasks discussed but not started, or partially done
3. **Design decisions and validated conclusions** — architectural choices, trade-offs considered, options rejected and why. Include conclusions from multi-agent discussions, research findings, and any "we decided X because Y" moments.
4. **Discussion context** — key topics explored during the session that inform future work, even if no code was written. This includes feasibility assessments, integration patterns, and cross-project relationships.
5. **Known risks and blockers** — failing tests, missing dependencies, environment-specific issues
6. **Commands to run first** — what the next shell should do to orient itself

This is critical: a handoff that only lists file changes without capturing the *reasoning and discussion* forces the next shell to re-discover context that was already established.

### Step 5: Produce next-shell prompt

Fill in the template from `references/next-shell-prompt-template.md` with exact facts from this session. If that file is missing, use this inline template:

```text
Continue work in <ABSOLUTE_REPO_PATH>.

Session handoff facts:
- Branch: <BRANCH>
- HEAD commit: <COMMIT_SHA> — <COMMIT_MESSAGE>
- Working tree: <CLEAN_OR_DIRTY_SUMMARY>

What was completed this session:
1. <DONE_ITEM_1>
2. <DONE_ITEM_2>
3. <DONE_ITEM_3>

Key decisions and context from this session:
- <DECISION_OR_CONCLUSION_1>
- <DECISION_OR_CONCLUSION_2>
- <DISCUSSION_TOPIC_WITH_OUTCOME>

What still needs to be done (priority order):
1. <NEXT_TASK_1>
2. <NEXT_TASK_2>
3. <NEXT_TASK_3>

Files touched this session:
- <FILE_1> (<ACTION: new/edited/deleted>)
- <FILE_2> (<ACTION>)

Canonical docs status:
- IMPLEMENTATION_PLAN.md: <UPDATED / NOT_FOUND>
- PROMPT.md: <UPDATED / NOT_FOUND>

Known risks and blockers:
- <RISK_OR_BLOCKER_1>
- <RISK_OR_BLOCKER_2>

Start by running:
1. <FIRST_COMMAND>
2. <SECOND_COMMAND>
```

Rules for filling the template:
- Every placeholder MUST be replaced with a concrete value or removed.
- "Key decisions and context" is NOT optional — if the session involved any discussion, design exploration, or validated conclusions, they go here.
- "What still needs to be done" should include tasks surfaced in discussion, not just tasks from a formal plan.
- Be specific enough that a new shell can continue without re-discovery.
- Prefer factual, verifiable statements over narrative.

### Step 6: Return handoff package

Return to the user:
- Commit result (hash + message, or no-op if clean).
- Updated plan/prompt files (or note they don't exist).
- Final copy-paste prompt for the new shell.

## Guardrails
- Preserve user intent and existing project conventions.
- Prefer factual, verifiable statements over narrative.
- Keep prompt content specific enough that a new shell can continue without re-discovery.
- If there are multiple repos/worktrees, confirm which repo to hand off before committing.
- Never omit discussion context just because no code was written — validated conclusions and design decisions are first-class handoff content.
