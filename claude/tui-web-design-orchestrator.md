---
argument-hint: --mode <web-page|web-app|tui-dashboard|tui-wizard> --brief "<text>" [--audience "..."] [--constraints "..."] [--style "..."] [--tech "..."] [--output markdown|json] [--outfile PATH]
description: Generate structured design prompt packets for TUIs and web UIs
---

# TUI/Web Design Orchestrator

**Arguments:** $ARGUMENTS

## Instructions

Run the skill packet generator and pass all user arguments through directly.

```bash
python3 ~/.claude/skills/tui-web-design-orchestrator/scripts/design_prompt_packet.py $ARGUMENTS
```

## Argument Reference

- `--mode`: Required. One of `web-page`, `web-app`, `tui-dashboard`, `tui-wizard`.
- `--brief`: Required. Natural-language design brief.
- `--audience`: Optional target persona.
- `--constraints`: Optional constraints (repeatable).
- `--style`: Optional style direction.
- `--tech`: Optional tech stack override.
- `--output`: `markdown` or `json`.
- `--outfile`: Optional output file path.

## Execution

1. Validate that required flags are present (`--mode`, `--brief`).
2. Run the command above.
3. If `--outfile` is set, confirm the path and summarize key sections.
4. If the command fails, show the error and suggest checking argument quoting.

## Examples

```bash
# Web app prompt packet
/tui-web-design-orchestrator --mode web-app --brief "Design a release dashboard" --audience "engineering managers"

# TUI dashboard packet
/tui-web-design-orchestrator --mode tui-dashboard --brief "Design an incident triage terminal UI" --audience "SRE on-call" --constraints "must run over SSH"

# JSON output to file
/tui-web-design-orchestrator --mode web-page --brief "Design a landing page for a developer tool" --output json --outfile /tmp/devtool-ui.json
```
