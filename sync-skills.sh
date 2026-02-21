#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_SRC="$HOME/.agents/skills"
CLAUDE_SRC="$HOME/.claude/commands"
CODEX_DST="$SKILLS_DIR/codex"
CLAUDE_DST="$SKILLS_DIR/claude"

# Exclusion lists — one skill name per line, lines starting with # are ignored.
# These files are gitignored so each machine can maintain its own private list.
CODEX_EXCLUDE_FILE="$SKILLS_DIR/.exclude-codex"
CLAUDE_EXCLUDE_FILE="$SKILLS_DIR/.exclude-claude"

is_excluded() {
    local name="$1" file="$2"
    [[ ! -f "$file" ]] && return 1
    grep -qxF "$name" <(grep -v '^#' "$file" | grep -v '^$') 2>/dev/null
}

usage() {
    cat <<'EOF'
Usage: sync-skills.sh <command>

Commands:
  pull      Copy skills FROM ~/.agents/skills/ and ~/.claude/commands/ INTO this repo
  push      Copy skills FROM this repo back TO ~/.agents/skills/ and ~/.claude/commands/
  diff      Show differences between repo and installed skills
  status    List which skills exist where
EOF
    exit 1
}

pull() {
    local skipped=0

    echo "Pulling Codex skills from $CODEX_SRC ..."
    mkdir -p "$CODEX_DST"
    # Remove repo skills that still exist in source (will be re-copied), keep repo-only ones
    for skill_dir in "$CODEX_SRC"/*/; do
        skill_name="$(basename "$skill_dir")"
        if is_excluded "$skill_name" "$CODEX_EXCLUDE_FILE"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            rm -rf "$CODEX_DST/$skill_name"
            continue
        fi
        rm -rf "$CODEX_DST/$skill_name"
        cp -a "$skill_dir" "$CODEX_DST/$skill_name"
    done

    echo "Pulling Claude Code commands from $CLAUDE_SRC ..."
    mkdir -p "$CLAUDE_DST"
    for cmd_file in "$CLAUDE_SRC"/*.md; do
        cmd_name="$(basename "$cmd_file" .md)"
        if is_excluded "$cmd_name" "$CLAUDE_EXCLUDE_FILE"; then
            echo "  SKIP (excluded): $cmd_name"
            skipped=$((skipped + 1))
            rm -f "$CLAUDE_DST/$cmd_name.md"
            continue
        fi
        cp -a "$cmd_file" "$CLAUDE_DST/"
    done

    echo ""
    echo "Codex:  $(ls -1d "$CODEX_DST"/*/ 2>/dev/null | wc -l) skills"
    echo "Claude: $(ls -1 "$CLAUDE_DST"/*.md 2>/dev/null | wc -l) commands"
    [ "$skipped" -gt 0 ] && echo "Excluded: $skipped"
    echo "Done. Review with: cd $SKILLS_DIR && git diff"
    echo "Tip: run ./audit-skills.sh check before committing."
}

push() {
    echo "Pushing Codex skills to $CODEX_SRC ..."
    for skill_dir in "$CODEX_DST"/*/; do
        skill_name="$(basename "$skill_dir")"
        rm -rf "$CODEX_SRC/$skill_name"
        cp -a "$skill_dir" "$CODEX_SRC/$skill_name"
        echo "  -> $skill_name"
    done

    echo "Pushing Claude Code commands to $CLAUDE_SRC ..."
    for cmd_file in "$CLAUDE_DST"/*.md; do
        cmd_name="$(basename "$cmd_file")"
        cp -a "$cmd_file" "$CLAUDE_SRC/$cmd_name"
        echo "  -> $cmd_name"
    done

    echo "Done."
}

do_diff() {
    local has_diff=0

    echo "=== Codex skills ==="
    for skill_dir in "$CODEX_DST"/*/; do
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
        skill_name="$(basename "$skill_dir")"
        if [ ! -d "$CODEX_DST/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done

    echo ""
    echo "=== Claude Code commands ==="
    for cmd_file in "$CLAUDE_DST"/*.md; do
        cmd_name="$(basename "$cmd_file")"
        if [ -f "$CLAUDE_SRC/$cmd_name" ]; then
            if ! diff -q "$cmd_file" "$CLAUDE_SRC/$cmd_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $cmd_name"
                diff -u "$CLAUDE_SRC/$cmd_name" "$cmd_file" || true
                has_diff=1
            fi
        else
            echo "  NEW (repo only): $cmd_name"
            has_diff=1
        fi
    done
    for cmd_file in "$CLAUDE_SRC"/*.md; do
        cmd_name="$(basename "$cmd_file")"
        if [ ! -f "$CLAUDE_DST/$cmd_name" ]; then
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
    printf "%-35s %-8s %-8s\n" "SKILL" "CODEX" "CLAUDE"
    printf "%-35s %-8s %-8s\n" "-----" "-----" "------"

    # Collect all skill names
    declare -A all_skills
    for d in "$CODEX_SRC"/*/; do all_skills["$(basename "$d")"]=1; done
    for f in "$CLAUDE_SRC"/*.md; do
        name="$(basename "$f" .md)"
        all_skills["$name"]=1
    done

    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        codex="--"
        claude="--"
        [ -d "$CODEX_SRC/$skill" ] && codex="yes"
        [ -f "$CLAUDE_SRC/$skill.md" ] && claude="yes"
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
