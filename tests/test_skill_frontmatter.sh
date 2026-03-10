#!/usr/bin/env bash
# Verify that every skill has argument-hint in its frontmatter.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

has_frontmatter_key() {
  local key="$1" file="$2"
  awk -v want="$key" '
    NR==1 && $0=="---" {in_fm=1; next}
    in_fm && $0=="---" {exit}
    in_fm && $0 ~ /^[A-Za-z0-9_-]+:/ {
      k=$0; sub(/:.*/, "", k)
      if (k==want) {found=1}
    }
    END {exit found ? 0 : 1}
  ' "$file"
}

manifest_path() {
  local dir="$1"
  for name in SKILL.md skill.md; do
    [[ -f "$dir/$name" ]] && echo "$dir/$name" && return 0
  done
  return 1
}

failures=0
checked=0

for skill_dir in "$SKILLS_DIR"/*/; do
  name="$(basename "$skill_dir")"
  manifest="$(manifest_path "$skill_dir" 2>/dev/null)" || continue
  checked=$((checked + 1))

  if ! has_frontmatter_key "argument-hint" "$manifest"; then
    echo "FAIL $name: missing argument-hint in frontmatter"
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -gt 0 ]]; then
  echo "FAIL argument-hint check: $failures issue(s) in $checked skills"
  exit 1
fi

echo "PASS argument-hint check: $checked skills verified"
