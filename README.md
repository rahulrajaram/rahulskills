# rahulskills

Shared AI agent skills and shell scripts for Claude Code and OpenAI Codex CLI. This repository is the single source of truth for reusable skills that get synced into individual projects via `sync-skills.sh`.

## What is this?

This repo collects skills (prompt-based automation units) for two AI coding assistants:

- **Claude Code commands** (`claude/`) -- single-file `.md` prompts loaded as `/slash-commands` in Claude Code sessions.
- **Codex skills** (`codex/`) -- directory-based skills with `SKILL.md` entry points, optional scripts, agents, and reference material.

Skills cover workflow automation (git history cleanup, session handoffs, PDF generation), multi-AI orchestration (debates, ideation across Claude/Codex/Gemini), infrastructure diagnostics (memory leak investigation, incident postmortems), and project-specific tooling (Yarli orchestration, Yore vocabulary curation).

Three shell scripts handle discovery, syncing, and audit across all local projects.

## Repository Structure

```
rahulskills/
  claude/                  # Claude Code commands (*.md)
  codex/                   # Codex skills (name/SKILL.md)
  audit-skills.sh          # Pre-commit guard against private reference leaks
  scan-skills.sh           # Cross-project skill discovery and reporting
  sync-skills.sh           # Bidirectional sync between repo and installed locations
  .githooks/pre-commit     # Repo-local hook calling audit-skills.sh
  .exclude-codex           # Per-machine Codex exclusion list (gitignored)
  .exclude-claude          # Per-machine Claude exclusion list (gitignored)
  .blocklist.local         # Per-machine term blocklist (gitignored)
```

## Skills Inventory

### Claude Code Commands (12)

| Command | Description |
|---------|-------------|
| `analyze-conversation` | Post-mortem analysis of conversations for anti-patterns and learnings |
| `archdiagram` | Generate architecture diagrams from context or codebase |
| `check-antipatterns` | Real-time anti-pattern detection during active work |
| `debate` | Multi-AI debate (Claude + Codex + Gemini) via gptengage |
| `ideate` | Evolutionary ideation across multiple AI models via gptengage |
| `install-commithooks` | Install shared commithooks framework into a project |
| `invokellm` | Invoke a single AI CLI (claude, codex, gemini) via gptengage |
| `markdown-to-pdf` | Convert markdown to PDF via pandoc + weasyprint |
| `memleak-investigate` | Investigate memory leaks using /proc, eBPF, and system tools |
| `speak` | Read text out loud using Kokoro TTS |
| `yore-vocabulary-harvest` | Extract candidate vocabulary terms from a Yore index |
| `yore-vocabulary-llm-filter` | Filter Yore vocabulary via LLM for Whisper-specific domains |

### Codex Skills (16)

| Skill | Description |
|-------|-------------|
| `archdiagram` | Generate architecture diagrams from context or codebase |
| `debate` | Multi-AI debate (Claude + Codex + Gemini) via gptengage |
| `handoff` | Commit workspace state and generate next-shell continuation prompt |
| `ideate` | Evolutionary ideation across multiple AI models via gptengage |
| `install-commithooks` | Install shared commithooks framework into a project |
| `invokellm` | Invoke a single AI CLI (claude, codex, gemini) via gptengage |
| `markdown-to-pdf` | Convert markdown to PDF via pandoc + weasyprint |
| `pythonpackagesevere` | Decompose a Python package into independent projects |
| `readme-doctor` | Build and validate project README and CLI help text |
| `reference-cleaner` | Remove blocklisted references from git history and source files |
| `squash-commits` | Analyze and squash contiguous thematic git commit groups |
| `vision-plan-tranche-sync` | Translate roadmap items into implementation tranches |
| `yarli-introspect` | Live introspection of running or completed Yarli runs |
| `yarli-repo-init` | Initialize and validate Yarli orchestration in a repository |
| `yore-vocabulary-harvest` | Extract candidate vocabulary terms from a Yore index |
| `yore-vocabulary-llm-filter` | Build Whisper-specific vocabulary by filtering common terms |

## Shell Scripts

### `sync-skills.sh`

Bidirectional sync between this repo and the installed skill locations (`~/.agents/skills/` for Codex, `~/.claude/commands/` for Claude Code).

```bash
./sync-skills.sh pull      # Copy installed skills into this repo
./sync-skills.sh push      # Deploy repo skills to installed locations
./sync-skills.sh diff      # Show differences between repo and installed
./sync-skills.sh status    # List which skills exist where
```

Respects per-machine exclusion lists in `.exclude-codex` and `.exclude-claude` (one skill name per line, gitignored).

### `scan-skills.sh`

Discover skills, scripts, agents, and build targets across all local projects listed in `~/Documents/listings.txt`.

```bash
./scan-skills.sh scan      # Detailed per-project report
./scan-skills.sh check     # Compact counts-only table
./scan-skills.sh report    # Generate skill-candidates.md tracking file
```

Tags each discovered item as `[COLLECTED]`, `[EXCLUDED]`, or `[NEW]` relative to this repo.

### `audit-skills.sh`

Pre-commit guard that scans skill files for private references (project names in blocklists, personal filesystem paths).

```bash
./audit-skills.sh check          # Scan all skill files
./audit-skills.sh pre-commit     # Scan only staged files (used by git hook)
./audit-skills.sh install-hook   # Write pre-commit hook into .git/hooks/
```

Uses patterns from `.exclude-codex`, `.exclude-claude`, and `.blocklist.local`. Also matches personal paths matching `~/<user>/Documents/*`.

## Installation

```bash
git clone git@github.com:rahulrajaram/rahulskills.git ~/Documents/rahulskills
cd ~/Documents/rahulskills
./setup.sh
```

`setup.sh` handles everything:
1. Clones [commithooks](https://github.com/rahulrajaram/commithooks) to `~/Documents/commithooks/` if not already present
2. Installs hook dispatchers into `.git/hooks/` and library modules into `.git/lib/`
3. Optionally deploys skills to `~/.agents/skills/` and `~/.claude/commands/`

Pass `--skip-skills` to skip the interactive skill deployment prompt.

## CI

The `audit-skills.sh check` scan runs on every push to `master` and on pull requests via GitHub Actions. This catches any private references that slip past the local pre-commit hook.

## Adding a New Skill

1. **Claude command**: Create `claude/<name>.md` with frontmatter (`allowed-tools`, `description`, optional `argument-hint`).
2. **Codex skill**: Create `codex/<name>/SKILL.md` with frontmatter (`name`, `description`, `allowed-tools`). Add optional `agents/`, `references/`, or `scripts/` subdirectories.
3. Run `./audit-skills.sh check` to verify no private references leaked.
4. Commit and `./sync-skills.sh push` to deploy.

## Git Hooks

This repo uses a two-tier hook system:

1. **Shared dispatchers** in `~/Documents/commithooks/` (set via `core.hooksPath`) handle delegation.
2. **Repo-local hooks** in `.githooks/` contain project-specific logic.

The pre-commit hook runs `audit-skills.sh pre-commit` to block commits containing private skill names or personal paths.

## License

Private repository. All rights reserved.
