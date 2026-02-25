#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_SRC="$HOME/.agents/skills"
CLAUDE_SRC="$HOME/.claude/skills"
CLAUDE_CMD_SRC="$HOME/.claude/commands"
SKILLS_DST="$SKILLS_DIR/codex"
COMMANDS_DST="$SKILLS_DIR/claude"

# Exclusion list — one skill name per line, lines starting with # are ignored.
# This file is gitignored so each machine can maintain its own private list.
EXCLUDE_FILE="$SKILLS_DIR/.exclude-skills"

is_excluded() {
    local name="$1"
    [[ ! -f "$EXCLUDE_FILE" ]] && return 1
    grep -qxF "$name" <(grep -v '^#' "$EXCLUDE_FILE" | grep -v '^$') 2>/dev/null
}

usage() {
    cat <<'EOF'
Usage: sync-skills.sh <command>

Commands:
  pull      Copy skills FROM installed locations INTO this repo
  push      Copy skills FROM this repo TO installed locations
  diff      Show differences between repo and installed skills
  status    List which skills exist where

Installed locations:
  Codex skills:     ~/.agents/skills/
  Claude skills:    ~/.claude/skills/
  Slash commands:   ~/.claude/commands/
EOF
    exit 1
}

pull() {
    local skipped=0

    echo "Pulling Codex skills from $CODEX_SRC ..."
    mkdir -p "$SKILLS_DST"
    for skill_dir in "$CODEX_SRC"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            rm -rf "$SKILLS_DST/$skill_name"
            continue
        fi
        rm -rf "$SKILLS_DST/$skill_name"
        cp -a "$skill_dir" "$SKILLS_DST/$skill_name"
    done

    echo "Pulling Claude skills from $CLAUDE_SRC ..."
    for skill_dir in "$CLAUDE_SRC"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            continue
        fi
        if [[ -d "$SKILLS_DST/$skill_name" ]]; then
            # Already pulled from Codex source, skip
            continue
        fi
        cp -a "$skill_dir" "$SKILLS_DST/$skill_name"
        echo "  NEW (from claude/skills): $skill_name"
    done

    echo ""
    echo "Pulling slash commands from $CLAUDE_CMD_SRC ..."
    mkdir -p "$COMMANDS_DST"
    local cmd_count=0
    for cmd_file in "$CLAUDE_CMD_SRC"/*.md; do
        [[ -f "$cmd_file" ]] || continue
        cmd_name="$(basename "$cmd_file")"
        if is_excluded "${cmd_name%.md}"; then
            echo "  SKIP (excluded): $cmd_name"
            skipped=$((skipped + 1))
            rm -f "$COMMANDS_DST/$cmd_name"
            continue
        fi
        cp -a "$cmd_file" "$COMMANDS_DST/$cmd_name"
        cmd_count=$((cmd_count + 1))
    done

    echo ""
    echo "Skills: $(ls -1d "$SKILLS_DST"/*/ 2>/dev/null | wc -l)"
    echo "Commands: $cmd_count"
    [ "$skipped" -gt 0 ] && echo "Excluded: $skipped"
    echo "Done. Review with: cd $SKILLS_DIR && git diff"
    echo "Tip: run ./audit-skills.sh check before committing."
}

push() {
    echo "Pushing skills to $CODEX_SRC ..."
    mkdir -p "$CODEX_SRC"
    for skill_dir in "$SKILLS_DST"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        rm -rf "$CODEX_SRC/$skill_name"
        cp -a "$skill_dir" "$CODEX_SRC/$skill_name"
        echo "  -> $skill_name"
    done

    echo "Pushing skills to $CLAUDE_SRC ..."
    mkdir -p "$CLAUDE_SRC"
    for skill_dir in "$SKILLS_DST"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        rm -rf "$CLAUDE_SRC/$skill_name"
        cp -a "$skill_dir" "$CLAUDE_SRC/$skill_name"
    done
    echo "  $(ls -1d "$SKILLS_DST"/*/ 2>/dev/null | wc -l) skills synced"

    echo "Pushing slash commands to $CLAUDE_CMD_SRC ..."
    mkdir -p "$CLAUDE_CMD_SRC"
    local cmd_count=0
    for cmd_file in "$COMMANDS_DST"/*.md; do
        [[ -f "$cmd_file" ]] || continue
        cp -a "$cmd_file" "$CLAUDE_CMD_SRC/$(basename "$cmd_file")"
        cmd_count=$((cmd_count + 1))
    done
    echo "  $cmd_count commands synced"

    echo "Done."
}

do_diff() {
    local has_diff=0

    echo "=== Codex skills (~/.agents/skills/) ==="
    for skill_dir in "$SKILLS_DST"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if [ -d "$CODEX_SRC/$skill_name" ]; then
            if ! diff -rq "$skill_dir" "$CODEX_SRC/$skill_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $skill_name"
                diff -ru "$CODEX_SRC/$skill_name" "$skill_dir" || true
                has_diff=1
            fi
        else
            echo "  NEW (repo only): $skill_name"
            has_diff=1
        fi
    done
    for skill_dir in "$CODEX_SRC"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if [ ! -d "$SKILLS_DST/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done

    echo ""
    echo "=== Claude skills (~/.claude/skills/) ==="
    for skill_dir in "$SKILLS_DST"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if [ -d "$CLAUDE_SRC/$skill_name" ]; then
            if ! diff -rq "$skill_dir" "$CLAUDE_SRC/$skill_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $skill_name"
                has_diff=1
            fi
        else
            echo "  MISSING (not installed): $skill_name"
            has_diff=1
        fi
    done
    for skill_dir in "$CLAUDE_SRC"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if [ ! -d "$SKILLS_DST/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done

    echo ""
    echo "=== Slash commands (~/.claude/commands/) ==="
    for cmd_file in "$COMMANDS_DST"/*.md; do
        [[ -f "$cmd_file" ]] || continue
        cmd_name="$(basename "$cmd_file")"
        if [ -f "$CLAUDE_CMD_SRC/$cmd_name" ]; then
            if ! diff -q "$cmd_file" "$CLAUDE_CMD_SRC/$cmd_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $cmd_name"
                diff -u "$CLAUDE_CMD_SRC/$cmd_name" "$cmd_file" || true
                has_diff=1
            fi
        else
            echo "  NEW (repo only): $cmd_name"
            has_diff=1
        fi
    done
    for cmd_file in "$CLAUDE_CMD_SRC"/*.md; do
        [[ -f "$cmd_file" ]] || continue
        cmd_name="$(basename "$cmd_file")"
        if [ ! -f "$COMMANDS_DST/$cmd_name" ]; then
            echo "  INSTALLED ONLY: $cmd_name"
            has_diff=1
        fi
    done

    if [ "$has_diff" -eq 0 ]; then
        echo ""
        echo "Everything in sync."
    fi
}

status() {
    printf "%-35s %-8s %-8s %-10s\n" "SKILL" "CODEX" "CLAUDE" "COMMANDS"
    printf "%-35s %-8s %-8s %-10s\n" "-----" "-----" "------" "--------"

    declare -A all_skills
    for d in "$CODEX_SRC"/*/; do [[ -d "$d" ]] && all_skills["$(basename "$d")"]=1; done
    for d in "$CLAUDE_SRC"/*/; do [[ -d "$d" ]] && all_skills["$(basename "$d")"]=1; done
    for f in "$CLAUDE_CMD_SRC"/*.md; do [[ -f "$f" ]] && { local _n; _n="$(basename "$f")"; all_skills["${_n%.md}"]=1; }; done

    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        codex="--"
        claude="--"
        commands="--"
        [ -d "$CODEX_SRC/$skill" ] && codex="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && claude="yes"
        [ -f "$CLAUDE_CMD_SRC/$skill.md" ] && commands="yes"
        printf "%-35s %-8s %-8s %-10s\n" "$skill" "$codex" "$claude" "$commands"
    done
}

[ $# -lt 1 ] && usage

case "$1" in
    pull)   pull ;;
    push)   push ;;
    diff)   do_diff ;;
    status) status ;;
    *)      usage ;;
esac
