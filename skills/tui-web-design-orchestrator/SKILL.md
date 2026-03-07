---
name: tui-web-design-orchestrator
description: "Generate structured design prompt packets for terminal UIs and web UIs from natural-language briefs. Use when the user asks to design/redesign a TUI, web page, landing page, dashboard, or UI flow, or says /tui-web-design-orchestrator."
argument-hint: "--mode <web-page|web-app|tui-dashboard|tui-wizard> --brief \"<text>\" [--audience \"...\"] [--constraints \"...\"] [--style \"...\"] [--tech \"...\"] [--output markdown|json] [--outfile PATH]"
---

# TUI/Web Design Orchestrator

Generate production-minded design prompt packets for `web-page`, `web-app`, `tui-dashboard`, and `tui-wizard` workflows.

## Usage

`/tui-web-design-orchestrator --mode <mode> --brief "<brief>" [options]`

## Arguments

- `--mode <web-page|web-app|tui-dashboard|tui-wizard>`: Required mode preset.
- `--brief "<text>"`: Required design brief.
- `--audience "<text>"`: Optional audience/persona.
- `--constraints "<text>"`: Optional constraint (repeatable).
- `--style "<text>"`: Optional style direction.
- `--tech "<text>"`: Optional implementation stack override.
- `--output <markdown|json>`: Optional output format (default: markdown).
- `--outfile <path>`: Optional path to write output file.

## Workflow

1. Validate arguments. Ensure `--mode` and `--brief` are present.
2. Run the packet generator script:

```bash
python3 ~/.claude/skills/tui-web-design-orchestrator/scripts/design_prompt_packet.py $ARGUMENTS
```

3. If `--outfile` is provided, confirm the file path written.
4. If no `--outfile` is provided, return the generated packet inline.
5. If the user asks for stronger rationale or benchmarking, pull patterns from:
- `~/.claude/skills/tui-web-design-orchestrator/references/source-crawl-synthesis.md`
- `~/.claude/skills/tui-web-design-orchestrator/references/design-prompt-blueprints.md`

## Output Contract

A complete packet should include:

1. North star
2. Audience + assumptions
3. IA and component map
4. State matrix (`default`, `hover/focus`, `active`, `disabled`, `error`, `empty`, `loading`, `success`)
5. Accessibility checks
6. Implementation prompt
7. Review prompt

## Mode Guidance

- `web-page`: conversion narrative and responsive section flow.
- `web-app`: recurring workflow efficiency and data-heavy UI patterns.
- `tui-dashboard`: keyboard-first, split-pane, terminal-width-aware operations.
- `tui-wizard`: low-error multi-step guidance with confirmation checkpoints.

## Examples

```bash
# Web app packet
/tui-web-design-orchestrator --mode web-app --brief "Design a release-readiness dashboard" --audience "engineering managers"

# TUI packet with constraints
/tui-web-design-orchestrator --mode tui-dashboard --brief "Design an incident triage terminal UI" --audience "SRE on-call" --constraints "must run over SSH" --constraints "keyboard only"

# JSON output to file
/tui-web-design-orchestrator --mode web-page --brief "Design a landing page for devtool analytics" --output json --outfile /tmp/devtool-ui.json
```

## Guardrails

- Do not invent constraints that the user did not specify; state assumptions explicitly.
- Preserve all provided constraints in the final packet.
- Keep terminal modes keyboard-first and width-aware.
- Always include accessibility checks and explicit state coverage.
