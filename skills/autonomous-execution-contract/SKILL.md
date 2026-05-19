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

If any field is missing, make the safest reasonable assumption and continue. Ask only when the missing field changes risk, public behavior, external shared state, or destructive action.

## Default Stop Rules

Keep working without asking unless one of these occurs:

- A product, API, release, security, privacy, or architecture decision cannot be inferred from repo context.
- A destructive operation is needed, such as deleting user work, rewriting shared history, dropping data, or pruning external resources.
- The next step affects external shared state, such as pushing, deploying, publishing, sending notifications, or changing production infrastructure, and the user has not already authorized it.
- Required credentials, secrets, paid services, or unavailable infrastructure block verification.
- The verification target is impossible after a reasonable sequence of concrete fixes, and the remaining work needs a strategy change.

Routine implementation details, test failures, benchmark artifacts, noisy local state, and non-destructive local commits are not reasons to stop when the contract grants autonomy.

## Execution Loop

1. Restate the active objective and stop rules briefly.
2. Gather the narrowest context needed for the next concrete step.
3. Patch the next failure or missing capability directly.
4. Run focused verification after each coherent patch.
5. Run the contract's proof target when focused checks pass.
6. If proof fails, inspect artifacts, classify the next failure, patch it, and continue.
7. Commit coherent checkpoints when permitted and the touched work is internally consistent.
8. Keep concise progress updates flowing during long commands.

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
```

Example:

```text
Use autonomous-execution-contract.

Objective: Make 13_managed_queue_worker pass a two-repeat --require-churn-free sweep.
Timebox: 3 hours.
Reasoning: low by default; escalate only for architecture/safety decisions.
Stop only for product/API decisions, secrets, destructive actions, or external infra.
Verification: focused tests after patches, then the two-repeat benchmark proof.
Git: commit coherent passing checkpoints; do not push.
```

## Final Response

When the contract ends, report:

- What changed.
- What verification passed or failed.
- Any commits/PRs created.
- The next concrete blocker or recommended continuation.

Do not bury tool-friction records in the user-facing report. If workarounds or missing tool capabilities slowed the loop, record them in the appropriate system-level friction log and then continue.
