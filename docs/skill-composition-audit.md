# Skill Composition and MetaBuilder Autonomy Audit

Date: 2026-08-30

## Executive conclusion

The package is a useful collection of 48 skills, but it is not yet a function-like
skill system. Its strongest composers call other skills explicitly, while most
other relationships remain prose conventions, shared tools, or implied artifact
handoffs. The capability catalog describes effects and overlaps, but it does not
define typed inputs, outputs, failures, provenance, compatibility, or sequencing.

The recommended architecture has two levels:

1. A phase-sized **Skill Contract** is the callable function. It declares typed
   ports, failures, effects, resources, authority, evidence, and recovery.
2. A MetaBuilder **Harness Module** statically composes those functions into a
   governed workflow with capability ceilings, bounded control flow, durable
   state, controller-owned evidence, and qualification.

`SKILL.md` remains human guidance. It is linked by digest to the callable
contract but does not become executable authority. A capability bundle remains
an authority envelope, not a function.

The first implementation should not include a real model worker. It should
prove `autonomy-loop` to `autonomous-execution-contract` composition inside one
static bundle using a deterministic local read-only command and declared file
output. Agent dispatch should come later as an effectful, claim-producing
adapter whose output requires controller verification.

## Freshness and runtime parity

The comparison used the repository's own assembly and synchronization paths,
then inspected differences per skill so existing worktree changes were not
overwritten.

- Repository: 48 package skill directories.
- Codex: 47 user-installed package skills plus 6 runtime-owned system skills.
- Pi: 46 installed package skills.
- `source-coverage` passed: every installed Pi and Codex skill has package
  source or an intentional Codex runtime-owned catalog entry.
- Codex had one newer package implementation: `metabuilder`. Its installed
  copy added consumer qualification commands, clean-binary provenance guidance,
  the deferred fresh-generation boundary, and maintainer-only self-hosting
  restrictions. Those changes were brought into
  `skills/metabuilder/SKILL.md`.
- Pi had no newer content. Forty-five entries are direct links to this
  repository. Its real `define-operating-charter` directory is content-identical
  to the repository and older by modification time.
- Pi lacks `figma` and `figma-implement-design`; that is installation coverage,
  not a freshness source. No external Pi state was changed.
- Codex's system-owned skills remain intentionally excluded from package
  installation. The package's shared `skill-creator` is newer locally and is
  used by Pi and Claude; Codex continues to use its runtime-owned copy.

Two metadata drifts remain visible:

- The README says there are 47 package-managed skills, while the current tree
  contains 48.
- `capabilities/skills.toml` contains 52 entries: 47 package entries and 5
  runtime-only entries. The package `metabuilder` skill has no catalog entry.

These are catalog/documentation findings, not evidence that another installed
skill is newer.

## Ecosystem coverage

The component map covers every package skill:

| Family | Skills | Current composition character |
| --- | --- | --- |
| Intent, governance, and design | `frame-goals-constraints`, `grill-me`, `grilling`, `define-operating-charter`, `objective-to-dag-decomposition`, `next-todos`, `archdiagram`, `diagram-review-viewer`, `tui-web-design-orchestrator` | Rich artifacts, but most handoffs are prose-only. |
| Long-horizon orchestration | `metabuilder`, `autonomy-loop`, `autonomous-execution-contract`, `handoff` | Strongest strategic fit; only the loop-to-executor relationship is explicit and reusable. |
| Deliberation and discovery | `invokellm`, `debate`, `ideate`, `ecosystem-borrow-audit` | Shared `gptengage` backend; results have no common typed evidence envelope. |
| Design and implementation | `figma`, `figma-implement-design`, `clean-code-refine`, `fp-refine`, `pythonpackagesevere`, `skill-creator` | Several strong pairs, but no common change-set or verification artifact. |
| Verification, diagnosis, and learning | `test`, `check-antipatterns`, `analyze-conversation`, `postmortem`, `system-memory-audit`, `memleak-investigate`, `pi-defects-harvester` | Good routing boundaries; learning outputs do not feed execution or MetaBuilder retrospectives structurally. |
| Writing and delivery | `clear-writing`, `humanize`, `whitepaper`, `markdown-to-pdf`, `max-columns`, `speak`, `readme-doctor` | Composable in practice, but format, audience, preservation, and evidence contracts are implicit. |
| Repository safety and release | `git-status-report`, `commit`, `squash-commits`, `rewrite-commit-messages`, `reference-cleaner`, `privateify`, `install-commithooks`, `pr-lifecycle`, `repo-topics` | `pr-lifecycle` and `handoff` are real composers; destructive and remote boundaries are well stated but not machine-composed. |
| Specialized data pipeline | `yore-vocabulary-harvest`, `yore-vocabulary-llm-filter` | Clean producer-consumer pair with a human-gated merge, but its artifact schema is local to the pair. |

The complete map is in
[`skill-ecosystem-components.mmd`](skill-ecosystem-components.mmd). Solid edges
are direct or declared routing. Dashed edges are useful relationships that still
depend on caller discipline.

## Relationships that are already strong

1. `autonomy-loop` explicitly uses `autonomous-execution-contract` as its
   bounded executor and declares how it composes with DAG planning, task
   wording, status, tests, commits, handoffs, model consultation, and FP review.
2. `pr-lifecycle` explicitly invokes `commit`, `squash-commits`, and
   `readme-doctor`, with approval gates before push and PR creation.
3. `handoff` write mode explicitly invokes `commit`, then records the exact
   post-commit state for resumption.
4. `grill-me` is a true alias for `grilling`; `grilling` can escalate to
   `debate` and closes speculative runs with an
   `autonomous-execution-contract` handoff.
5. `figma` feeds `figma-implement-design`; `yore-vocabulary-harvest` feeds
   `yore-vocabulary-llm-filter`.
6. `clean-code-refine` and `fp-refine` route between each other when one
   concern should veto the other.
7. `system-memory-audit` routes named-process longitudinal analysis to
   `memleak-investigate`; `check-antipatterns` routes completed sessions to
   `analyze-conversation`.
8. `frame-goals-constraints` is an explicit semantic source for `humanize`.

These relationships prove that composition is useful, but every composer
currently invents its own calling convention.

## Ranked composition gaps

### Critical

1. **No function signature.** Skills do not declare input and output schemas,
   cardinality, provenance, failure types, determinism, or recovery. A caller
   cannot prove that one skill's output satisfies another's input.
2. **No authority-safe composition rule.** The catalog records effects and a
   few approval boundaries but cannot prove that a child remains within the
   parent's ceiling or that an adapter enforces the declared effect.
3. **No compatibility contract.** There is no rule for additive, breaking, or
   authority-expanding skill changes, no edge schema digest, and no lockfile
   for in-flight compositions.
4. **No governed agent-dispatch adapter.** MetaBuilder treats worker output as
   a claim and production fresh generation fails closed without an externally
   enforced spend ceiling. A prose skill cannot bridge that boundary.

### High

5. **The framing pipeline has no shared artifact.** Product thesis, grilling
   record, charter, DAG, and MetaBuilder brief overlap semantically but cannot
   be joined without manual rewriting and lost provenance.
6. **No recipe or pack abstraction.** Users must know which skills belong in a
   long-horizon harness. Completeness should mean that every required role and
   evidence obligation is present, not that all 48 skills are loaded.
7. **Human approval is structurally bound but unauthenticated.** Current
   MetaBuilder receipts bind content and stage; they do not prove who approved
   a decision. Authority-expanding transitions need a trusted verifier.
8. **No composition linter.** Explicit skill calls, catalog entries, effects,
   references, runtime exclusions, and actual installed copies are checked by
   separate tools and conventions.

### Medium

9. **Diagram paths are fragmented.** `archdiagram`,
   `diagram-review-viewer`, and MetaBuilder diagram receipts have related but
   distinct semantics. Only MetaBuilder can produce a gate-bound review
   bundle, and there is no typed adapter from the general diagram skills.
10. **Learning loops are disconnected.** MetaBuilder retrospectives,
    `check-antipatterns`, `analyze-conversation`, `postmortem`, Pi defect
    harvesting, and the system friction ledger do not share a learning record
    or promotion contract.
11. **Catalog shape is inconsistent.** Some entries use `effect`, some also use
    `effects`; not every package skill declares a layer; overlaps mix mutual
    exclusion, shared backend, and composition candidates.
12. **Specialized skills are islands.** Writing, repository safety, memory
    diagnosis, UI implementation, and vocabulary curation have useful local
    sequences but no generic artifact or verification envelope.

## Proposed callable contract

A skill directory may expose one or more phase-sized callable units. A phase is
the right boundary when it has one meaningful result, one effect and authority
envelope, and one retry/recovery policy. A whole skill may be a composite;
direct commands remain lower-level actions.

Each Skill Contract should declare:

| Concern | Required contract |
| --- | --- |
| Identity | Stable unit name, schema and semantic version, guidance digest, contract digest, adapter digest. |
| Inputs | Schema digest, required fields, cardinality, size bounds, provenance, and whether each value is an artifact, observation, claim, or human decision. |
| Outputs | Schema digest, cardinality, size bounds, artifact identity, and epistemic class: claim, diagnostic, controller evidence, or rendering. |
| Preconditions | Source identity, prior stages, approvals, toolchains, platforms, and accepted contract versions. |
| Failures | Invalid input, denied effect, conclusive failure, timeout, cancellation, ambiguous `Unknown`, retryability, and recovery operation. |
| Effects | Filesystem, process, network, credential, model, external-state, install, Git, release, and deployment effects with an enforcing adapter. |
| Determinism | Pure or effectful status, canonical serialization, replay inputs, observed nondeterminism, and clock/randomness rules. |
| Resources | Time, processes, bytes, storage, concurrency, retries, epochs, tokens, and hard monetary ceiling. |
| Authority | Author, harness author, controller, runtime, human gates, revocation, and expiry. |
| Evidence | Acceptance checks, artifact provenance, journal events, qualification corpus, and report boundary. |

Compatibility should be structural and monotonic:

- Exact schema match or an explicit versioned lossless adapter is required.
- Effect, authority, confinement, resource, recovery, cardinality, or output
  meaning widening is breaking.
- An authority-expanding delta requires human ratification even when its data
  schema is backward compatible.
- In-flight runs remain pinned to exact contract, module, bundle, policy, and
  adapter digests.
- Replay reuses the persisted observation; it never silently reruns a
  nondeterministic provider.

## MetaBuilder's role

MetaBuilder already has most of the correct runtime substrate:

- Harness Module v2 admission and deterministic bundle compilation;
- static sequence, choice, parallel, race, join, wait, workflow reference, and
  bounded repeat control flow;
- capability brokerage, effect preview, sandboxed direct commands, declared
  file outputs, durable attempts, `Unknown`, recovery, replay, evidence, and
  qualification;
- controller-owned worker and epoch retrospectives; and
- a separate maintainer-only bounded self-improvement campaign.

MetaBuilder should own generic contract admission, static composition,
compatibility checking, capability intersection, durable execution, recovery,
replay, and evidence. It should not learn the semantics of 48 named skills.
The repository should own skill meaning, contracts, recipes, target checks, and
consumer judgment.

The proposed focused architecture is in
[`metabuilder-autonomy-components.mmd`](metabuilder-autonomy-components.mmd).

The simplest user-facing shape is a repository-owned recipe plus a generic
MetaBuilder frontend, conceptually:

```text
metabuilder harness compose --catalog <skill-contracts> \
  --recipe long-horizon-local --out harness.module.json
metabuilder harness update --input harness.module.json \
  --catalog <new-contracts> --check
```

These commands are interface sketches, not current CLI claims. The recipe
selects required roles and contracts; the compiler produces the ordinary
Harness Module and bundle. Updating means re-resolving compatible contracts,
showing the exact delta, and refusing effect or authority widening without the
required decision.

## Supervisor arbitration after the Luna grilling

The speculative review used separate Luna griller and respondent roles over
two rounds. The supervisor's decisions are:

1. **Unit:** use phase-sized Skill Contracts; represent a whole skill as one
   unit only when it truly has one outcome and one envelope.
2. **Dispatch:** model future agent dispatch as an effectful runtime intent,
   but treat its output as a claim. Keep it out of the first slice.
3. **Topology:** use current static composition and bounded runtime controls.
   A supervisor may admit a separate future run; dynamic child harnesses are
   not required for the first product.
4. **Compatibility:** combine exact schema digests with semantic change class
   and monotonic effect, authority, confinement, recovery, and resource checks.
5. **Human boundary:** define a pluggable approval-verifier interface, but do
   not let current unauthenticated actor labels cross authority-expanding gates.
6. **Profile:** keep the initial read-only, no-network profile exact. Add new
   versioned profiles only after their adapters and denial/recovery tests exist.
7. **Completeness:** ship recipes that cover required roles, evidence, and stop
   rules; never load every skill merely to claim completeness.

## First vertical slice

Use the explicit `autonomy-loop` to `autonomous-execution-contract` chain.

1. Define the phase contract schema and add contracts for those two skills.
2. Add a `long-horizon-local` static recipe and composition lock.
3. Hand-author or deterministically compose one Harness Module containing the
   outer controller phase, one bounded executor phase, and one local read-only
   direct command with a declared output.
4. Prove typed transfer, malformed-input refusal, incompatible-version
   refusal, capability denial, timeout and legal retry, interruption after
   intent persistence, `Unknown` recovery without redispatch, stale human
   intervention refusal, artifact provenance, and byte-stable replay.
5. Invalidate qualification when module, bundle, policy, adapter, reporter, or
   evidence identity changes.
6. Accept one explicit additive-compatible update and refuse one narrowed-input
   or effect-widening update.
7. Run the focused proof twice from unchanged source.

This slice proves the composition substrate. It does not prove that a real
agent can be safely dispatched, that consumer unattended loops are supported,
or that fresh generation is active.

## Rollout and stop rules

| Phase | Outcome | Rough effort | Stop boundary |
| --- | --- | --- | --- |
| 0. Contract registry | Schema, all-skill inventory, explicit edges, linter, MetaBuilder catalog entry | 2–4 focused days | Stop if phase boundaries cannot be stated without mixing effects or authority. |
| 1. Static vertical slice | One recipe compiled and qualified through current local runtime | 1–2 focused weeks | Zero tolerance for unauthorized effects, replay mismatch, forged/stale admission, or blind redispatch. |
| 2. Broader local recipes | Git, diagnostics, writing, and UI families with typed artifacts | 2–4 focused weeks | Stop after three repeated ordinary proof failures or any contract ambiguity that changes meaning. |
| 3. Agent claim adapter | Exact-route dispatch, external hard spend ceiling, usage evidence, controller verification | Separate ratified epic | Preparation-only until the external ceiling and recovery contract are mechanically enforced. |
| 4. Profile expansion | Versioned network, credential, or target-write profiles | Separate ratified epics | Refuse any effect without an enforcing adapter and independent adversarial qualification. |

Immediately invalidate a composed qualification for an unauthorized effect,
accepted forged or stale receipt, replay mismatch, blind `Unknown` redispatch,
identity mismatch, missing provenance, unratified authority expansion, or an
agent-generated statement accepted as human approval. Preserve the failed run
and evidence; return to the last qualified bundle instead of erasing history.

MetaBuilder's current autonomous self-improvement epic is complete, and its
checkpoint explicitly requires the principal to ratify the next epic. This
audit therefore recommends the next bounded product direction but does not
authorize implementation in the MetaBuilder repository.
