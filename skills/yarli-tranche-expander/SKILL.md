---
name: "yarli-tranche-expander"
description: "Research an epic, discover implementation gaps and architecture hotspots, and enqueue a broad validated Yarli tranche wave without losing sight of the overarching goals."
argument-hint: "[--project-root PATH] [--goal TEXT] [--start-key NXT-###] [--apply]"
---

# Yarli Tranche Expander

All writes use the shared idempotent enqueue boundary documented in
[`../../references/yarli-primitives.md`](../../references/yarli-primitives.md).

Use this skill when the user asks to expand a Yarli backlog, enqueue many tranches, discover missing work, or make sure nothing slips through the cracks.

## Autonomy Routing

This skill is for durable backlog expansion, not ordinary implementation
routing. If the user explicitly invokes it, research and enqueue the tranche
wave without asking whether to use Yarli. Do not recommend this skill when the
user simply asked to implement the next local task. After expansion, if the user
asks to execute selected tranches, proceed directly or hand off to
`yarli-execution-loop` only when durable/background orchestration materially
helps.

## Preamble

Before you touch `.yarli/tranches.toml`, tell the user what you are about to research and what constraints will govern the tranche wave. Keep the preamble concrete. Name the active epic, the architectural direction, and the guardrails that matter for this repository.

Default guardrails:

- Stay aligned with the epic goals, not just local cleanup.
- Prefer architecture-first tranche waves over opportunistic helper extraction.
- Bias toward FP-first, immutable, DSL-oriented shapes where the codebase and house style support them.
- Look for opportunities to adopt Hulista-aligned primitives such as `Result`, persistent collections, `sealed_typing.assert_exhaustive`, `live_dispatch`, traced pipelines, and task-group collection patterns.
- Treat Hulista itself as part of the design space: if this repo is blocked by a missing combinator, collector, adapter, typing helper, or immutable utility, enqueue an explicit upstream or vendoring tranche instead of working around it forever.
- Push decomposition toward implementation files under 1000 lines, with line-count ratchets and tranche follow-through.
- Avoid duplicate or redundant tranche ideas; advance the roadmap instead of renaming existing work.
- Do not implement the queued work unless the user also asked for execution.

## Inputs To Gather First

Read only what you need, but do not skip the research pass.

1. User brief:
   - Active epic goals
   - Architectural preferences
   - Any named hotspots or must-do tranches
2. Repository planning context:
   - `PROMPT.md`
   - `IMPLEMENTATION_PLAN.md`
   - `VISION.md` or equivalent, if present
   - `AGENTS.md` / `CLAUDE.md` / house-style notes, if present
3. Current Yarli state:
   - Existing tranche keys, summaries, and status
   - Highest current `NXT-###`
   - Open tranche clusters and duplicates
4. Codebase pressure points:
   - Large-file inventory, especially anything over 1000 lines
   - C901 or similar complexity hotspots
   - Existing decomposition helper modules and facade candidates
   - FP / DSL / Hulista adoption gaps
   - Places where repo progress likely requires Hulista improvements rather than only local refactors
   - Async fan-out sites, string dispatch sites, mutable-state hot spots
5. Validation reality:
   - Relevant focused test commands
   - Current lint or audit commands already used by the repo
   - Places where the current validation slice is too weak for safe long-running Yarli execution

## Research Workflow

1. Establish the epic lens.
   - Summarize the big goals in one short paragraph before proposing tranches.
   - Distinguish the critical-path subsystem from adjacent backlog opportunities.

2. Inventory the backlog surface.
   - List existing tranche ranges already covering the active epic.
   - Identify gaps, duplicates, and sequencing hazards.

3. Scan for missed work.
   - Large files over the repo target ceiling
   - Mutable state models that should become pure reducers or frozen snapshots
   - String-dispatch or exception-control-flow code that wants enums, DSL tables, or `Result`
   - Async gather/fan-out code that wants a collection abstraction
   - Modules already half-decomposed that still need facade collapse, import cleanup, tests, or ratchets

4. Group new tranche ideas into categories.
   Useful categories:
   - Active epic critical path
   - File-size decomposition program
   - FP / DSL / Hulista adoption
   - Hulista upstream or vendoring opportunities
   - Validation and guardrails
   - Alternate-path and blocker-recovery work
   - Documentation / continuation hygiene

5. Sequence before writing.
   - Put architectural mapping and destination planning ahead of code motion.
   - Keep extraction order coherent so later tranches depend on earlier maps, reducers, or module graphs.
   - Prefer tranche waves that can be validated incrementally.
   - Add explicit escape hatches when the preferred plan may hit import cycles, heavy coupling, flaky tests, or missing library primitives.

## Special Research Prompts

During the research pass, explicitly ask:

- What improvements to Hulista would let this repo delete local workaround code or adopt the desired FP style more naturally?
- Which tranche waves need their own verification ratchet before more refactoring is safe?
- Where should Yarli be authorized to take an alternate route if the ideal decomposition path proves too coupled in practice?
- What evidence would tell us a tranche is blocked versus merely inconvenient?

## Tranche Writing Rules

When adding tranches:

- Use the next available sequential `NXT-###` keys unless the user specifies another range.
- Write summaries as imperative, testable work items.
- Keep each tranche about one meaningful deliverable.
- Avoid vague nouns like "cleanup" or "improve" unless paired with a concrete outcome.
- Prefer explicit module names, seams, abstractions, or validation outcomes.
- Keep the tranche wave broad enough to cover the epic, but specific enough that an implementation agent can act on it.
- Add verification tranches deliberately; do not assume implementation tranches will stay honest on their own.
- Add blocker-handling tranches when a likely failure mode could otherwise strand a Yarli run.
- When appropriate, create a paired tranche for "preferred path" and "fallback path" so the execution loop can keep moving without losing architectural intent.

When the repository uses richer tranche metadata, include it:

- `key`
- `summary`
- `status = "incomplete"`
- `group = "next-todos"` unless local convention says otherwise
- `allowed_paths` when the tranche should stay scoped
- `verify` with focused checks
- `done_when` with observable completion criteria
- `max_tokens` when the repo already uses it

## Validation

After editing the tranche file:

1. Run `yarli plan validate`.
2. Re-scan the new tranche range to confirm numbering, ordering, and wording.
3. Check that verification and fallback tranches are present wherever the main wave carries nontrivial coupling or risk.
4. Report how many tranches were added and how they break down by category.
5. Call out the highest-priority next tranche range explicitly.

## Output Shape

Give the user:

1. A short statement of the epic lens used.
2. The tranche categories added.
3. The new key range.
4. Validation results.
5. Any notable gaps that still need future research.

## Repo-Specific Heuristics To Keep In Mind

When the surrounding repo signals these priorities, lean into them:

- Swarm or executor god objects usually need subsystem maps before more helper peeling.
- FP-first means new work should prefer pure reducers, frozen models, declarative transition tables, and `Result`-style validation boundaries.
- Hulista adoption is strongest when attached to an actual seam: async collection, immutable state, traced pipelines, or exhaustive dispatch.
- A broad tranche wave should include guardrails such as line-count dashboards, import-cycle checks, and focused regression coverage, not just decomposition tasks.
- When a tranche depends on missing FP infrastructure, prefer naming the missing primitive explicitly so a later agent can decide between upstreaming, vendoring, or local compatibility layers.
