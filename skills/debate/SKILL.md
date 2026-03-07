---
name: debate
description: "Run a multi-AI debate (Claude + Codex + Gemini) via gptengage. Use when the user asks for a debate, multi-AI discussion, or says /debate."
---

# Debate

Run a structured multi-AI debate through gptengage.

## Workflow

1. Parse user arguments.
Extract:
- `<TOPIC>` — the debate topic.
- Any optional flags (--rounds, --participants, --agent, --instances, --model, --agent-file, --template, --output, --timeout, --write, --synthesize, --synthesizer).

2. Run the debate.

```bash
~/.local/bin/gptengage debate "<TOPIC>" [OPTIONS] 2>&1
```

Use `timeout 600` wrapper since debates are long-running:

```bash
timeout 600 ~/.local/bin/gptengage debate "<TOPIC>" [OPTIONS] 2>&1
```

3. Display the full output to the user.

## Options Reference

| Flag | Description | Example |
|------|-------------|---------|
| `-r, --rounds N` | Number of rounds (default: 3) | `--rounds 5` |
| `--agent CLI` | Single CLI for all participants | `--agent claude` |
| `--instances N` | Number of instances with --agent | `--instances 3` |
| `-m, --model MODEL` | Model override (requires --agent) | `--model claude-sonnet-4-20250514` |
| `-p, --participants` | Participants with personas | `-p "claude:CTO,codex:Architect"` |
| `--agent-file FILE` | JSON agent definitions | `--agent-file agents.json` |
| `--template NAME` | Predefined template | `--template code-review` |
| `-o, --output FORMAT` | Output: text, json, markdown | `--output json` |
| `-t, --timeout SECS` | Timeout per invocation (default: 120) | `--timeout 180` |
| `--write` | Allow write access in current directory | |
| `--synthesize` | Generate synthesis after debate | |
| `--synthesizer CLI` | CLI for synthesis (default: claude) | `--synthesizer codex` |

## Participant Formats

**No personas (default):** Claude, Codex, and Gemini debate without assigned roles.

**With personas:** `-p "cli:persona,cli:persona,..."`
```
-p "claude:CTO,claude:Architect,codex:Engineer"
-p "claude:Security Expert,gemini:UX Designer"
-p "claude:CEO:claude-sonnet-4-20250514,codex:CTO:gpt-4o"
```

**Multi-instance:** Same CLI debates itself leveraging nondeterminism.
```
--agent claude --instances 3
```

**Agent file:** Structured JSON definitions from `gptengage generate-agents`.
```
--agent-file agents.json
```

## Examples

```bash
# Default 3-way debate
~/.local/bin/gptengage debate "Should we migrate to microservices?"

# With personas
~/.local/bin/gptengage debate "Tech stack decision" -p "claude:CTO,codex:Architect,gemini:PM"

# Multi-instance Claude debate
~/.local/bin/gptengage debate "Code review strategy" --agent claude --instances 3

# 5 rounds with synthesis
~/.local/bin/gptengage debate "REST vs GraphQL" --rounds 5 --synthesize

# JSON output
~/.local/bin/gptengage debate "REST vs GraphQL" --rounds 5 --output json
```

## Guardrails

- Pass all user arguments through to gptengage directly.
- If the command fails, report the error and suggest running `gptengage status` to check CLI availability.
- Do not invent or modify the user's topic.
- Debates are long-running; use appropriate timeout (600s default wrapper).
