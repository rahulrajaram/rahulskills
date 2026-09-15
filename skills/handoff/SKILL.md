---
name: handoff
description: "Write a verified NEXT_SHELL_PROMPT.md handoff. To activate or resume an existing one instead, use the handoff-extract skill."
argument-hint: ""
---

# Handoff

Use this workflow to write a clean shell handoff. To resume an existing one,
use the `handoff-extract` skill.

## Workflow

Prepare a coherent commit when covered by current authority,
then write a verified continuation artifact; this mode includes commit triage.
Read [references/write-workflow.md](references/write-workflow.md)
completely and run the write workflow.

## Boundary with governed harness runs

For work executing inside a MetaBuilder harness, in-run recovery belongs to
the harness's durable attempts and controller observations, not to this file.
Use this skill for the human-facing cross-shell resume: record the harness
run and checkpoint identities in the prompt so the next shell re-enters
through `metabuilder-consumer-qualification` instead of re-deriving state.
