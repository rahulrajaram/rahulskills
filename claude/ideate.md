---
argument-hint: <seed> [--sigma 1.0] [--depth 2] [--cli claude] [--select]
description: Generate divergent ideas from a seed using evolutionary ideation via gptengage
---

# Ideate

**Arguments:** $ARGUMENTS

## Instructions

Run the `gptengage ideate` command with the user's arguments. Pass all arguments through directly.

```bash
~/.local/bin/gptengage ideate $ARGUMENTS 2>&1
```

### Argument Reference

- `<SEED>` - The seed idea to diverge from
- `--sigma N` - Creativity level: 0.5 (conservative), 1.0 (notable), 1.5 (reimagining), 2.0 (radical) (default: 1.0)
- `--depth N` - Tree depth: 1 (L1 only) or 2 (L1 + L2) (default: 2)
- `--cli CLI` - Which CLI to use (default: claude)
- `--select` - Interactively select which L1 ideas to expand
- `--output text|json` - Output format (default: text)
- `--timeout SECS` - Timeout per invocation (default: 120)
- `--color auto|truecolor|256|none` - Color mode (default: auto)
- `--pager` - Display in scrollable pager

### Examples

```bash
# Quick brainstorm (3 ideas, depth 1)
~/.local/bin/gptengage ideate "Build a social app for pet owners" --sigma 1.0 --depth 1

# Full tree with high creativity
~/.local/bin/gptengage ideate "AI tutoring platform" --sigma 2.0

# Interactive selection
~/.local/bin/gptengage ideate "Marketplace for freelancers" --sigma 1.5 --select

# JSON output for programmatic use
~/.local/bin/gptengage ideate "Build an app" --output json
```

### Execution

1. Run the command via Bash with a timeout of 600 seconds (ideation generates multiple AI calls)
2. Display the full output to the user
3. If the command fails, show the error and suggest checking `gptengage status`
