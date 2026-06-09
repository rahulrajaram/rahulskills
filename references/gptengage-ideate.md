# GPTEngage ideate recipe

Use this recipe only for `gptengage ideate`.

## Inputs and limits

- Syntax: `gptengage ideate <SEED> [OPTIONS]`.
- Defaults are sigma 1, depth 2, and the Claude backend.
- Normal sigma is 0-3 and normal depth is 1-5. Values above either safety limit
  require `--force` and explicit user intent.
- `--select` requires an interactive selection path.
- Output is `text` or `json`; validate JSON before programmatic use.

Supported options are `--sigma`, `--depth`, `--cli`, `--select`, `--force`,
`--output`, `--timeout`, `--color`, and `--pager`. Validate them against current
`gptengage ideate --help`.

## Command shape

```text
~/.local/bin/gptengage ideate SEED [OPTIONS]
```

Each level expands the idea tree, so external calls and cost grow
exponentially with depth. Prefer a shallow tree unless the user requested broad
exploration. Treat incomplete expansion as partial output rather than a fully
successful tree.
