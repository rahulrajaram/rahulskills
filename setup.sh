#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
GIT_DIR="$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-dir)"

replace_hook_library() {
  local source_dir="$1"
  local git_dir_real target stage backup_root backup=""

  git_dir_real="$(realpath -e -- "$GIT_DIR")"
  [[ "$git_dir_real" != "/" && ! -L "$GIT_DIR" ]] || {
    echo "ERROR: refusing library install into unsafe git directory: $GIT_DIR" >&2
    return 1
  }

  target="$git_dir_real/lib"
  [[ "$(realpath -m -- "$(dirname -- "$target")")" == "$git_dir_real" ]] || {
    echo "ERROR: refusing library install outside git directory: $target" >&2
    return 1
  }

  stage="$(mktemp -d "$git_dir_real/.lib-stage.XXXXXX")"
  cp -a "$source_dir/." "$stage/"
  if [[ -e "$target" || -L "$target" ]]; then
    backup_root="$git_dir_real/rahulskills-backups/setup-$(date -u +%Y%m%dT%H%M%SZ)-$$"
    backup="$backup_root/lib"
    mkdir -p "$backup_root"
    mv -- "$target" "$backup"
    echo "  [backup] prior lib retained at $backup"
  fi

  if ! mv -- "$stage" "$target"; then
    echo "ERROR: library install failed; staged tree retained at $stage" >&2
    if [[ -n "$backup" && ! -e "$target" && ! -L "$target" ]]; then
      mv -- "$backup" "$target"
      echo "  [restore] prior lib restored" >&2
    fi
    return 1
  fi
}

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

# Copy library modules as a staged, recoverable replacement.
replace_hook_library "$COMMITHOOKS_DIR/lib"
module_count="$(find "$GIT_DIR/lib" -mindepth 1 -maxdepth 1 -printf '.' | wc -c)"
echo "  [ok]   lib/ ($module_count modules)"

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
echo "  all     Deploy all skills to ~/.agents/skills/ and ~/.claude/skills/"
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
