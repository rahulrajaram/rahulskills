---
name: autonomous-execution-contract
description: Execute agreed long-running engineering work autonomously from a bounded objective, using explicit stop rules, verification targets, and low-reasoning defaults.
argument-hint: "<objective>"
---

# Autonomous Execution Contract

Use this skill when the user asks for long-running uninterrupted work, says to keep going for hours, grants broad autonomy, asks how to avoid routine interruptions, or explicitly invokes `autonomous-execution-contract`.

## Contract Shape

Treat the user's prompt as an execution contract. Extract or infer:

- Objective: the concrete finish line.
- Timebox: how long to keep working before summarizing or reassessing.
- Reasoning posture: low by default for routine inspect/patch/test loops; escalate only for architecture, safety, product behavior, or unclear tradeoffs.
- Stop rules: the few conditions that require user intervention.
- Verification target: the proof command, benchmark, test, CI state, or artifact that defines done.
- Git policy: whether commits, squashes, pushes, PRs, or merges are allowed.
- Resource policy: what heavy resources (Docker, emulators, K8s, GPU, benchmarks) the contract may use, and the finite fault-containment breakers that must stop it.
- Via: whether the executing agent does the work itself (`self`) or delegates mechanical inspect/patch/test/benchmark work to lower-reasoning sub-agents (`sub-agents`), keeping proof and authorization judgment for the executor. If unspecified and sub-agent tooling is available, prefer `sub-agents`; keep faithful to the host's governor-orchestrator convention when one is documented.

If any field is missing, make the safest reasonable assumption and continue. A missing `Via` defaults to following the host's documented orchestrator convention when present, else `self`. A missing `Resource policy` defaults to a preflight + the finite-breaker defaults below. Ask only when the missing field changes risk, public behavior, external shared state, or destructive action.

## Default Stop Rules

Keep working without asking unless one of these occurs:

- A product, API, release, security, privacy, or architecture decision cannot be inferred from repo context.
- A destructive operation is needed, such as deleting user work, rewriting shared history, dropping data, or pruning external resources.
- The next step affects external shared state, such as pushing, deploying, publishing, sending notifications, or changing production infrastructure, and the user has not already authorized it.
- Required credentials, secrets, paid services, or unavailable infrastructure block verification.
- The verification target is impossible after a reasonable sequence of concrete fixes, and the remaining work needs a strategy change.
- The same verification target has failed N consecutive times in a row (default circuit breaker: 3) with no material progress between attempts. Stop and report the persistent failure; do not burn hours re-grinding a stuck target.
- A resource breaker trips (preflight values regress below a safe floor, the host hits critically low disk/memory/pressure, or Docker/emulator becomes unhealthy) and the required fix would need broad destructive cleanup or external infrastructure.

Routine implementation details, test failures, benchmark artifacts, noisy local state, and non-destructive local commits are not reasons to stop when the contract grants autonomy.

## Execution Loop

1. Restate the active objective and stop rules briefly.
2. Orient: if resuming a long-running campaign, recall the canonical checkpoint state (project docs, submodule/HEAD state, prior decisions, proof status, open blockers) before acting. Never assume continuity you have not verified.
3. Gather the narrowest context needed for the next concrete step.
4. Patch the next failure or missing capability directly (or delegate the mechanical patch to a sub-agent per the `Via` field; review its diff before accepting).
5. Run focused verification after each coherent patch. If `Via: sub-agents`, delegate the run and re-run the acceptance check yourself (trust but verify).
6. Run the contract's proof target when focused checks pass.
7. If proof fails, inspect artifacts, classify the next failure, patch it, and continue — but stop if the 3-strike circuit breaker triggers.
8. Commit coherent checkpoints when permitted and the touched work is internally consistent.
9. Update the checkpoint state when progress is material (completed tasks, current task, verification outcomes, submodule pointers, next action) so the work is resumable across shells.
10. Keep concise progress updates flowing during long commands.

Prefer the next concrete fix over a broad plan once the objective and stop rules are clear.

## Reasoning Posture

Use low reasoning for:

- Reading logs and summaries.
- Running focused tests or benchmark repeats.
- Making local, pattern-following code edits.
- Updating tests for an already-understood failure mode.
- Commit hygiene and status reporting.

Escalate reasoning only for:

- Conflicting architectural directions.
- New abstractions or DSL boundaries.
- User-visible behavior changes.
- Safety, privacy, or public-release implications.
- Repeated proof failures whose root cause is no longer local or mechanical.
- Circuit-breaker review: when 3 consecutive same-target failures trip, the *judgement* of whether to re-strategize or stop belongs to the executor (or its orchestrator), not a fresh blind retry.

## Resource Discipline (when heavy resources are in scope)

Before Docker, emulator, Kubernetes, GPU, or benchmark work, capture a cheap preflight and set the safe floor:

- `df -h /` (disk headroom)
- `free -h` and host memory-pressure state (e.g. `/proc/pressure/memory`) when CPU/GPU work is heavy
- `docker system df` and running-container state when Docker is involved

Identify expected generated artifacts, containers, images, caches, and temp dirs *before* creating them; prefer project-provided cleanup scripts and narrowly scoped cleanup. After heavy work, capture a postflight.

Default finite breakers (stop and report, do not improvise broad cleanup):

- Disk headroom falls below a safe floor (e.g. <10% free) with no project-provided safe cleanup.
- Host memory pressure is critically high and a long-run OOM would corrupt the workspace.
- Docker/emulator is unhealthy or container/registry resources are accumulating without a project cleanup path.
- The host crashes mid-proof; do not resume blind, re-orient first.

Cost is not a stop reason by itself, but finite fault-containment breakers are; the executor chooses/escalates the breaker set, the orchestrator confirms them.

## User Prompt Template

Recommended user prompt:

```text
Use autonomous-execution-contract.

Objective: <specific finish line>
Timebox: <2-4 hours>
Reasoning: low by default; escalate only for architecture/safety decisions.
Stop only if: <explicit blockers>
Verification: <exact proof target>
Git: <commit/push/PR/merge policy>
Via: <self | sub-agents>
Resource: <heavy-resource scope + breaker floors, or 'none'>
```

For a multi-slice campaign rather than a single bounded task, wrap this contract inside the loop authority (`autonomy-loop` skill) and pass the campaign goal + task-selection and checkpoint rules there; keep this skill as the per-target executor. Use a `Via: sub-agents` line when the host's governor-orchestrator convention expects the bulk work to be delegated.

Example:

```text
Use autonomous-execution-contract.

Objective: Make 13_managed_queue_worker pass a two-repeat --require-churn-free sweep.
Timebox: 3 hours.
Reasoning: low by default; escalate only for architecture/safety decisions.
Stop only for product/API decisions, secrets, destructive actions, or external infra; also after 3 straight same-target proof failures.
Verification: focused tests after patches, then the two-repeat benchmark proof.
Git: commit coherent passing checkpoints; do not push.
Via: sub-agents for inspect/patch/test/benchmark; keep proof and authorization judgment here.
Resource: Docker benchmarks; preflight df-h + docker system df; stop if disk<10% or Docker unhealthy.
```

## Final Response

When the contract ends, report:

- What changed.
- What verification passed or failed.
- Any commits/PRs created.
- The next concrete blocker or recommended continuation.
- Whether any resource breakers tripped and what state was left behind.
- Whether the work is checkpointed and resumable, and the exact next command to resume.

Do not bury tool-friction records in the user-facing report. If workarounds or missing tool capabilities slowed the loop, record them in the appropriate system-level friction log and then continue.
