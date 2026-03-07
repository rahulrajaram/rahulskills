---
name: ecosystem-borrow-audit
description: "Audit ~/Documents/listings.txt and all depth-1 git repos for borrowable components, missed architectural opportunities, and integration gaps; then run independent gptengage ideate sweeps across multiple sigma values. Use when the user asks for ecosystem review, cross-repo borrowing analysis, missed-opportunity checks, or multi-sigma ideation after repo analysis."
argument-hint: "[scope-root] [--sigma LIST] [--cli claude|codex|gemini]"
---

# Ecosystem Borrow Audit

Run a repeatable ecosystem audit across `~/Documents` and produce an evidence-backed backlog of borrowable components, missed opportunities, and ideation-driven follow-ups.

## Inputs

Extract from user request:
- Scope root (default: `~/Documents`)
- Listings file path (default: `~/Documents/listings.txt`)
- Repo depth (default: depth 1)
- Ideate sigma list (default: `0.25, 0.5, 1, 1.5`)
- Ideate CLI preference (`codex`, `claude`, or `gemini`; default: `claude`)

## Workflow

1. Normalize paths and scope.
- Verify listings path exists; correct typo if user wrote `Documetns`.
- Enumerate all depth-1 git repos under `~/Documents`.
- Build unified catalog: listings entries + git repos.

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

6. Run ideate sweeps independently per sigma.
- Check availability first:
```bash
timeout 120 ~/.local/bin/gptengage status 2>&1
```
- Run each sigma independently and save both JSON and text output:
```bash
SEED="<user-seed>"
for SIG in 0.25 0.5 1 1.5; do
  timeout 600 ~/.local/bin/gptengage ideate "$SEED" --sigma "$SIG" --depth 2 --output json --cli <CLI> --timeout 300 2>&1 | tee "/tmp/ecosystem_audit/ideate_sigma_${SIG}_json.out"
  timeout 600 ~/.local/bin/gptengage ideate "$SEED" --sigma "$SIG" --depth 2 --output text --cli <CLI> --timeout 300 2>&1 | tee "/tmp/ecosystem_audit/ideate_sigma_${SIG}_text.out"
done
```

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
4. Ideate summary by sigma
5. Artifact paths to raw scans and ideate outputs

## Guardrails

- Keep analysis evidence-backed with file paths and commands.
- Do not treat non-git listings entries as repos; include them as contextual entries.
- If `gptengage` fails, report error and suggest:
```bash
~/.local/bin/gptengage status
```
- If preferred ideate CLI stalls/timeouts repeatedly, report the issue and run a fallback CLI only with user approval.
