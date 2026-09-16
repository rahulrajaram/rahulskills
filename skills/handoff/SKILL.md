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

## Claim verification (required)

A handoff's negative claims ("missing", "not done", "still needs") are
assertions about filesystem state and must be checked before publishing.
Run `scripts/validate_handoff_claims.py <draft> --repo <root> --strict`
as part of the write workflow: SUSPECT findings mean a path reported missing
actually exists (stale-claim class, f-2030); UNRESOLVED evidence claims must
gain their evidence path or be rewritten as unverified. Record the validator
exit code in the handoff.

## Boundary with governed harness runs

For work executing inside a MetaBuilder harness, in-run recovery belongs to
the harness's durable attempts and controller observations, not to this file.
Use this skill for the human-facing cross-shell resume: record the harness
run and checkpoint identities in the prompt so the next shell re-enters
through `metabuilder-consumer-qualification` instead of re-deriving state.
