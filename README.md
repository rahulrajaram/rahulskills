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

Pi Coding Agent resolves selected links from `~/.pi/agent/skills/`. Run
[`install-pi-skills.sh`](#install-pi-skills.sh) with the desired profile after
cloning or pulling. It preserves unrelated links and user-managed directories;
profile changes do not prune optional copies. Invoke a skill explicitly in Pi as
`/skill:<name>`; for example, `/skill:handoff extract` reviews
`NEXT_SHELL_PROMPT.md`, adopts it as the current request, and immediately
executes its authorized work.

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

### Package-managed skills (50)

Authored in this package and available for explicit selection on Pi, Codex, and
Claude Code. The default `core` profile omits the optional design skills
`figma`, `figma-implement-design`, and `tui-web-design-orchestrator`. Runtime
exclusions prevent package copies from shadowing system-owned skills.

| Skill | Description |
|-------|-------------|
| `analyze-conversation` | Post-mortem analysis of conversations for anti-patterns and learnings |
| `archdiagram` | Generate architecture diagrams from context or codebase |
| `autonomous-execution-contract` | Execute agreed long-running engineering work autonomously from a bounded objective |
| `autonomy-loop` | Drive an epic as a principal-architect loop with bounded execution and controlled reactor chaining |
| `check-antipatterns` | Read-only transcript anti-pattern checks plus evidence-backed review of active code changes |
| `clear-writing` | Edit dense, awkward, repetitive, or AI-generated prose into clear, direct, readable writing as an editor, not a ghostwriter; default and grill modes |
| `clean-code-refine` | Review or refactor code across behavior, idiom, size, complexity, dataflow, testability, and simplicity |
| `commit` | Smart commit with file triage, artifact filtering, and secret detection |
| `debate` | Multi-AI debate (Claude + Codex + Gemini) via gptengage |
| `define-operating-charter` | Define and ratify authority, lifecycle, evidence, and stop rules for long-running agentic systems |
| `diagram-review-viewer` | Create Mermaid diagrams with an interactive browser review viewer |
| `ecosystem-borrow-audit` | Cross-repo borrowing analysis and multi-sigma ideation sweeps |
| `figma` | Use Figma MCP for design context, screenshots, variables, assets, setup, and design-to-code work |
| `figma-implement-design` | Translate Figma nodes into production code with 1:1 visual fidelity |
| `fp-refine` | Transform imperative code into functional-programming-first structures |
| `frame-goals-constraints` | Turn complex product and system direction into a living, customer-legible product thesis |
| `git-status-report` | Report git sync status of repo and submodules as ASCII table |
| `grilling` | Hard, dependency-aware questions with human-first rendering; speculative factory research, internal debate, and a plain-language orchestrator close |
| `grill-me` | Alias trigger that invokes the grilling skill |
| `handoff` | Commit and write `NEXT_SHELL_PROMPT.md`, or review and execute it as resumed work |
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

Symlink the selected profile or explicitly named skills into Pi's skill
directory. Selection defaults to `core` and preserves unrelated entries.

```bash
./install-pi-skills.sh                       # Link the core profile
./install-pi-skills.sh --profile design      # Add optional design skills
./install-pi-skills.sh --profile all         # Select every package profile
./install-pi-skills.sh --skill grilling      # Select one skill only
./install-pi-skills.sh --preview --pi-root /tmp/pi-agent  # Isolated preview
```

Existing package-owned links can be updated and explicitly removed with
`--remove NAME`. Unmanaged copies and unrelated Pi symlinks are retained;
ownership is recorded in `.rahulskills-ownership.json` under the Pi runtime.
No optional profile selection activates MCPs, commands, or other dependencies.
Runtime exclusions and `.exclude-skills` are honored.

### `stitch-skills.sh`

Assembles selected generic skills with CLI-specific overlays and can install to
both CLIs. `--output PATH` always assembles into a fresh isolated destination;
`preview` uses an isolated assembly and reports additions, updates, retained
entries, ownership conflicts, and explicit removals without changing installs.
`install` previews both runtimes before applying ownership-safe updates.

```bash
./stitch-skills.sh repo-layout   # Validate skills/ and overlays/ directories
./stitch-skills.sh assemble --profile core
./stitch-skills.sh assemble --profile design --output /tmp/rahulskills-design
./stitch-skills.sh preview --profile core --codex-root /tmp/codex --claude-root /tmp/claude
./stitch-skills.sh install --profile core
./stitch-skills.sh check --profile core
./stitch-skills.sh all --profile all
```

Use `--remove NAME` only for an explicit removal of a verified package-owned
entry. A read-only preview of the actual default installs is:

```bash
./stitch-skills.sh preview --codex-root "$HOME/.codex" --claude-root "$HOME/.claude"
./install-pi-skills.sh --preview --pi-root "$HOME/.pi/agent"
```

### `sync-skills.sh`

Bidirectional sync between this repo and installed locations. Push delegates to
`stitch-skills.sh install`. Pull stages each incoming skill and moves an
existing source tree into a timestamped Git-metadata backup before publishing
the replacement. Excluded skills are left untouched.

```bash
./sync-skills.sh pull      # Copy installed skills into this repo (strips CLI-specific keys)
./sync-skills.sh push      # Assemble and install skills to all CLI locations
./sync-skills.sh diff      # Freshly assemble, then show installed differences
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

Pre-commit guard that scans skill files for private references (project names
in blocklists and personal filesystem paths). The full check also validates
every manifest, verifies that source, README inventory, and capability catalog
agree, and checks that maintained local Markdown links resolve, including new
skill/reference/docs files before their first commit.

```bash
./audit-skills.sh check          # Run the full package integrity audit
./audit-skills.sh pre-commit     # Scan only staged files (used by git hook)
./audit-skills.sh install-hook   # Write pre-commit hook into .git/hooks/
```

Uses patterns from `.blocklist.local`. Also matches personal home-directory paths under `Documents/`.

Secret scans use exact historical fingerprints in `.gitleaksignore`; no rule is
disabled. `.trufflehog-exclude-paths` excludes only Git internals, generated
builds, and tool caches so filesystem scans stay bounded to maintained source.

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

The `audit-skills.sh check` audit and focused analyzer/checker/validator unit
tests run on every push to `master` and on pull requests via GitHub Actions.
They catch private references, invalid manifests, inventory/catalog drift,
broken local links, and transcript-normalization regressions that slip past the
focused pre-commit hook.

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with required `name` and `description` frontmatter. Preserve supported optional fields such as `argument-hint`, and add `agents/`, `references/`, or `scripts/` only when needed.
2. If the skill needs Claude-specific metadata (e.g. `allowed-tools`), create `overlays/claude/<name>.yml`.
3. Run `./audit-skills.sh check` to validate the package and verify no private references leaked.
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
