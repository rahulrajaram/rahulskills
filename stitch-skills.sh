#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMON_DIR="$ROOT_DIR/skills"
LEGACY_CODEX_DIR="$ROOT_DIR/codex"
SYNC_SCRIPT="$ROOT_DIR/sync-skills.sh"

usage() {
    cat <<'USAGE'
Usage: stitch-skills.sh <command>

Commands:
  repo-layout   Ensure skills/ is canonical and codex -> skills symlink exists
  install       Push shared skills/ to ~/.agents/skills and ~/.claude/skills
  check         Run compare + diff checks
  all           Run repo-layout, then install, then check
USAGE
    exit 1
}

ensure_repo_layout() {
    if [[ -d "$COMMON_DIR" && ! -L "$COMMON_DIR" ]]; then
        :
    elif [[ -d "$LEGACY_CODEX_DIR" && ! -L "$LEGACY_CODEX_DIR" ]]; then
        echo "Migrating repo skills: codex/ -> skills/"
        mv "$LEGACY_CODEX_DIR" "$COMMON_DIR"
    else
        mkdir -p "$COMMON_DIR"
    fi

    if [[ -L "$LEGACY_CODEX_DIR" ]]; then
        local target
        target="$(readlink "$LEGACY_CODEX_DIR")"
        if [[ "$target" == "skills" || "$target" == "./skills" ]]; then
            echo "codex symlink is already correct"
            return 0
        fi
        rm "$LEGACY_CODEX_DIR"
    elif [[ -e "$LEGACY_CODEX_DIR" ]]; then
        rm -rf "$LEGACY_CODEX_DIR"
    fi

    ln -s skills "$LEGACY_CODEX_DIR"
    echo "Created compatibility symlink: codex -> skills"
}

install_skills() {
    ensure_repo_layout
    "$SYNC_SCRIPT" push
}

check_sync() {
    ensure_repo_layout
    "$SYNC_SCRIPT" compare-implementations
    "$SYNC_SCRIPT" diff
}

[[ $# -lt 1 ]] && usage

case "$1" in
    repo-layout) ensure_repo_layout ;;
    install)     install_skills ;;
    check)       check_sync ;;
    all)
        ensure_repo_layout
        install_skills
        check_sync
        ;;
    *) usage ;;
esac
