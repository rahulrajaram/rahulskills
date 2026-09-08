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

## Intent, scope, and local bindings

Rank and complete bounded work toward the user's current epic. Ordinary execution
of an already selected task belongs to `autonomous-execution-contract`; that task
does not need this loop's ranking machinery or reactor gates.

Resolve the objective, acceptance criteria, repository, existing plan/checkpoint,
verification commands, authority, and budgets from current instructions and
observed project state. Reuse valid decisions; ask only about a material unresolved
scope or effect after independent preparation makes the choice concrete.

Select evidence and continuation separately. **Standalone evidence** uses
the project's ordinary plan, command outputs, relevant source/environment identity,
and checkpoints; it needs no synthetic epic digest, receipt, or controller.
**Governed-runtime evidence** applies only when an actual selected runtime
provides the compiled contract, proof policy, receipt checks, and durable events.
**Selecting the governed runtime:** when the epic qualifies as long-horizon
(see `work-intake`), prefer the MetaBuilder lifecycle as that runtime —
compile the epic through `metabuilder-harness-design` and consume controller
receipts from `metabuilder-consumer-qualification` rather than reconstructing
equivalent guarantees by hand.
The compiled-contract/receipt sections below specify that profile. For standalone
work their corresponding steps use the ordinary plan, observed verification, and
project checkpoint. Do not fabricate runtime guarantees, IDs, digests, receipts,
or usage; missing required governed evidence holds that action without silently
switching profiles. Reactor continuation can use either evidence profile while
retaining its own stricter gates.

## Non-goals and must not

This loop does not select a new product direction, runtime installation, external
publication, or an enforced controller by default. Necessary scoped investigation,
local implementation, and recovery remain autonomous. Do not replace the user's
outcome with the examples or budgets below, expand an active continuation
envelope silently, or claim completion because a budget ended. Never treat a
passing check, worker claim, or detailed plan as effect authorization.

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
   resource health. On resume, inspect relevant authority/source changes and
   missing evidence; validate digests when the governed profile provides them.
2. Reconstruct the active epic, stable acceptance IDs, proof schedule, budgets,
   and stop rules in the existing plan, or one compiled epic contract for the
   governed profile.
3. At epic start, a major pivot, or an architecture-changing blocker, create or
   refresh the typed execution DAG. Otherwise preserve it.
4. Maintain a ranked ready frontier of at most 5 tasks. After a slice, rescore
   only nodes whose dependencies, evidence, risk, or authority changed. A full
   frontier refresh is due only at a pivot, compaction recovery, or detected
   drift.
5. Select one bounded task and express only its per-slice delta: task ID,
   objective, selection reason, changed risk/authority, focused verification,
   expected evidence, and budget delta.
6. Execute that delta with `autonomous-execution-contract`, which inherits the
   selected plan and authority; governed execution also verifies its compiled
   epic invariants by reference and digest.
7. Run focused verification, append the required checkpoint/receipt events,
   and add the result to the current tranche.
8. Commit when the tranche is coherent and the compiled proof schedule says
   the commit or milestone gate is satisfied. A slice need not equal a commit.
9. Rescore the affected frontier and either stop at a clean checkpoint or
   continue if the prompt explicitly grants multi-slice/reactor execution.

For ordinary "continue" prompts, complete one coherent loop iteration. For
explicit multi-slice, epic-completion, "chain", or "reactor" prompts,
keep looping across bounded tasks until a stop rule, budget, or clean milestone
triggers.

## Reactor Mode

Reactor mode is this loop's stricter local continuation profile. Select it for
an explicit request to chain this loop across slices or run its reactor. A long
timebox on an executor-only task does not select it. State the selected envelope
before chaining; preserve a different explicitly agreed execution workflow.

The external-effect exclusions below apply even when a separate effect grant
exists. If the requested next task exceeds the active reactor envelope, prepare
the concrete task, effect, verification, and proposed scope change for its owner.
Stop dependent continuation until an authorized envelope amendment or explicit
handoff to a different workflow resolves the conflict. Do not hide the conflict
by reinterpreting a gate as a preference. Independent authorized preparation may
continue. An ordinary bounded executor outside this envelope instead follows
its own existing grants and stop rules.

In reactor mode:

1. Complete one bounded slice through `autonomous-execution-contract`.
2. Verify the slice with focused checks.
3. Record its result and observed verification (or required governed receipt)
   in the current tranche.
4. Commit locally only when the tranche is coherent, commits are permitted,
   and the compiled proof schedule is satisfied.
5. Record mandatory checkpoint events and re-read only changed
   git/resource/proof/authority state.
6. Rescore the affected ready frontier; preserve unaffected DAG rankings.
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

- Stop after 4 hours of active controller work, 5 local commits, or 3 submodule
  commits plus parent checkpoints, whichever comes first. Tool wait and user
  wait are reported separately when the runtime exposes them.
- Permit at most 2 expensive global-proof groups per activation unless the
  compiled repository authority requires more or the user explicitly grants a
  larger proof budget. A twice-green gate is one proof group with two runs.
- Stop after 3 consecutive failures of the same verification target.
- Stop before an expensive global proof unless the proof budget says it is due.
- Stop at the first clean milestone where the next task would be a new epic.
- External spend defaults to zero. Track any explicitly authorized cost against
  a separate ceiling; never infer spend authority from a time or commit budget.

If the user gives a smaller budget, obey it. If the user gives a larger budget,
still enforce all guardrails and stop conditions.

### Budget Precedence

Before every expensive proof and before starting another slice, evaluate
budgets in this order:

1. authority and non-negotiable stop rules,
2. safety/resource breakers,
3. explicit user ceilings,
4. proof-run and repeated-failure ceilings,
5. active-time and external-cost ceilings,
6. commit/tranche ceilings.

A lower item never overrides a higher one. Reaching a budget produces a clean
checkpoint/stop reason; it does not establish that the epic is complete.

## Compiled Epic Contract

For a selected governed runtime, compile the following once at epic start and
revise it only when authority or the epic changes. Standalone work records the
corresponding objective, decisions, checks, and bounds in its existing plan; it
does not fabricate digests or create a runtime to satisfy this section:

- stable epic ID, objective digest, and acceptance-criterion IDs;
- authority/source digests and precedence;
- stop rules and delegated/reserved decisions;
- proof schedule: focused checks, milestone/global checks, repeat count, and
  exact receipt-reuse conditions;
- Git, checkpoint, resource, delegation, and external-cost policy;
- execution DAG, ranked ready frontier, and budget ledger.

The goal runtime may still expose only a flat objective. In that case, keep the
compiled contract in the project's canonical checkpoint source and put a
concise objective plus its digest in goal mode. Do not treat the flat goal as
the whole campaign state.

## Proof Schedule And Receipts

Compile repository authority into one proof schedule before implementation.
Project authority wins over this skill. If project rules and the requested
budget conflict, surface the conflict once and stop only when authority cannot
be satisfied.

- Run focused checks after each coherent patch or slice.
- Run expensive/global proof only when the compiled schedule says it is due.
- In the governed profile, a controller-owned receipt should record command/manifest, exit status,
  duration, source commit/tree, lock/dependency identity, toolchain, features,
  environment contract, and relevant artifact digests.
- Reuse a receipt only when every identity field required by its proof policy is
  unchanged. Agent testimony, matching prose, or a commit-message-only claim is
  not a receipt.
- Delegated deterministic proof need not be rerun merely because it was
  delegated when the controller owns and validates such a receipt. Without a
  valid required receipt, rerun the acceptance check through the governed
  mechanism. In standalone work, inspect actual delegated outputs and relevant
  source/input/environment coverage; rerun only unverifiable, stale, missing, or
  insufficient evidence. Matching HEAD alone does not establish reuse validity.

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
- Reactor continuation stops before secrets, credentials, paid services, or
  production infrastructure under its stated gates. Outside reactor continuation,
  apply the selected executor's authority; unavailable required infrastructure
  still blocks dependent work.
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
  the project plan and task, or the compiled epic-contract reference/digest
  plus per-slice delta when that governed runtime exists. Do not
  retransmit unchanged stop, Git, proof, checkpoint, or delegation policy.
- **`objective-to-dag-decomposition`**: use when the epic is vague, strategic,
  or spans multiple subsystems. Produce or refresh the DAG only at epic start,
  major pivots, or after a blocker changes the architecture.
- **`next-todos`**: use its output discipline: imperative, specific, testable,
  one sentence each. Use at most 5 ready-frontier tasks during execution; a
  longer list is an epic-orientation artifact. Invoke the full skill only when
  the user wants durable todo/tranche side effects; otherwise draft the
  frontier directly to avoid accidental queue mutation.
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
   and local handoff files. Record relevant identities; compute required
   digests only for an actual governed policy. On later iterations, re-read
   only changed authority or the narrow evidence needed by the selected task.
4. Query memory for prior decisions and current house style when available.
5. Check whether a local code index can safely improve impact analysis. Use it
   only if available and relevant.
6. Identify the north star, active constraints, latest proof state, known
   blockers, and open risks.
7. If the epic is still blurry, run a compact `objective-to-dag-decomposition`
   pass before task selection.
8. Set an orientation budget appropriate to the repository. If orientation
   keeps expanding without changing the ready frontier, stop reading and select
   the smallest evidence-gathering task instead.

## Project Trajectory Compass

Rank against the user's active objective, the actual customer's outcome,
acceptance criteria, dependency readiness, and current risks. Use repo docs,
memory, recent commits, and proof artifacts as evidence; they do not override
the current user direction.

For an evidence/governance product only, relevant vertical slices might include
schema-backed evidence, history, verifier/recovery visibility, or metering.
Those are conditional examples, not a trajectory for unrelated projects. A
compiler, terminal UI, or documentation project uses its own user outcomes.
Avoid drifting into adjacent product stories merely because they are available.
If no task clearly advances the current epic, stop at a clean checkpoint and
recommend the next epic instead of silently switching.

## Task Ranking Rubric

Rank candidate tasks by these criteria:

1. Advances the stated project north star.
2. Advances the project's customer outcome or resolves a concrete acceptance,
   reliability, delivery, or evidence risk identified for this epic.
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
Evidence profile: <standalone | governed runtime>
Project checkpoint: <existing plan/state path>
Epic contract (governed only): <canonical path + verified objective/authority digest>
Task ID: <existing task/plan ID; DAG node when the project uses one>
Task source: autonomy-loop ranked backlog for <epic>.
Selection: selected because <strategic value>, <verification clarity>, and <dependency order>.
Reasoning: low by default; escalate for architecture, safety, product/API, or repeated failure.
Slice delta: <changed authority/risk, focused commands, expected evidence, and budget delta only>.
Inherited policy: <existing project stop/Git/proof/checkpoint/delegation rules>.
```

For reactor mode, add:

```text
Reactor mode: enabled.
Reactor budget: <commit/time/slice budget, or defaults>.
Reactor gates: clean checkpoint after each slice; re-rank before each next slice; stop on guardrail, repeated failure, resource pressure, or new-epic boundary.
```

## Checkpointing

For an entire epic, maintain resumability:

- In the governed profile, when structured checkpoint state is warranted, emit
  append-only events that
  conform to `references/checkpoint-event.schema.json`. This compatibility
  format does not make a sidecar authoritative when the project already has a
  canonical state mechanism.

- Prefer project-native state: implementation plans, prompt/handoff docs, issue
  files, benchmark manifests, durable tranche files, or other canonical
  project state.
- If no project-native state exists, create a concise local loop-state file
  only for substantial multi-step work.
- Record stable acceptance and DAG IDs, completed/current tasks, verification
  receipts, resource issues, budgets consumed, commits/tree identities,
  blockers, rank changes with reasons, and the next ready frontier.
- Commit checkpoints only when the workspace is internally consistent and
  verification appropriate to that checkpoint has passed.

For governed execution:
Append a checkpoint event after every commit, expensive proof run, budget or
stop event, authority revision, and context compaction. Standalone execution
updates its existing checkpoint at these material boundaries without requiring
a synthetic event ledger. Also checkpoint before
a long command that risks losing recoverable state. A checkpoint is not a
claim of completion.

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
- Active/tool/wait/user-idle time and fresh/cached/output/reasoning tokens when
  the runtime exposes them; otherwise label the available aggregate precisely.
- Verification evidence (or governed proof receipts) produced or reused, its
  relevant identities, and why reuse was
  admissible.
- The next bounded task that should be fed to `autonomous-execution-contract`,
  or the next reactor-ready slice when reactor mode remains appropriate.
