#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_SRC="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
CODEX_SYSTEM_SRC="${CODEX_SYSTEM_SKILLS_DIR:-$CODEX_SRC/.system}"
PI_SRC="${PI_SKILLS_DIR:-$HOME/.pi/agent/skills}"
CLAUDE_SRC="$HOME/.claude/skills"
REPO_SKILLS_DIR="$SKILLS_DIR/skills"
BUILD_DIR="$SKILLS_DIR/build"
STITCH_SCRIPT="$SKILLS_DIR/stitch-skills.sh"
RUNTIME_EXCLUSIONS_DIR="$SKILLS_DIR/runtime-exclusions"
CAPABILITY_CATALOG="$SKILLS_DIR/capabilities/skills.toml"

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

is_runtime_excluded() {
    local cli="$1" skill_name="$2"
    local exclusions="$RUNTIME_EXCLUSIONS_DIR/$cli.txt"
    [[ -f "$exclusions" ]] || return 1
    grep -qxF "$skill_name" <(grep -v '^[[:space:]]*#' "$exclusions" | sed '/^[[:space:]]*$/d')
}

has_capability_entry() {
    local skill_name="$1"
    [[ -f "$CAPABILITY_CATALOG" ]] || return 1
    grep -qxF "[skills.$skill_name]" "$CAPABILITY_CATALOG"
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
  source-coverage          Verify every installed Pi/Codex skill is represented here
  compare-implementations  Compare skill parity across repo, Codex, and Claude
  audit-catalog            Audit loaded roots for divergent names and bloat
  capability-health        Report unavailable command/MCP/platform dependencies

Installed locations:
  Codex skills:     ~/.codex/skills/
  Pi skills:        ~/.pi/agent/skills/
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
        cp -aL "$CODEX_SRC/$skill_name" "$REPO_SKILLS_DIR/$skill_name"
    done < <(list_skill_names "$CODEX_SRC")

    echo "Pulling Pi-only skills from $PI_SRC ..."
    while IFS= read -r skill_name; do
        if is_excluded "$skill_name"; then
            echo "  SKIP (excluded): $skill_name"
            skipped=$((skipped + 1))
            continue
        fi
        if [[ -d "$REPO_SKILLS_DIR/$skill_name" ]]; then
            continue
        fi
        cp -aL "$PI_SRC/$skill_name" "$REPO_SKILLS_DIR/$skill_name"
        echo "  NEW (from pi/agent/skills): $skill_name"
    done < <(list_skill_names "$PI_SRC")

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
        cp -aL "$CLAUDE_SRC/$skill_name" "$REPO_SKILLS_DIR/$skill_name"
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
        IFS=',' read -ra _keys <<< "$CLI_SPECIFIC_KEYS"
        for key in "${_keys[@]}"; do
            key="${key## }"; key="${key%% }"
            if has_frontmatter_key "$key" "$manifest"; then
                echo "  WARN: $sname has '$key' — should be in overlays/claude/$sname.yml. Stripping."
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

    echo "=== Codex skills (~/.codex/skills/) ==="
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
    echo "=== Pi skills (~/.pi/agent/skills/) ==="
    for skill_dir in "$REPO_SKILLS_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        if [ -d "$PI_SRC/$skill_name" ]; then
            if ! diff -rq "$skill_dir" "$PI_SRC/$skill_name" > /dev/null 2>&1; then
                echo "  MODIFIED: $skill_name"
                has_diff=1
            fi
        else
            echo "  MISSING (not installed): $skill_name"
            has_diff=1
        fi
    done

    while IFS= read -r skill_name; do
        if [ ! -d "$REPO_SKILLS_DIR/$skill_name" ]; then
            echo "  INSTALLED ONLY: $skill_name"
            has_diff=1
        fi
    done < <(list_skill_names "$PI_SRC")

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
        echo "  Pi skills: repo $(count_skill_names "$REPO_SKILLS_DIR"), installed $(count_skill_names "$PI_SRC")"
        echo "  Claude skills: assembled $(find "$BUILD_DIR/claude/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '), installed $(count_skill_names "$CLAUDE_SRC")"
        echo "Everything in sync."
    fi
}

compare_implementations() {
    local has_issue=0
    local skill
    local in_repo
    local in_codex
    local in_pi
    local in_claude
    local runtime_only
    declare -A all_skills

    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$REPO_SKILLS_DIR")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SYSTEM_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$PI_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CLAUDE_SRC")

    echo "=== Skill Name Parity (repo/codex/pi/claude) ==="
    while IFS= read -r skill; do
        in_repo="no"
        in_codex="no"
        in_pi="no"
        in_claude="no"
        runtime_only="no"
        [ -d "$REPO_SKILLS_DIR/$skill" ] && in_repo="yes"
        [ -d "$CODEX_SRC/$skill" ] && in_codex="yes"
        if [[ "$in_codex" == "no" ]] && is_runtime_excluded codex "$skill" && [[ -d "$CODEX_SYSTEM_SRC/$skill" ]]; then
            in_codex="runtime"
            if [[ "$in_repo" == "no" ]]; then
                in_repo="catalog"
                runtime_only="yes"
            fi
        fi
        [ -d "$PI_SRC/$skill" ] && in_pi="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && in_claude="yes"

        if [[ "$runtime_only" == "yes" ]]; then
            continue
        fi
        if [ "$in_repo" != "yes" ] || [[ "$in_codex" != "yes" && "$in_codex" != "runtime" ]] || [ "$in_pi" != "yes" ] || [ "$in_claude" != "yes" ]; then
            printf "  MISMATCH: %-30s repo=%s codex=%s pi=%s claude=%s\n" "$skill" "$in_repo" "$in_codex" "$in_pi" "$in_claude"
            has_issue=1
        fi
    done < <(printf '%s\n' "${!all_skills[@]}" | sort)

    echo ""
    echo "Summary:"
    echo "  repo=$(count_skill_names "$REPO_SKILLS_DIR"), codex=$(count_skill_names "$CODEX_SRC"), pi=$(count_skill_names "$PI_SRC"), claude=$(count_skill_names "$CLAUDE_SRC")"

    if [ "$has_issue" -eq 0 ]; then
        echo "PASS: repo, Codex, Pi, and Claude skill sets are consistent."
    else
        echo "FAIL: Skill sets are out of sync."
        return 1
    fi
}

source_coverage() {
    local has_issue=0
    local skill
    local root
    local label

    for root in "$CODEX_SRC" "$PI_SRC"; do
        if [[ "$root" == "$CODEX_SRC" ]]; then
            label="codex"
        else
            label="pi"
        fi
        while IFS= read -r skill; do
            if [[ ! -d "$REPO_SKILLS_DIR/$skill" ]]; then
                echo "MISSING SOURCE [$label]: $skill"
                has_issue=1
            fi
        done < <(list_skill_names "$root")
    done

    while IFS= read -r skill; do
        if ! is_runtime_excluded codex "$skill"; then
            echo "MISSING RUNTIME EXCLUSION [codex]: $skill"
            has_issue=1
            continue
        fi
        if ! has_capability_entry "$skill"; then
            echo "MISSING CAPABILITY CATALOG ENTRY [codex]: $skill"
            has_issue=1
        fi
    done < <(list_skill_names "$CODEX_SYSTEM_SRC")

    if [[ "$has_issue" -eq 0 ]]; then
        echo "PASS: every installed Pi and Codex skill has package source or a Codex runtime-owned catalog entry."
    else
        echo "FAIL: installed skills are missing from package source or runtime ownership metadata."
        return 1
    fi
}

status() {
    local skill
    local repo
    local codex
    local pi
    local claude
    declare -A all_skills

    printf "%-35s %-8s %-8s %-8s %-8s\n" "SKILL" "REPO" "CODEX" "PI" "CLAUDE"
    printf "%-35s %-8s %-8s %-8s %-8s\n" "-----" "----" "-----" "--" "------"

    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$REPO_SKILLS_DIR")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CODEX_SYSTEM_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$PI_SRC")
    while IFS= read -r skill; do all_skills["$skill"]=1; done < <(list_skill_names "$CLAUDE_SRC")

    while IFS= read -r skill; do
        repo="--"
        codex="--"
        pi="--"
        claude="--"
        [ -d "$REPO_SKILLS_DIR/$skill" ] && repo="yes"
        [ -d "$CODEX_SRC/$skill" ] && codex="yes"
        if [[ "$codex" == "--" ]] && is_runtime_excluded codex "$skill" && [[ -d "$CODEX_SYSTEM_SRC/$skill" ]]; then
            codex="runtime"
            [[ "$repo" == "--" ]] && repo="catalog"
        fi
        [ -d "$PI_SRC/$skill" ] && pi="yes"
        [ -d "$CLAUDE_SRC/$skill" ] && claude="yes"
        printf "%-35s %-8s %-8s %-8s %-8s\n" "$skill" "$repo" "$codex" "$pi" "$claude"
    done < <(printf '%s\n' "${!all_skills[@]}" | sort)

    echo ""
    echo "Totals: repo=$(count_skill_names "$REPO_SKILLS_DIR"), codex=$(count_skill_names "$CODEX_SRC") user + $(count_skill_names "$CODEX_SYSTEM_SRC") runtime, pi=$(count_skill_names "$PI_SRC"), claude=$(count_skill_names "$CLAUDE_SRC")"
}

[ $# -lt 1 ] && usage

case "$1" in
    pull)   pull ;;
    push)   push ;;
    diff)   do_diff ;;
    compare-implementations) compare_implementations ;;
    source-coverage) source_coverage ;;
    audit-catalog) python3 "$SKILLS_DIR/scripts/audit_catalog.py" "${@:2}" ;;
    capability-health) python3 "$SKILLS_DIR/scripts/capability_health.py" "${@:2}" ;;
    status) status ;;
    *)      usage ;;
esac
