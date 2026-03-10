#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <codex|claude> <install-root>" >&2
  exit 2
fi

CLI_NAME="$1"
INSTALL_ROOT="$2"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$REPO_ROOT/build}"
BUILD_SKILLS_DIR="$BUILD_DIR/$CLI_NAME/skills"
REFERENCE_SKILL="${REFERENCE_SKILL:-archdiagram}"

manifest_path() {
  local dir="$1"
  if [[ -f "$dir/SKILL.md" ]]; then
    echo "$dir/SKILL.md"
    return 0
  fi
  if [[ -f "$dir/skill.md" ]]; then
    echo "$dir/skill.md"
    return 0
  fi
  return 1
}

frontmatter_keys() {
  local manifest="$1"
  awk '
    NR==1 && $0=="---" {in_fm=1; next}
    in_fm && $0=="---" {exit}
    in_fm && $0 ~ /^[A-Za-z0-9_-]+:[[:space:]]*/ {
      key=$0
      sub(/:.*/, "", key)
      print key
    }
  ' "$manifest" | sort -u
}

has_key() {
  local key="$1"
  local manifest="$2"
  awk -v want="$key" '
    NR==1 && $0=="---" {in_fm=1; next}
    in_fm && $0=="---" {exit}
    in_fm && $0 ~ /^[A-Za-z0-9_-]+:[[:space:]]*/ {
      k=$0
      sub(/:.*/, "", k)
      if (k==want) {found=1}
    }
    END {exit found ? 0 : 1}
  ' "$manifest"
}

# Validate against assembled build output if available, otherwise fall back to repo skills
if [[ -d "$BUILD_SKILLS_DIR" ]]; then
  SOURCE_DIR="$BUILD_SKILLS_DIR"
  echo "[$CLI_NAME] validating against assembled build output: $BUILD_SKILLS_DIR"
else
  SOURCE_DIR="${REPO_SKILLS_DIR:-$REPO_ROOT/skills}"
  echo "[$CLI_NAME] no build output found, validating against repo skills: $SOURCE_DIR"
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "ERROR: source skills directory not found: $SOURCE_DIR" >&2
  exit 1
fi

if [[ ! -d "$INSTALL_ROOT" ]]; then
  echo "ERROR: $CLI_NAME install root not found: $INSTALL_ROOT" >&2
  exit 1
fi

reference_dir="$INSTALL_ROOT/$REFERENCE_SKILL"
if [[ ! -d "$reference_dir" ]]; then
  echo "ERROR: reference skill not found for $CLI_NAME: $reference_dir" >&2
  exit 1
fi

reference_manifest="$(manifest_path "$reference_dir")" || {
  echo "ERROR: reference skill has no manifest for $CLI_NAME: $reference_dir" >&2
  exit 1
}

mapfile -t required_keys < <(frontmatter_keys "$reference_manifest")
if [[ ${#required_keys[@]} -eq 0 ]]; then
  echo "ERROR: could not infer frontmatter keys from $reference_manifest" >&2
  exit 1
fi

echo "[$CLI_NAME] reference skill: $REFERENCE_SKILL"
echo "[$CLI_NAME] required frontmatter keys: ${required_keys[*]}"

declare -A source_skills=()
declare -A installed_skills=()

while IFS= read -r skill; do
  [[ -n "$skill" ]] && source_skills["$skill"]=1
done < <(find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)

while IFS= read -r skill; do
  [[ -n "$skill" ]] && installed_skills["$skill"]=1
done < <(find "$INSTALL_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)

failures=0

for skill in "${!source_skills[@]}"; do
  source_dir="$SOURCE_DIR/$skill"
  install_dir="$INSTALL_ROOT/$skill"

  if [[ ! -d "$install_dir" ]]; then
    echo "FAIL [$CLI_NAME] missing installed skill: $skill"
    failures=$((failures + 1))
    continue
  fi

  source_manifest="$(manifest_path "$source_dir")" || {
    echo "FAIL [$CLI_NAME] source skill missing manifest: $skill"
    failures=$((failures + 1))
    continue
  }

  install_manifest="$(manifest_path "$install_dir")" || {
    echo "FAIL [$CLI_NAME] installed skill missing manifest: $skill"
    failures=$((failures + 1))
    continue
  }

  for key in "${required_keys[@]}"; do
    if ! has_key "$key" "$source_manifest"; then
      echo "FAIL [$CLI_NAME] source skill missing key '$key': $skill"
      failures=$((failures + 1))
    fi
    if ! has_key "$key" "$install_manifest"; then
      echo "FAIL [$CLI_NAME] installed skill missing key '$key': $skill"
      failures=$((failures + 1))
    fi
  done
done

for skill in "${!installed_skills[@]}"; do
  if [[ -z "${source_skills[$skill]+x}" ]]; then
    echo "FAIL [$CLI_NAME] installed-only skill not in source: $skill"
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -gt 0 ]]; then
  echo "FAIL [$CLI_NAME] skill structure checks failed: $failures issue(s)"
  exit 1
fi

echo "PASS [$CLI_NAME] ${#source_skills[@]} skills validated"
