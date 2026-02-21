---
argument-hint: <topic> [--rounds N] [--participants "cli:persona,..."] [--agent CLI] [--synthesize]
description: Run a multi-AI debate (Claude + Codex + Gemini) via gptengage
---

# GPT Debate

**Arguments:** $ARGUMENTS

## Instructions

Run the `gptengage debate` command with the user's arguments. Pass all arguments through directly.

```bash
~/.local/bin/gptengage debate $ARGUMENTS 2>&1
```

### Argument Reference

- `<TOPIC>` - The debate topic
- `--rounds N` - Number of rounds (default: 3)
- `--agent CLI` - Use a single CLI for all participants (with `--instances N`)
- `--instances N` - Number of instances when using --agent (default: 3)
- `--model MODEL` - Model override (requires --agent)
- `-p, --participants "cli:persona,..."` - Participants with optional personas
- `--agent-file FILE` - JSON agent definitions (from generate-agents)
- `--template NAME` - Use a predefined template
- `--output text|json|markdown` - Output format (default: text)
- `--timeout SECS` - Timeout per invocation (default: 120)
- `--write` - Allow write access in current directory
- `--synthesize` - Generate a synthesis after debate
- `--synthesizer CLI` - CLI for synthesis (default: claude)

### Examples

```bash
# Default 3-way debate
~/.local/bin/gptengage debate "Should we migrate to microservices?"

# With personas
~/.local/bin/gptengage debate "Tech stack" -p "claude:CTO,codex:Architect,gemini:PM"

# Multi-instance Claude debate
~/.local/bin/gptengage debate "Code review strategy" --agent claude --instances 3

# 5 rounds with synthesis
~/.local/bin/gptengage debate "REST vs GraphQL" --rounds 5 --synthesize
```

### Execution

1. Run the command via Bash with a timeout of 600 seconds (debates are long-running)
2. Stream/display the full output to the user
3. If the command fails, show the error and suggest checking `gptengage status`
