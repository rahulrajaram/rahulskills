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

For consumer work, use the installed CLI and verify its current public surface
before authoring artifacts:

```bash
command -v metabuilder
metabuilder --help
metabuilder harness --help
metabuilder qualify guide
```

The current consumer surface includes `metabuilder harness brief` and
`metabuilder qualify`. If the installed binary lacks either family, stop and
report installation drift. Do not fall back to a hidden legacy command. Do not
substitute an uncommitted development binary unless the MetaBuilder maintainer
has explicitly admitted and identified those exact bytes.

Do not infer authority from this skill or the README.

## Route the lifecycle

Use the companion skills as the detailed operating procedures:

1. For a new objective without an agreed Harness Module, read and follow
   [metabuilder-harness-design](../metabuilder-harness-design/SKILL.md). It owns
   repository discovery, thorough grilling, exact brief agreement, typed
   intent, executable module design, compilation, and bundle re-admission.
2. After design produces an exact admitted bundle, read and follow
   [metabuilder-consumer-qualification](../metabuilder-consumer-qualification/SKILL.md).
   It owns execution, recovery, evidence assessment, attestations, and the
   qualification report without changing the approved design.
3. If an already agreed module and bundle are supplied, begin at consumer
   qualification. If qualification exposes a design gap, return upstream; do
   not repair the design silently.
4. When modifying MetaBuilder itself, use the repository-local
   `metabuilder-rust-functional-core` skill and repository authority. That
   maintainer discipline is not part of a target project's consumer workflow.

Design states what should be tested. The Harness Module commits to executable
checks. Qualification records what the controller observed and leaves semantic
adequacy to the consumer. No layer alone proves production readiness.

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
