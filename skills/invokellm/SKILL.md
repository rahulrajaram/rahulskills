---
name: invokellm
description: "Invoke a single AI CLI (claude, codex, gemini) via gptengage. Use when the user asks to invoke, query, or prompt a specific LLM CLI, or says /invokellm."
---

# Invoke LLM

Invoke a single AI CLI tool through gptengage.

## Workflow

1. Parse user arguments.
Extract:
- `<CLI>` — which CLI to invoke: claude, codex, gemini, or a plugin name.
- `[PROMPT]` — the prompt to send.
- Any optional flags (--model, --session, --context-file, --timeout, --write).

2. Run the invocation.

```bash
~/.local/bin/gptengage invoke <CLI> "<PROMPT>" [OPTIONS] 2>&1
```

Use `timeout 180` wrapper for safety:

```bash
timeout 180 ~/.local/bin/gptengage invoke <CLI> "<PROMPT>" [OPTIONS] 2>&1
```

3. Display the result to the user.

## Options Reference

| Flag | Description | Example |
|------|-------------|---------|
| `-m, --model MODEL` | Model override | `--model gpt-4o` |
| `-s, --session NAME` | Persistent conversation session | `--session auth-review` |
| `-c, --context-file FILE` | File to include as context | `--context-file src/main.rs` |
| `-t, --timeout SECS` | Timeout in seconds (default: 120) | `--timeout 180` |
| `--write` | Allow write access in current directory | |
| `--stdin-as auto\|context\|ignore` | How to interpret piped stdin | `--stdin-as context` |

## Examples

```bash
# Simple invocation
~/.local/bin/gptengage invoke claude "Explain quantum computing"

# With model override
~/.local/bin/gptengage invoke codex "Review this code" --model gpt-4o

# With session persistence
~/.local/bin/gptengage invoke claude "Review auth code" --session auth-review
~/.local/bin/gptengage invoke claude "Fix the JWT bug" --session auth-review

# With context file
~/.local/bin/gptengage invoke gemini "Analyze this" --context-file src/main.rs
```

## Guardrails

- Pass all user arguments through to gptengage directly.
- If the command fails, report the error and suggest running `gptengage status` to check CLI availability.
- Do not invent or modify the user's prompt.
