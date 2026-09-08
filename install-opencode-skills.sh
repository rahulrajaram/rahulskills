#!/usr/bin/env bash
# Install only the selected canonical repository skills as opencode links.
# Never prune unrelated entries or replace unowned directories; profile
# changes retain optional copies.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_SKILLS_DIR="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"
SELECTION_ARGS=()
REMOVAL_ARGS=()
OPERATION=apply

usage() {
    printf '%s\n' \
        'Usage: install-opencode-skills.sh [options] [skill ...]' \
        '  --profile core|design|all  Select a profile (repeatable; default core)' \
        '  --skill NAME              Select an individual canonical skill' \
        '  -n, --dry-run, --preview   Read-only migration and ownership preview' \
        '  --opencode-root PATH      Runtime root (default ~/.config/opencode)' \
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
        --opencode-root)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            OPENCODE_SKILLS_DIR="$2/skills"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        -*) usage >&2; exit 2 ;;
        *) SELECTION_ARGS+=(--skill "$1"); shift ;;
    esac
done
if [[ "$OPERATION" == apply && "$(id -u)" -eq 0 ]]; then
    printf 'Refusing to install opencode skills as root.\n' >&2
    exit 1
fi
if [[ "$(basename "$OPENCODE_SKILLS_DIR")" != skills ]]; then
    printf 'OPENCODE_SKILLS_DIR must end in /skills; use --opencode-root for an isolated runtime.\n' >&2
    exit 2
fi
python3 "$ROOT_DIR/scripts/skill_profiles.py" "$OPERATION" \
    --root "$ROOT_DIR" --runtime opencode --source "$ROOT_DIR" \
    --destination "$(dirname "$OPENCODE_SKILLS_DIR")" --links \
    "${SELECTION_ARGS[@]}" "${REMOVAL_ARGS[@]}"
