# Harness design workflow

Use this reference while producing a new brief and translating it into a
MetaBuilder program. Repository policy and the CLI remain authoritative.

## 1. Establish the frame

Record these before solutioning:

| Item | Required content |
| --- | --- |
| Request | The user's exact requested change or outcome |
| Target | Repository path, commit, tree, and dirty-state observation |
| Actors | Consumer, product owner, technical owner, controller, approvers |
| Stops | Unauthorized effects, destructive work, unavailable infrastructure, repeated proof failure |
| Success | Observable target behavior and the evidence needed to assess it |

Do not silently merge roles. A controller can prove what it admitted and
observed; it cannot take over the consumer's judgment that a check is adequate.

## 2. Inspect recoverable evidence

Read applicable repository instructions and inspect the exact source before
asking questions already answered locally. Capture:

- source identity and cleanliness;
- build, test, lint, typecheck, and packaging commands;
- public interfaces and compatibility requirements;
- state, recovery, replay, concurrency, and failure behavior;
- required System or Rustup toolchains;
- declared outputs and any repository-local auxiliary directories;
- permissions and effects implied by each candidate command; and
- known gaps, unsupported conditions, and manual review needs.

Do not install tools, access credentials, mutate the target, or broaden the
effect boundary during discovery. An agent's summary or a web page may inform
design, but neither becomes controller-owned execution evidence.

## 3. Maintain a typed finding ledger

Classify each material statement:

| Class | Meaning | Required annotation |
| --- | --- | --- |
| Fact | Recoverably observed | Source path, command output, or cited source |
| Assumption | Temporarily accepted proposition | Owner, impact, review trigger |
| Preference | Reversible design choice | Owner and tradeoff |
| Unknown | Unresolved material question | Owner and resolution path |
| Decision | Choice that fixes product or technical behavior | Exact approval evidence |

Resolve technical questions with evidence when possible. Route genuine product
choices to the product owner. Fresh generation cannot continue with a material
open unknown; an owned assumption is acceptable only when its impact and
revisit trigger are explicit.

## 4. Grill and prepare the brief

The grilling record must cover goals, constraints, risks, success criteria,
actors, and material unknowns. Include non-goals, effect boundaries, negative
behavior, recovery, and evidence adequacy when they affect the design.

Start from the installed executable surface:

```bash
metabuilder harness brief template > harness-brief.candidate.json
```

Edit every field. Replace zero digest placeholders with SHA-256 digests of the
exact records they cite. A digest binds bytes; it does not authenticate a human
or upgrade an answer into effect authority.

Prepare and inspect without overwriting the candidate:

```bash
metabuilder harness brief prepare \
  --input harness-brief.candidate.json > harness-brief.prepared.json
metabuilder harness brief inspect --input harness-brief.prepared.json \
  > harness-brief.inspection.json
```

The inspection returns `brief_digest` and structural gate refusals. Resolve all
refusals, then ask each `agreement_required` actor to review that exact digest.
Create an approval request shaped as:

```json
{
  "schema_version": 1,
  "controller_id": "controller",
  "approvals": [
    {
      "actor_id": "principal",
      "brief_digest": "<prepared brief_digest>",
      "evidence_digest": "<digest of exact approval record>"
    }
  ]
}
```

Finalize and verify:

```bash
metabuilder harness brief finalize \
  --input harness-brief.prepared.json \
  --approvals harness-brief.approvals.json > harness-brief.agreed.json
metabuilder harness brief check --input harness-brief.agreed.json
```

The receipt proves structural binding under the controller contract. It is not
cryptographic proof of real-world reviewer identity.

## 5. Translate meaning into typed intent

Apply these mappings:

| Brief/domain concept | `defineIntent` construct |
| --- | --- |
| Desired deliverable or change | `achieve` |
| Independently assessable claim | `establish` |
| Canonical data crossing obligations | `artifact` plus `produces`/`consumes` |
| Required order | `sequence` |
| Independent work with no sibling dependency | `parallel` |
| Controller-selected alternative | `caseOf` |
| Observed prerequisite | `waitUntil` |
| Bounded convergence | `repeatUntil` |
| Reviewable execution phases | root `stages` |
| Completion | `established` naming an unconditional assurance |

Use `verification` when an assurance must name exact subject artifact(s) and a
separate evidence artifact. Never put shell, argv, toolchains, providers,
credentials, grants, ambient paths, or runtime retries in intent source.

Run `metabuilder intent check --input intent.mb.ts --json`. A valid report says
`executable: false` and `construction_approved: false`; that is the expected
authority-free state.

## 6. Commit to an executable module

For a hand-authored consumer module, begin with
`metabuilder qualify template --kind module`. Preserve the agreed meaning while
adding implementation commitments:

- each requirement states one claim and cites all sufficient evidence actions;
- each direct command uses an argv array, normalized cwd, explicit System or
  Rustup toolchain, and bounded timeout;
- canonical cross-step data is a declared file, not standard output;
- output paths and byte ceilings are explicit;
- ignored or untracked repository-local inputs use separately observed,
  digest-bound auxiliary-directory declarations;
- the typed workflow preserves ordering, parallelism, choices, waits, repeats,
  and acceptance dependencies; and
- bounds and logical worker/epoch retrospectives remain explicit.

Compile and check the exact bytes. Generated implementation is a separate path:
follow `docs/define-intent-lifecycle.md`, and do not dispatch a provider without
an exact authorized route and enforced spend ceiling.

## 7. Preflight and hand off

For each action, record required reads, writes, process execution, toolchains,
network, credentials, external state, and irreversible effects. Compare those
requirements with the controller's admitted ceiling. Refuse any mismatch.

After `harness compile` and `harness check` both succeed, hand the artifacts to
`metabuilder-consumer-qualification`. Preserve limitations and untested
conditions; do not translate structural validity into production readiness.
