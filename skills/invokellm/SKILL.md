---
name: invokellm
description: "Invoke one or more AI CLIs through gptengage. Use when the user asks to consult, query, or compare Claude, Codex, Gemini, or a plugin, or says /invokellm or $invokellm."
argument-hint: "[cli[,cli...]] <prompt> [--model MODEL] [--session NAME] [--context-file FILE] [--timeout SECS] [--write]"
---

# Invoke LLM

Read the shared
[`../../references/gptengage-invocation.md`](../../references/gptengage-invocation.md)
contract and the selected
[`../../references/gptengage-invoke.md`](../../references/gptengage-invoke.md)
recipe before calling a backend.

## Workflow

1. Parse the CLI selector, prompt, and supported options using the operation
   recipe. Treat the first token as a selector only when it names a known CLI,
   comma-separated CLI list, or plugin.
2. Default to `gemini`, `claude`, then `codex` when no selector is present.
   Invoke each separately with the identical prompt and applicable options.
3. Resolve the authorized existing `gptengage` executable and run only its
   `invoke` operation. Default the inner
   `--timeout` to 600 seconds unless the user supplied one.
4. Label multi-CLI results by backend, inspect failures and malformed output,
   and integrate the results into the user's requested work.

## Boundaries

- One requested CLI suppresses the default trio; never silently substitute a
  different backend.
- A session persists full conversation turns and must be deliberately named.
- `--write` requires explicit write intent and grants no remote-write authority.
- Never change the prompt merely to make backends agree.
