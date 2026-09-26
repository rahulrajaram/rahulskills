---
name: metabuilder-assess
description: Assess MetaBuilder skills and prompts, harness construction, runtime behavior, and target usefulness from supplied evidence, then recommend bounded improvement, continuation, escalation, or design routing. Use at a harness epoch boundary or when a missing generic capability needs evidence-based classification.
---

# MetaBuilder assessment

## Harness state diagrams

When work in this skill concerns a harness's states or transitions, follow [harness state diagrams](../metabuilder/references/harness-state-diagrams.md) and include the required Mermaid and ASCII diagrams in the final response.

## Intent and applicability

Use this skill as a thin, evidence-first assessor for an existing MetaBuilder
campaign or supplied skill, prompt, harness, runtime, or target evidence. It
reuses available qualification evidence and retrospectives; it does not create
a second analysis engine. At every new harness epoch, assess the layers that
the evidence can reach and make a justified improvement or no-change
recommendation. End with an advisory `stop`, `continue`, or `seek_authority`
outcome.

The assessment is advisory. It cannot dispatch workers, grant authority, alter
an approved objective, or claim production readiness.

## Inputs and local bindings

Bind the exact campaign, epoch/run, objective and source identities, approved
brief/module/bundle when present, runtime executable identity and relevant CLI
help, target repository instructions, qualification/journal evidence,
retrospectives, and any supplied skill or prompt files. Preserve the evidence
source and digest where available. If a required binding is missing, record the
coverage limit and continue independent assessment.

For a runtime v2 epoch retrospective, use the installed runtime's canonical
CLI scaffold and edit the complete scaffolded object. Read the current help or
guide first and preserve its exact schema, field names, enums, and flags; do
not invent fields, flags, or a substitute report format. A legacy runtime that
cannot emit the v2 report is a reported runtime limitation, not a reason to
fabricate a v2 record. Failures, interruptions, timeouts, and `Unknown` remain
incomplete; they cannot be turned into a successful stage record.

## Non-goals

This skill does not design a new harness, qualify a consumer run, repair source
or skills, run an automatic review panel, or implement a new runtime/reporting
engine. It does not replace `metabuilder-harness-design`,
`metabuilder-consumer-qualification`, or
`metabuilder-harness-improvement`. Optional `code-review`,
`check-antipatterns`, `analyze-conversation`, and `oracle-design` work is
selected only when a concrete evidence gap requires that skill and the caller
has requested or already authorized it.

## Must not

- Do not invent aggregate scores, coverage percentages, successful stages,
  receipts, observations, approvals, or semantic conclusions.
- Do not conflate controller-observed runtime facts with consumer semantic
  judgment or worker claims.
- Do not silently treat an unknown or unassessed layer as passing. Give every
  unassessed layer a reason, and preserve alternative causes where evidence
  does not identify one cause.
- Do not dispatch, grant authority, apply effects, mutate an old bundle/run, or
  reopen a closed epoch. Existing authorized continuation needs no redundant
  per-epoch approval, but the assessor cannot supply that authorization.

## Procedure

1. Establish the evidence boundary and identities. Separate observed facts,
   supplied claims, inferences, unknowns, and proposed actions. Check whether
   the epoch is complete; if its terminal result is failed, interrupted, timed
   out, or `Unknown`, assess the incomplete evidence without upgrading it.
2. Select assessment layers from reachable evidence: skills and prompts;
   harness construction/model commitments; runtime behavior and report
   contract; and target usefulness/semantic adequacy. Assess only selected
   layers, and state why each omitted layer is `not_assessed` or `unknown`.
3. For each selected layer, record evidence references, observations,
   inferences (clearly labeled), counterevidence, alternative causes,
   limitations, and a concrete proposed change or explicit no-change reason.
   Check whether the harness model, qualification checks, and retrospective
   evidence actually support the claimed conclusion; passing commands alone do
   not establish semantic adequacy.
4. At an epoch boundary, compare the current evidence with the objective and
   prior gap lineage. Recommend one of `improve`, `no_change`, `blocked`, or
   `changed_objective`; justify the recommendation from evidence and identify
   the next bounded action. A recommendation is not execution.
5. Route ownership precisely:
   - bounded same-objective harness repair → `metabuilder-harness-improvement`;
   - changed objective, brief, or design commitment →
     `metabuilder-harness-design` with lineage;
   - runtime/report-contract capability → the Rust MetaBuilder maintainer;
   - skill or prompt defect → the skills maintainer for this repository;
   - target-specific usefulness or test gap → target owner;
   - missing authority → the named authority owner;
   - missing qualification or exact-run evidence →
     `metabuilder-consumer-qualification`.
   State proposed owner, causal hypothesis, and validation evidence for every
   routed action. On later assessments, revisit that hypothesis using comparable
   before/after evidence and record supported improvement, no improvement,
   regression, or unresolved. Distinguish proposed, applied, and verified changes;
   do not require a new benchmark campaign when existing evidence is sufficient.
   Report effort or cost changes only when actually observed.
6. Emit the advisory disposition: `stop` when the objective is complete,
   evidence is insufficient for a safe next action, or a terminal boundary is
   reached; `continue` when existing authority covers a dependency-ready next
   epoch; `seek_authority` when the next action needs a new or changed grant.
   Include the exact dependency-ready next action or the reason none exists.

## Completion and evidence

Produce a concise assessment containing: bound identities and epoch; selected
layers; evidence references; observations versus inferences; unknown and
not-assessed reasons; alternative causes; per-layer findings; recommendation;
proposed owner and validation; advisory stop/continue/seek-authority
disposition; and unresolved limitations. If a canonical v2 retrospective is
required, record only the exact complete object accepted by the runtime CLI
and report its command result. A missing or legacy v2 capability remains an
explicit limitation. The final report must distinguish observed execution,
consumer assessment, worker claims, proposed repair, and approval.
