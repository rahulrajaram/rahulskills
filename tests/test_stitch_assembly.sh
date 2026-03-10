#!/usr/bin/env bash
# Validate stitch assembly output:
# - All skills produce output for each CLI
# - Overlay keys appear in assembled output
# - Skills without overlays have unchanged frontmatter
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
OVERLAYS_DIR="$REPO_ROOT/overlays"
BUILD_DIR="$REPO_ROOT/build"
STITCH_SCRIPT="$REPO_ROOT/stitch-skills.sh"

CLIS=(claude codex)

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

# Run assemble
echo "Running stitch-skills.sh assemble ..."
"$STITCH_SCRIPT" assemble

failures=0

# Count skills in repo
repo_count=0
for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_dir" ]] || continue
  manifest_path "$skill_dir" > /dev/null 2>&1 || continue
  repo_count=$((repo_count + 1))
done

echo "Repo skills: $repo_count"

# Check all skills produce output for each CLI
for cli in "${CLIS[@]}"; do
  build_skill_dir="$BUILD_DIR/$cli/skills"
  if [[ ! -d "$build_skill_dir" ]]; then
    echo "FAIL: no assembled output for $cli"
    failures=$((failures + 1))
    continue
  fi

  build_count="$(find "$build_skill_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  if [[ "$build_count" -ne "$repo_count" ]]; then
    echo "FAIL [$cli] expected $repo_count assembled skills, got $build_count"
    failures=$((failures + 1))
  else
    echo "PASS [$cli] $build_count skills assembled"
  fi

  # Check each skill
  for skill_dir in "$SKILLS_DIR"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    manifest_path "$skill_dir" > /dev/null 2>&1 || continue

    assembled_dir="$build_skill_dir/$skill_name"
    if [[ ! -d "$assembled_dir" ]]; then
      echo "FAIL [$cli] missing assembled skill: $skill_name"
      failures=$((failures + 1))
      continue
    fi

    assembled_manifest="$(manifest_path "$assembled_dir")" || {
      echo "FAIL [$cli] assembled skill missing manifest: $skill_name"
      failures=$((failures + 1))
      continue
    }

    # If overlay exists, check that overlay keys appear in assembled output
    overlay_file="$OVERLAYS_DIR/$cli/${skill_name}.yml"
    if [[ -f "$overlay_file" ]]; then
      while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        if [[ "$line" =~ ^([A-Za-z0-9_-]+):[[:space:]]*(.*) ]]; then
          key="${BASH_REMATCH[1]}"
          if ! has_frontmatter_key "$key" "$assembled_manifest"; then
            echo "FAIL [$cli/$skill_name] overlay key '$key' not in assembled output"
            failures=$((failures + 1))
          fi
        fi
      done < "$overlay_file"
    fi
  done
done

echo ""
if [[ "$failures" -gt 0 ]]; then
  echo "FAIL stitch assembly: $failures issue(s)"
  exit 1
fi

echo "PASS stitch assembly: all checks passed"
