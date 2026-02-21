---
argument-hint: <cli> <prompt> [--model MODEL] [--session NAME] [--context-file FILE] [--timeout SECS] [--write]
description: Invoke a single AI CLI (claude, codex, gemini) via gptengage
---

# GPT Invoke

**Arguments:** $ARGUMENTS

## Instructions

Run the `gptengage invoke` command with the user's arguments. Pass all arguments through directly.

```bash
~/.local/bin/gptengage invoke $ARGUMENTS 2>&1
```

### Argument Reference

- `<CLI>` - Which CLI: claude, codex, gemini, or a plugin name
- `[PROMPT]` - The prompt to send
- `--model MODEL` - Model override (e.g., claude-sonnet-4-20250514, gpt-4o, gemini-2.5-pro)
- `--session NAME` - Persistent conversation session
- `--context-file FILE` - File to include as context
- `--timeout SECS` - Timeout in seconds (default: 120)
- `--write` - Allow write access in current directory

### Examples

```bash
# Simple invocation
~/.local/bin/gptengage invoke claude "Explain this code"

# With model override
~/.local/bin/gptengage invoke codex "Review code" --model gpt-4o

# With session persistence
~/.local/bin/gptengage invoke claude "Review auth code" --session auth-review

# With context file
~/.local/bin/gptengage invoke gemini "Analyze" --context-file src/main.rs
```

### Execution

1. Run the command via Bash with a timeout of 180 seconds
2. Display the full output to the user
3. If the command fails, show the error and suggest checking `gptengage status`
