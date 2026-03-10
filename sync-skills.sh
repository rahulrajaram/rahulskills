#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_SRC="$HOME/.agents/skills"
CLAUDE_SRC="$HOME/.claude/skills"
REPO_SKILLS_DIR="$SKILLS_DIR/skills"
BUILD_DIR="$SKILLS_DIR/build"
STITCH_SCRIPT="$SKILLS_DIR/stitch-skills.sh"

# Exclusion list — one skill name per line, lines starting with # are ignored.
# This file is gitignored so each machine can maintain its own private list.
EXCLUDE_FILE="$SKILLS_DIR/.exclude-skills"

# Keys that belong in overlays, not in generic SKILL.md frontmatter
CLI_SPECIFIC_KEYS="allowed-tools"

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

count_skill_names() {
    local base="$1"
    list_skill_names "$base" | wc -l | tr -d ' '
}

usage() {
    cat <<'USAGE'
Usage: sync-skills.sh <command>

Commands:
  pull      Copy skills FROM installed locations INTO this repo
  push      Assemble and install skills to all CLI locations
  diff      Show differences between assembled output and installed skills
  status    List which skills exist where
  compare-implementations  Compare skill parity across repo, Codex, and Claude

Installed locations:
  Codex skills:     ~/.agents/skills/
  Claude skills:    ~/.claude/skills/
USAGE
    exit 1
}

# Check if a frontmatter key exists in a manifest file
has_frontmatter_key() {
    local key="$1" file="$2"
    awk -v want="$key" '
        NR==1 && $0=="---" {in_fm=1; next}
        in_fm && $0=="---" {exit}
        in_fm && $0 ~ /^[A-Za-z0-9_-]+:/ {
            k=$0; sub(/:.*/, "", k)
            if (k==want) {found=1}
        }
        END {exit found ? 0 : 1}
    ' "$file"
}

# Strip CLI-specific keys from frontmatter (used during pull)
strip_cli_keys() {
    local file="$1"
    local tmpfile
    tmpfile="$(mktemp)"
    awk -v keys="$CLI_SPECIFIC_KEYS" '
        BEGIN { split(keys, ka, ","); for (i in ka) { gsub(/^ +| +$/, "", ka[i]); strip[ka[i]]=1 } }
        NR==1 && $0=="---" { in_fm=1; print; next }
        in_fm && $0=="---" { in_fm=0; print; next }
        in_fm {
            key=$0; sub(/:.*/, "", key)
            if (key in strip) { next }
        }
        { print }
    ' "$file" > "$tmpfile"
    mv "$tmpfile" "$file"
}

pull() {
    local skipped=0
    local skill_name
    local warnings=0

    echo "Pulling Codex skills from $CODEX_SRC ..."
    mkdir -p "$REPO_SKILLS_DIR"
    while IFS= read -r skill_name; do
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            rm -rf "$REPO_SKILLS_DIR/$skill_name"
            continue
        fi
        rm -rf "$REPO_SKILLS_DIR/$skill_name"
        cp -a "$CODEX_SRC/$skill_name" "$REPO_SKILLS_DIR/$skill_name"
    done < <(list_skill_names "$CODEX_SRC")

    echo "Pulling Claude skills from $CLAUDE_SRC ..."
    while IFS= read -r skill_name; do
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            continue
        fi
        if [[ -d "$REPO_SKILLS_DIR/$skill_name" ]]; then
            # Already pulled from Codex source, skip
            continue
        fi
        cp -a "$CLAUDE_SRC/$skill_name" "$REPO_SKILLS_DIR/$skill_name"
        echo "  NEW (from claude/skills): $skill_name"
    done < <(list_skill_names "$CLAUDE_SRC")

    # Strip CLI-specific keys from pulled skills and warn
    echo ""
    echo "Checking pulled skills for CLI-specific keys ..."
    for skill_dir in "$REPO_SKILLS_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local manifest
        manifest=""
        [[ -f "$skill_dir/SKILL.md" ]] && manifest="$skill_dir/SKILL.md"
        [[ -f "$skill_dir/skill.md" ]] && manifest="$skill_dir/skill.md"
        [[ -n "$manifest" ]] || continue

        local sname
        sname="$(basename "$skill_dir")"
        for key in $CLI_SPECIFIC_KEYS; do
            if has_frontmatter_key "$key" "$manifest"; then
                echo "  WARN: $sname has '$key' — should be in overlays/$key. Stripping."
                warnings=$((warnings + 1))
            fi
        done
        strip_cli_keys "$manifest"
    done

    echo ""
    echo "Skills: $(count_skill_names "$REPO_SKILLS_DIR")"
    [ "$skipped" -gt 0 ] && echo "Excluded: $skipped"
    [ "$warnings" -gt 0 ] && echo "Warnings: $warnings (CLI-specific keys stripped)"
    echo "Done. Review with: cd $SKILLS_DIR && git diff"
}

push() {
    echo "Delegating to stitch-skills.sh install ..."
    "$STITCH_SCRIPT" install
}

do_diff() {
    local has_diff=0
    local skill_name

    # Ensure assembled output exists
    if [[ ! -d "$BUILD_DIR/claude/skills" || ! -d "$BUILD_DIR/codex/skills" ]]; then
        echo "No assembled output found. Running assemble first ..."
        "$STITCH_SCRIPT" assemble
    fi

    echo "=== Codex skills (~/.agents/skills/) ==="
    for skill_dir in "$BUILD_DIR/codex/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if [ -d "$CODEX_SRC/$skill_name" ]; then
            if ! diff -rq "$skill_dir" "$CODEX_SRC/$skill_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $skill_name"
                diff -ru "$CODEX_SRC/$skill_name" "$skill_dir" || true
                has_diff=1
            fi
        else
            echo "  NEW (not installed): $skill_name"
            has_diff=1
        fi
    done

    while IFS= read -r skill_name; do
        if [ ! -d "$BUILD_DIR/codex/skills/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$CODEX_SRC")

    echo ""
    echo "=== Claude skills (~/.claude/skills/) ==="
    for skill_dir in "$BUILD_DIR/claude/skills"/*/; do
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

    while IFS= read -r skill_name; do
        if [ ! -d "$BUILD_DIR/claude/skills/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$CLAUDE_SRC")

    if [ "$has_diff" -eq 0 ]; then
        echo ""
        echo "Summary:"
        echo "  Codex skills: assembled $(find "$BUILD_DIR/codex/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '), installed $(count_skill_names "$CODEX_SRC")"
        echo "  Claude skills: assembled $(find "$BUILD_DIR/claude/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '), installed $(count_skill_names "$CLAUDE_SRC")"
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

    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$REPO_SKILLS_DIR")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CLAUDE_SRC")

    echo "=== Skill Name Parity (repo/codex/claude) ==="
    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        in_repo="no"
        in_codex="no"
        in_claude="no"
        [ -d "$REPO_SKILLS_DIR/$skill" ] && in_repo="yes"
        [ -d "$CODEX_SRC/$skill" ] && in_codex="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && in_claude="yes"

        if [ "$in_repo" != "yes" ] || [ "$in_codex" != "yes" ] || [ "$in_claude" != "yes" ]; then
            printf "  MISMATCH: %-30s repo=%s codex=%s claude=%s\n" "$skill" "$in_repo" "$in_codex" "$in_claude"
            has_issue=1
        fi
    done

    echo ""
    echo "Summary:"
    echo "  repo=$(count_skill_names "$REPO_SKILLS_DIR"), codex=$(count_skill_names "$CODEX_SRC"), claude=$(count_skill_names "$CLAUDE_SRC")"

    if [ "$has_issue" -eq 0 ]; then
        echo "PASS: Codex and Claude skill sets are consistent."
    else
        echo "FAIL: Skill sets are out of sync."
        return 1
    fi
}

status() {
    local skill
    local codex
    local claude
    declare -A all_skills

    printf "%-35s %-8s %-8s\n" "SKILL" "CODEX" "CLAUDE"
    printf "%-35s %-8s %-8s\n" "-----" "-----" "------"

    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CLAUDE_SRC")

    for skill in $(echo "${!all_skills[@]}" | tr ' ' '\n' | sort); do
        codex="--"
        claude="--"
        [ -d "$CODEX_SRC/$skill" ] && codex="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && claude="yes"
        printf "%-35s %-8s %-8s\n" "$skill" "$codex" "$claude"
    done

    echo ""
    echo "Totals: codex=$(count_skill_names "$CODEX_SRC"), claude=$(count_skill_names "$CLAUDE_SRC")"
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
