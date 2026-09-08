---
name: work-intake
description: "Classify incoming engineering work by horizon and route it: bounded work to autonomy-loop or autonomous-execution-contract, long-horizon work to the MetaBuilder lifecycle. Use at the start of any non-trivial work, at epic or campaign start, or when unsure which workflow should own the work."
argument-hint: "<work-description>"
---

# Work Intake

## Intent and applicability

Classify work once, before a workflow is chosen, and route it to the correct
owner. Use when starting non-trivial work, when the user asks which workflow
should own something, or when work grows past its original envelope. Do not
re-run intake for work already routed; re-classify only when a signal below
appears mid-work.

## Inputs and local bindings

Resolve from the request and observed project state: the stated outcome,
expected sessions, effect classes already authorized (read, write, process,
network, credential), whether evidence must survive interruption, and which
workflows are actually installed. Missing or conflicting bindings require a
decision only when they change the route.

## Classification

Work is **long-horizon** when either holds:

1. **Multi-session:** the work is expected to span more than one working
   session, resume from durable state, or outlive a single conversation.
2. **Durable-evidence:** the work needs governed recovery or qualification
   evidence, spans multiple effect classes, requires controller-observed
   verification of worker claims, or includes a review/self-improvement loop
   over the work itself.

Otherwise the work is **bounded**. Ambiguity resolves to bounded unless a
durable-evidence signal is present; record the open signal and re-classify
when it fires.

## Routing

For **bounded** work:

- One already-selected task: use `autonomous-execution-contract` directly.
- An epic needing repeated task selection, ranking, and chaining: use
  `autonomy-loop`.
- Goal-mode CLIs remain valid for their own hosted work.

For **long-horizon** work, route to the MetaBuilder lifecycle starting at the
[metabuilder](../metabuilder/SKILL.md) entry skill
(`metabuilder-harness-design`, then `metabuilder-consumer-qualification`).

Before committing the long-horizon route, run the **profile check**: if the
work requires effects outside MetaBuilder's currently enforced confinement
profile — agent dispatch, network, credentials, or target writes — route to
harness **design only**, prepare the exact request for the unratified effect
class, and stop the dependent execution there. Do not treat a planned or
rumored capability as available; verify against the installed CLI and source
as the metabuilder skill directs.

## Non-goals

Intake does not plan, decompose, grill, or execute the work, and does not
replace the routing inside the destination skills. Explicit user or parent
selection of a workflow is honored without re-classification.

## Must not

- Must not route qualifying long-horizon work around MetaBuilder for
  convenience, budget pressure, or an unavailable CLI operation.
- Must not describe work as governed when no MetaBuilder controller observed
  it.
- Must not widen an effect class to force a route, or narrow reporting of
  needed effects to fit the current profile.
- Should not ask the user to classify what the signals already determine.

## Interaction and authority

Classification is autonomous. Escalate only when the user's stated outcome and
the observed effect classes conflict, or when the long-horizon route requires
an effect class outside the current profile and the user must ratify the
design-only boundary.

## Completion and evidence

Report the classification (long-horizon or bounded), the decisive signals,
the selected route, and any profile-check boundary reached. One recorded line
suffices; downstream skills reuse it instead of re-classifying.

A long-horizon route carries the maturation obligation: the campaign must file
its MetaBuilder gap records through the metabuilder skill's
improve-through-use path before closing, so routing work through MetaBuilder
is also how MetaBuilder matures.
