# GPTEngage invoke recipe

Use this recipe only for `gptengage invoke`.

## Inputs and routing

- Syntax: `gptengage invoke <CLI> <PROMPT> [OPTIONS]`.
- Supported selectors include `claude`, `codex`, `gemini`, and installed plugin
  names. The `invokellm` wrapper also accepts a comma-separated list.
- When the wrapper receives no selector, invoke `gemini`, `claude`, then
  `codex` separately with the same prompt and applicable options.
- Treat the first positional token as a selector only when it clearly matches a
  known CLI, CLI list, or plugin; otherwise it begins the prompt.

## Operation options

Forward only parsed options supported by current help: `--model`, `--session`,
`--topic`, `--context-file`, repeatable `--image`, `--timeout`, `--write`, and
`--stdin-as auto|context|ignore`. Images currently work only with backends that
implement image passthrough.

The wrapper's inner timeout defaults to 600 seconds, overriding the CLI's
120-second default. If an outer watchdog is useful, make it longer than the
inner timeout.

## Command shape

```text
~/.local/bin/gptengage invoke CLI PROMPT --timeout SECONDS [OPTIONS]
```

For multiple CLIs, construct and execute one argument vector per CLI. Label
each result and keep the prompt identical. Call count equals the selected
backend count.
