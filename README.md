<p align="center">
  <img src="logo.png" alt="rahulskills" />
  <br/>
  <em>A curated collection of special recipes I use extensively with AI coding assistants.</em>
</p>

Shared AI agent skills and shell scripts for Claude Code and OpenAI Codex CLI. This repository is the single source of truth for reusable skills that get synced into individual projects via `sync-skills.sh`.

## What is this?

This repo collects skills (prompt-based automation units) for two AI coding assistants:

- **Codex** (`~/.codex/skills/`) -- OpenAI Codex CLI skills
- **Claude Code** (`~/.claude/skills/`) -- Claude Code skills

Both use the same directory-based format with `SKILL.md` entry points, optional scripts, agents, and reference material. The `skills/` directory in this repo is the single source of truth, synced to both locations.

Pi Coding Agent resolves skills from `~/.pi/agent/skills/` first, then the
assembled Codex location at `~/.codex/skills/` and any other location in its
discovery chain. Pi also scans `~/.agents/skills/` as a global location, so
that directory must stay **empty** — codex owns `~/.codex/skills/` and claude
owns `~/.claude/skills/`, and a duplicate name in `~/.agents/skills/` would
make Pi report a collision for every skill. Run
[`install-pi-skills.sh`](#install-pi-skills.sh) after cloning or pulling to link
every repo skill into `~/.pi/agent/skills/` so Pi loads the repository copies
directly and never a stale shadowing copy. Invoke a skill explicitly in Pi as
`/skill:<name>`; for example, `/skill:handoff extract` resumes work from
`NEXT_SHELL_PROMPT.md`.

Skills cover workflow automation (git history cleanup, session handoffs, PDF generation), multi-AI orchestration (debates, ideation across Claude/Codex/Gemini), infrastructure diagnostics (memory leak investigation, incident postmortems), and project-specific tooling (Yore vocabulary curation).

Five shell scripts handle discovery, assembly, syncing, Pi linking, and audit across all local projects.

## Repository Structure

```
rahulskills/
  skills/<name>/SKILL.md   # Generic skill body + shared frontmatter (name, description, argument-hint)
  overlays/claude/<name>.yml  # Claude-only overrides (allowed-tools, etc.)
  overlays/codex/.gitkeep  # Codex overrides (empty for now)
  build/                   # Gitignored — assembled output from stitch step
  bin/                     # Shared assistant shell helpers
  audit-skills.sh          # Pre-commit guard against private reference leaks
  install-pi-skills.sh     # Symlink repo skills into ~/.pi/agent/skills for Pi
  stitch-skills.sh         # Assemble skills + overlays, install to CLI locations
  runtime-exclusions/      # Runtime-owned names that must not be installed twice
  scripts/audit_catalog.py # Audit resolved roots for collisions and portability
  capabilities/skills.toml # Dependencies, effects, layers, and overlap contracts
  scan-skills.sh           # Cross-project skill discovery and reporting
  sync-skills.sh           # Bidirectional sync between repo and installed locations
  setup.sh                 # Contributor bootstrap (hooks + optional skill deploy)
  .github/workflows/       # CI: assemble + structure tests on PRs and pushes
  .githooks/pre-commit     # Repo-local hook calling audit-skills.sh
  .githooks/commit-msg     # Repo-local hook enforcing conventional commits
  .exclude-skills          # Per-machine skill exclusion list (gitignored)
  .blocklist.local         # Per-machine term blocklist (gitignored)
```

Skill logic is authored once in `skills/`. CLI-specific metadata (like `allowed-tools` for Claude) lives in thin overlay files under `overlays/`. The `stitch-skills.sh assemble` step merges them into `build/` before installation.

## Skills Inventory

### Package-managed skills (48)

Authored in this package and deployed to Pi, Codex, and Claude Code. Runtime
exclusions prevent package copies from shadowing system-owned Codex skills.

| Skill | Description |
|-------|-------------|
| `analyze-conversation` | Post-mortem analysis of conversations for anti-patterns and learnings |
| `archdiagram` | Generate architecture diagrams from context or codebase |
| `autonomous-execution-contract` | Execute agreed long-running engineering work autonomously from a bounded objective |
| `autonomy-loop` | Drive an epic as a principal-architect loop with bounded execution and controlled reactor chaining |
| `check-antipatterns` | Real-time anti-pattern detection during active work |
| `clear-writing` | Edit dense, awkward, repetitive, or AI-generated prose into clear, direct, readable writing as an editor, not a ghostwriter; default and grill modes |
| `commit` | Smart commit with file triage, artifact filtering, and secret detection |
| `debate` | Multi-AI debate (Claude + Codex + Gemini) via gptengage |
| `define-operating-charter` | Define and ratify authority, lifecycle, evidence, and stop rules for long-running agentic systems |
| `ecosystem-borrow-audit` | Cross-repo borrowing analysis and multi-sigma ideation sweeps |
| `figma` | Use Figma MCP for design context, screenshots, variables, assets, setup, and design-to-code work |
| `figma-implement-design` | Translate Figma nodes into production code with 1:1 visual fidelity |
| `fp-refine` | Transform imperative code into functional-programming-first structures |
| `frame-goals-constraints` | Turn complex product and system direction into a living, customer-legible product thesis |
| `git-status-report` | Report git sync status of repo and submodules as ASCII table |
| `grilling` | Hard, dependency-aware questions with human-first rendering; speculative factory research, internal debate, and a plain-language orchestrator close |
| `grill-me` | Alias trigger that invokes the grilling skill |
| `handoff` | Commit and write `NEXT_SHELL_PROMPT.md`, or load it to resume work |
| `humanize` | Rewrite rigorous narratives for human readers without weakening their truth |
| `ideate` | Evolutionary ideation across multiple AI models via gptengage |
| `install-commithooks` | Install shared commithooks framework into a project |
| `invokellm` | Invoke one or more AI CLIs via gptengage, defaulting to gemini, claude, and codex |
| `markdown-to-pdf` | Convert markdown to PDF via pandoc + weasyprint |
| `max-columns` | Keep output within a user-specified column width |
| `memleak-investigate` | Investigate memory leaks using /proc, eBPF, and system tools |
| `metabuilder` | Define, compile, inspect, run, recover, and improve governed MetaBuilder harnesses |
| `metabuilder-consumer-qualification` | Run and assess an already designed consumer harness without conflating controller evidence with product judgment |
| `metabuilder-harness-design` | Turn a target objective into an agreed brief and typed MetaBuilder harness design |
| `next-todos` | Generate imperative next-step to-do lists as full sentences with clear objectives |
| `objective-to-dag-decomposition` | Decompose vague objectives into typed reasoning trees, an execution DAG, and phased plans |
| `postmortem` | Generate Amazon COE-style 5-whys postmortem reports |
| `pi-defects-harvester` | Harvest local Pi and shell artifacts into a compact defect digest |
| `pr-lifecycle` | Create and manage a PR from local prep through green CI |
| `privateify` | Lock down a repo to stay private via CI guards, hooks, manifest flags, and agent directives |
| `pythonpackagesevere` | Decompose a Python package into independent projects |
| `readme-doctor` | Build and validate project README and CLI help text |
| `reference-cleaner` | Remove blocklisted references from git history and source files |
| `repo-topics` | Analyze a GitHub repo and apply relevant topic labels |
| `rewrite-commit-messages` | Bulk rewrite git commit messages with filter-repo |
| `skill-creator` | Create or update scoped skills and their supporting resources across the package runtimes |
| `speak` | Read text out loud using Kokoro TTS |
| `squash-commits` | Analyze and squash contiguous thematic git commit groups |
| `system-memory-audit` | Audit Linux system-wide memory health, swap, PSI, and top consumers |
| `test` | Run tests with overwatch for streaming output and failure detection |
| `tui-web-design-orchestrator` | Generate structured design prompt packets for TUIs and web UIs |
| `whitepaper` | Author an investor-facing enterprise whitepaper (case for building a product) with YC-flavored, un-theatrical voice, cost/revenue model, naming/branding, and a branded PDF with embedded fonts |
| `yore-vocabulary-harvest` | Extract candidate vocabulary terms from a Yore index |
| `yore-vocabulary-llm-filter` | Build Whisper-specific vocabulary by filtering common terms |

### Codex runtime-owned skills (6)

These are represented in the capability catalog and runtime exclusion list,
but are not vendored or reinstalled because Codex owns and updates them:
`imagegen`, `openai-docs`, `plugin-creator`, `review-agent`, `skill-creator`, and
`skill-installer`. The package still carries its shared `skill-creator` source
for Pi and Claude while excluding that copy from the Codex assembly.

## Shell Scripts

### `install-pi-skills.sh`

Symlink every repo skill into the Pi coding agent's skill directory so Pi loads
the repository copies directly (repo = single source of truth).

```bash
./install-pi-skills.sh           # Link all repo skills into ~/.pi/agent/skills
./install-pi-skills.sh grilling  # Link a single skill
./install-pi-skills.sh -n        # Dry run
```

Pi resolves `~/.pi/agent/skills/` before `~/.agents/skills/`, so existing real
directories are moved to `~/.pi/agent/backups/<name>.pre-pi-sync` (outside Pi's
scan dirs) and replaced with symlinks pointing back at this repo; nothing is
deleted. The installer also prunes stale symlinks into deleted repo skills and
leftover `.pre-pi-sync` dirs, so Pi reports no skill collisions. Honors
`.exclude-skills`.

### `stitch-skills.sh`

Assembles generic skills with CLI-specific overlays and installs to both CLIs.

```bash
./stitch-skills.sh repo-layout   # Validate skills/ and overlays/ directories
./stitch-skills.sh assemble      # Build assembled output in build/ from skills/ + overlays/
./stitch-skills.sh install       # Assemble + install to ~/.codex/skills, ~/.claude/skills
./stitch-skills.sh check         # Compare assembled output against installed locations
./stitch-skills.sh all           # repo-layout + install + check
```

### `sync-skills.sh`

Bidirectional sync between this repo and installed locations. Push delegates to `stitch-skills.sh install`.

```bash
./sync-skills.sh pull      # Copy installed skills into this repo (strips CLI-specific keys)
./sync-skills.sh push      # Assemble and install skills to all CLI locations
./sync-skills.sh diff      # Show differences between assembled output and installed
./sync-skills.sh status    # List which skills exist in repo, Codex, Pi, and Claude
./sync-skills.sh source-coverage  # Verify all installed Pi/Codex skills are represented
./sync-skills.sh compare-implementations  # Validate repo/Codex/Pi/Claude skill parity
./sync-skills.sh audit-catalog --strict   # Fail on divergent loaded skill names
./sync-skills.sh capability-health --mcp figma  # Check commands/MCPs/platforms
```

Respects per-machine exclusion list in `.exclude-skills` (one skill name per line, gitignored).

### `scan-skills.sh`

Discover skills, scripts, agents, and build targets across all local projects listed in `~/Documents/listings.txt`.

```bash
./scan-skills.sh scan      # Detailed per-project report
./scan-skills.sh check     # Compact counts-only table
./scan-skills.sh report    # Generate skill-candidates.md tracking file
```

Tags each discovered item as `[COLLECTED]`, `[EXCLUDED]`, or `[NEW]` relative to this repo.
### `audit-skills.sh`

Pre-commit guard that scans skill files for private references (project names in blocklists, personal filesystem paths). The full check also parses `capabilities/skills.toml` so malformed or duplicate TOML keys fail in CI.

```bash
./audit-skills.sh check          # Scan all skill files
./audit-skills.sh pre-commit     # Scan only staged files (used by git hook)
./audit-skills.sh install-hook   # Write pre-commit hook into .git/hooks/
```

Uses patterns from `.blocklist.local`. Also matches personal home-directory paths under `Documents/`.

### `bin/` Shared Assistant Helpers

Reusable helper scripts that skills can call from any repo without depending on a specific project checkout.

Current helpers:
- `bin/` helper scripts

## Installation

```bash
git clone git@github.com:rahulrajaram/rahulskills.git ~/Documents/rahulskills
cd ~/Documents/rahulskills
./setup.sh
```

`setup.sh` handles everything:
1. Clones [commithooks](https://github.com/rahulrajaram/commithooks) to `~/Documents/commithooks/` if not already present
2. Installs hook dispatchers into `.git/hooks/` and library modules into `.git/lib/`
3. Optionally deploys skills to `~/.codex/skills/` and `~/.claude/skills/`

Pass `--skip-skills` to skip the interactive skill deployment prompt.

## CI

The `audit-skills.sh check` scan runs on every push to `master` and on pull requests via GitHub Actions. This catches any private references that slip past the local pre-commit hook.

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with required `name` and `description` frontmatter. Preserve supported optional fields such as `argument-hint`, and add `agents/`, `references/`, or `scripts/` only when needed.
2. If the skill needs Claude-specific metadata (e.g. `allowed-tools`), create `overlays/claude/<name>.yml`.
3. Run `./audit-skills.sh check` to verify no private references leaked.
4. Commit and `./sync-skills.sh push` to assemble and deploy to all CLI locations.

## Git Hooks

This repo uses a two-tier hook system:

1. **Shared dispatchers** copied into `.git/hooks/` from [commithooks](https://github.com/rahulrajaram/commithooks) handle delegation.
2. **Repo-local hooks** in `.githooks/` contain project-specific logic.

The dispatchers look for executable hooks in `.githooks/` (or `scripts/git-hooks/`) and `exec` them. Currently active:
- **`pre-commit`** runs `audit-skills.sh pre-commit` to block commits containing private skill names or personal paths.
- **`commit-msg`** enforces conventional commit format and subject line rules.

## License

Private repository. All rights reserved.
