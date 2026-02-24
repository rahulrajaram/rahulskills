---
name: readme-doctor
description: "Build and validate project README and CLI help text. Ensures README accuracy against code, CLI help-text congruence across all commands, and correct usage examples. Use when user says /readme-doctor, 'update readme', 'fix help text', 'documentation audit', or asks to validate CLI documentation."
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# README Doctor

Two responsibilities: (1) build a comprehensive, accurate README and (2) validate that all CLI help text is correct and congruent.

## When to Use

- After significant feature work to update the README
- Before releases to ensure documentation accuracy
- When CLI commands or arguments change
- When user asks to audit or fix documentation

## Part 1: README Generation

### Content Requirements

A complete README MUST contain these sections in order:

1. **Title + one-line description**
2. **What is this?** — 2-3 paragraph explanation of the project, its purpose, and who it's for
3. **Features** — bullet list of capabilities
4. **Installation** — building from source, cargo install, Docker
5. **Quick Start** — minimal steps to get running (init → serve → use)
6. **CLI Reference** — every command and subcommand with actual `--help` output
7. **AI Agent Integration** — MCP setup for Claude Code, Codex, and other MCP clients
8. **gRPC API** — service definition, key RPCs, connection examples
9. **REST API** — route overview, example curl commands
10. **Configuration** — environment variables, `.haake.yml` format
11. **Architecture** — system diagram, key concepts explained
12. **Security** — auth, TLS, rate limiting, input validation
13. **Examples** — runnable code examples
14. **License**

### Accuracy Rules

- **Every CLI example MUST be verified** against actual `--help` output. Run `cargo run --offline -- <cmd> --help` and compare.
- **Flag names, defaults, and descriptions** must match what clap actually produces.
- **gRPC RPCs** must match the proto file exactly.
- **REST routes** must match the Axum router in rest.rs.
- **MCP tools** must match the tool definitions in mcp.rs.
- **Environment variables** must match what the code actually reads (check with `grep -r "HAAKE_" src/`).
- **No aspirational features** — only document what actually works.

### Style Rules

- Use active voice
- Prefer concrete examples over abstract descriptions
- Keep sentences concise
- Use consistent formatting throughout
- Code blocks must specify the language (bash, rust, yaml, etc.)
- No emojis unless the user requests them
- Use backtick formatting for CLI commands, flags, env vars, file paths

## Part 2: CLI Help-Text Audit

### What to Check

For every command and subcommand:

1. **Run `<binary> <cmd> --help`** and capture the output
2. **Verify congruence** across all commands:
   - Consistent terminology (e.g., "Agent name" vs "Agent or scope name" — pick one)
   - Consistent flag naming patterns (e.g., `-y/--yes` for skip confirmation everywhere)
   - Consistent default value formatting
   - No superfluous or confusing syntax in usage lines
3. **Verify correctness against code**:
   - Every `#[arg]` attribute matches the help output
   - Default values shown in help match actual defaults in code
   - Descriptions are accurate and not misleading
   - Possible values listed are complete and correct
4. **Flag for issues**:
   - Missing descriptions
   - Inconsistent capitalization
   - Arguments that exist in code but don't appear in help
   - Help text that references removed features
   - Duplicate or conflicting short flags

### Congruence Report Format

```
CLI Help-Text Audit Report
==========================

Commands scanned: N
Issues found: N

INCONSISTENCIES:
  [WARN] `haake query` uses "Agent name" but `haake memory insert` uses
         "Agent or scope name" — should be consistent
  [FIX]  `haake memory insert --type` should be `--memory-type` to match
         other commands

MISSING:
  [MISS] `haake serve` does not document HAAKE_REST_PORT env var

INCORRECT:
  [ERR]  `haake import --type` default shown as "working" but code
         defaults to "semantic"

SUPERFLUOUS:
  [TRIM] `haake memory insert` shows "-V, --version" which is noise
         for a subcommand
```

## Workflow

### Step 1: Gather

- Read current README.md
- Run `<binary> --help` and all subcommand `--help`
- Read proto files, rest.rs routes, mcp.rs tool definitions
- Read Cargo.toml for version and metadata
- Grep for env vars: `grep -rn "HAAKE_\|SW4RM_" src/`

### Step 2: Audit Help Text

- Run Part 2 checks
- Produce the congruence report
- Fix any issues found in the clap definitions (with user approval)

### Step 3: Write README

- Generate the full README following Part 1 structure
- Every CLI example must use exact flag names from `--help` output
- Present a diff summary to the user before writing

### Step 4: Validate

- Re-run all `--help` commands and verify README matches
- Check all internal links resolve
- Verify code examples are syntactically valid

## Safety

- Always read existing README before overwriting
- Present changes for approval on first use
- Do not modify clap definitions without asking
- Do not add features to README that don't exist in code
