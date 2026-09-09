---
name: continue-work
description: "Single resume/continue entry point: find the most specific resumable state — handoff artifact, governed MetaBuilder campaign, active epic plan, or pinned human gate — and force the owning workflow (handoff extract, metabuilder continuation, autonomy-loop, or work-intake when nothing is resumable). Use when the user says continue, resume, keep going, next epoch/tranche, or re-enters a project mid-campaign."
argument-hint: "[scope-or-repo-path]"
---

# Continue Work

## Intent and applicability

Resume-first front door. Where `work-intake` classifies a work statement,
this skill starts from the opposite end: assume work already exists, find
the most specific resumable surface, and force its owning workflow. Use for
"continue", "resume", "keep going", "next epoch", or any re-entry into a
project without a fresh task statement. Never freeform-execute: an
invocation of this skill always ends inside a routed owner.

## Binding

Resolve the scope from the invocation argument, the live request, or the
current working repository — in that order. A named scope ("continue the
reliability campaign", "continue epoch 9") narrows discovery; it never
bypasses routing.

## Discovery (fixed order, presence checks only)

1. `NEXT_SHELL_PROMPT.md` at the repository root (cross-shell handoff).
2. Governed-campaign surfaces bound to the repository: a MetaBuilder
   harness design directory or qualification records, metabuilder run
   roots, a qualification continuation handoff, a recorded campaign
   checkpoint.
3. An active plan or ranked backlog that claims execution authority:
   `IMPLEMENTATION_PLAN.md`, an epic plan with open tranches, durable
   todo state, the latest Haake checkpoint.
4. A pinned human gate: a recorded decision owed to the principal,
   pending adjudication, or an exhausted envelope.

Scan only these surfaces; discovery beyond them belongs to the routed
skill.

## Routing

Every routed continuation carries the existing campaign or epic scope,
continuation policy, budget, authority, and stop conditions to exactly one
owner. A bare "continue" resumes that binding; it does not reduce a
multi-epoch or multi-slice grant to one iteration. The owner must complete
the required reporting and evidence for the current epoch before beginning
the next one. Checkpoints are continuation boundaries, not terminal states,
unless the inherited policy says they are. Stop only on the inherited stop
conditions (including exhaustion, expiry or revocation, envelope expansion,
a reserved decision, recovery failure, or a ratified terminal milestone);
do not manufacture work after the objective is complete.

- Handoff artifact present → `handoff` extract mode. Its activation
  protocol governs. If the artifact records harness run or checkpoint
  identities, re-enter through `metabuilder-consumer-qualification`
  exactly as the handoff skill's boundary section directs.
- Qualification continuation handoff → `metabuilder-harness-design`, already
  long-horizon and without re-classification. Carry the handoff's existing
  campaign scope, continuation policy, standing delegation, remaining budget,
  and stop conditions unchanged. Same-envelope continuation requires a still-
  valid standing delegation with budget remaining. Apply its ratified renewal
  policy: an authorized automatic renewal may replenish the batch; a renewal
  requiring approval, an exhausted nonrenewable batch, or an expanding envelope
  routes the prepared request to the principal. Any human gate remains a gate. The owner
  must finish current-epoch reporting and evidence before re-entering the next
  epoch; a checkpoint is not terminal unless the inherited policy makes it so.
- Governed campaign whose plan carries its own execution discipline
  (epoch envelopes, commit-per-repair, verification gates recorded in
  the plan) → continue THAT plan under its own governance; the plan is
  the authority and MetaBuilder remains its evidence layer. Cite the
  intake classification the plan already records instead of
  re-classifying.
- Governed campaign with in-run recovery owed (incomplete run, failed
  action) → `metabuilder-consumer-qualification` for the durable
  attempts and controller observations.
- Active epic plan or ranked backlog without its own discipline →
  `autonomy-loop`, which owns ranking and next-slice selection.
- Only a checkpoint resumability record exists (no plan, no artifact) →
  adopt its objective and next step, then re-route what it describes by
  the rules above.
- A pinned human gate is the next action → report the gate and the
  evidence behind it; do not route to an executor as if executable work
  existed.
- Nothing resumable → pass a bounded, invocation-local `no_resumable_state`
  result to `work-intake`, including only the repository and scope checked,
  the discovery order used, and the live request (if any). Intake consumes
  this result once: it classifies a genuine new work statement, or asks one
  compact question when the request is bare/absent. It must not send the same
  invocation back through discovery without changed relevant state or a new
  invocation.

## Conflict and staleness rules

For a campaign carrying `continuation-state.json`, discovery passes that file
and its provenance to the selected owner. The owner runs the repository's
`scripts/continuation_state.py --state STATE --observation OBSERVATION
--grant GRANT --as-of RFC3339` before dependent execution. Observations must
come from current repository/controller inspection and the grant from the
trusted owner binding, separately from the proposed state. A successful
assessment is eligibility only; it neither grants authority nor dispatches.
Unknown or ambiguous attempts return to controller reconciliation; duplicate,
stale, terminal, revoked, expired or exhausted state cannot start another action.
Preserve the existing policy, including permitted renewal, across fresh sessions.
Legacy prose handoffs still route to their owner, which validates their decisive
facts and prepares typed state when using this contract; absence of the new
format alone must not erase existing authorization or restart intake.

The newer explicit instruction wins: live request over handoff artifact
over plan over memory. Handoff facts, branch claims, and completion
claims are hints — validate the decisive one (branch/HEAD, run state,
open tranches) before acting; the handoff skill mandates this for
artifacts. A campaign whose plan shows all tranches complete and
qualification closed is not resumable; return the same bounded
`no_resumable_state` result to `work-intake`. When two
repositories carry resumable state and nothing disambiguates, make ONE
compact ask listing the candidates — real cross-repository ambiguity
needs that approval anyway.

## Non-goals

This skill does not classify work (work-intake owns that), does not
plan or decompose, and does not execute. It owns resume discovery and
selects and forces exactly one owner, including the no-resumable handoff
to intake.

## Must not

- Must not re-classify already-routed work; land in-flight work on its
  existing owner.
- Must not route governed work around MetaBuilder for convenience,
  budget pressure, or a missing CLI operation.
- Must not perform a destination skill's startup work; presence checks
  are the ceiling.
- Must not inherit destructive, push, deploy, credential, or
  cross-repo authority from a stale artifact; those need fresh approval.
- Must not silently choose among conflicting surfaces.
- Must not downgrade an inherited multi-epoch or multi-slice authorization
  because the live request is only "continue"; preserve it while routing to
  the one selected owner.

## Completion and evidence

Record one line: surface found, decisive signal, forced owner, and the
staleness validation performed. For no resumable state, record the bounded
repository/scope binding and pass the `no_resumable_state` result to intake;
that result is valid only for this invocation and cannot trigger a discovery
cycle. Downstream skills and future resumes reuse the line instead of
re-discovering.
