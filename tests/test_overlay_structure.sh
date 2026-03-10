#!/usr/bin/env bash
# Validate overlay structure:
# - Every overlay references an existing skill
# - Overlays contain only recognized keys
# - Overlays are valid YAML-like format (key: value lines)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
OVERLAYS_DIR="$REPO_ROOT/overlays"

RECOGNIZED_KEYS="allowed-tools"

failures=0
checked=0

if [[ ! -d "$OVERLAYS_DIR" ]]; then
  echo "ERROR: overlays/ directory not found" >&2
  exit 1
fi

for cli_dir in "$OVERLAYS_DIR"/*/; do
  [[ -d "$cli_dir" ]] || continue
  cli_name="$(basename "$cli_dir")"

  for overlay_file in "$cli_dir"*.yml; do
    [[ -f "$overlay_file" ]] || continue
    checked=$((checked + 1))

    skill_name="$(basename "${overlay_file%.yml}")"

    # Check that the skill exists
    if [[ ! -d "$SKILLS_DIR/$skill_name" ]]; then
      echo "FAIL [$cli_name] overlay references non-existent skill: $skill_name"
      failures=$((failures + 1))
      continue
    fi

    # Check each line for recognized keys
    while IFS= read -r line; do
      [[ -z "$line" || "$line" =~ ^# ]] && continue
      if [[ "$line" =~ ^([A-Za-z0-9_-]+):[[:space:]]*(.*) ]]; then
        key="${BASH_REMATCH[1]}"
        found=0
        for rk in $RECOGNIZED_KEYS; do
          [[ "$key" == "$rk" ]] && found=1 && break
        done
        if [[ "$found" -eq 0 ]]; then
          echo "FAIL [$cli_name/$skill_name] unrecognized overlay key: $key"
          failures=$((failures + 1))
        fi
      else
        echo "FAIL [$cli_name/$skill_name] malformed line: $line"
        failures=$((failures + 1))
      fi
    done < "$overlay_file"
  done
done

if [[ "$failures" -gt 0 ]]; then
  echo "FAIL overlay structure: $failures issue(s) in $checked overlays"
  exit 1
fi

echo "PASS overlay structure: $checked overlays validated"
