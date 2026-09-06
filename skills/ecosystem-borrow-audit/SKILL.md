---
name: ecosystem-borrow-audit
description: "Audit a workspace listing and all depth-1 git repos for borrowable components, missed architectural opportunities, and integration gaps; then run independent gptengage ideate sweeps across multiple sigma values. Use when the user asks for ecosystem review, cross-repo borrowing analysis, missed-opportunity checks, or multi-sigma ideation after repo analysis."
argument-hint: "[scope-root] [--sigma LIST] [--cli claude|codex|gemini]"
---

# Ecosystem Borrow Audit

All gptengage calls follow
[`../../references/gptengage-invocation.md`](../../references/gptengage-invocation.md).

## Intent and applicability

Produce a repository-evidenced backlog for the supplied ecosystem scope. Generic
inferred ecosystem/borrowing analysis defaults to evidence-only. A bare explicit
`/ecosystem-borrow-audit` preserves the full historical workflow, including
`0.25, 0.5, 1, 1.5` ideation, unless the user selects evidence-only. Explicit
external ideation follows the shared invocation authority/data contract.

## Non-goals and must not

Do not widen a named-repository scope to the whole workspace, install tooling,
invoke a second paid call for formatting, or present model ideas as source facts.
Required investigation and local report preparation remain autonomous. Resolve
only material scope/provider/data/spend decisions left unsettled; reuse grants.


## Inputs

Extract from user request:
- Scope root (default: `${WORKSPACE_ROOT:-$HOME/Documents}`)
- Listings file path (default: `$WORKSPACE_ROOT/listings.txt`)
- Repo depth (default: depth 1)
- Ideate sigma list (default: `0.25, 0.5, 1, 1.5`)
- Ideate CLI preference (`codex`, `claude`, or `gemini`; default: `claude`)

## Workflow

1. Normalize paths and scope.
- Use supplied paths and validate them. A missing optional listings file does
  not block repository inspection. Do not silently repair an ambiguous path.
- Enumerate repositories within the selected scope/depth. Use `git -C PATH
  rev-parse --show-toplevel` and compare resolved roots to recognize ordinary
  repositories and linked worktrees without counting arbitrary nested folders.
- Build unified catalog: listings entries + git repos. Listings entries that
  are not git repos are contextual only: never scanned, scored, or ranked.

2. Run tier-1 scan across the unified catalog.
- For each repo/path, capture lightweight signals:
  - language/toolchain markers
  - recent commit date and remotes (for git repos)
  - README/docs architecture keywords (`worker`, `policy`, `queue`, `memory`, `gate`, `retry`, `metrics`, etc.)
- Score each project:
  - relevance (0-5)
  - borrowability (0-5)
  - integration cost (1-5)
  - novelty (0-5)

3. Run tier-2 deep reviews.
- Always include:
  - the target project repository
  - directly-related repositories discovered from docs, configs, and imports
  - any repository with high relevance and high borrowability from tier-1 scoring
- Add highest-scoring repos from tier-1.
- Extract concrete borrow candidates and file-backed evidence.

4. Reconcile missed opportunities.
- Compare findings with project roadmap/state docs (for target repo):
  - `VISION.md`, `IMPLEMENTATION_PLAN.md`, `PROMPT.md`
- Label findings:
  - already implemented
  - partially implemented
  - missed and high-value
  - low-value/not applicable

5. Produce ranked action backlog.
- Rank by impact, effort, risk, and dependency ordering.
- Include explicit next actions and validation checks.

6. Only in selected external-ideation mode, run sweeps independently per sigma.
- Resolve the existing `gptengage` command and verify relevant help. Choose a
  unique private artifact directory before execution. Do not use a shared fixed
  `/tmp/ecosystem_audit` directory or embed arbitrary seed text in shell code.
- For each distinct selected sigma, invoke **once** with `--output json`, the
  selected CLI/depth and per-invocation timeout. Capture stdout, stderr and exit
  status separately. For example, bind reviewed values before executing:

```bash
if "$GPTENGAGE" ideate "$SEED" --sigma "$SIG" --depth "$DEPTH" \
    --output json --cli "$CLI" --timeout "$CALL_TIMEOUT" \
    > "$RUN_DIR/$INDEX.json" 2> "$RUN_DIR/$INDEX.stderr"; then
  status=0
else
  status=$?
fi
printf '%s\n' "$status" > "$RUN_DIR/$INDEX.exit"
```

- Increment a safe numeric `INDEX` per selected sigma and record the sigma/file
  mapping. Validate successful stdout as one JSON document. Render that saved
  result locally into readable Markdown/text; never invoke another model just
  to obtain the same run's alternate format. Preserve failed outputs as failure
  evidence, not valid ideas. Even exit zero may contain partial expansions:
  inspect stderr/coverage and report missing branches.
- A per-call timeout is not a total sweep deadline. Account for sequential levels,
  concurrent waves and cleanup when setting an outer supervisor deadline; omit
  an arbitrary shorter outer timeout if no reliable total bound is known. If an
  explicit total deadline is required, use supervision that terminates children
  and records interruption. Do not silently substitute a backend after failure.

7. Merge ideation with repo-grounded findings.
- Deduplicate themes.
- Label each final idea:
  - `repo-grounded`
  - `hybrid`
  - `ideate-only`
- Prioritize repo-grounded and hybrid items.

## Output Format

Return:
1. Coverage summary (counts + scope)
2. Ranked backlog (impact/effort/risk)
3. Missed previously section
4. Ideate summary by sigma when selected, otherwise evidence-only mode
5. Artifact paths to raw scans and ideate outputs

## Guardrails

- Keep analysis evidence-backed with file paths and commands.
- Verify scoped repository identity with Git, including `.git` files used by
  worktrees; report nonrepository listings as contextual and all skipped coverage.
- If `gptengage` fails, report error and suggest:
```bash
~/.local/bin/gptengage status
```
- If preferred ideate CLI stalls/timeouts repeatedly, report the issue and run a fallback CLI only with user approval.
