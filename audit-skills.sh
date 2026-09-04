#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
BLOCKLIST_FILE="$SKILLS_DIR/.blocklist.local"
REPO_SKILLS_DIR="$SKILLS_DIR/skills"
LEGACY_SKILLS_DIR="$SKILLS_DIR/codex"

usage() {
    cat <<'EOF'
Usage: audit-skills.sh <command>

Commands:
  check          Audit private references, manifests, inventory, catalog, and local links
  pre-commit     Scan only staged skill files (called by git hook)
  install-hook   Write the pre-commit hook into .git/hooks/
EOF
    exit 1
}

skill_root_dir() {
    if [[ -d "$REPO_SKILLS_DIR" ]]; then
        echo "$REPO_SKILLS_DIR"
    else
        echo "$LEGACY_SKILLS_DIR"
    fi
}

# Build a combined grep pattern from exclude file, blocklist, and personal path regex.
# Returns 1 if no patterns were found (nothing to check).
build_pattern() {
    local names=()

    if [[ -f "$BLOCKLIST_FILE" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" || "$line" == \#* ]] && continue
            names+=("$line")
        done < "$BLOCKLIST_FILE"
    fi

    # Hardcoded personal-path patterns (home dir + Documents subtree)
    local path_re='/home/[^/]+/Documents/[^ ]*'
    local dash_re='-home-[a-zA-Z0-9_]+-Documents-[a-zA-Z0-9_-]+'

    if [[ ${#names[@]} -eq 0 ]]; then
        # Only path patterns
        echo "($path_re|$dash_re)"
        return 0
    fi

    # Escape names for grep -E (handle dots, etc.)
    local escaped=()
    for n in "${names[@]}"; do
        escaped+=("$(printf '%s' "$n" | sed 's/[.[\(*+?^$|]/\\&/g')")
    done

    local name_pattern
    name_pattern="$(IFS='|'; echo "${escaped[*]}")"

    echo "($name_pattern|$path_re|$dash_re)"
}

# Scan a list of files (one per line on stdin) against the pattern.
# Returns 0 if clean, 1 if violations found.
scan_files() {
    local pattern="$1"
    local violations=0
    local file

    while IFS= read -r file; do
        [[ -f "$file" ]] || continue
        local matches
        if matches="$(grep -niE "$pattern" "$file" 2>/dev/null)"; then
            while IFS= read -r match; do
                # Ignore the canonical /home/example/ placeholder used in test fixtures.
                case "$match" in
                    *"/home/example/"*|*"-home-example-"*) continue ;;
                esac
                echo "$file:$match"
                violations=$((violations + 1))
            done <<< "$matches"
        fi
    done

    if [[ $violations -gt 0 ]]; then
        echo ""
        echo "AUDIT FAILED: $violations violation(s) found."
        echo "Remove private skill references and personal paths before committing."
        return 1
    fi
    return 0
}

validate_capability_catalog() {
    local catalog="$SKILLS_DIR/capabilities/skills.toml"
    [[ -f "$catalog" ]] || return 0

    python3 - "$catalog" "$SKILLS_DIR/overlays/claude" <<'PY'
import re
import sys
import tomllib
from pathlib import Path

catalog = Path(sys.argv[1])
overlay_dir = Path(sys.argv[2])
with catalog.open("rb") as handle:
    document = tomllib.load(handle)

skills = document.get("skills")
if not isinstance(skills, dict):
    raise SystemExit("Capability catalog must define a [skills] table")

allowed_layers = {"primitive", "workflow", "composer"}
problems = []
for name, entry in sorted(skills.items()):
    effect = entry.get("effect")
    layer = entry.get("layer")
    commands = entry.get("commands", [])
    if not isinstance(effect, str) or not effect.strip():
        problems.append(f"skills.{name}: missing non-empty effect")
    if layer not in allowed_layers:
        allowed = ", ".join(sorted(allowed_layers))
        problems.append(f"skills.{name}: layer must be one of {allowed}")
    if not isinstance(commands, list) or not all(
        isinstance(command, str) and command for command in commands
    ):
        problems.append(f"skills.{name}: commands must be a list of non-empty strings")

scoped_bash = re.compile(r"Bash\(([^:(),]+):\*\)")
prohibited_preapprovals = {"curl", "rm"}
for overlay in sorted(overlay_dir.glob("*.yml")):
    skill_name = overlay.stem
    entry = skills.get(skill_name)
    if entry is None:
        problems.append(f"{overlay}: no matching skills.{skill_name} catalog entry")
        continue
    granted = set(scoped_bash.findall(overlay.read_text(encoding="utf-8")))
    prohibited = sorted(granted & prohibited_preapprovals)
    if prohibited:
        problems.append(
            f"{overlay}: unsafe preapproved command(s): {', '.join(prohibited)}"
        )
    undeclared = sorted(granted - set(entry.get("commands", [])))
    if undeclared:
        problems.append(
            f"{overlay}: scoped Bash command(s) absent from catalog: "
            + ", ".join(undeclared)
        )

if problems:
    raise SystemExit("Capability catalog validation failed:\n" + "\n".join(problems))

print(
    f"Capability catalog and scoped Claude grants are valid: "
    f"{len(skills)} skills checked."
)
PY
}

validate_skill_manifests() {
    local validator="$REPO_SKILLS_DIR/skill-creator/scripts/quick_validate.py"
    local skill_dir
    local failures=0
    local count=0

    [[ -f "$validator" ]] || {
        echo "ERROR: skill validator not found: $validator" >&2
        return 1
    }

    for skill_dir in "$REPO_SKILLS_DIR"/*/; do
        [[ -f "$skill_dir/SKILL.md" ]] || continue
        count=$((count + 1))
        if ! python3 "$validator" "$skill_dir" >/dev/null; then
            echo "INVALID MANIFEST: $skill_dir"
            python3 "$validator" "$skill_dir" || true
            failures=$((failures + 1))
        fi
    done

    if [[ "$failures" -gt 0 ]]; then
        echo "Manifest validation failed: $failures of $count skill(s)."
        return 1
    fi
    echo "Skill manifests are valid: $count checked."
}

validate_package_inventory() {
    python3 - "$SKILLS_DIR" <<'PY'
import re
import sys
import tomllib
from pathlib import Path

root = Path(sys.argv[1])
package_skills = {
    path.parent.name for path in (root / "skills").glob("*/SKILL.md")
}

with (root / "capabilities" / "skills.toml").open("rb") as handle:
    catalog_skills = set(tomllib.load(handle).get("skills", {}))

readme = (root / "README.md").read_text(encoding="utf-8")
section_match = re.search(
    r"### Package-managed skills \((\d+)\)\n(?P<body>.*?)"
    r"\n### Codex runtime-owned skills",
    readme,
    re.DOTALL,
)
if not section_match:
    raise SystemExit("README package-managed skill inventory section was not found")

declared_count = int(section_match.group(1))
readme_skills = set(
    re.findall(r"^\|\s*`([^`]+)`\s*\|", section_match.group("body"), re.MULTILINE)
)

problems = []
if declared_count != len(package_skills):
    problems.append(
        f"README declares {declared_count} package skills; source contains {len(package_skills)}"
    )
if missing := sorted(package_skills - readme_skills):
    problems.append("README is missing: " + ", ".join(missing))
if extra := sorted(readme_skills - package_skills):
    problems.append("README contains non-package skills: " + ", ".join(extra))
if uncataloged := sorted(package_skills - catalog_skills):
    problems.append("Capability catalog is missing: " + ", ".join(uncataloged))

if problems:
    raise SystemExit("\n".join(problems))

print(
    f"Package inventory is congruent: {len(package_skills)} source, README, and catalog entries."
)
PY
}

validate_markdown_links() {
    python3 - "$SKILLS_DIR" <<'PY'
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

root = Path(sys.argv[1])
tracked = set(subprocess.run(
    ["git", "-C", str(root), "ls-files", "*.md"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines())

# Include new, not-yet-tracked package documentation so a broken link cannot
# evade the pre-commit audit on its first commit. Deliberately exclude arbitrary
# root-level scratch/handoff files from this package-maintenance check.
maintained = set(tracked)
maintained.update(
    path.relative_to(root).as_posix()
    for top_level in ("skills", "references", "docs")
    for path in (root / top_level).rglob("*.md")
    if path.is_file()
)
if (root / "README.md").is_file():
    maintained.add("README.md")

link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
scheme_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
broken = []
checked = 0

for relative in sorted(maintained):
    source = root / relative
    if not source.is_file():
        continue
    checked += 1
    in_fence = False
    fence_marker = ""
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        fence = re.match(r"^[ \t]*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue

        searchable = re.sub(r"`[^`]*`", "", line)
        for match in link_pattern.finditer(searchable):
            raw_target = match.group(1).strip()
            if raw_target.startswith("<") and raw_target.endswith(">"):
                raw_target = raw_target[1:-1]
            else:
                raw_target = raw_target.split(maxsplit=1)[0]
            if not raw_target or raw_target.startswith("#") or scheme_pattern.match(raw_target):
                continue
            target = unquote(raw_target.split("#", 1)[0])
            resolved = source.parent / target
            if target.startswith("/") or not resolved.exists():
                broken.append(f"{relative}:{line_number}: {raw_target}")

if broken:
    raise SystemExit("Broken local Markdown link(s):\n" + "\n".join(broken))

print(f"Maintained Markdown links resolve: {checked} files checked.")
PY
}

do_check() {
    local pattern
    local root
    pattern="$(build_pattern)"
    root="$(skill_root_dir)"

    echo "Scanning all skill files for private references..."
    echo "Pattern: $pattern"
    echo ""

    find "$root" \
        -type d \( \
            -name __pycache__ -o \
            -name .ruff_cache -o \
            -name .mypy_cache -o \
            -name .pytest_cache \
        \) -prune -o \
        -type f ! -name '*.pyc' ! -name '*.pyo' -print \
        2>/dev/null | scan_files "$pattern"

    local rc=$?
    if [[ $rc -eq 0 ]] && ! validate_capability_catalog; then
        rc=1
    fi
    if [[ $rc -eq 0 ]] && ! validate_skill_manifests; then
        rc=1
    fi
    if [[ $rc -eq 0 ]] && ! validate_package_inventory; then
        rc=1
    fi
    if [[ $rc -eq 0 ]] && ! validate_markdown_links; then
        rc=1
    fi
    [[ $rc -eq 0 ]] && echo "All clean."
    return $rc
}

do_pre_commit() {
    local pattern
    pattern="$(build_pattern)"

    # Collect all staged files
    local staged
    staged="$(git -C "$SKILLS_DIR" diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)"

    if [[ -z "$staged" ]]; then
        exit 0
    fi

    echo "Auditing all staged files for private references..."
    echo ""

    # Convert relative paths to absolute
    echo "$staged" | while IFS= read -r rel; do
        echo "$SKILLS_DIR/$rel"
    done | scan_files "$pattern"
}

do_install_hook() {
    local hook_dir="$SKILLS_DIR/.git/hooks"
    local hook_file="$hook_dir/pre-commit"

    if [[ ! -d "$hook_dir" ]]; then
        echo "Error: $hook_dir does not exist. Is this a git repository?" >&2
        exit 1
    fi

    if [[ -f "$hook_file" ]]; then
        echo "Warning: $hook_file already exists. Overwriting."
    fi

    cat > "$hook_file" <<'HOOK'
#!/usr/bin/env bash
exec "$(git rev-parse --show-toplevel)/audit-skills.sh" pre-commit
HOOK
    chmod +x "$hook_file"

    echo "Installed pre-commit hook at $hook_file"
}

[[ $# -lt 1 ]] && usage

case "$1" in
    check)        do_check ;;
    pre-commit)   do_pre_commit ;;
    install-hook) do_install_hook ;;
    *)            usage ;;
esac
