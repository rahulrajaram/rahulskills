---
name: autonomy-loop
description: "Drive an epic as a principal-architect loop: rank tasks, execute bounded slices, verify, checkpoint, and optionally chain safely."
argument-hint: "<epic-or-objective>"
---

# Autonomy Loop

Use this skill when the user asks to keep meaningful work moving across an
entire epic, act as principal architect, choose the next work repeatedly, run an
autonomous loop, continue a project without routine user involvement, or let
the work chain after each completed slice.

This is a meta-orchestrator. It owns judgment, sequencing, and epic state. It
uses `autonomous-execution-contract` as the bounded executor for each selected
task.

## Reasoning Posture

Use adaptive reasoning:

- **Loop controller:** medium reasoning by default. Ranking tasks, preserving
  the epic thesis, interpreting proof/resource state, and choosing bounded
  slices require principal-architect judgment.
- **Bounded executor:** low reasoning by default once a task is selected and
  handed to `autonomous-execution-contract`.
- **Escalate to high reasoning only for:** architecture or API boundaries,
  product/release/security/privacy decisions, destructive/resource cleanup,
  parallelization plans, expensive proof-gate decisions, or repeated failures
  after the executor circuit breaker.

## Core Contract

Default loop:

1. Orient on project state, project doctrine, recent work, proof artifacts, and
   resource health.
2. Reconstruct the active epic and acceptance criteria.
3. Generate or refresh the next 10 candidate tasks.
4. Rank candidates by strategic value, verification clarity, risk, locality,
   dependency order, and resource cost.
5. Select one bounded task.
6. Execute that task with `autonomous-execution-contract`.
7. Verify, checkpoint, and commit locally when permitted.
8. Re-rank and either stop at a clean checkpoint or continue if the prompt
   explicitly grants multi-slice/reactor execution.

For ordinary "continue" prompts, complete one coherent loop iteration. For
explicit multi-hour, multi-slice, epic-completion, "chain", or "reactor" prompts,
keep looping across bounded tasks until a stop rule, budget, or clean milestone
triggers.

## Reactor Mode

Reactor mode is controlled chaining, not unbounded wandering. Enter it only
when the user explicitly asks for longer looping, a larger chunk, a chain
reaction, multi-slice execution, epic-completion work, or similar wording.

In reactor mode:

1. Complete one bounded slice through `autonomous-execution-contract`.
2. Verify the slice with focused checks.
3. Commit locally when the slice is coherent and commits are permitted.
4. Update the checkpoint source when progress is material.
5. Re-read current git/resource/proof state.
6. Re-rank the next 10 candidate tasks against the active epic.
7. Start the next bounded slice only if all reactor continuation gates pass.

### Reactor Continuation Gates

Continue only when all are true:

- The active epic is still the same epic, not a new strategic direction.
- The worktree can be made clean after the slice, or all remaining changes are
  intentionally part of the next immediate slice.
- Focused verification for the previous slice passed, or the next slice is a
  direct bounded fix for a newly discovered failure.
- The next task has a clear local verification path.
- The next task does not require push, deploy, publish, production mutation,
  credentials, secrets, paid services, or unavailable infrastructure.
- Resource state is acceptable for the next task.
- The loop has not exhausted its configured budget.

### Reactor Default Budgets

If the user grants reactor-style autonomy but does not specify a budget, use
these defaults:

- Stop after 5 local commits or 3 submodule commits plus parent checkpoints,
  whichever comes first.
- Stop after 3 consecutive failures of the same verification target.
- Stop before an expensive global proof unless the proof budget says it is due.
- Stop at the first clean milestone where the next task would be a new epic.

If the user gives a smaller budget, obey it. If the user gives a larger budget,
still enforce all guardrails and stop conditions.

## Non-Negotiable Guardrails

- Do not push, publish, deploy, open PRs, merge, rewrite shared history, or
  change external shared state unless the user explicitly authorizes it in the
  active conversation.
- Do not delete files outside the active project root unless the user
  explicitly names and authorizes that scope.
- Do not run broad destructive cleanup such as `git reset --hard`, broad
  `git clean`, `rm -rf`, blanket Docker prune, or cluster/resource pruning
  unless the user explicitly authorizes it or the command is limited to known
  loop-created/generated resources.
- Preserve user changes. If the worktree is dirty, classify changes before
  editing and never revert unrelated edits.
- Treat private-repo policy as binding when present. Never make a private repo
  public or weaken visibility/publish guards.
- Stop for secrets, credentials, paid services, production infra, or unavailable
  required infrastructure.
- Stop when the same verification failure persists after the circuit breaker in
  `autonomous-execution-contract`.

## Resource Discipline

Before Docker, benchmark, emulator, Kubernetes, or other heavy work:

1. Capture a resource preflight:
   - `df -h /`
   - `docker system df` when Docker is involved
   - `docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Status}}'`
     when Docker is involved
2. Identify expected generated artifacts, containers, images, clusters, caches,
   or temp directories before creating them.
3. Prefer project-provided cleanup scripts and narrowly scoped cleanup commands.
4. After heavy work, capture a postflight and clean only resources that are
   known to be loop-created or documented as safe generated output.
5. If disk is critically low, Docker is unhealthy, or the system crashes during
   proof work, stop, report the resource state, and recommend the smallest safe
   cleanup. Do not improvise broad cleanup outside the project root.

## Skill Composition Map

Use precise slices of other skills. Do not load or follow their full workflows
when a narrow contract is enough.

- **`autonomous-execution-contract`**: use for each selected bounded task. Pass
  objective, task source, selection rule, stop rules, verification, proof
  budget, git policy, checkpoint policy, and parallelism boundaries.
- **`objective-to-dag-decomposition`**: use when the epic is vague, strategic,
  or spans multiple subsystems. Produce or refresh the DAG only at epic start,
  major pivots, or after a blocker changes the architecture.
- **`next-todos`**: use its output discipline for the next 10 tasks: imperative,
  specific, testable, one sentence each. Invoke the full skill only when the
  user wants durable todo/tranche side effects; otherwise draft the list
  directly to avoid accidental queue mutation.
- **`git-status-report`**: use for sync/ahead/behind reporting or before a
  handoff. For quick local orientation, raw `git status --short --branch` and
  `git submodule status` are enough.
- **`test`**: use for substantial test, lint, typecheck, Playwright, or
  benchmark commands. Prefer focused verification first, then global proof.
- **`commit`**: use for local checkpoint commits when commits are permitted and
  touched files need triage. Never push as part of this loop.
- **`handoff`**: use at the end of a long run, before context loss, or when the
  user asks to continue in a new shell. For small material updates, update the
  canonical plan/handoff docs directly.
- **`invokellm`**: use sparingly for high-stakes architecture choices, product
  direction, or repeated failure diagnosis. Integrate the result; do not
  outsource responsibility.
- **`fp-refine`**: use when the chosen task is DSL/FP cleanup, or when new
  domain code is drifting into mutable, stringly, exception-driven shape.
- **Domain-specific RCA/recovery skills**: use when logs, traces, or benchmark
  artifacts need evidence-backed failure classification before patching.
- **Durable background runners**: use only when background tranche execution
  materially helps. Direct execution is preferred for ordinary local patches.

## Memory And Code Indexes

- Query durable memory at every epic start, resume, and major re-rank when a
  memory tool is available. Use it to recover prior decisions, house style,
  proof status, blockers, and user preferences.
- Use local code indexes opportunistically when present and fresh for code
  navigation, impact analysis, verification routing, drift detection, and
  cleanup planning.
- Never make correctness depend on a memory tool or code index. If one is
  absent, stale, or uncertain, fall back to `rg`, repo docs, tests, and
  conservative verification.
- Treat memory and indexes as orientation aids. Local files, tests, and proof
  artifacts remain the authority for current workspace truth.

## Epic Orientation

At the start of an epic or resumed loop:

1. Establish the project root and deletion boundary.
2. Read current git/submodule state.
3. Read canonical project docs when present: project agent instructions,
   implementation plans, prompt/handoff docs, roadmap docs, benchmark reports,
   and local handoff files.
4. Query memory for prior decisions and current house style when available.
5. Check whether a local code index can safely improve impact analysis. Use it
   only if available and relevant.
6. Identify the north star, active constraints, latest proof state, known
   blockers, and open risks.
7. If the epic is still blurry, run a compact `objective-to-dag-decomposition`
   pass before task selection.

## Project Trajectory Compass

Infer the active epic from user instructions, repo docs, memory, recent commits,
and proof artifacts. Prefer tasks that move the project from internal proof
toward product-ready proof: schema-backed evidence, history, target
drilldowns, verifier/recovery/artifact visibility, metering/risk surfaces, demo
readiness, and fresh confidence in the active proof gate.

Avoid drifting into adjacent product stories merely because they are available.
If no task clearly advances the current epic, stop at a clean checkpoint and
recommend the next epic instead of silently switching.

## Task Ranking Rubric

Rank candidate tasks by these criteria:

1. Advances the stated project north star.
2. Improves proof, recovery, evidence, governance, metering, reliability, or
   user-visible product readiness.
3. Has a clear local verification path.
4. Preserves or improves the active proof gate.
5. Avoids hardcoding, public-scope drift, and product-story drift.
6. Is small enough to execute and commit as a coherent checkpoint.
7. Reduces future agent confusion through clearer contracts, tests, or docs.
8. Has acceptable resource cost for the current machine state.

When rankings are close, prefer the task that creates a vertical slice of
working product evidence over a broad refactor.

## Execution Unit Template

For each selected task, instantiate `autonomous-execution-contract` like this:

```text
Use autonomous-execution-contract.

Objective: <one bounded task from the ranked epic backlog>
Task source: autonomy-loop ranked backlog for <epic>.
Selection: selected because <strategic value>, <verification clarity>, and <dependency order>.
Reasoning: low by default; escalate for architecture, safety, product/API, or repeated failure.
Stop only for: push/deploy/publish, secrets, destructive cleanup, deletion outside project root,
external shared state, unavailable required infra, or repeated same failure after the circuit breaker.
Verification: <focused commands>; global proof only when proof budget says due.
Proof budget: focused checks after each patch; expensive proof at milestone/final unless explicitly requested earlier.
Git: local commits allowed when coherent; do not push.
Checkpoint: update canonical plan/handoff docs after material progress.
Parallelism: serial implementation unless file ownership and verification boundaries are independent.
```

For reactor mode, add:

```text
Reactor mode: enabled.
Reactor budget: <commit/time/slice budget, or defaults>.
Reactor gates: clean checkpoint after each slice; re-rank before each next slice; stop on guardrail, repeated failure, resource pressure, or new-epic boundary.
```

## Checkpointing

For an entire epic, maintain resumability:

- Prefer project-native state: implementation plans, prompt/handoff docs, issue
  files, benchmark manifests, durable tranche files, or other canonical
  project state.
- If no project-native state exists, create a concise local loop-state file
  only for substantial multi-step work.
- Record completed tasks, current task, verification results, resource issues,
  commits, submodule pointers, blockers, and the next recommended action.
- Commit checkpoints only when the workspace is internally consistent and
  verification appropriate to that checkpoint has passed.

## Stop Conditions

Stop and report clearly when:

- The epic acceptance criteria are satisfied.
- The next decision changes product/API/release/security/privacy strategy.
- Required infrastructure, credentials, or system resources are unavailable.
- Resource cleanup would require broad destructive action.
- The loop reaches a coherent checkpoint and no explicit multi-loop/timebox was
  provided.
- Reactor mode reaches its slice, commit, time, or failure budget.
- Repeated failures trigger the executor circuit breaker.
- The remaining work is a new epic rather than the current epic.

## Final Report

Report:

- Current epic and whether it is complete, blocked, or paused at a checkpoint.
- Tasks completed and tasks still ranked next.
- Verification passed, failed, or skipped.
- Commits created and whether anything was pushed.
- Current branch, submodule pointers, and workspace cleanliness.
- Resource state and cleanup performed when heavy resources were used.
- The next bounded task that should be fed to `autonomous-execution-contract`,
  or the next reactor-ready slice when reactor mode remains appropriate.
