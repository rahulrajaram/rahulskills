#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
BLOCKLIST_FILE="$SKILLS_DIR/.blocklist.local"
REPO_SKILLS_DIR="$SKILLS_DIR/skills"
LEGACY_SKILLS_DIR="$SKILLS_DIR/codex"

usage() {
    cat <<'EOF'
Usage: audit-skills.sh <command>

Commands:
  check          Scan skill files for private references and validate the capability catalog
  pre-commit     Scan only staged skill files (called by git hook)
  install-hook   Write the pre-commit hook into .git/hooks/
EOF
    exit 1
}

skill_root_dir() {
    if [[ -d "$REPO_SKILLS_DIR" ]]; then
        echo "$REPO_SKILLS_DIR"
    else
        echo "$LEGACY_SKILLS_DIR"
    fi
}

# Build a combined grep pattern from exclude file, blocklist, and personal path regex.
# Returns 1 if no patterns were found (nothing to check).
build_pattern() {
    local names=()

    if [[ -f "$BLOCKLIST_FILE" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" || "$line" == \#* ]] && continue
            names+=("$line")
        done < "$BLOCKLIST_FILE"
    fi

    # Hardcoded personal-path patterns (home dir + Documents subtree)
    local path_re='/home/[^/]+/Documents/[^ ]*'
    local dash_re='-home-[a-zA-Z0-9_]+-Documents-[a-zA-Z0-9_-]+'

    if [[ ${#names[@]} -eq 0 ]]; then
        # Only path patterns
        echo "($path_re|$dash_re)"
        return 0
    fi

    # Escape names for grep -E (handle dots, etc.)
    local escaped=()
    for n in "${names[@]}"; do
        escaped+=("$(printf '%s' "$n" | sed 's/[.[\(*+?^$|]/\\&/g')")
    done

    local name_pattern
    name_pattern="$(IFS='|'; echo "${escaped[*]}")"

    echo "($name_pattern|$path_re|$dash_re)"
}

# Scan a list of files (one per line on stdin) against the pattern.
# Returns 0 if clean, 1 if violations found.
scan_files() {
    local pattern="$1"
    local violations=0
    local file

    while IFS= read -r file; do
        [[ -f "$file" ]] || continue
        local matches
        if matches="$(grep -niE "$pattern" "$file" 2>/dev/null)"; then
            while IFS= read -r match; do
                # Ignore the canonical /home/example/ placeholder used in test fixtures.
                case "$match" in
                    *"/home/example/"*|*"-home-example-"*) continue ;;
                esac
                echo "$file:$match"
                violations=$((violations + 1))
            done <<< "$matches"
        fi
    done

    if [[ $violations -gt 0 ]]; then
        echo ""
        echo "AUDIT FAILED: $violations violation(s) found."
        echo "Remove private skill references and personal paths before committing."
        return 1
    fi
    return 0
}

validate_capability_catalog() {
    local catalog="$SKILLS_DIR/capabilities/skills.toml"
    [[ -f "$catalog" ]] || return 0

    python3 - "$catalog" <<'PY'
import sys
import tomllib
from pathlib import Path

catalog = Path(sys.argv[1])
with catalog.open("rb") as handle:
    tomllib.load(handle)
print(f"Capability catalog is valid TOML: {catalog}")
PY
}

do_check() {
    local pattern
    local root
    pattern="$(build_pattern)"
    root="$(skill_root_dir)"

    echo "Scanning all skill files for private references..."
    echo "Pattern: $pattern"
    echo ""

    find "$root" \
        -type d -name __pycache__ -prune -o \
        -type f ! -name '*.pyc' ! -name '*.pyo' -print \
        2>/dev/null | scan_files "$pattern"

    local rc=$?
    if [[ $rc -eq 0 ]] && ! validate_capability_catalog; then
        rc=1
    fi
    [[ $rc -eq 0 ]] && echo "All clean."
    return $rc
}

do_pre_commit() {
    local pattern
    pattern="$(build_pattern)"

    # Collect all staged files
    local staged
    staged="$(git -C "$SKILLS_DIR" diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)"

    if [[ -z "$staged" ]]; then
        exit 0
    fi

    echo "Auditing all staged files for private references..."
    echo ""

    # Convert relative paths to absolute
    echo "$staged" | while IFS= read -r rel; do
        echo "$SKILLS_DIR/$rel"
    done | scan_files "$pattern"
}

do_install_hook() {
    local hook_dir="$SKILLS_DIR/.git/hooks"
    local hook_file="$hook_dir/pre-commit"

    if [[ ! -d "$hook_dir" ]]; then
        echo "Error: $hook_dir does not exist. Is this a git repository?" >&2
        exit 1
    fi

    if [[ -f "$hook_file" ]]; then
        echo "Warning: $hook_file already exists. Overwriting."
    fi

    cat > "$hook_file" <<'HOOK'
#!/usr/bin/env bash
exec "$(git rev-parse --show-toplevel)/audit-skills.sh" pre-commit
HOOK
    chmod +x "$hook_file"

    echo "Installed pre-commit hook at $hook_file"
}

[[ $# -lt 1 ]] && usage

case "$1" in
    check)        do_check ;;
    pre-commit)   do_pre_commit ;;
    install-hook) do_install_hook ;;
    *)            usage ;;
esac
