---
name: metabuilder-harness-design
description: Design a new MetaBuilder harness from repository evidence and a user objective through thorough grilling, an agreed brief, and typed intent/module/workflow commitments. Use before fresh harness construction; use consumer qualification later to run and assess an already designed harness.
---

# MetaBuilder harness design

Turn an underspecified request into reviewable MetaBuilder design artifacts. Own
task and repository discovery, the question-and-evidence process, brief
agreement, and translation into typed MetaBuilder intent and Harness Module
commitments. Stop after the module compiles and its bundle re-admits; hand the
result to `metabuilder-consumer-qualification` for execution and semantic
assessment. When the user requests design-only work or withholds an effect or
artifact-write boundary, stop at that earlier boundary and label every
uncreated downstream identity; never create artifacts merely to fill out the
normal packet.

This skill is guidance, not authority. The Rust CLI admits the artifacts, the
controller grants effects, and the consumer decides whether the resulting
checks are meaningful.

## Boundary

- Read the target repository's applicable instructions before designing.
- Honor a user boundary narrower than this workflow. Missing approval or write
  authority produces an explicit design-only handoff, not invented evidence.
- Formal fresh construction is consequential under the CLI gate. Reuse
  evidenced grilling coverage and decisions; investigate only missing or
  changed material issues. Routine inspection and provisional preparation
  do not themselves cross that gate.
- Keep facts, assumptions, preferences, unknowns, and decisions distinct.
  Resolve each material unknown or record an owner, impact, and review trigger.
- Require a named product owner to approve every formal decision and every
  required approver to accept the exact prepared brief.
- Do not infer filesystem, process, network, credential, installation,
  external-state, release, deployment, provider, spend, or continuation
  authority from an objective, approval, digest, generated file, or passing
  check. Stop at an unsupported effect boundary.
- Preserve the three layers: `defineIntent` states meaning without executable
  authority; a Harness Module commits to actions and evidence; a run records
  controller observations. None proves the consumer's final semantic claim by
  itself.

## Authority by phase

- **Analysis:** The user's design or inspection request permits relevant local
  reads and evidence gathering within existing permissions. Establish missing
  owners before their decisions are needed; continue independent investigation.
- **Provisional design:** Prepare findings, candidate briefs, alternatives, and
  authority-free intent sketches within authorized local output paths. Label
  unresolved decisions and proposed commitments. These are review materials,
  not approved modules, receipts, or permission to execute.
- **Ratification:** Before formal construction, require named product-owner
  evidence for every formal decision and acceptance of the exact prepared
  brief by every required approver. Technical evidence can resolve a grilling
  question but cannot stand in for formal user approval. A speculative model
  respondent cannot ratify on a human's behalf.
- **Formal artifact publication:** Finalize the agreed brief and construct,
  compile, and admit the module/bundle only when the required ratification and
  artifact-write authority are satisfied. Local publication does not authorize
  remote publication. Neither a template nor a successful check supplies a grant.
- **Execution:** Authoring a run, applying effects, provider dispatch, and spend
  require the corresponding existing grants and controller enforcement. Design
  acceptance alone does not authorize them. Consumer assessment remains separate
  from both approval and controller-observed execution.

Reuse an agreed brief and explicit decisions when their approval-relevant
identity, actors, decisions, effect scope, and grants remain valid. Verify the
receipt with the current CLI; a changed prepared brief digest needs acceptance
for that new digest under the controller's rules. Changed approvers, ambiguous
ownership, stale evidence, or added effects reopen the affected decision.
Do not restart a settled interview merely because a companion skill is loaded.
For an unresolved boundary, finish independent authorized preparation, ask for
the specific missing decision with the concrete artifact/effect in view, and
hold only dependent work. Silence is not approval.

The emitted brief template contains zero digests as visible placeholders. They
are structurally valid so the Rust gate can demonstrate the full shape, but
they are not evidence. Replace every placeholder with the digest of the exact
answer, policy, investigation, or approval record it cites before agreement.

## Consume preparation artifacts

Before grilling from scratch, look for artifacts already produced by the
preparation skills and consume them as cited inputs:

- A `frame-goals-constraints` product thesis fills the brief's goals,
  non-goals, constraints, and risks. Cite the thesis artifact and its digest;
  do not re-derive or silently paraphrase it.
- A `grilling` or `grill-me` resolved-question record maps directly into the
  brief's `grilling.resolved_questions` with its original basis and evidence
  digest. Grill only the material questions those records do not cover.
- A ratified `define-operating-charter` charter is authoritative for the
  brief's actors and authority boundaries; the brief restates, never
  re-decides, them.
- An `objective-to-dag-decomposition` execution DAG feeds the typed intent
  and workflow topology: obligations come from its task and verification
  nodes, and ordering follows its `depends_on` projection.

When preparation records do not cover a material unknown, convene an
autonomous grilling by default (`grilling` speculative mode with its bounded
internal debate) to resolve TECHNICAL unknowns before asking the principal;
record its resolved questions with basis and evidence digest like any other.
Product, authority, and approval decisions are never resolved this way —
they still require the named owner.

Reuse stays subject to the freshness rule above: changed actors, effect
scope, or evidence reopen the affected decision, and each cited artifact's
digest must be recomputed and recorded in the prepared brief.

## Workflow

1. Establish the requester, consumer, product decision owner, technical owner,
   controller, required approvers, exact target repository, objective, and
   explicit stop conditions.
2. Inspect recoverable repository evidence: applicable instructions, current
   source identity and cleanliness, build and test configuration, public
   contracts, existing checks, toolchains, ignored auxiliary inputs, and known
   limitations. Use external research only when it is necessary and separately
   authorized; record it as a cited input, never controller evidence.
3. Build a finding ledger with one classification per item: fact, assumption,
   preference, unknown, or decision. Name provenance and an owner. Ask only
   questions that can change scope, risk, success, authority, or design.
4. Reuse valid answers and conduct the remaining grilling across goals, non-goals, constraints, risks,
   success criteria, actors, material unknowns, effects, failure/recovery, and
   evidence adequacy. Read [references/design-workflow.md](references/design-workflow.md)
   for the exact artifact sequence and approval shape.
5. If no valid agreed brief already covers this design, emit and edit a
   provisional brief candidate:

   ```bash
   metabuilder harness brief template > harness-brief.candidate.json
   metabuilder harness brief prepare \
     --input harness-brief.candidate.json > harness-brief.prepared.json
   metabuilder harness brief inspect --input harness-brief.prepared.json
   ```

   Prepare the approval request for review; populate approval evidence only
   after every required approver has accepted the exact prepared brief digest.
   Reuse existing acceptance of that same digest when still valid. Finalize to a new file; never overwrite an earlier
   candidate or receipt.
6. Translate the agreed meaning into `defineIntent`: objectives become
   `achieve` obligations, independently testable claims become `establish`
   obligations, canonical data becomes declared artifacts, dependencies become
   typed flow, and ordering/choice/convergence become the smallest fitting
   workflow construct. Read
   [references/worked-examples.md](references/worked-examples.md) when choosing
   among small, multi-artifact, or staged/parallel designs. Check source with:

   ```bash
   metabuilder intent check --input intent.mb.ts --json
   ```

7. Translate the approved intent into a Harness Module without adding meaning
   or authority: requirements state the claims; `evidence_actions` name the
   exact checks; actions declare direct argv, cwd, toolchain, timeout, inputs,
   outputs, and auxiliary-directory digests; the workflow preserves the
   approved topology; bounds and retrospectives are explicit. The source
   language itself never contains commands, providers, credentials, or grants.
8. Preflight every requested effect against current MetaBuilder enforcement.
   Prefer the read-only Linux-local consumer profile. If a requirement needs an
   unsupported or unauthorized effect, report it instead of bypassing the
   harness. Compile and re-admit the exact bundle:

   ```bash
   metabuilder harness compile --input harness.module.json > harness.bundle.json
   metabuilder harness check --input harness.bundle.json
   ```

9. At the authorized stopping point, hand the exact agreed brief, intent source,
   module, bundle, target source identity, limitations, assumptions, and open
   unsupported effects to
   `metabuilder-consumer-qualification`. That downstream workflow executes the
   bundle and keeps MetaBuilder observations separate from consumer judgment.

## Deliverable

Return a compact design packet containing:

- the target source identity and evidence inventory;
- the classified finding ledger and resolved grilling record;
- candidate, prepared, and agreed brief identities;
- the checked `defineIntent` source;
- the compiled/re-admitted module and bundle identities;
- the effect preflight, assumptions, limitations, unsupported conditions, and
  stop decisions; and
- an explicit qualification handoff with no production-readiness claim.

Include only identities that were actually created and admitted. For a
design-only result, replace downstream identities with a concise list of the
approval or authority needed to create them.

For exact grammar and product limits, use the repository's
`docs/define-intent-language.md`, `docs/define-intent-capabilities.md`, and
`docs/define-intent-lifecycle.md`. Do not copy their contracts into a competing
skill-local authority.
