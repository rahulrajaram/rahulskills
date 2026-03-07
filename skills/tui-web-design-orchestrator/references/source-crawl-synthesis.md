# Source Crawl Synthesis (March 1, 2026)

## Scope

Deep crawl coverage came from:
- http://thedesignsystem.guide
- http://collection.componly.co
- http://designsystemchecklist.com
- http://designsystems.surf
- http://designsystemsrepo.com
- http://component.gallery

Raw crawl artifact: `research/design-system-sites-crawl.json`.

## What Each Source Is Best For

## 1) The Design System Guide

Strengths:
- end-to-end design-system lifecycle content (`start`, `audit`, `foundations`, `tokens`, `documentation`, `metrics`)
- discovery and governance framing
- practical operations themes (inventory, automation, collaboration)

Use it for:
- design-system maturity scaffolding in prompts
- deciding documentation and metric outputs for a new UI

## 2) Componly Collection

Strengths:
- broad component examples across major systems exposed via `componentcollection.s3.amazonaws.com`
- repeated coverage of high-value systems (Fluent UI, MUI, Polaris, Carbon, EUI, Base Web, Salesforce, etc.)

Use it for:
- fast component variant ideation
- comparing composition choices before implementation

Note:
- app is JS-heavy; source extraction is often required to inspect full inventory.

## 3) Design System Checklist

Strengths:
- quality gates broken into 4 pillars seen in open-source checklist data:
  - design language
  - foundations
  - components
  - maintenance
- checklist mindset reduces omissions in state and governance coverage

Use it for:
- definition-of-done checks in prompts
- balancing visual detail with process/documentation readiness

## 4) Design Systems Surf

Strengths:
- large catalog of real design systems and references
- useful for benchmarking patterns and selecting precedent systems

Use it for:
- triangulating against mature systems before proposing novel interaction models
- collecting component and token references quickly

## 5) Design Systems Repo

Strengths:
- curated directory of systems, tools, articles, talks, books
- quick way to find proven practices and historical context

Use it for:
- adding rationale and implementation references to design prompts
- identifying tooling/documentation ecosystem options

## 6) Component Gallery

Strengths:
- component-centric comparison hub with broad cross-system examples
- home page signals a large, maintained corpus (component + system + example counts)
- useful for behavior and state pattern comparison by component type

Use it for:
- behavior/state benchmarking (accordion, table, tabs, dialog, etc.)
- extracting shared conventions before creating custom patterns

## Cross-Source Heuristics

1. Start every design prompt with the 4 checklist pillars:
- language
- foundations
- components
- maintenance

2. For each critical component, compare at least two mature systems before finalizing pattern.

3. Require explicit state matrices:
- `default`
- `hover/focus`
- `active`
- `disabled`
- `error`
- `empty`
- `loading`
- `success`

4. Separate concept output from build output:
- first: design spec
- second: implementation prompt with file-oriented instructions

5. Add governance from day one:
- naming/tokens
- documentation format
- adoption metrics

## TUI Translation Heuristics

Map web patterns into terminal-friendly primitives:
- tabs -> segmented key-switch regions (`1/2/3`)
- cards -> bordered blocks with heading + actions
- table + side panel -> split-pane list/detail view
- modal -> full-screen step or inline confirmation panel
- toasts -> transient status line plus event log

Always include:
- keyboard-first navigation map
- explicit no-mouse assumption
- 80-column fallback layout
- ANSI + monochrome fallback tokens

## Prompting Checklist (Condensed)

Before sending a prompt to a coding agent, ensure it contains:
- target mode (`web-page`, `web-app`, `tui-dashboard`, `tui-wizard`)
- user goal and persona
- information architecture and task path
- component inventory and states
- accessibility expectations
- output format and tech stack constraints
