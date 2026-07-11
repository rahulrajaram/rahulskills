---
name: invokellm
description: "Invoke one or more AI CLIs (gemini, claude, codex) via gptengage. Use when the user asks to invoke, query, or prompt a specific LLM CLI, compare multiple CLIs, consult gemini/claude/codex together, or says /invokellm."
argument-hint: "[cli[,cli...]] <prompt> [--model MODEL] [--session NAME] [--context-file FILE] [--timeout SECS] [--write]"
---

# Invoke LLM

Follow the shared
[`../../references/gptengage-invocation.md`](../../references/gptengage-invocation.md)
contract before invoking a backend.

Invoke one or more AI CLI tools through gptengage.

## Autonomy Routing

This skill delegates work; it does not transfer responsibility away from the
orchestrating agent. Invoke the requested CLI(s), then inspect and integrate the
result when the user asked for execution. If the subprocess cannot write, times
out, or returns only a plan, continue locally when the next engineering step is
clear. Do not ask whether to use `/goal`, Yarli, or direct execution unless that
choice changes safety, shared state, durability, or user-visible behavior.

## Workflow

1. Parse user arguments.
Extract:
- `[CLI]` — optional CLI selector: `gemini`, `claude`, `codex`, a comma-separated list of them, or a plugin name.
- `[PROMPT]` — the prompt to send.
- Any optional flags (--model, --session, --context-file, --timeout, --write).

If no CLI is specified, default to consulting `gemini`, `claude`, and `codex`
in that order.

Treat the first positional token as a CLI selector only if it clearly matches a
known CLI, a comma-separated CLI list, or plugin syntax. Otherwise, treat the
input as the prompt and use the default trio.

2. Run the invocation.

Always invoke through `~/.local/bin/gptengage invoke`. Do not call `codex`,
`claude`, or `gemini` directly from this skill.

Default to `--timeout 600` unless the user explicitly provides a different
timeout. Pass that timeout to `gptengage` itself.

A bare outer shell wrapper such as `timeout 600 codex ...` is ineffective for
this purpose. It only caps total wall-clock runtime and does **not** change
`gptengage`'s internal per-invocation timeout, which otherwise defaults to 120
seconds. Likewise, `timeout 600 ~/.local/bin/gptengage invoke ...` without
`--timeout 600` is still wrong for this skill.

If you add an outer shell timeout as a secondary watchdog, keep it larger than
the inner `gptengage --timeout` value.

For a single CLI:

```bash
~/.local/bin/gptengage invoke <CLI> "<PROMPT>" --timeout 600 [OPTIONS] 2>&1
```

For the default multi-CLI consultation, run the same prompt separately for each
CLI and preserve any other user-provided options:

```bash
for cli in gemini claude codex; do
  ~/.local/bin/gptengage invoke "$cli" "<PROMPT>" --timeout 600 [OPTIONS] 2>&1
done
```

Optional outer watchdog:

```bash
timeout 660 ~/.local/bin/gptengage invoke <CLI> "<PROMPT>" --timeout 600 [OPTIONS] 2>&1
```

3. Display the result to the user.

If multiple CLIs were consulted, label each result clearly by CLI.

## Options Reference

| Flag | Description | Example |
|------|-------------|---------|
| `-m, --model MODEL` | Model override | `--model gpt-4o` |
| `-s, --session NAME` | Persistent conversation session | `--session auth-review` |
| `-c, --context-file FILE` | File to include as context | `--context-file src/main.rs` |
| `-t, --timeout SECS` | Timeout in seconds (default: 600 in this skill) | `--timeout 600` |
| `--write` | Allow write access in current directory | |
| `--stdin-as auto\|context\|ignore` | How to interpret piped stdin | `--stdin-as context` |

## Examples

```bash
# Default 3-way consultation
/invokellm "Review this design"

# Simple single-CLI invocation
/invokellm claude "Explain quantum computing"

# Explicit multi-CLI invocation
/invokellm gemini,claude,codex "Compare these approaches"

# With model override
/invokellm codex "Review this code" --model gpt-4o

# With session persistence
/invokellm claude "Review auth code" --session auth-review
/invokellm claude "Fix the JWT bug" --session auth-review

# With context file
/invokellm "Analyze this" --context-file src/main.rs
```

## Guardrails

- Pass all user arguments through to gptengage directly.
- Never invoke `codex`, `claude`, or `gemini` directly from this skill.
- If the user specifies one CLI, do not also invoke the default trio.
- If consulting multiple CLIs, keep the prompt identical across them.
- Never rely on a bare outer `timeout` wrapper to replace `--timeout`.
- If the command fails, report the error and suggest running `gptengage status` to check CLI availability.
- Do not invent or modify the user's prompt.
