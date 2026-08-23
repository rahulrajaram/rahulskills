#!/usr/bin/env bash
# Install repo skills into the Pi coding agent's skill directory as symlinks,
# so Pi loads the repository copies directly (repo = single source of truth).
#
# Pi discovers skills from (in order): ~/.pi/agent/skills/, ~/.agents/skills/,
# then project-local .pi/skills and .agents/skills. Pi scans ~/.agents/skills/
# as a global location, so that directory must stay EMPTY for the two harnesses
# (codex owns ~/.codex/skills/, claude owns ~/.claude/skills/) to avoid
# duplicate-name collision warnings. This script makes every repo skill
# available to Pi via a symlink pointing back at the repo, so Pi and the repo
# can never drift.
#
# Existing real directories are moved aside to backups under
# ~/.pi/agent/backups/ (outside Pi's scan dirs) before being replaced with
# symlinks; nothing is deleted. Honors .exclude-skills.
#
# Safety: refuses to run as root, and skill names are validated as plain
# single directory names (no / or ..) so a crafted name cannot escape the
# destination directory.
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_SKILLS_DIR="$SKILLS_DIR/skills"
PI_SKILLS_DIR="${PI_SKILLS_DIR:-$HOME/.pi/agent/skills}"
BACKUP_ROOT="${PI_SKILLS_DIR%/skills}/backups"
EXCLUDE_FILE="$SKILLS_DIR/.exclude-skills"
DRY_RUN=0

if [[ "$(id -u)" -eq 0 ]]; then
    echo "Refusing to run as root: install-pi-skills.sh must not alter root-owned" >&2
    echo "paths or symlink into /root. Run as your normal user." >&2
    exit 1
fi

valid_skill_name() {
    local name="$1"
    [[ -n "$name" && "$name" != */* && "$name" != *..* && "$name" != *\\* && "$name" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]]
}

usage() {
    cat <<'EOF'
Usage: install-pi-skills.sh [options] [skill ...]

Install repository skills into the Pi coding agent skill directory as symlinks
pointing back at this repo.

Options:
  -n, --dry-run   Show what would be done without changing anything
  -h, --help      Show this help

With no skill names, every repo skill is installed. With skill names, only
those skills are processed.

Honors .exclude-skills (one name per line, # comments ignored).
Existing real directories are renamed to <name>.pre-pi-sync under
~/.pi/agent/backups/ (outside Pi's scan dirs) and replaced with symlinks;
existing symlinks are re-pointed. Stale symlinks into deleted repo skills and
leftover .pre-pi-sync dirs are pruned so Pi reports no collisions. Nothing is
deleted.
EOF
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -n|--dry-run) DRY_RUN=1; shift ;;
            -h|--help) usage ;;
            -*) echo "Unknown option: $1" >&2; exit 1 ;;
            *) break ;;
        esac
    done
    SELECTED=("$@")
}

is_excluded() {
    local name="$1"
    [[ ! -f "$EXCLUDE_FILE" ]] && return 1
    grep -qxF "$name" <(grep -v '^#' "$EXCLUDE_FILE" | grep -v '^$') 2>/dev/null
}

has_manifest() {
    local dir="$1"
    [[ -d "$dir" && ( -f "$dir/SKILL.md" || -f "$dir/skill.md" ) ]]
}

already_linked() {
    local link="$1" target="$2"
    [[ -L "$link" ]] && [[ "$(readlink "$link")" == "$target" ]]
}

prune_dst() {
    # Remove stale/broken symlinks and relocate *.pre-pi-sync backups out of
    # the scanned skill dir (pi scans every subdir for SKILL.md and reports
    # name collisions across global locations).
    [[ -d "$PI_SKILLS_DIR" ]] || return 0
    local entry base target dest
    for entry in "$PI_SKILLS_DIR"/*; do
        [[ -e "$entry" || -L "$entry" ]] || continue
        base="$(basename "$entry")"
        if [[ -L "$entry" ]]; then
            target="$(readlink "$entry")"
            if [[ ! -e "$entry" || "$target" != "$REPO_SKILLS_DIR/"* ]]; then
                echo "  PRUNE (stale symlink): $base"
                [[ $DRY_RUN -eq 1 ]] || rm "$entry"
            fi
        elif [[ "$base" == *.pre-pi-sync ]]; then
            dest="$BACKUP_ROOT/$base"
            if [[ ! -e "$dest" ]]; then
                echo "  MOVE (backup out of scan path): $base -> $dest"
                [[ $DRY_RUN -eq 1 ]] || { mkdir -p "$BACKUP_ROOT"; mv "$entry" "$dest"; }
            else
                echo "  SKIP (backup already archived): $base"
            fi
        fi
    done
}

install_one() {
    local name="$1"
    local src="$REPO_SKILLS_DIR/$name"
    local dst="$PI_SKILLS_DIR/$name"

    # Hard guard: reject any name that could escape the destination dir.
    if ! valid_skill_name "$name"; then
        echo "  SKIP (invalid skill name): $name" >&2
        return
    fi

    if is_excluded "$name"; then
        echo "  SKIP (excluded): $name"
        return
    fi

    if already_linked "$dst" "$src"; then
        echo "  OK (already linked): $name"
        return
    fi

    echo "  LINK: $name -> $src"
    if [[ $DRY_RUN -eq 1 ]]; then
        return
    fi

    mkdir -p "$PI_SKILLS_DIR"
    if [[ -e "$dst" && ! -L "$dst" ]]; then
        local bak="$BACKUP_ROOT/$name.pre-pi-sync"
        if [[ -e "$bak" ]]; then
            local n=1
            while [[ -e "$bak.$n" ]]; do n=$((n + 1)); done
            bak="$bak.$n"
        fi
        echo "    backed up existing dir to $bak"
        mkdir -p "$BACKUP_ROOT"
        mv "$dst" "$bak"
    fi
    ln -sfn "$src" "$dst"
}

main() {
    parse_args "$@"

    if [[ $DRY_RUN -eq 1 ]]; then
        echo "Dry run - no changes will be made"
    fi
    echo "Pi skills directory: $PI_SKILLS_DIR"

    prune_dst

    if [[ ${#SELECTED[@]} -gt 0 ]]; then
        for name in "${SELECTED[@]}"; do
            if ! has_manifest "$REPO_SKILLS_DIR/$name"; then
                echo "  SKIP (no manifest in repo): $name"
                continue
            fi
            install_one "$name"
        done
    else
        local name
        for dir in "$REPO_SKILLS_DIR"/*/; do
            [[ -d "$dir" ]] || continue
            name="$(basename "$dir")"
            [[ "$name" == .* ]] && continue
            has_manifest "$dir" || continue
            install_one "$name"
        done
    fi

    echo ""
    echo "Done. Restart Pi sessions to pick up the new skills."
    echo "Pi scans ~/.pi/agent/skills/ and ~/.agents/skills/. The ~/.agents/skills/"
    echo "directory must stay empty (codex owns ~/.codex/skills/, claude owns"
    echo "~/.claude/skills/), so the symlinked repo copies are the only ones Pi sees."
}

main "$@"
