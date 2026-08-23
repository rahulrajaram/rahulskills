---
name: debate
description: "Run a structured multi-AI debate through gptengage. Use when the user asks for debate or multi-model deliberation, or says /debate or $debate."
argument-hint: "<topic> [--rounds N] [--participants \"cli:persona,...\"] [--agent CLI] [--synthesize]"
---

# Debate

Read the shared
[`../../references/gptengage-invocation.md`](../../references/gptengage-invocation.md)
contract and the selected
[`../../references/gptengage-debate.md`](../../references/gptengage-debate.md)
recipe before calling a backend.

## Workflow

1. Parse the topic and debate options, validating participant selection and
   dependent flags with the operation recipe.
2. Run only through `~/.local/bin/gptengage debate`, passing an inner
   per-invocation timeout when the user supplied one.
3. Capture the full debate, distinguish orchestration failures from individual
   backend failures, and return or integrate the requested output format.

## Boundaries

- Rounds, participant count, and synthesis increase external calls and cost;
  synthesis is an additional backend call.
- `--write` requires explicit write intent and grants no remote-write authority.
- An outer watchdog is only a secondary limit and must allow for the full
  multi-round orchestration, not merely one backend timeout.
- Never invent participants, personas, or a different topic.
