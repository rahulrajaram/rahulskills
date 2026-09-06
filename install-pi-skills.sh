#!/usr/bin/env bash
# Install only the selected canonical repository skills. Never prune unrelated
# links or replace unowned directories; profile changes retain optional copies.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_SKILLS_DIR="${PI_SKILLS_DIR:-$HOME/.pi/agent/skills}"
SELECTION_ARGS=()
REMOVAL_ARGS=()
OPERATION=apply

usage() {
    printf '%s\n' \
        'Usage: install-pi-skills.sh [options] [skill ...]' \
        '  --profile core|design|all  Select a profile (repeatable; default core)' \
        '  --skill NAME              Select an individual canonical skill' \
        '  -n, --dry-run, --preview   Read-only migration and ownership preview' \
        '  --pi-root PATH            Runtime root (default ~/.pi/agent)' \
        '  --remove NAME             Explicitly remove an unselected owned link' \
        'Runtime exclusions apply. Unrelated links and user-managed copies remain.'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--dry-run|--preview) OPERATION=preview; shift ;;
        --profile|--skill)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            SELECTION_ARGS+=("$1" "$2"); shift 2 ;;
        --remove)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            REMOVAL_ARGS+=("$1" "$2"); shift 2 ;;
        --pi-root)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            PI_SKILLS_DIR="$2/skills"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        -*) usage >&2; exit 2 ;;
        *) SELECTION_ARGS+=(--skill "$1"); shift ;;
    esac
done
if [[ "$OPERATION" == apply && "$(id -u)" -eq 0 ]]; then
    printf 'Refusing to install Pi skills as root.\n' >&2
    exit 1
fi
if [[ "$(basename "$PI_SKILLS_DIR")" != skills ]]; then
    printf 'PI_SKILLS_DIR must end in /skills; use --pi-root for an isolated runtime.\n' >&2
    exit 2
fi
python3 "$ROOT_DIR/scripts/skill_profiles.py" "$OPERATION" \
    --root "$ROOT_DIR" --runtime pi --source "$ROOT_DIR" \
    --destination "$(dirname "$PI_SKILLS_DIR")" --links \
    "${SELECTION_ARGS[@]}" "${REMOVAL_ARGS[@]}"
