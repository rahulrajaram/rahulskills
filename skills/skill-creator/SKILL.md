---
name: skill-creator
description: Guide for creating effective skills for Claude and Codex. Use when users want to create or update a skill.
argument-hint: "<skill-name>"
---

# Skill Creator

Create and update skills for Claude and Codex in a consistent, lightweight format.

## Canonical Source Rule

- Create or update the skill once under `$RAHULSKILLS_HOME/skills/<name>/`.
- Put runtime-only metadata under `overlays/<runtime>/<name>.yml`.
- Run `stitch-skills.sh assemble` and validate before installation.
- Use `runtime-exclusions/<runtime>.txt` for names owned by that runtime.
- Never maintain divergent installed copies by hand.

## Standard Workflow

1. Gather concrete examples and expected usage.
2. Plan reusable resources (scripts, references, assets) if any.
3. Scaffold and/or update SKILL.md content for the target skill.
4. Assemble the runtime variants from the canonical source.
5. Run catalog and structure validation before installation.
6. Keep docs concise and avoid non-essential auxiliary files.

## Validation

From `$RAHULSKILLS_HOME`, run:

```bash
python skills/skill-creator/scripts/validate.py <skill-name>
python scripts/audit_catalog.py --strict
./stitch-skills.sh assemble
```

The validator checks that `~/.codex/skills/<skill-name>/SKILL.md` and
`~/.claude/skills/<skill-name>/SKILL.md` both exist, both have frontmatter with
`name` and `description`, and are byte-identical. Runtime-only metadata
exceptions must be explicit before they are allowed:

```bash
python scripts/validate.py <skill-name> --allow-runtime-metadata-diff
```

Run the built-in fixture test with:

```bash
python scripts/validate.py --self-test
```
