#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_SRC="$HOME/.agents/skills"
CLAUDE_SRC="$HOME/.claude/skills"
SKILLS_DST="$SKILLS_DIR/codex"

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
  Codex skills:  ~/.agents/skills/
  Claude skills: ~/.claude/skills/
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
    echo "Skills: $(ls -1d "$SKILLS_DST"/*/ 2>/dev/null | wc -l)"
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

    if [ "$has_diff" -eq 0 ]; then
        echo ""
        echo "Everything in sync."
    fi
}

status() {
    printf "%-35s %-8s %-8s\n" "SKILL" "CODEX" "CLAUDE"
    printf "%-35s %-8s %-8s\n" "-----" "-----" "------"

    declare -A all_skills
    for d in "$CODEX_SRC"/*/; do [[ -d "$d" ]] && all_skills["$(basename "$d")"]=1; done
    for d in "$CLAUDE_SRC"/*/; do [[ -d "$d" ]] && all_skills["$(basename "$d")"]=1; done

    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        codex="--"
        claude="--"
        [ -d "$CODEX_SRC/$skill" ] && codex="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && claude="yes"
        printf "%-35s %-8s %-8s\n" "$skill" "$codex" "$claude"
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
