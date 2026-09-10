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
| `continue-work` ↔ `work-intake` | router | Resume discovery belongs only to `continue-work`; intake classifies fresh work and preserves known owners. An invocation-local no-resumable result prevents fallback from routing back into discovery without relevant state change. |
| `metabuilder` → { `metabuilder-harness-design`, `metabuilder-consumer-qualification` } | router | Lifecycle entry routes fresh design before qualification, assessment to metabuilder-assess, and same-objective repair to metabuilder-harness-improvement. Changed objectives return to design. |
| `autonomy-loop` → `autonomous-execution-contract` | composer | The contract is the loop's bounded executor, unchanged. |
| `autonomy-loop` governed profile → MetaBuilder | router (new) | When an epic is long-horizon, the governed runtime is the MetaBuilder lifecycle; the loop consumes controller receipts rather than reconstructing them. |
| `handoff` ↔ MetaBuilder checkpoints | boundary (new) | In-run recovery belongs to harness durable attempts; `handoff` owns human cross-shell resume and records harness run/checkpoint identities for re-entry. |
| `metabuilder-consumer-qualification` → `metabuilder-harness-design` | producer-consumer (new) | Every close emits a continuation handoff (leftover checkpoint + proposed next ObjectiveRequest + envelope class + delegation budget accounting). Same-envelope handoffs with budget remaining return directly to design; cross-shell discovery belongs to `continue-work`; exhaustion or expansion exits to the principal. Batch size M and renewal policy are fixed once in the charter's continuation standing delegation. |
| `metabuilder-consumer-qualification` → `metabuilder-assess` | producer-consumer | Exact run and retrospective evidence feeds adaptive epoch assessment. Recommendations cannot grant continuation or replace controller observations. |
| `metabuilder-assess` → `metabuilder-harness-improvement` | producer-consumer | Justified same-objective harness changes enter the existing package lifecycle with evidence and gap lineage. Other causes route to their owners. |
| `metabuilder-harness-improvement` → repository-local improvement skill | package adapter | The global skill discovers and delegates to the existing authoritative CLI workflow; matched requalification preserves the exact brief identity. |
| `metabuilder-assess` → { `check-antipatterns`, `analyze-conversation`, `code-review` } | selective composition | Request only the analysis needed to resolve an evidenced uncertainty; no universal review panel or duplicate retrospective engine. |
| `check-antipatterns` → `analyze-conversation` | router | Focused session-execution checks stay with check-antipatterns, including completed sessions. A requested durable retrospective report routes to analyze-conversation. |
| `check-antipatterns` → `code-review` | distinct use cases | Explicit source-code review routes to code-review; session execution inspection does not acquire a source-audit phase. |
| `code-review` → local codereview package | consumer adapter | Select only needed perspectives and stages; package protocols, source bindings and controller receipts govern completed reviews. Full epoch review is opt-in. |
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
