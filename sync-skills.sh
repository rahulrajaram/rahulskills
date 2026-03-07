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

has_skill_manifest() {
    local dir="$1"
    [[ -d "$dir" && ( -f "$dir/SKILL.md" || -f "$dir/skill.md" ) ]]
}

list_skill_names() {
    local base="$1"
    local child
    [[ -d "$base" ]] || return 0

    for child in "$base"/*; do
        [[ -d "$child" ]] || continue
        [[ "$(basename "$child")" == .* ]] && continue
        has_skill_manifest "$child" || continue
        basename "$child"
    done | sort -u
}

list_command_names() {
    local base="$1"
    local file
    [[ -d "$base" ]] || return 0

    for file in "$base"/*.md; do
        [[ -f "$file" ]] || continue
        basename "${file%.md}"
    done | sort -u
}

count_skill_names() {
    local base="$1"
    list_skill_names "$base" | wc -l | tr -d ' '
}

count_command_names() {
    local base="$1"
    list_command_names "$base" | wc -l | tr -d ' '
}

usage() {
    cat <<'USAGE'
Usage: sync-skills.sh <command>

Commands:
  pull      Copy skills FROM installed locations INTO this repo
  push      Copy skills FROM this repo TO installed locations
  diff      Show differences between repo and installed skills
  status    List which skills exist where
  compare-implementations  Compare skill parity across repo, Codex, and Claude

Installed locations:
  Codex skills:     ~/.agents/skills/
  Claude skills:    ~/.claude/skills/
  Slash commands:   ~/.claude/commands/
USAGE
    exit 1
}

pull() {
    local skipped=0
    local skill_name
    local cmd_name
    local cmd_count=0

    echo "Pulling Codex skills from $CODEX_SRC ..."
    mkdir -p "$SKILLS_DST"
    while IFS= read -r skill_name; do
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            rm -rf "$SKILLS_DST/$skill_name"
            continue
        fi
        rm -rf "$SKILLS_DST/$skill_name"
        cp -a "$CODEX_SRC/$skill_name" "$SKILLS_DST/$skill_name"
    done < <(list_skill_names "$CODEX_SRC")

    echo "Pulling Claude skills from $CLAUDE_SRC ..."
    while IFS= read -r skill_name; do
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            continue
        fi
        if [[ -d "$SKILLS_DST/$skill_name" ]]; then
            # Already pulled from Codex source, skip
            continue
        fi
        cp -a "$CLAUDE_SRC/$skill_name" "$SKILLS_DST/$skill_name"
        echo "  NEW (from claude/skills): $skill_name"
    done < <(list_skill_names "$CLAUDE_SRC")

    echo ""
    echo "Pulling slash commands from $CLAUDE_CMD_SRC ..."
    mkdir -p "$COMMANDS_DST"
    while IFS= read -r cmd_name; do
        if is_excluded "$cmd_name"; then
            echo "  SKIP (excluded): ${cmd_name}.md"
            skipped=$((skipped + 1))
            rm -f "$COMMANDS_DST/${cmd_name}.md"
            continue
        fi
        cp -a "$CLAUDE_CMD_SRC/${cmd_name}.md" "$COMMANDS_DST/${cmd_name}.md"
        cmd_count=$((cmd_count + 1))
    done < <(list_command_names "$CLAUDE_CMD_SRC")

    echo ""
    echo "Skills: $(count_skill_names "$SKILLS_DST")"
    echo "Commands: $cmd_count"
    [ "$skipped" -gt 0 ] && echo "Excluded: $skipped"
    echo "Done. Review with: cd $SKILLS_DIR && git diff"
    echo "Tip: run ./audit-skills.sh check before committing."
}

push() {
    local skill_name
    local cmd_name
    local cmd_count=0

    echo "Pushing skills to $CODEX_SRC ..."
    mkdir -p "$CODEX_SRC"
    while IFS= read -r skill_name; do
        rm -rf "$CODEX_SRC/$skill_name"
        cp -a "$SKILLS_DST/$skill_name" "$CODEX_SRC/$skill_name"
        echo "  -> $skill_name"
    done < <(list_skill_names "$SKILLS_DST")

    echo "Pushing skills to $CLAUDE_SRC ..."
    mkdir -p "$CLAUDE_SRC"
    while IFS= read -r skill_name; do
        rm -rf "$CLAUDE_SRC/$skill_name"
        cp -a "$SKILLS_DST/$skill_name" "$CLAUDE_SRC/$skill_name"
    done < <(list_skill_names "$SKILLS_DST")
    echo "  $(count_skill_names "$SKILLS_DST") skills synced"

    echo "Pushing slash commands to $CLAUDE_CMD_SRC ..."
    mkdir -p "$CLAUDE_CMD_SRC"
    while IFS= read -r cmd_name; do
        cp -a "$COMMANDS_DST/${cmd_name}.md" "$CLAUDE_CMD_SRC/${cmd_name}.md"
        cmd_count=$((cmd_count + 1))
    done < <(list_command_names "$COMMANDS_DST")
    echo "  $cmd_count commands synced"

    echo "Done."
}

do_diff() {
    local has_diff=0
    local skill_name
    local cmd_name

    echo "=== Codex skills (~/.agents/skills/) ==="
    while IFS= read -r skill_name; do
        if [ -d "$CODEX_SRC/$skill_name" ]; then
            if ! diff -rq "$SKILLS_DST/$skill_name" "$CODEX_SRC/$skill_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $skill_name"
                diff -ru "$CODEX_SRC/$skill_name" "$SKILLS_DST/$skill_name" || true
                has_diff=1
            fi
        else
            echo "  NEW (repo only): $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$SKILLS_DST")

    while IFS= read -r skill_name; do
        if [ ! -d "$SKILLS_DST/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$CODEX_SRC")

    echo ""
    echo "=== Claude skills (~/.claude/skills/) ==="
    while IFS= read -r skill_name; do
        if [ -d "$CLAUDE_SRC/$skill_name" ]; then
            if ! diff -rq "$SKILLS_DST/$skill_name" "$CLAUDE_SRC/$skill_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $skill_name"
                has_diff=1
            fi
        else
            echo "  MISSING (not installed): $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$SKILLS_DST")

    while IFS= read -r skill_name; do
        if [ ! -d "$SKILLS_DST/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$CLAUDE_SRC")

    echo ""
    echo "=== Slash commands (~/.claude/commands/) ==="
    while IFS= read -r cmd_name; do
        if [ -f "$CLAUDE_CMD_SRC/${cmd_name}.md" ]; then
            if ! diff -q "$COMMANDS_DST/${cmd_name}.md" "$CLAUDE_CMD_SRC/${cmd_name}.md" > /dev/null 2>&1; then
                echo "  MODIFIED: ${cmd_name}.md"
                diff -u "$CLAUDE_CMD_SRC/${cmd_name}.md" "$COMMANDS_DST/${cmd_name}.md" || true
                has_diff=1
            fi
        else
            echo "  NEW (repo only): ${cmd_name}.md"
            has_diff=1
        fi
    done < <(list_command_names "$COMMANDS_DST")

    while IFS= read -r cmd_name; do
        if [ ! -f "$COMMANDS_DST/${cmd_name}.md" ]; then
            echo "  INSTALLED ONLY: ${cmd_name}.md"
            has_diff=1
        fi
    done < <(list_command_names "$CLAUDE_CMD_SRC")

    if [ "$has_diff" -eq 0 ]; then
        echo ""
        echo "Summary:"
        echo "  Codex skills: repo $(count_skill_names "$SKILLS_DST"), installed $(count_skill_names "$CODEX_SRC")"
        echo "  Claude skills: repo $(count_skill_names "$SKILLS_DST"), installed $(count_skill_names "$CLAUDE_SRC")"
        echo "  Slash commands: repo $(count_command_names "$COMMANDS_DST"), installed $(count_command_names "$CLAUDE_CMD_SRC")"
        echo "Everything in sync."
    fi
}

compare_implementations() {
    local has_issue=0
    local skill
    local in_repo
    local in_codex
    local in_claude
    declare -A all_skills

    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$SKILLS_DST")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CLAUDE_SRC")

    echo "=== Skill Name Parity (repo/codex/claude) ==="
    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        in_repo="no"
        in_codex="no"
        in_claude="no"
        [ -d "$SKILLS_DST/$skill" ] && in_repo="yes"
        [ -d "$CODEX_SRC/$skill" ] && in_codex="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && in_claude="yes"

        if [ "$in_repo" != "yes" ] || [ "$in_codex" != "yes" ] || [ "$in_claude" != "yes" ]; then
            printf "  MISMATCH: %-30s repo=%s codex=%s claude=%s\n" "$skill" "$in_repo" "$in_codex" "$in_claude"
            has_issue=1
        fi
    done

    echo ""
    echo "=== Codex vs Claude Content Parity ==="
    while IFS= read -r skill; do
        [ -d "$CODEX_SRC/$skill" ] || continue
        [ -d "$CLAUDE_SRC/$skill" ] || continue

        if ! diff -rq "$CODEX_SRC/$skill" "$CLAUDE_SRC/$skill" > /dev/null 2>&1; then
            echo "  DIVERGED: $skill"
            has_issue=1
        fi
    done < <(list_skill_names "$SKILLS_DST")

    echo ""
    echo "Summary:"
    echo "  repo=$(count_skill_names "$SKILLS_DST"), codex=$(count_skill_names "$CODEX_SRC"), claude=$(count_skill_names "$CLAUDE_SRC")"

    if [ "$has_issue" -eq 0 ]; then
        echo "PASS: Codex and Claude skill variants are consistent."
    else
        echo "FAIL: Skill variants are out of sync."
        return 1
    fi
}

status() {
    local skill
    local _n
    local codex
    local claude
    local commands
    declare -A all_skills

    printf "%-35s %-8s %-8s %-10s\n" "SKILL" "CODEX" "CLAUDE" "COMMANDS"
    printf "%-35s %-8s %-8s %-10s\n" "-----" "-----" "------" "--------"

    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CLAUDE_SRC")
    while IFS= read -r _n; do all_skills["$_n"]=1; done < <(list_command_names "$CLAUDE_CMD_SRC")

    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        codex="--"
        claude="--"
        commands="--"
        [ -d "$CODEX_SRC/$skill" ] && codex="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && claude="yes"
        [ -f "$CLAUDE_CMD_SRC/$skill.md" ] && commands="yes"
        printf "%-35s %-8s %-8s %-10s\n" "$skill" "$codex" "$claude" "$commands"
    done

    echo ""
    echo "Totals: codex skills=$(count_skill_names "$CODEX_SRC"), claude skills=$(count_skill_names "$CLAUDE_SRC"), commands=$(count_command_names "$CLAUDE_CMD_SRC")"
}

[ $# -lt 1 ] && usage

case "$1" in
    pull)   pull ;;
    push)   push ;;
    diff)   do_diff ;;
    compare-implementations) compare_implementations ;;
    status) status ;;
    *)      usage ;;
esac
