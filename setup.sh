#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
GIT_DIR="$(git -C "$REPO_ROOT" rev-parse --git-dir)"

# --- Commithooks bootstrap ---------------------------------------------------

COMMITHOOKS_DIR="${COMMITHOOKS_DIR:-$HOME/Documents/commithooks}"
COMMITHOOKS_REPO="https://github.com/rahulrajaram/commithooks.git"

if [ ! -d "$COMMITHOOKS_DIR/lib" ]; then
  echo "commithooks not found at $COMMITHOOKS_DIR"
  echo "Cloning from $COMMITHOOKS_REPO ..."
  git clone "$COMMITHOOKS_REPO" "$COMMITHOOKS_DIR"
fi

echo "Installing git hooks from $COMMITHOOKS_DIR ..."

# Copy dispatchers (skip if a non-sample hook already exists)
for hook in pre-commit commit-msg pre-push post-checkout post-merge; do
  src="$COMMITHOOKS_DIR/$hook"
  dst="$GIT_DIR/hooks/$hook"
  [ -f "$src" ] || continue
  if [ -f "$dst" ] && [ "$(cat "$dst")" != "$(cat "$dst.sample" 2>/dev/null || true)" ]; then
    echo "  [skip] $hook (existing custom hook)"
    continue
  fi
  cp "$src" "$dst"
  chmod +x "$dst"
  echo "  [ok]   $hook"
done

# Copy library modules
rm -rf "$GIT_DIR/lib"
cp -r "$COMMITHOOKS_DIR/lib" "$GIT_DIR/lib"
echo "  [ok]   lib/ ($(ls "$GIT_DIR/lib" | wc -l) modules)"

# Ensure .githooks/ are executable
if [ -d "$REPO_ROOT/.githooks" ]; then
  chmod +x "$REPO_ROOT/.githooks"/* 2>/dev/null || true
fi

# Unset core.hooksPath if set (we use .git/hooks/ directly)
if git -C "$REPO_ROOT" config core.hooksPath &>/dev/null; then
  git -C "$REPO_ROOT" config --unset core.hooksPath
  echo "  [fix]  Unset core.hooksPath (using .git/hooks/ directly)"
fi

echo ""
echo "Hooks installed."

# --- Skill deployment (optional) ---------------------------------------------

if [ "${1:-}" = "--skip-skills" ]; then
  echo "Skipping skill deployment (--skip-skills)."
  exit 0
fi

echo ""
echo "Available skill targets:"
echo "  all     Deploy all skills to ~/.agents/skills/ and ~/.claude/commands/"
echo "  none    Skip skill deployment"
echo ""

read -rp "Deploy skills? [all/none] (default: none): " choice
choice="${choice:-none}"

case "$choice" in
  all)
    "$REPO_ROOT/sync-skills.sh" push
    ;;
  none)
    echo "Skipping skill deployment."
    ;;
  *)
    echo "Unknown choice: $choice. Skipping."
    ;;
esac
