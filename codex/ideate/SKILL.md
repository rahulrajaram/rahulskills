---
name: ideate
description: "Generate divergent ideas from a seed using evolutionary ideation via gptengage. Use when the user asks for brainstorming, idea generation, ideation, or says /ideate."
---

# Ideate

Generate a tree of divergent ideas from a seed concept through gptengage.

## Workflow

1. Parse user arguments.
Extract:
- `<SEED>` — the seed idea to diverge from.
- Any optional flags (--sigma, --depth, --cli, --select, --output, --timeout, --color, --pager).

2. Run ideation.

```bash
~/.local/bin/gptengage ideate "<SEED>" [OPTIONS] 2>&1
```

Use `timeout 600` wrapper since ideation generates multiple AI calls:

```bash
timeout 600 ~/.local/bin/gptengage ideate "<SEED>" [OPTIONS] 2>&1
```

3. Display the full output to the user.

## Options Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--sigma N` | Creativity: 0.5 (conservative), 1.0 (notable), 1.5 (reimagining), 2.0 (radical) | `--sigma 1.5` |
| `--depth N` | Tree depth: 1 (L1 only) or 2 (L1 + L2) (default: 2) | `--depth 1` |
| `--cli CLI` | Which CLI to use (default: claude) | `--cli codex` |
| `--select` | Interactively select which L1 ideas to expand | |
| `-o, --output FORMAT` | Output: text or json (default: text) | `--output json` |
| `-t, --timeout SECS` | Timeout per invocation (default: 120) | `--timeout 180` |
| `--color MODE` | Color: auto, truecolor, 256, none | `--color truecolor` |
| `--pager` | Display in scrollable pager | |

## Sigma Creativity Levels

| Sigma | Style | Description |
|-------|-------|-------------|
| 0.5 | Conservative | Incremental improvements on the seed |
| 1.0 | Notable | Meaningfully different approaches (default) |
| 1.5 | Reimagining | Reframes the problem space |
| 2.0 | Radical | Wild, boundary-breaking divergence |

## Examples

```bash
# Quick brainstorm (3 ideas, depth 1)
~/.local/bin/gptengage ideate "Build a social app for pet owners" --sigma 1.0 --depth 1

# Full tree with high creativity
~/.local/bin/gptengage ideate "AI tutoring platform" --sigma 2.0

# Interactive selection of which ideas to expand
~/.local/bin/gptengage ideate "Marketplace for freelancers" --sigma 1.5 --select

# JSON output for programmatic use
~/.local/bin/gptengage ideate "Build an app" --output json

# Using a different CLI
~/.local/bin/gptengage ideate "New CLI tool" --cli codex
```

## Guardrails

- Pass all user arguments through to gptengage directly.
- If the command fails, report the error and suggest running `gptengage status` to check CLI availability.
- Do not invent or modify the user's seed idea.
- Ideation is long-running; use appropriate timeout (600s default wrapper).
