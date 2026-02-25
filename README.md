# rahulskills

Shared AI agent skills and shell scripts for Claude Code and OpenAI Codex CLI. This repository is the single source of truth for reusable skills that get synced into individual projects via `sync-skills.sh`.

## What is this?

This repo collects skills (prompt-based automation units) for two AI coding assistants:

- **Codex** (`~/.agents/skills/`) -- OpenAI Codex CLI skills
- **Claude Code** (`~/.claude/skills/`) -- Claude Code skills

Both use the same directory-based format with `SKILL.md` entry points, optional scripts, agents, and reference material. The `codex/` directory in this repo is the single source of truth, synced to both locations.

Skills cover workflow automation (git history cleanup, session handoffs, PDF generation), multi-AI orchestration (debates, ideation across Claude/Codex/Gemini), infrastructure diagnostics (memory leak investigation, incident postmortems), and project-specific tooling (Yarli orchestration, Yore vocabulary curation).

Three shell scripts handle discovery, syncing, and audit across all local projects.

## Repository Structure

```
rahulskills/
  codex/                   # Skills (name/SKILL.md) — synced to ~/.agents/skills/ + ~/.claude/skills/
  claude/                  # Claude Code slash commands (*.md) — synced to ~/.claude/commands/
  audit-skills.sh          # Pre-commit guard against private reference leaks
  scan-skills.sh           # Cross-project skill discovery and reporting
  sync-skills.sh           # Bidirectional sync between repo and installed locations
  setup.sh                 # Contributor bootstrap (hooks + optional skill deploy)
  .github/workflows/       # CI: audit-skills.sh on PRs and pushes
  .githooks/pre-commit     # Repo-local hook calling audit-skills.sh
  .githooks/commit-msg     # Repo-local hook enforcing conventional commits
  .exclude-skills          # Per-machine skill exclusion list (gitignored)
  .blocklist.local         # Per-machine term blocklist (gitignored)
```

## Skills Inventory

### Skills (23)

Synced to both `~/.agents/skills/` (Codex) and `~/.claude/skills/` (Claude Code).

| Skill | Description |
|-------|-------------|
| `analyze-conversation` | Post-mortem analysis of conversations for anti-patterns and learnings |
| `archdiagram` | Generate architecture diagrams from context or codebase |
| `check-antipatterns` | Real-time anti-pattern detection during active work |
| `debate` | Multi-AI debate (Claude + Codex + Gemini) via gptengage |
| `git-status-report` | Report git sync status of repo and submodules as ASCII table |
| `handoff` | Commit workspace state and generate next-shell continuation prompt |
| `ideate` | Evolutionary ideation across multiple AI models via gptengage |
| `install-commithooks` | Install shared commithooks framework into a project |
| `invokellm` | Invoke a single AI CLI (claude, codex, gemini) via gptengage |
| `kokoro-tts` | Read text out loud using Kokoro TTS |
| `markdown-to-pdf` | Convert markdown to PDF via pandoc + weasyprint |
| `memleak-investigate` | Investigate memory leaks using /proc, eBPF, and system tools |
| `postmortem` | Generate Amazon COE-style 5-whys postmortem reports |
| `pythonpackagesevere` | Decompose a Python package into independent projects |
| `readme-doctor` | Build and validate project README and CLI help text |
| `reference-cleaner` | Remove blocklisted references from git history and source files |
| `squash-commits` | Analyze and squash contiguous thematic git commit groups |
| `test` | Run tests with overwatch for streaming output and failure detection |
| `vision-plan-tranche-sync` | Translate roadmap items into implementation tranches |
| `yarli-introspect` | Live introspection of running or completed Yarli runs |
| `yarli-repo-init` | Initialize and validate Yarli orchestration in a repository |
| `yore-vocabulary-harvest` | Extract candidate vocabulary terms from a Yore index |
| `yore-vocabulary-llm-filter` | Build Whisper-specific vocabulary by filtering common terms |

### Claude Code Slash Commands (11)

Synced to `~/.claude/commands/`. These are invoked as `/command-name` inside Claude Code.

| Command | Description |
|---------|-------------|
| `analyze-conversation` | Analyze completed conversations for anti-patterns, tooling gaps, and learnings |
| `archdiagram` | Generate an architecture diagram from the current context or codebase |
| `check-antipatterns` | Real-time checking of current conversation against known anti-patterns |
| `debate` | Run a multi-AI debate (Claude + Codex + Gemini) via gptengage |
| `ideate` | Generate divergent ideas from a seed using evolutionary ideation via gptengage |
| `install-commithooks` | Install shared commithooks framework into a project |
| `invokellm` | Invoke a single AI CLI (claude, codex, gemini) via gptengage |
| `markdown-to-pdf` | Convert markdown to PDF via pandoc + weasyprint with optional CSS stylesheet |
| `memleak-investigate` | Investigate memory leaks in any Linux process using /proc, eBPF, and system tools |
| `yore-vocabulary-harvest` | Extract candidate vocabulary terms from a Yore index for Whisper vocabulary curation |
| `yore-vocabulary-llm-filter` | Filter Yore vocabulary via LLM to build Whisper-specific domain vocabulary |

## Shell Scripts

### `sync-skills.sh`

Bidirectional sync between this repo and three installed locations (`~/.agents/skills/` for Codex, `~/.claude/skills/` for Claude Code skills, `~/.claude/commands/` for Claude Code slash commands).

```bash
./sync-skills.sh pull      # Copy installed skills into this repo
./sync-skills.sh push      # Deploy repo skills to installed locations
./sync-skills.sh diff      # Show differences between repo and installed
./sync-skills.sh status    # List which skills exist where
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

Pre-commit guard that scans skill files for private references (project names in blocklists, personal filesystem paths).

```bash
./audit-skills.sh check          # Scan all skill files
./audit-skills.sh pre-commit     # Scan only staged files (used by git hook)
./audit-skills.sh install-hook   # Write pre-commit hook into .git/hooks/
```

Uses patterns from `.blocklist.local`. Also matches personal home-directory paths under `Documents/`.

## Installation

```bash
git clone git@github.com:rahulrajaram/rahulskills.git ~/Documents/rahulskills
cd ~/Documents/rahulskills
./setup.sh
```

`setup.sh` handles everything:
1. Clones [commithooks](https://github.com/rahulrajaram/commithooks) to `~/Documents/commithooks/` if not already present
2. Installs hook dispatchers into `.git/hooks/` and library modules into `.git/lib/`
3. Optionally deploys skills to `~/.agents/skills/`, `~/.claude/skills/`, and `~/.claude/commands/`

Pass `--skip-skills` to skip the interactive skill deployment prompt.

## CI

The `audit-skills.sh check` scan runs on every push to `master` and on pull requests via GitHub Actions. This catches any private references that slip past the local pre-commit hook.

## Adding a New Skill

1. Create `codex/<name>/SKILL.md` with frontmatter (`name`, `description`, `allowed-tools`). Add optional `agents/`, `references/`, or `scripts/` subdirectories.
2. Run `./audit-skills.sh check` to verify no private references leaked.
3. Commit and `./sync-skills.sh push` to deploy to `~/.agents/skills/`, `~/.claude/skills/`, and `~/.claude/commands/`.

## Git Hooks

This repo uses a two-tier hook system:

1. **Shared dispatchers** copied into `.git/hooks/` from [commithooks](https://github.com/rahulrajaram/commithooks) handle delegation.
2. **Repo-local hooks** in `.githooks/` contain project-specific logic.

The dispatchers look for executable hooks in `.githooks/` (or `scripts/git-hooks/`) and `exec` them. Currently active:
- **`pre-commit`** runs `audit-skills.sh pre-commit` to block commits containing private skill names or personal paths.
- **`commit-msg`** enforces conventional commit format and subject line rules.

## License

Private repository. All rights reserved.
