# Design Prompt Blueprints

Use these blueprints when generating output from user briefs.

## Shared Output Contract

Every mode should output these sections:

1. `North Star`
2. `Audience`
3. `Primary Tasks`
4. `Information Architecture`
5. `Component Map`
6. `State Matrix`
7. `Accessibility`
8. `Implementation Prompt`
9. `Review Prompt`

## Mode: web-page

Focus:
- single primary conversion goal
- narrative flow
- responsive sections

Required specifics:
- hero proposition
- trust/proof blocks
- primary and secondary CTA behavior
- mobile-first section reflow

## Mode: web-app

Focus:
- repeat task efficiency
- discoverability + density balance
- nav and data workflows

Required specifics:
- global nav model
- page-level IA
- table/form/search/filter patterns
- authorization or role-based UI notes if relevant

## Mode: tui-dashboard

Focus:
- command speed
- scanability under pressure
- keyboard-only operations

Required specifics:
- keymap (`j/k`, arrows, enter, esc, `/`, `?`)
- split-pane behavior at 80/120 columns
- event/status line behavior
- monochrome fallback without color semantics

## Mode: tui-wizard

Focus:
- low-error guided flow
- progress visibility
- safe confirmation/rollback points

Required specifics:
- step model and transitions
- field validation timing
- abort/retry behavior
- final confirmation summary

## Implementation Prompt Template

Use and fill this skeleton:

```text
Design and implement a [MODE] for [AUDIENCE] that helps them [PRIMARY GOAL].

Deliverables:
1) IA and screen map
2) Component definitions with all interaction states
3) Accessible interaction model
4) Production-minded implementation in [TECH STACK]

Constraints:
- [CONSTRAINT 1]
- [CONSTRAINT 2]
- [CONSTRAINT 3]

Must include:
- Empty/loading/error/success states
- Keyboard interactions (and shortcuts for TUI)
- Responsive behavior (for web)
- Tokenized color/spacing/typography system

Output format:
- First: concise spec
- Second: implementation plan with file-by-file changes
- Third: test checklist
```

## Review Prompt Template

```text
Review the proposed [MODE] design for regressions and blind spots.
Prioritize:
1) usability failure points
2) accessibility gaps
3) missing component states
4) mismatch between IA and primary tasks
5) implementation ambiguity

Return findings ordered by severity with concrete fixes.
```
