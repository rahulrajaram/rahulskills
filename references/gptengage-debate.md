# GPTEngage debate recipe

Use this recipe only for `gptengage debate`.

## Inputs and validation

- Syntax: `gptengage debate <TOPIC> [OPTIONS]`.
- Choose at most one participant source: `--agent` with optional `--instances`,
  `--participants`, `--agent-file`, or `--template`.
- `--instances` and `--model` require `--agent`.
- `--synthesizer` matters only with `--synthesize`.
- Preserve the default of three rounds unless the user supplied `--rounds` or a
  template provides its own default.

Supported option families include participant selection, rounds, output,
per-invocation timeout, stdin policy, explicit write access, and synthesis.
Validate the selected combination against current `gptengage debate --help`.

## Command shape

```text
~/.local/bin/gptengage debate TOPIC [OPTIONS]
```

`--timeout` applies to each child CLI invocation, not the entire debate. An
outer watchdog must account for participants, rounds, and optional synthesis.
Call count grows with those choices, and synthesis adds another external call.

When structured output is requested, validate it before summarizing or feeding
it into later work. Report individual backend failure separately from failure
of the debate orchestration.
