#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$ROOT_DIR/skills"
OVERLAYS_DIR="$ROOT_DIR/overlays"
BUILD_DIR="$ROOT_DIR/build"

CODEX_INSTALL="$HOME/.agents/skills"
CLAUDE_SKILLS_INSTALL="$HOME/.claude/skills"

CLIS=(claude codex)
RUNTIME_EXCLUSIONS_DIR="$ROOT_DIR/runtime-exclusions"

# Keys that belong in overlays, not in generic SKILL.md.
# When no overlay exists for a CLI, these keys are stripped from the build.
CLI_SPECIFIC_KEYS="allowed-tools"

usage() {
    cat <<'USAGE'
Usage: stitch-skills.sh <command>

Commands:
  repo-layout   Validate skills/ and overlays/ directories exist
  assemble      Build assembled output in build/ from skills/ + overlays/
  install       Assemble, then copy build/ output to install locations
  check         Run compare + diff checks against assembled output
  all           repo-layout + install + check
USAGE
    exit 1
}

# ---------------------------------------------------------------------------
# Frontmatter helpers (pure awk)
# ---------------------------------------------------------------------------

# Print only the frontmatter lines (between --- fences), excluding the fences.
extract_frontmatter() {
    awk '
        NR==1 && $0=="---" { in_fm=1; next }
        in_fm && $0=="---" { exit }
        in_fm { print }
    ' "$1"
}

# Print everything after the closing --- fence of the frontmatter.
extract_body() {
    awk '
        NR==1 && $0=="---" { in_fm=1; next }
        in_fm && $0=="---" { in_fm=0; next }
        !in_fm { print }
    ' "$1"
}

# Merge overlay keys into frontmatter.
# stdin = original frontmatter lines, $1 = overlay file path.
# Overlay keys overwrite originals; new keys are appended.
merge_overlay() {
    local overlay_file="$1"
    local -a orig_lines=()
    local -A orig_keys=()
    local -A overlay_map=()
    local -a overlay_order=()
    local line key val

    # Read original frontmatter from stdin
    while IFS= read -r line; do
        orig_lines+=("$line")
        if [[ "$line" =~ ^([A-Za-z0-9_-]+):[[:space:]]*(.*) ]]; then
            orig_keys["${BASH_REMATCH[1]}"]=1
        fi
    done

    # Read overlay file
    while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        if [[ "$line" =~ ^([A-Za-z0-9_-]+):[[:space:]]*(.*) ]]; then
            key="${BASH_REMATCH[1]}"
            val="${BASH_REMATCH[2]}"
            overlay_map["$key"]="$val"
            overlay_order+=("$key")
        fi
    done < "$overlay_file"

    # Output original lines, replacing values for overlay keys
    for line in "${orig_lines[@]}"; do
        if [[ "$line" =~ ^([A-Za-z0-9_-]+):[[:space:]]*(.*) ]]; then
            key="${BASH_REMATCH[1]}"
            if [[ -n "${overlay_map[$key]+x}" ]]; then
                echo "$key: ${overlay_map[$key]}"
                unset "overlay_map[$key]"
                continue
            fi
        fi
        echo "$line"
    done

    # Append any remaining overlay keys not in original
    for key in "${overlay_order[@]}"; do
        if [[ -n "${overlay_map[$key]+x}" ]]; then
            echo "$key: ${overlay_map[$key]}"
        fi
    done
}

# Strip CLI-specific keys from frontmatter string (stdin -> stdout).
strip_cli_keys() {
    awk -v keys="$CLI_SPECIFIC_KEYS" '
        BEGIN { split(keys, ka, ","); for (i in ka) { gsub(/^ +| +$/, "", ka[i]); strip[ka[i]]=1 } }
        {
            key=$0; sub(/:.*/, "", key)
            if (key in strip) next
            print
        }
    '
}

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

ensure_repo_layout() {
    local ok=1
    if [[ ! -d "$SKILLS_DIR" ]]; then
        echo "ERROR: skills/ directory not found" >&2
        ok=0
    fi
    if [[ ! -d "$OVERLAYS_DIR" ]]; then
        echo "ERROR: overlays/ directory not found" >&2
        ok=0
    fi
    [[ "$ok" -eq 1 ]] && echo "repo-layout OK: skills/ and overlays/ present"
    return $(( ok == 0 ))
}

manifest_path() {
    local dir="$1"
    if [[ -f "$dir/SKILL.md" ]]; then
        echo "$dir/SKILL.md"
    elif [[ -f "$dir/skill.md" ]]; then
        echo "$dir/skill.md"
    else
        return 1
    fi
}

is_runtime_excluded() {
    local cli="$1" skill_name="$2"
    local exclusions="$RUNTIME_EXCLUSIONS_DIR/$cli.txt"
    [[ -f "$exclusions" ]] || return 1
    grep -qxF "$skill_name" <(grep -v '^[[:space:]]*#' "$exclusions" | sed '/^[[:space:]]*$/d')
}

assemble_skills() {
    echo "Assembling skills into $BUILD_DIR ..."
    rm -rf "$BUILD_DIR"

    local skill_dir skill_name manifest cli overlay_file
    local fm body merged

    for skill_dir in "$SKILLS_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"

        manifest="$(manifest_path "$skill_dir")" || {
            echo "  SKIP (no manifest): $skill_name"
            continue
        }

        fm="$(extract_frontmatter "$manifest")"
        body="$(extract_body "$manifest")"

        for cli in "${CLIS[@]}"; do
            if is_runtime_excluded "$cli" "$skill_name"; then
                echo "  SKIP [$cli] runtime-owned conflict: $skill_name"
                continue
            fi
            local out_dir="$BUILD_DIR/$cli/skills/$skill_name"
            mkdir -p "$out_dir"

            # Merge overlay if present; otherwise strip CLI-specific keys
            overlay_file="$OVERLAYS_DIR/$cli/${skill_name}.yml"
            if [[ -f "$overlay_file" ]]; then
                merged="$(echo "$fm" | merge_overlay "$overlay_file")"
            else
                merged="$(echo "$fm" | strip_cli_keys)"
            fi

            # Write assembled SKILL.md
            {
                echo "---"
                echo "$merged"
                echo "---"
                echo "$body"
            } > "$out_dir/SKILL.md"

            # Copy supporting files (scripts/, agents/, templates/, etc.)
            for sub in "$skill_dir"*/; do
                [[ -d "$sub" ]] || continue
                local sub_name
                sub_name="$(basename "$sub")"
                cp -a "$sub" "$out_dir/$sub_name"
            done

            # Copy any non-SKILL.md files at the skill root (e.g. .py, .json)
            for f in "$skill_dir"*; do
                [[ -f "$f" ]] || continue
                local fname
                fname="$(basename "$f")"
                [[ "$fname" == "SKILL.md" || "$fname" == "skill.md" ]] && continue
                cp -a "$f" "$out_dir/$fname"
            done

        done
    done

    # Shared primitives live one level above installed skill directories so
    # skill links such as ../../references/<name>.md resolve in every runtime.
    if [[ -d "$ROOT_DIR/references" ]]; then
        for cli in "${CLIS[@]}"; do
            mkdir -p "$BUILD_DIR/$cli/references"
            cp -a "$ROOT_DIR/references/." "$BUILD_DIR/$cli/references/"
        done
    fi

    # Count assembled skills
    local claude_count codex_count
    claude_count="$(find "$BUILD_DIR/claude/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
    codex_count="$(find "$BUILD_DIR/codex/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
    echo "Assembled: claude=$claude_count skills, codex=$codex_count skills"
}

install_skills() {
    ensure_repo_layout
    assemble_skills

    echo ""
    echo "Installing from assembled output ..."

    local skill_name installed=0

    # Codex: ~/.agents/skills/ — overwrite managed skills, leave others untouched
    mkdir -p "$CODEX_INSTALL"
    for skill_dir in "$BUILD_DIR/codex/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        rm -rf "$CODEX_INSTALL/$skill_name"
        cp -a "$skill_dir" "$CODEX_INSTALL/$skill_name"
        installed=$((installed + 1))
    done
    echo "  Codex: $installed skills -> $CODEX_INSTALL"
    if [[ -d "$BUILD_DIR/codex/references" ]]; then
        mkdir -p "$(dirname "$CODEX_INSTALL")/references"
        cp -a "$BUILD_DIR/codex/references/." "$(dirname "$CODEX_INSTALL")/references/"
    fi

    # Claude skills: ~/.claude/skills/ — overwrite managed skills, leave others untouched
    mkdir -p "$CLAUDE_SKILLS_INSTALL"
    installed=0
    for skill_dir in "$BUILD_DIR/claude/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        rm -rf "$CLAUDE_SKILLS_INSTALL/$skill_name"
        cp -a "$skill_dir" "$CLAUDE_SKILLS_INSTALL/$skill_name"
        installed=$((installed + 1))
    done
    echo "  Claude skills: $installed skills -> $CLAUDE_SKILLS_INSTALL"
    if [[ -d "$BUILD_DIR/claude/references" ]]; then
        mkdir -p "$(dirname "$CLAUDE_SKILLS_INSTALL")/references"
        cp -a "$BUILD_DIR/claude/references/." "$(dirname "$CLAUDE_SKILLS_INSTALL")/references/"
    fi

    echo "Done."
}

check_sync() {
    ensure_repo_layout

    # Ensure build exists
    if [[ ! -d "$BUILD_DIR/claude/skills" || ! -d "$BUILD_DIR/codex/skills" ]]; then
        echo "No assembled output found. Running assemble first ..."
        assemble_skills
    fi

    local has_issue=0

    echo "=== Checking installed vs assembled ==="
    for cli_label in codex claude; do
        local install_dir
        if [[ "$cli_label" == "codex" ]]; then
            install_dir="$CODEX_INSTALL"
        else
            install_dir="$CLAUDE_SKILLS_INSTALL"
        fi

        [[ -d "$install_dir" ]] || { echo "  SKIP $cli_label: install dir not found"; continue; }

        local build_skills="$BUILD_DIR/$cli_label/skills"
        for skill_dir in "$build_skills"/*/; do
            [[ -d "$skill_dir" ]] || continue
            local sname
            sname="$(basename "$skill_dir")"
            if [[ ! -d "$install_dir/$sname" ]]; then
                echo "  MISSING [$cli_label]: $sname (not installed)"
                has_issue=1
            elif ! diff -rq "$skill_dir" "$install_dir/$sname" > /dev/null 2>&1; then
                echo "  MODIFIED [$cli_label]: $sname"
                has_issue=1
            fi
        done
    done

    if [[ "$has_issue" -eq 0 ]]; then
        echo "PASS: installed skills match assembled output"
    else
        echo "FAIL: some skills differ from assembled output"
        return 1
    fi
}

[[ $# -lt 1 ]] && usage

case "$1" in
    repo-layout) ensure_repo_layout ;;
    assemble)    assemble_skills ;;
    install)     install_skills ;;
    check)       check_sync ;;
    all)
        ensure_repo_layout
        install_skills
        check_sync
        ;;
    *) usage ;;
esac
