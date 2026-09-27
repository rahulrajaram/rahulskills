#!/usr/bin/env bash
# Assemble and install only the selected Claude Code skills. Claude needs
# stitched copies (canonical SKILL.md + overlays/claude/<name>.yml), so this
# copies rather than links: re-run it after pulling. Reruns are idempotent;
# only package-owned, unmodified entries are updated. Never prunes unrelated
# entries or replaces unowned directories; profile changes retain copies.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills}"
SELECTION_ARGS=()
PASS_ARGS=()
OPERATION=install

usage() {
    printf '%s\n' \
        'Usage: install-claude-skills.sh [options] [skill ...]' \
        '  --profile core|design|all  Select a profile (repeatable; default core)' \
        '  --skill NAME              Select an individual canonical skill' \
        '  -n, --dry-run, --preview   Read-only migration and ownership preview' \
        '  --claude-root PATH        Runtime root (default ${CLAUDE_CONFIG_DIR:-~/.claude});' \
        '                            skills install under PATH/skills' \
        '  --remove NAME             Explicitly remove an unselected owned skill' \
        '  --adopt-source            Re-root an ownership ledger written by another' \
        '                            checkout (e.g. a worktree); refused by default' \
        'Runtime exclusions (runtime-exclusions/claude.txt, .exclude-skills) and' \
        'catalog `runtimes` apply. Unrelated entries and user-modified copies remain.'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--dry-run|--preview) OPERATION=preview; shift ;;
        --profile|--skill)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            SELECTION_ARGS+=("$1" "$2"); shift 2 ;;
        --remove)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            PASS_ARGS+=("$1" "$2"); shift 2 ;;
        --adopt-source) PASS_ARGS+=("$1"); shift ;;
        --claude-root)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            CLAUDE_SKILLS_DIR="$2/skills"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        -*) usage >&2; exit 2 ;;
        *) SELECTION_ARGS+=(--skill "$1"); shift ;;
    esac
done
if [[ "$OPERATION" == install && "$(id -u)" -eq 0 ]]; then
    printf 'Refusing to install Claude skills as root.\n' >&2
    exit 1
fi
if [[ "$(basename "$CLAUDE_SKILLS_DIR")" != skills ]]; then
    printf 'CLAUDE_SKILLS_DIR must end in /skills; use --claude-root for an isolated runtime.\n' >&2
    exit 2
fi

# Assemble into a private throwaway directory so repeated runs never replace
# or back up the shared build/ tree.
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/rahulskills-claude.XXXXXX")"
trap 'rm -rf -- "$WORK_DIR"' EXIT
"$ROOT_DIR/stitch-skills.sh" "$OPERATION" --runtime claude \
    --claude-root "$(dirname "$CLAUDE_SKILLS_DIR")" --output "$WORK_DIR/assembled" \
    "${SELECTION_ARGS[@]}" "${PASS_ARGS[@]}"
