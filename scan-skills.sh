#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
LISTINGS="$HOME/Documents/listings.txt"
CODEX_EXCLUDE_FILE="$SKILLS_DIR/.exclude-codex"
CLAUDE_EXCLUDE_FILE="$SKILLS_DIR/.exclude-claude"
REPORT_FILE="$SKILLS_DIR/skill-candidates.md"

# Collected skill/command names for status tagging
collected_commands=()
collected_skills=()
excluded_commands=()
excluded_skills=()

load_collected() {
    local f
    for f in "$SKILLS_DIR/claude"/*.md; do
        [[ -f "$f" ]] && collected_commands+=("$(basename "$f" .md)")
    done
    for f in "$SKILLS_DIR/codex"/*/; do
        [[ -d "$f" ]] && collected_skills+=("$(basename "$f")")
    done
    if [[ -f "$CLAUDE_EXCLUDE_FILE" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" || "$line" == \#* ]] && continue
            excluded_commands+=("$line")
        done < "$CLAUDE_EXCLUDE_FILE"
    fi
    if [[ -f "$CODEX_EXCLUDE_FILE" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" || "$line" == \#* ]] && continue
            excluded_skills+=("$line")
        done < "$CODEX_EXCLUDE_FILE"
    fi
}

in_array() {
    local needle="$1"; shift
    local item
    for item in "$@"; do [[ "$item" == "$needle" ]] && return 0; done
    return 1
}

# Tag a name: [COLLECTED], [EXCLUDED], or [NEW]
tag_item() {
    local name="$1" type="$2"
    if [[ "$type" == "cmd" ]]; then
        in_array "$name" "${collected_commands[@]+"${collected_commands[@]}"}" && { echo "[COLLECTED]"; return; }
        in_array "$name" "${excluded_commands[@]+"${excluded_commands[@]}"}" && { echo "[EXCLUDED]"; return; }
    elif [[ "$type" == "skl" ]]; then
        in_array "$name" "${collected_skills[@]+"${collected_skills[@]}"}" && { echo "[COLLECTED]"; return; }
        in_array "$name" "${excluded_skills[@]+"${excluded_skills[@]}"}" && { echo "[EXCLUDED]"; return; }
    fi
    echo "[NEW]"
}

usage() {
    cat <<'EOF'
Usage: scan-skills.sh <command>

Commands:
  scan     Detailed per-project report of discovered skills/scripts
  check    Compact counts-only table for quick dashboarding
  report   Generate persistent skill-candidates.md tracking file
EOF
    exit 1
}

# Read project paths from listings.txt, returns lines of "path|description"
read_projects() {
    [[ -f "$LISTINGS" ]] || { echo "Error: $LISTINGS not found" >&2; exit 1; }
    while IFS= read -r line; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        local proj_path
        proj_path="$(echo "$line" | cut -d'|' -f1 | xargs)"
        [[ -z "$proj_path" ]] && continue
        # Skip self
        [[ "$(realpath "$proj_path" 2>/dev/null)" == "$(realpath "$SKILLS_DIR")" ]] && continue
        echo "$proj_path"
    done < "$LISTINGS"
}

# Count items in a glob pattern (returns 0 if none match)
count_glob() {
    local pattern="$1"
    # shellcheck disable=SC2086
    local files
    files=( $pattern ) 2>/dev/null || true
    [[ -e "${files[0]:-}" ]] && echo "${#files[@]}" || echo 0
}

# List items from a glob pattern
list_glob() {
    local pattern="$1"
    local files
    files=( $pattern ) 2>/dev/null || true
    [[ -e "${files[0]:-}" ]] || return 0
    for f in "${files[@]}"; do
        basename "$f"
    done
}

# Count Makefile/justfile targets
count_build_targets() {
    local proj="$1"
    local count=0
    if [[ -f "$proj/Makefile" ]]; then
        count=$((count + $(grep -cE '^[a-zA-Z_][a-zA-Z0-9_-]*:' "$proj/Makefile" 2>/dev/null || echo 0)))
    fi
    if [[ -f "$proj/justfile" ]]; then
        count=$((count + $(grep -cE '^[a-zA-Z_][a-zA-Z0-9_-]*:' "$proj/justfile" 2>/dev/null || echo 0)))
    fi
    echo "$count"
}

# List Makefile/justfile targets
list_build_targets() {
    local proj="$1"
    for bf in "$proj/Makefile" "$proj/justfile"; do
        [[ -f "$bf" ]] || continue
        grep -oE '^[a-zA-Z_][a-zA-Z0-9_-]*:' "$bf" 2>/dev/null | sed 's/:$//' || true
    done
}

# Print items with overflow, tagging Tier 1 items
print_items() {
    local label="$1" tag_type="$2"; shift 2
    local items=("$@")
    local total=${#items[@]}
    [[ $total -eq 0 ]] && return
    local show=5
    echo "  $label ($total):"
    local i=0
    for item in "${items[@]}"; do
        [[ $i -ge $show ]] && break
        if [[ -n "$tag_type" ]]; then
            local name="${item%.md}"
            local tag
            tag="$(tag_item "$name" "$tag_type")"
            echo "    $item $tag"
        else
            echo "    $item"
        fi
        i=$((i + 1))
    done
    local remaining=$((total - show))
    [[ $remaining -gt 0 ]] && echo "    (+ $remaining more)"
    return 0
}

do_scan() {
    load_collected
    local projects
    projects="$(read_projects)"

    while IFS= read -r proj; do
        [[ -d "$proj" ]] || { echo "WARN: $proj does not exist, skipping" >&2; continue; }

        local name
        name="$(basename "$proj")"

        # Gather items
        local cmds=() skls=() agts=() ins=() scrs=() blds=()

        # Tier 1: Claude commands
        while IFS= read -r f; do [[ -n "$f" ]] && cmds+=("$f"); done < <(list_glob "$proj/.claude/commands/*.md")
        # Tier 1: Codex skills
        if [[ -d "$proj/.agents/skills" ]]; then
            for d in "$proj/.agents/skills"/*/; do
                [[ -d "$d" ]] && skls+=("$(basename "$d")")
            done
        fi
        # Tier 1: Claude agents
        while IFS= read -r f; do [[ -n "$f" ]] && agts+=("$f"); done < <(list_glob "$proj/.claude/agents/*.md")

        # Tier 2: Instruction files
        [[ -f "$proj/CLAUDE.md" ]] && ins+=("CLAUDE.md")
        [[ -f "$proj/AGENTS.md" ]] && ins+=("AGENTS.md")

        # Tier 3: Scripts
        for dir in scripts bin tools; do
            if [[ -d "$proj/$dir" ]]; then
                for f in "$proj/$dir"/*; do
                    [[ -f "$f" ]] && scrs+=("$dir/$(basename "$f")")
                done
            fi
        done

        # Tier 4: Build targets
        while IFS= read -r t; do [[ -n "$t" ]] && blds+=("$t"); done < <(list_build_targets "$proj")

        local total=$(( ${#cmds[@]} + ${#skls[@]} + ${#agts[@]} + ${#ins[@]} + ${#scrs[@]} + ${#blds[@]} ))
        [[ $total -eq 0 ]] && continue

        echo "=== $name ==="
        echo "  $proj"
        print_items "Commands (CMD)" "cmd" "${cmds[@]+"${cmds[@]}"}"
        print_items "Skills (SKL)" "skl" "${skls[@]+"${skls[@]}"}"
        print_items "Agents (AGT)" "" "${agts[@]+"${agts[@]}"}"
        print_items "Instructions (INS)" "" "${ins[@]+"${ins[@]}"}"
        print_items "Scripts (SCR)" "" "${scrs[@]+"${scrs[@]}"}"
        print_items "Build targets (BLD)" "" "${blds[@]+"${blds[@]}"}"
        echo ""
    done <<< "$projects"
}

do_check() {
    local projects
    projects="$(read_projects)"

    printf "%-35s %4s %4s %4s %4s %4s %4s\n" "PROJECT" "CMD" "SKL" "AGT" "INS" "SCR" "BLD"

    local t_cmd=0 t_skl=0 t_agt=0 t_ins=0 t_scr=0 t_bld=0

    while IFS= read -r proj; do
        [[ -d "$proj" ]] || continue

        local name
        name="$(basename "$proj")"

        local n_cmd n_skl n_agt n_ins n_scr n_bld
        n_cmd=$(count_glob "$proj/.claude/commands/*.md")

        # Count skill dirs
        if [[ -d "$proj/.agents/skills" ]]; then
            local sd=( "$proj/.agents/skills"/*/ ) 2>/dev/null || true
            [[ -d "${sd[0]:-}" ]] && n_skl=${#sd[@]} || n_skl=0
        else
            n_skl=0
        fi

        n_agt=$(count_glob "$proj/.claude/agents/*.md")

        n_ins=0
        [[ -f "$proj/CLAUDE.md" ]] && n_ins=$((n_ins + 1))
        [[ -f "$proj/AGENTS.md" ]] && n_ins=$((n_ins + 1))

        n_scr=0
        for dir in scripts bin tools; do
            if [[ -d "$proj/$dir" ]]; then
                for f in "$proj/$dir"/*; do
                    [[ -f "$f" ]] && n_scr=$((n_scr + 1))
                done
            fi
        done

        n_bld=$(count_build_targets "$proj")

        printf "%-35s %4d %4d %4d %4d %4d %4d\n" "$name" "$n_cmd" "$n_skl" "$n_agt" "$n_ins" "$n_scr" "$n_bld"

        t_cmd=$((t_cmd + n_cmd)); t_skl=$((t_skl + n_skl)); t_agt=$((t_agt + n_agt))
        t_ins=$((t_ins + n_ins)); t_scr=$((t_scr + n_scr)); t_bld=$((t_bld + n_bld))
    done <<< "$projects"

    printf "%-35s %4d %4d %4d %4d %4d %4d\n" "TOTAL" "$t_cmd" "$t_skl" "$t_agt" "$t_ins" "$t_scr" "$t_bld"
}

do_report() {
    load_collected

    {
        echo "# Skill Candidates"
        echo ""
        echo "Generated: $(date -Iseconds)"
        echo ""
        echo "Scanned from: $LISTINGS"
        echo ""

        local projects
        projects="$(read_projects)"

        while IFS= read -r proj; do
            [[ -d "$proj" ]] || continue

            local name
            name="$(basename "$proj")"
            local has_content=0
            local section=""

            # Tier 1: Commands
            local cmds=()
            while IFS= read -r f; do [[ -n "$f" ]] && cmds+=("$f"); done < <(list_glob "$proj/.claude/commands/*.md")
            if [[ ${#cmds[@]} -gt 0 ]]; then
                has_content=1
                section+="### Commands\n"
                for c in "${cmds[@]}"; do
                    local tag; tag="$(tag_item "${c%.md}" "cmd")"
                    section+="- \`$c\` $tag\n"
                done
                section+="\n"
            fi

            # Tier 1: Skills
            local skls=()
            if [[ -d "$proj/.agents/skills" ]]; then
                for d in "$proj/.agents/skills"/*/; do
                    [[ -d "$d" ]] && skls+=("$(basename "$d")")
                done
            fi
            if [[ ${#skls[@]} -gt 0 ]]; then
                has_content=1
                section+="### Skills\n"
                for s in "${skls[@]}"; do
                    local tag; tag="$(tag_item "$s" "skl")"
                    section+="- \`$s\` $tag\n"
                done
                section+="\n"
            fi

            # Tier 1: Agents
            local agts=()
            while IFS= read -r f; do [[ -n "$f" ]] && agts+=("$f"); done < <(list_glob "$proj/.claude/agents/*.md")
            if [[ ${#agts[@]} -gt 0 ]]; then
                has_content=1
                section+="### Agents\n"
                for a in "${agts[@]}"; do section+="- \`$a\`\n"; done
                section+="\n"
            fi

            # Tier 2: Instructions
            local ins=()
            [[ -f "$proj/CLAUDE.md" ]] && ins+=("CLAUDE.md")
            [[ -f "$proj/AGENTS.md" ]] && ins+=("AGENTS.md")
            if [[ ${#ins[@]} -gt 0 ]]; then
                has_content=1
                section+="### Instructions\n"
                for i in "${ins[@]}"; do section+="- \`$i\`\n"; done
                section+="\n"
            fi

            # Tier 3: Scripts
            local scrs=()
            for dir in scripts bin tools; do
                if [[ -d "$proj/$dir" ]]; then
                    for f in "$proj/$dir"/*; do
                        [[ -f "$f" ]] && scrs+=("$dir/$(basename "$f")")
                    done
                fi
            done
            if [[ ${#scrs[@]} -gt 0 ]]; then
                has_content=1
                section+="### Scripts\n"
                for s in "${scrs[@]}"; do section+="- \`$s\`\n"; done
                section+="\n"
            fi

            # Tier 4: Build targets
            local blds=()
            while IFS= read -r t; do [[ -n "$t" ]] && blds+=("$t"); done < <(list_build_targets "$proj")
            if [[ ${#blds[@]} -gt 0 ]]; then
                has_content=1
                section+="### Build targets\n"
                for b in "${blds[@]}"; do section+="- \`$b\`\n"; done
                section+="\n"
            fi

            if [[ $has_content -eq 1 ]]; then
                echo "## $name"
                echo ""
                echo "\`$proj\`"
                echo ""
                echo -e "$section"
            fi
        done <<< "$projects"
    } > "$REPORT_FILE"

    echo "Written: $REPORT_FILE"
    echo "$(wc -l < "$REPORT_FILE") lines"
}

[[ $# -lt 1 ]] && usage

case "$1" in
    scan)   do_scan ;;
    check)  do_check ;;
    report) do_report ;;
    *)      usage ;;
esac
