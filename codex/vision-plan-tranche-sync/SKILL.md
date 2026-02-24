---
name: vision-plan-tranche-sync
description: Translate actionable roadmap items into implementation planning and sync open tranches into tranches TOML, with principal-architect fallback when no vision source exists.
---

# Vision → Implementation → Tranches Sync

Use this skill when the user asks to keep execution planning synchronized between:

1. A vision roadmap file (`VISION.md` default)
2. An implementation plan file (`IMPLEMENTATION_PLAN.md` default)
3. A tranches TOML file (`.yarli/tranches.toml` default)

## What this skill does

- Extracts actionable items from a vision file.
- Adds missing items as new tranches in an implementation plan.
- Syncs open tranches from the implementation plan into tranches TOML.
- Enforces principal-architect fallback if no vision source exists.

## Files this skill works with

- Vision source: `<project>/VISION.md` (or `Vision.md`, `vision.md`)
- Implementation plan: `<project>/IMPLEMENTATION_PLAN.md`
- Tranches manifest: `<project>/.yarli/tranches.toml`

All file paths are overrideable through CLI flags.

## Script

Use the helper script from the skill directory:

```bash
VISION_PLAN_TRANCHE_SYNC_DIR="$HOME/.agents/skills/vision-plan-tranche-sync"
python3 "$VISION_PLAN_TRANCHE_SYNC_DIR/scripts/vision-plan-tranche-sync.py" --help
```

## Default behavior

By default, run in dry-run mode and print a proposed sync plan.

```bash
python3 "$VISION_PLAN_TRANCHE_SYNC_DIR/scripts/vision-plan-tranche-sync.py" --project-root <project-root>
```

Apply changes only when explicitly requested:

```bash
python3 "$VISION_PLAN_TRANCHE_SYNC_DIR/scripts/vision-plan-tranche-sync.py" --project-root <project-root> --apply
```

## Required options

- `--project-root <project-root>`
  - repository/project root containing the target files.
- `--apply`
  - write changes to files. Without this flag, it is dry-run.

## Optional flags

- `--vision-file`, `--plan-file`, `--tranches-file`
  - override default pathnames.
- `--only-plan`
  - only map vision -> implementation plan.
- `--only-tranches`
  - only map implementation plan -> tranches TOML.
- `--force-principal-architect`
  - fail hard if no vision source exists and no principal-architect definition is found.

For non-standard paths:

```bash
python3 "$VISION_PLAN_TRANCHE_SYNC_DIR/scripts/vision-plan-tranche-sync.py" \
  --project-root . \
  --vision-file notes/vision.md \
  --plan-file docs/IMPLEMENTATION_PLAN.md \
  --tranches-file ops/.yarli/tranches.toml \
  --apply
```

## Principal architect forcing behavior

If no vision file is found:

1. the skill checks for principal-architect definitions in:
   - `<project>/.claude/agents`
   - `~/.claude/agents`
   - `<project>/.claude`
   - `~/.agents/agents`
   - `<project>/agents`
2. If a matching definition exists, report exact path and ask the user to launch it.
3. If none exists and `--force-principal-architect` is set, stop with a hard failure marker.

## Sync rules

### Vision → Implementation

- Uses actionable headings/bullets from the vision file.
- Skips bullets already represented by an existing tranche title.
- Uses new tranche IDs by highest existing `I###` number + 1 in the plan file.
- Adds standard tranche shape required by `./bin/yarli-lint-implementation-plan.sh`.

### Plan → Tranches

- Reads open (`incomplete` / `blocked`) tranche keys from the plan file.
- Adds missing tranches to tranches TOML as
  - `key`
  - `summary`
  - `status`
  - `group`
- Never mutates existing tranche entries.

## Post-action checks

- `./bin/yarli-lint-implementation-plan.sh <plan-file>`
- Optional: `./bin/yarli-sanitize-continuation.sh`
- If tranches TOML was changed, run your normal Yarli validation flow.
