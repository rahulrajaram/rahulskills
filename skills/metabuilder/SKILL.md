---
name: metabuilder
description: "Use MetaBuilder to design, agree, compile, inspect, run, qualify, recover, or improve a governed engineering harness. This is the global entry point for building a new harness in an arbitrary target repository and routes fresh design through metabuilder-harness-design before metabuilder-consumer-qualification."
---

# Use MetaBuilder

## Start

1. Locate the existing MetaBuilder checkout. Use the path supplied by the user
   or current workspace. Do not clone or install another copy.
2. Read the MetaBuilder root `README.md` completely.
3. Read every authority file that the README lists.
4. Read the target repository's instructions and current state.
5. State the target, exact objective, acceptance evidence, effects, bounds,
   source identity, and stop conditions.

For consumer work, resolve the installed CLI and inspect the help and guide
needed by the selected phase before authoring artifacts:

```bash
command -v metabuilder
metabuilder --help
metabuilder harness --help
metabuilder qualify --help
metabuilder qualify guide
```

The public consumer journeys are `harness`, `intent`, `qualify`, and `run`.
Use scoped help for exact operations and effects. Qualification templates and
reports use `metabuilder qualify template|guide|prepare|report|check`.
Local CLI help and `crates/mb-core/src/bin/mb/command_surface.rs` verified this
mapping on 2026-09-06: `harness qualification ...` is a hidden compatibility
alias, not the canonical recipe. Maintainer generation uses
`harness generation create|check`; it is not an ordinary consumer shortcut.
If a required operation is absent, report the affected capability as unavailable
and continue independent authorized preparation. Do not install tooling or
substitute an uncommitted development binary without the requisite explicit
authority and identification of those exact bytes.

Carry the resolved executable identity, relevant help/guide evidence, and
still-valid authority context through companion-skill handoffs. Recheck when
the executable, needed operation, environment, or applicable constraints
change; switching skills alone does not require repeating discovery.

Do not infer authority from this skill or the README.

## Route the lifecycle

Use the companion skills as the detailed operating procedures:

1. For a new objective without an agreed Harness Module, read and follow
   [metabuilder-harness-design](../metabuilder-harness-design/SKILL.md). It owns
   repository discovery, provisional design, remaining material questions, exact
   brief agreement, typed intent, executable module design, compilation, and
   bundle re-admission.
2. Before authoring any module whose actions must actually execute under
   `run workflow apply`, verify the current confinement profile against the
   installed qualification guide and MetaBuilder source. Account explicitly
   for no network, the 4 GiB address-space limit, a read-only workspace,
   tmpfs-backed `/tmp`, a fixed environment, the admitted toolchain surface,
   auxiliary-directory rules, and a run root outside the target repository.
   If an already-installed `metabuilder-sandbox-runtime` playbook is available,
   use it as operational guidance but revalidate it against the current binary.
3. After design produces an exact admitted bundle, read and follow
   [metabuilder-consumer-qualification](../metabuilder-consumer-qualification/SKILL.md).
   It owns execution, recovery, evidence assessment, attestations, and the
   qualification report without changing the approved design.
4. If an already agreed module and bundle are supplied, verify their identities
   and still-valid decisions, then begin at consumer qualification within the
   requested inspection or execution scope. If qualification exposes a design
   gap, return upstream; do not repair the design silently.
5. When modifying MetaBuilder itself, use the repository-local
   `metabuilder-rust-functional-core` skill and repository authority. That
   maintainer discipline is not part of a target project's consumer workflow.

Design states what should be tested. The Harness Module commits to executable
checks. Qualification records what the controller observed and leaves semantic
adequacy to the consumer. No layer alone proves production readiness.

## Model-first discipline

The first material artifact of any harness campaign is the reviewed PROGRAM
(Harness Module, or the defineIntent source rendition beside it), not target
implementation code. Do not edit target source until the model passes
`harness check` and an independent semantic review against the principal's
hypotheses; record the review (verdict, findings, disposition) beside the
module. MetaBuilder actions acquire no source-mutation authority: when
evidence exposes a defect, make one normal repository repair, commit it,
recompute digests, and author a FRESH run bound to the new commit — never
mutate an old bundle or pretend an old run covers a new tree.

The two authoring surfaces:

- **Hand-authored Harness Module v2/v3 JSON** — the supported consumer route
  (`harness qualification template --kind module` → `harness compile` →
  `harness check`). v3 actions wrap invocations as
  `invocation: {kind: "command"|"external_target"|"mcp_tool"|"agent", ...}`.
- **defineIntent source (`*.mb.ts`)** — the TypeScript-esque meaning layer.
  Validate any rendition with `metabuilder intent check --input X --json`
  (valid:true, executable:false). The FULL source-origin pipeline
  (`harness package create` → `harness generation create` → `intent propose|approve`
  → `lower` → `freeze` → `author`) requires provider dispatch and may incur
  spend. Proceed only under an existing exact provider/data/effect/spend
  authorization; otherwise prepare the concrete request and stop only the
  dependent dispatch. Grammar traps: semantic IDs and
  artifact IDs are kebab-case slugs; object keys containing `-` must be
  quoted strings; verification cannot be mixed with generic
  consumes/produces.

Verify each operation against the current README, CLI help, and code. Do not
assume a planned feature exists or infer an MCP server; MetaBuilder currently
uses its CLI and skills.

## Execute

1. Inspect source identity, run state, and effects before mutation.
2. Declare every required capability.
3. Refuse any effect that lacks an enforced adapter.
4. Prepare an effect before applying it.
5. Preserve `Unknown` after ambiguous outcomes. Reconcile before retrying.
6. Treat worker output as a claim. Admit only controller-owned evidence.
7. Preserve journals, receipts, outputs, and failure evidence.
8. Run the target's checks and MetaBuilder's required checks.

## Improve MetaBuilder through use

Every long-horizon engagement routed here owes the maturation flywheel: before
closing the campaign, file a record for each gap it exposed. Campaign-level
MetaBuilder gaps follow the steps below; tool-ecosystem-level friction also
goes to the friction ledger, and both surface in
`docs/metabuilder-maturity-backlog.md`.

When the target exposes a MetaBuilder gap:

1. Stop the unsupported target operation.
2. Record the missing operation, capability, evidence, and recovery contract.
3. Design a generic typed boundary. Keep target-specific behavior outside the
   MetaBuilder core.
4. Confirm that existing authority covers the MetaBuilder change.
5. Implement MetaBuilder product changes in Rust.
6. Add success, refusal, replay, and ambiguous-outcome tests.
7. Re-run the target harness through the new boundary.

Do not bypass MetaBuilder and describe the result as governed.

The `metabuilder maintain candidate ...` and
`metabuilder maintain improvement ...` command families are maintainer-only.
Do not use them to build or qualify a consumer harness, infer target-write
authority, or create an unattended consumer loop.

## Keep the target separate

- Do not add MetaBuilder as the target's runtime or library.
- Do not force the target to use Rust.
- Do not expose credentials, raw host control, or privileged sockets to workers.
- Do not weaken target policy to fit MetaBuilder.
- Do not delete target files or preserved evidence.

## Report

Report these items separately:

- target work completed and its evidence;
- MetaBuilder changes completed and their tests;
- unsupported effects, unresolved evidence, and the next exact action.
