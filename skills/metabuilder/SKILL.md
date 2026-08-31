---
name: metabuilder
description: "Use MetaBuilder to define, compile, inspect, run, recover, or improve a governed engineering harness. Use when asked to use MetaBuilder, build a harness with MetaBuilder, operate a MetaBuilder run, or check whether MetaBuilder supports a required effect."
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

For consumer work, use the installed CLI and verify its public guidance before
authoring artifacts:

```bash
command -v metabuilder
metabuilder --help
metabuilder harness qualification guide
```

Do not substitute an uncommitted development binary unless the MetaBuilder
maintainer has explicitly admitted and identified those exact bytes.

Do not infer authority from this skill or the README.

## Choose a path

Use the README's current CLI sequence.

- Compile a hand-authored Harness Module when one already exists.
- Use the full grilling, brief, diagram, package, and generation path for a
  fresh harness only when current repository authority has activated that
  path. If the README says fresh generation is deferred, hand-author a Harness
  Module for qualification or stop at the unsupported boundary.
- Use status, preview, effects, prepare, apply, monitor, and recover for an
  active run.

Verify each operation against the current README, CLI help, and code. Do not
assume a planned feature exists.

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

The `metabuilder self-host candidate ...` and
`metabuilder self-improvement ...` command families are maintainer-only. Do
not use them to build or qualify a consumer harness, infer target-write
authority, or create an unattended consumer loop. Use the repository-local
`metabuilder-consumer-qualification` skill for consumer assessment.

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
