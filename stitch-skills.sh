#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$ROOT_DIR/skills"
OVERLAYS_DIR="$ROOT_DIR/overlays"
BUILD_DIR="$ROOT_DIR/build"

CODEX_INSTALL="$HOME/.codex/skills"
CLAUDE_SKILLS_INSTALL="$HOME/.claude/skills"

CLIS=(claude codex)
RUNTIME_EXCLUSIONS_DIR="$ROOT_DIR/runtime-exclusions"

# Keys that belong in overlays, not in generic SKILL.md.
# When no overlay exists for a CLI, these keys are stripped from the build.
CLI_SPECIFIC_KEYS="allowed-tools"

new_backup_root() {
    local parent="$1" label="$2"
    [[ "$label" =~ ^[a-z0-9][a-z0-9-]*$ ]] || {
        echo "ERROR: refusing unsafe backup label: $label" >&2
        return 1
    }
    mkdir -p "$parent"
    mktemp -d "$parent/${label}-$(date -u +%Y%m%dT%H%M%SZ)-$$.XXXXXX"
}

git_common_dir() {
    git -C "$ROOT_DIR" rev-parse --path-format=absolute --git-common-dir
}

assert_exact_build_target() {
    local root_real expected_real target_real
    root_real="$(realpath -e -- "$ROOT_DIR")"
    expected_real="$root_real/build"
    target_real="$(realpath -m -- "$BUILD_DIR")"

    if [[ "$target_real" != "$expected_real" || "$target_real" == "/" ]]; then
        echo "ERROR: refusing build replacement; unexpected target: $target_real" >&2
        return 1
    fi
    if [[ -L "$BUILD_DIR" ]]; then
        echo "ERROR: refusing build replacement through symlink: $BUILD_DIR" >&2
        return 1
    fi
}

assert_install_root() {
    local install_root="$1" expected_root="$2" label="$3"
    local actual_real expected_real

    [[ -n "${HOME:-}" && "$HOME" == /* && "$HOME" != "/" ]] || {
        echo "ERROR: refusing $label install; HOME is not a safe absolute path" >&2
        return 1
    }
    actual_real="$(realpath -m -- "$install_root")"
    expected_real="$(realpath -m -- "$expected_root")"
    if [[ "$actual_real" != "$expected_real" || "$actual_real" == "/" ]]; then
        echo "ERROR: refusing $label install; unexpected root: $actual_real" >&2
        return 1
    fi
    if [[ -L "$install_root" ]]; then
        echo "ERROR: refusing $label install through symlink: $install_root" >&2
        return 1
    fi
}

assert_skill_name() {
    local skill_name="$1"
    [[ "$skill_name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || {
        echo "ERROR: refusing unsafe skill name: $skill_name" >&2
        return 1
    }
}

copy_tree_without_caches() {
    local source_dir="$1" destination_dir="$2"
    mkdir -p "$destination_dir"
    tar \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        -C "$source_dir" -cf - . \
        | tar -C "$destination_dir" -xf -
}

move_existing_to_backup() {
    local target="$1" backup_root="$2" backup_name="$3"
    MOVED_BACKUP=""
    if [[ ! -e "$target" && ! -L "$target" ]]; then
        return 0
    fi

    mkdir -p "$backup_root"
    MOVED_BACKUP="$backup_root/$backup_name"
    if [[ -e "$MOVED_BACKUP" || -L "$MOVED_BACKUP" ]]; then
        echo "ERROR: refusing to overwrite backup: $MOVED_BACKUP" >&2
        return 1
    fi
    mv -- "$target" "$MOVED_BACKUP"
    echo "  Backup retained: $MOVED_BACKUP"
}

replace_installed_skill() {
    local source_dir="$1" install_root="$2" backup_root="$3" skill_name="$4"
    local target stage

    assert_skill_name "$skill_name"
    target="$install_root/$skill_name"
    [[ "$(realpath -m -- "$(dirname -- "$target")")" == "$(realpath -e -- "$install_root")" ]] || {
        echo "ERROR: refusing install outside expected root: $target" >&2
        return 1
    }

    stage="$(mktemp -d "$install_root/.${skill_name}.stage.XXXXXX")"
    cp -a "$source_dir/." "$stage/"
    move_existing_to_backup "$target" "$backup_root" "$skill_name"
    if ! mv -- "$stage" "$target"; then
        echo "ERROR: install failed; staged tree retained at $stage" >&2
        if [[ -n "$MOVED_BACKUP" && ! -e "$target" && ! -L "$target" ]]; then
            mv -- "$MOVED_BACKUP" "$target"
            echo "  Restored prior install: $target" >&2
        fi
        return 1
    fi
}

usage() {
    cat <<'USAGE'
Usage: stitch-skills.sh <command>

Commands:
  repo-layout   Validate skills/ and overlays/ directories exist
  assemble      Build assembled output in build/ from skills/ + overlays/
  install       Assemble, then copy build/ output to install locations
  check         Freshly assemble, then compare against installed output
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
    local -A overlay_map=()
    local -a overlay_order=()
    local line key val

    # Read original frontmatter from stdin
    while IFS= read -r line; do
        orig_lines+=("$line")
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

assemble_skills_into() {
    local output_root="$1"
    echo "Assembling skills into staging directory $output_root ..."

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
            local out_dir="$output_root/$cli/skills/$skill_name"
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
                [[ "$sub_name" == "__pycache__" ]] && continue
                copy_tree_without_caches "$sub" "$out_dir/$sub_name"
            done

            # Copy any non-SKILL.md files at the skill root (e.g. .py, .json)
            for f in "$skill_dir"*; do
                [[ -f "$f" ]] || continue
                local fname
                fname="$(basename "$f")"
                [[ "$fname" == "SKILL.md" || "$fname" == "skill.md" ]] && continue
                [[ "$fname" == *.pyc || "$fname" == *.pyo ]] && continue
                cp -a "$f" "$out_dir/$fname"
            done

        done
    done

    # Shared primitives live one level above installed skill directories so
    # skill links such as ../../references/<name>.md resolve in every runtime.
    if [[ -d "$ROOT_DIR/references" ]]; then
        for cli in "${CLIS[@]}"; do
            copy_tree_without_caches \
                "$ROOT_DIR/references" \
                "$output_root/$cli/references"
        done
    fi

    # Count assembled skills
    local claude_count codex_count
    claude_count="$(find "$output_root/claude/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
    codex_count="$(find "$output_root/codex/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
    echo "Assembled: claude=$claude_count skills, codex=$codex_count skills"
}

assemble_skills() {
    local stage backup_root

    ensure_repo_layout
    assert_exact_build_target
    stage="$(mktemp -d "$ROOT_DIR/.build-stage.XXXXXX")"
    # Invoke directly so `set -e` remains effective inside the function. A
    # failed assembly intentionally leaves this printed staging path intact.
    echo "Assembly staging path: $stage"
    assemble_skills_into "$stage"

    backup_root="$(new_backup_root "$(git_common_dir)/rahulskills-backups" build)"
    move_existing_to_backup "$BUILD_DIR" "$backup_root" "build"
    if ! mv -- "$stage" "$BUILD_DIR"; then
        echo "ERROR: publish failed; assembled tree retained at $stage" >&2
        if [[ -n "$MOVED_BACKUP" && ! -e "$BUILD_DIR" && ! -L "$BUILD_DIR" ]]; then
            mv -- "$MOVED_BACKUP" "$BUILD_DIR"
            echo "  Restored prior build: $BUILD_DIR" >&2
        fi
        return 1
    fi
    echo "Published assembled output: $BUILD_DIR"
}

install_skills() {
    ensure_repo_layout
    assemble_skills

    echo ""
    echo "Installing from assembled output ..."

    local skill_name installed=0 codex_backup_root claude_backup_root

    # Codex: replace managed skills with backups; leave others untouched.
    # NOT ~/.agents/skills: pi scans that global dir and would report a
    # duplicate-name collision for every codex copy.
    assert_install_root "$CODEX_INSTALL" "$HOME/.codex/skills" "Codex"
    mkdir -p "$CODEX_INSTALL"
    codex_backup_root="$(
        new_backup_root "$(dirname "$CODEX_INSTALL")/skill-backups" codex
    )"
    for skill_dir in "$BUILD_DIR/codex/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        replace_installed_skill \
            "$skill_dir" "$CODEX_INSTALL" "$codex_backup_root" "$skill_name"
        installed=$((installed + 1))
    done
    echo "  Codex: $installed skills -> $CODEX_INSTALL"
    if [[ -d "$BUILD_DIR/codex/references" ]]; then
        mkdir -p "$(dirname "$CODEX_INSTALL")/references"
        cp -a "$BUILD_DIR/codex/references/." "$(dirname "$CODEX_INSTALL")/references/"
    fi

    # Claude: replace managed skills with backups; leave others untouched.
    assert_install_root "$CLAUDE_SKILLS_INSTALL" "$HOME/.claude/skills" "Claude"
    mkdir -p "$CLAUDE_SKILLS_INSTALL"
    claude_backup_root="$(
        new_backup_root "$(dirname "$CLAUDE_SKILLS_INSTALL")/skill-backups" claude
    )"
    installed=0
    for skill_dir in "$BUILD_DIR/claude/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        replace_installed_skill \
            "$skill_dir" "$CLAUDE_SKILLS_INSTALL" "$claude_backup_root" "$skill_name"
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
    # A pre-existing build may represent an older source revision. Rebuild
    # unconditionally so a successful comparison always covers current source.
    assemble_skills

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

main() {
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
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
