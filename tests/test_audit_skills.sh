#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CACHE_ROOT="$(mktemp -d "$REPO_ROOT/skills/.audit-cache.XXXXXX")"

cleanup() {
  case "$CACHE_ROOT" in
    "$REPO_ROOT"/skills/.audit-cache.*) rm -rf -- "$CACHE_ROOT" ;;
    *) echo "refusing to remove unexpected test path: $CACHE_ROOT" >&2 ;;
  esac
}
trap cleanup EXIT

mkdir -p "$CACHE_ROOT/__pycache__"
printf '/home/example/Documents/private-project\n' \
  > "$CACHE_ROOT/__pycache__/generated.cpython-311.pyc"

"$REPO_ROOT/audit-skills.sh" check >/dev/null
echo "PASS audit ignores generated Python bytecode"
