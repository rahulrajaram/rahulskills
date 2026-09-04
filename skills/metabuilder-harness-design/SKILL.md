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
- Treat fresh construction as consequential and use thorough grilling. A
  requester cannot downgrade it to routine.
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

The emitted brief template contains zero digests as visible placeholders. They
are structurally valid so the Rust gate can demonstrate the full shape, but
they are not evidence. Replace every placeholder with the digest of the exact
answer, policy, investigation, or approval record it cites before agreement.

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
4. Conduct thorough grilling across goals, non-goals, constraints, risks,
   success criteria, actors, material unknowns, effects, failure/recovery, and
   evidence adequacy. Read [references/design-workflow.md](references/design-workflow.md)
   for the exact artifact sequence and approval shape.
5. Emit and edit the executable candidate:

   ```bash
   metabuilder harness brief template > harness-brief.candidate.json
   metabuilder harness brief prepare \
     --input harness-brief.candidate.json > harness-brief.prepared.json
   metabuilder harness brief inspect --input harness-brief.prepared.json
   ```

   Create the approval request only after every approver reviews the exact
   prepared brief digest. Finalize to a new file; never overwrite an earlier
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

9. Hand the exact agreed brief, intent source, module, bundle, target source
   identity, limitations, assumptions, and open unsupported effects to
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
