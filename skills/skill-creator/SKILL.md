---
name: skill-creator
description: Guide for creating effective skills for Claude and Codex. Use when users want to create or update a skill.
argument-hint: "<skill-name>"
---

# Skill Creator

Create and update skills for Claude and Codex in a consistent, lightweight format.

## Dual-Location Rule

- Create/update the skill in `~/.claude/skills/<name>/SKILL.md`.
- Create/update the **identical** skill in `~/.agents/skills/<name>/SKILL.md`.
- Keep behavior, references, scripts, and tests aligned.
- Adapt only preamble metadata if runtime format differs.
- **Do NOT use `~/.codex/skills/`** — that is the wrong location.

## Standard Workflow

1. Gather concrete examples and expected usage.
2. Plan reusable resources (scripts, references, assets) if any.
3. Scaffold and/or update SKILL.md content for the target skill.
4. Apply the same content in both skill roots when requested for both runtimes.
5. Run validation for the runtime(s) being edited (`quick_validate.py` when available).
6. Keep docs concise and avoid non-essential auxiliary files.

