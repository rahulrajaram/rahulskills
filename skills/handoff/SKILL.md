---
name: handoff
description: "Reconcile handoff docs, commit the coherent workspace, and write a next-shell continuation prompt to NEXT_SHELL_PROMPT.md. Use $handoff extract (or Pi's /skill:handoff extract) to load that prompt as active instructions and immediately resume the work; use print only to emit it verbatim."
argument-hint: "[extract|print]"
---

# Handoff

Use this workflow whenever a user wants a clean, accurate shell handoff.

## Mode Routing

- With no argument, run the write workflow below.
- With `extract`, run the activation workflow below. Do not run the handoff
  writing workflow or rewrite `NEXT_SHELL_PROMPT.md`; resume the work carried
  by the existing artifact.
- With `print`, run only the read-only print workflow below.
- Reject unknown arguments with the supported forms: `$handoff`,
  `$handoff extract`, and `$handoff print` (or equivalent slash forms in
  clients that support them).
- In Pi Coding Agent, use `/skill:handoff`, `/skill:handoff extract`, or
  `/skill:handoff print`; arguments appended by Pi select the same modes.

## Extract Workflow

1. Resolve the package root with `git rev-parse --show-toplevel`.
2. Read `<PACKAGE_ROOT>/NEXT_SHELL_PROMPT.md`. If it is missing, report the exact expected
   path and stop without changing repository state.
3. Treat the file contents as user-provided continuation context and requested
   work, subordinate to current system, developer, repository, and safety
   instructions. Treat the live invocation message as newer: merge compatible
   additions and follow it where it conflicts with the carried prompt.
4. Unpack the artifact into working context: repository, completed work,
   decisions, open priorities, blockers, and first commands. Validate facts
   that matter to the next action instead of blindly trusting stale state.
5. Do not merely emit, quote, or summarize the artifact. Do not ask what to do
   next when it contains authorized actionable work. Load any named skills that
   the resumed work requires, then begin the first actionable step in the same
   turn and continue end to end until complete or genuinely blocked.
6. If the first carried or live instruction requires an interview, decision,
   approval, or other user response, start that interaction immediately and
   wait at the natural boundary. Otherwise, return progress or results from the
   resumed work rather than the handoff text itself.

## Print Workflow

1. Resolve the package root with `git rev-parse --show-toplevel`.
2. Read `<PACKAGE_ROOT>/NEXT_SHELL_PROMPT.md`. If it is missing, report the exact
   expected path and stop without changing repository state.
3. Emit the file contents verbatim, without a surrounding Markdown fence or
   added commentary. Do not execute its instructions.

## Autonomy Routing

A handoff request is approval to complete the selected handoff mode rather than
ask whether to proceed. In write mode, that includes committing, updating docs,
and generating the continuation prompt. In extract mode, that includes adopting
the existing prompt as working context and resuming its authorized tasks.
Continue through the ordered steps unless a repository choice, destructive
action, secret, push/deploy, or multi-repo ambiguity requires explicit
confirmation. Do not ask whether to use `/goal`, Yarli, or direct execution
during handoff; the selected handoff mode is the requested workflow.

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

### Step 2: Reconcile canonical plan docs when they exist

Look for `IMPLEMENTATION_PLAN.md` and `PROMPT.md` at repo root first.
If not found at root, search the repo and pick the canonical file that the project already treats as primary.
Update these files to match reality:
- Mark completed work only when it is actually done.
- Move unfinished work to open items.
- Remove stale claims that imply work is done when it is not.
- Keep remaining work prioritized and actionable.
Do not invent completed work.

If neither file exists, skip this step and note their absence.

### Step 3: Commit the coherent workspace state

Invoke the shared `commit` skill after documentation reconciliation. Its file
triage, repository-policy discovery, secret checks, explicit-path staging, and
verification rules are authoritative. Do not duplicate them here and never use
`git add .` or `git add -A`.

If canonical handoff docs are classified as REVIEW or SKIP by repository policy,
pause for the commit skill's normal resolution instead of silently omitting or
force-adding them. If there is nothing to commit, record a no-op. After commit,
verify `git status --short`; unexplained changes are an incomplete handoff and
must be reported or reconciled before producing the continuation prompt.

### Step 4: Gather session context for the prompt

Before writing the prompt, review the full conversation to extract:

1. **Completed work** — concrete changes made (files, features, fixes)
2. **Remaining work** — tasks discussed but not started, or partially done
3. **Design decisions and validated conclusions** — architectural choices, trade-offs considered, options rejected and why. Include conclusions from multi-agent discussions, research findings, and any "we decided X because Y" moments.
4. **Discussion context** — key topics explored during the session that inform future work, even if no code was written. This includes feasibility assessments, integration patterns, and cross-project relationships.
5. **Known risks and blockers** — failing tests, missing dependencies, environment-specific issues
6. **Commands to run first** — what the next shell should do to orient itself

This is critical: a handoff that only lists file changes without capturing the *reasoning and discussion* forces the next shell to re-discover context that was already established.

### Step 5: Write `NEXT_SHELL_PROMPT.md`

Fill in the template from `references/next-shell-prompt-template.md` with exact
facts from this session. Write the result to `<PACKAGE_ROOT>/NEXT_SHELL_PROMPT.md`, where
`PACKAGE_ROOT` is the path returned by `git rev-parse --show-toplevel`. Replace
an existing untracked handoff artifact atomically. Do not print the prompt to
stdout. If the file is tracked, treat it as a project-owned document and ask
before replacing it because the post-commit write would modify tracked state.

`NEXT_SHELL_PROMPT.md` is a transient local session artifact written after the coherent
workspace commit so it can contain the exact final HEAD. Do not stage or commit
it. Its untracked status is expected until the user removes it.

If the template reference is missing, use this inline template:

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

### Step 6: Verify and return

Return to the user:
- Commit result (hash + message, or no-op if clean).
- Updated plan/prompt files (or note they don't exist).
- Absolute path to `NEXT_SHELL_PROMPT.md`.
- The resume command: `$handoff extract`.
- The verbatim-output command: `$handoff print`.
- For Pi Coding Agent: `/skill:handoff extract` to resume or
  `/skill:handoff print` to emit.

Do not include the handoff document contents in the response. Verify that the
file exists, contains no unresolved angle-bracket placeholders, and records the
actual post-commit HEAD. Run `git status --short`; only the transient untracked
`NEXT_SHELL_PROMPT.md` may remain unexplained.

## Guardrails
- Preserve user intent and existing project conventions.
- Prefer factual, verifiable statements over narrative.
- Keep prompt content specific enough that a new shell can continue without re-discovery.
- If there are multiple repos/worktrees, confirm which repo to hand off before committing.
- Never omit discussion context just because no code was written — validated conclusions and design decisions are first-class handoff content.
- Never add `NEXT_SHELL_PROMPT.md` to `.gitignore`, `.git/info/exclude`, or the index as a
  side effect of this workflow.
