# Skill Overlap Dispositions

Date: 2026-09-07

Dispositions for the overlaps identified in
[`skill-composition-audit.md`](skill-composition-audit.md). This document
records the decided routing rule for each named overlap so later work
consumes it instead of re-deriving it. The catalog key `overlap_kind` carries
the same classification mechanically in `capabilities/skills.toml`.

## Overlap kind taxonomy

| Kind | Meaning |
| --- | --- |
| `alias` | Same contract under another trigger; inherits target's behavior. |
| `router` | One skill delegates a bounded subclass of work to another. |
| `composer` | One skill explicitly invokes the other inside its own procedure. |
| `producer-consumer` | One skill's durable artifact is the other's cited input. |
| `shared-backend` | Both use the same external backend; no artifact handoff. |

## Preparation pipeline into the harness brief

The `prepareObjective` chain from
[`metabuilder-autonomy-functional-model.md`](metabuilder-autonomy-functional-model.md)
is now encoded as producer-consumer handoffs. Each producer preserves a
durable artifact; `metabuilder-harness-design` consumes it as a cited input
with a recomputed digest instead of re-deriving it.

| Producer | Artifact | Consumed by | Brief destination |
| --- | --- | --- | --- |
| `frame-goals-constraints` | Product thesis | `metabuilder-harness-design` | `goals`, `non_goals`, `constraints`, `risks` |
| `grilling` / `grill-me` | Resolved-question records | `metabuilder-harness-design` | `grilling.resolved_questions` (basis + evidence digest) |
| `define-operating-charter` | Ratified charter | `metabuilder-harness-design` | `actors`, authority boundaries (restated, never re-decided) |
| `objective-to-dag-decomposition` | Execution DAG | `metabuilder-harness-design` | typed intent obligations; workflow ordering follows `depends_on` |

Freshness rule: changed actors, effect scope, or evidence reopen the affected
decision; a stale cited artifact is not valid reuse.

## Routing dispositions

| Pair | Kind | Rule |
| --- | --- | --- |
| `work-intake` → { `autonomy-loop`, `autonomous-execution-contract`, `metabuilder` } | router | Horizon classification decides: bounded → loop/contract; long-horizon → MetaBuilder lifecycle with the confinement profile check. |
| `metabuilder` → { `metabuilder-harness-design`, `metabuilder-consumer-qualification` } | router | Lifecycle entry routes design before qualification; qualification returns upstream on design gaps. |
| `autonomy-loop` → `autonomous-execution-contract` | composer | The contract is the loop's bounded executor, unchanged. |
| `autonomy-loop` governed profile → MetaBuilder | router (new) | When an epic is long-horizon, the governed runtime is the MetaBuilder lifecycle; the loop consumes controller receipts rather than reconstructing them. |
| `handoff` ↔ MetaBuilder checkpoints | boundary (new) | In-run recovery belongs to harness durable attempts; `handoff` owns human cross-shell resume and records harness run/checkpoint identities for re-entry. |
| `metabuilder-consumer-qualification` → { `work-intake`, `metabuilder-harness-design` } | producer-consumer (new) | Every close emits a continuation handoff (leftover checkpoint + proposed next ObjectiveRequest + envelope class + delegation budget accounting). Same-envelope handoffs with budget remaining take the intake fast path to design; exhaustion or expansion exits to the principal. Batch size M and renewal policy are fixed once in the charter's continuation standing delegation. |
| `check-antipatterns` → `analyze-conversation` | router | Completed sessions route to retrospective analysis. |
| `clean-code-refine` ↔ `fp-refine` | router | Mutual routing with veto, unchanged. |
| `system-memory-audit` → `memleak-investigate` | router | Named-process longitudinal analysis routes onward. |
| `humanize` ← `frame-goals-constraints` | producer-consumer | The thesis is the explicit semantic source. |
| `frame-goals-constraints` → `objective-to-dag-decomposition` | producer-consumer | The thesis feeds decomposition when planning is requested. |
| `figma` → `figma-implement-design` | producer-consumer | Unchanged. |
| `pr-lifecycle` → { `commit`, `squash-commits`, `readme-doctor` } | composer | Unchanged. |
| `handoff` → `commit` | composer | Unchanged. |
| `grill-me` → `grilling` | alias | True alias; now recorded in the catalog. |
| { `debate`, `ideate` } ← `invokellm` | shared-backend | Shared `gptengage` backend; a typed evidence envelope remains open (audit critical gap 4 family). |

## Deferred

- `archdiagram` / `diagram-review-viewer` → MetaBuilder diagram receipts:
  the typed adapter (audit medium gap 9) is deferred until the contract
  registry (Phase 0) gives diagrams a shared output contract.
- Deliberation-skill typed evidence envelope: deferred with the agent-dispatch
  adapter epic (audit rollout phase 3).
