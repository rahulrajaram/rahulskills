---
name: reference-cleaner
description: "Remove references to blocklisted terms from git history and source files. Use when user says /reference-cleaner, 'clean references', 'remove mentions of X', 'scrub project names from history', or asks to sanitize a repo before publishing."
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Reference Cleaner

Remove all references to blocklisted terms from a git repository's source files, commit messages, and file history. Designed for sanitizing repos before open-sourcing or publishing.

## When to Use

- Before pushing a private repo to a public remote
- When renaming a project and cleaning up old name references
- When removing references to internal tools, orchestrators, or services
- When scrubbing vendor/partner names from commit history

## Inputs

The user provides a **blocklist** of terms to remove. Each term can be:
- A simple string (e.g., `yarli`, `ralph`)
- A pattern (e.g., `YRLI-\d+` for tranche IDs)

Optionally, the user provides a **whitelist** of terms that look similar but should be preserved (e.g., `sw4rm` is OK, `yarli` is not).

## Workflow

### Step 0: Record State

```bash
ORIGINAL_HEAD=$(git rev-parse HEAD)
echo "Original HEAD: $ORIGINAL_HEAD"
echo "To restore: git reset --hard $ORIGINAL_HEAD"
```

### Step 1: Scan Source Files

For each blocklisted term, search all tracked files:

```bash
git ls-files | xargs grep -li '<term>' 2>/dev/null
```

Categorize matches into:
- **DELETE**: Files that are entirely about the blocklisted project (config files, orchestration artifacts, docs dedicated to the tool)
- **EDIT**: Files where the term appears in comments, identifiers, or strings but the file itself is needed
- **RENAME**: Files or directories whose names contain the blocklisted term

Present a table:

```
| Action | Path                        | Term    | Context                          |
|--------|-----------------------------|---------|----------------------------------|
| DELETE | .yarli/tranches.toml        | yarli   | Orchestration config file        |
| EDIT   | src/rest.rs                 | YRLI    | Comment references (YRLI-58)     |
| RENAME | bin/yarli-lint-tranches.sh  | yarli   | Script name contains term        |
```

### Step 2: Scan Commit Messages

```bash
git log --format="%H %s" | grep -iE '<term1>|<term2>|...'
```

Present commits that need message rewrites.

### Step 3: Confirm

Ask the user to approve the plan. Show:
- Files to delete (count)
- Files to edit (count, with preview of changes)
- Commit messages to rewrite (count, with before/after)
- Files to purge from history via filter-repo

### Step 4: Clean Source Files

1. `git rm` files marked for deletion
2. For EDIT files, strip references using pattern replacement:
   - Strip `(TERM-XX)` from comments
   - Strip `TERM-XX: ` prefixes from comments
   - Rename identifiers (e.g., `<blocked>_haake_import_v1` -> `haake_import_v1`)
   - Remove blocklisted entries from .gitignore/.dockerignore
3. Run the project's test suite to verify nothing broke
4. Commit the changes

### Step 5: Rewrite Commit Messages

Use `git-filter-repo --message-callback` with a Python callback that:
- Replaces known full-message patterns with clean versions
- Strips `TERM-XX` references via regex
- Strips standalone occurrences of blocklisted terms

```bash
git-filter-repo --message-callback '
import re
m = message.decode("utf-8")
# ... replacements ...
return m.encode("utf-8")
' --force
```

### Step 6: Purge Files from History

Use `git-filter-repo --invert-paths` to remove deleted files from all historical commits:

```bash
git-filter-repo --invert-paths \
  --path-glob '.yarli/*' \
  --path 'yarli.toml' \
  ... \
  --force
```

### Step 7: Verify

1. Search all tracked files for blocklisted terms: `git ls-files | xargs grep -liE '<terms>'`
2. Search all commit messages: `git log --format="%B" | grep -iE '<terms>'`
3. Search file paths in history: `git log --all --diff-filter=ACDMR --name-only --format="" | grep -iE '<terms>'`
4. Run the test suite
5. Report results

## Safety Guardrails

- **Never auto-execute**: Always present the full plan and wait for approval
- **Record original HEAD**: Print the full SHA at start and end for recovery
- **Backup tag**: Create `pre-clean-backup` tag before any destructive operation
- **Test after each phase**: Run tests after source edits and after history rewrites
- **Dirty tree check**: Refuse to start if `git status --porcelain` shows uncommitted changes
- **Remote tracking check**: Warn if branch tracks a remote (force push will be needed)
- **Whitelist support**: Never touch terms on the whitelist even if they match patterns

## Edge Cases

- **Identifiers in code**: If a blocklisted term is part of a variable name (e.g., `yarli_config`), rename the identifier. Verify with `cargo check` / `npm run build` / equivalent.
- **Binary files**: Flag binary files containing the term but do not attempt to edit them. Suggest deletion or manual review.
- **Test fixtures**: If test data contains blocklisted terms (e.g., project IDs in test JSON), rename them to generic values.
- **README/docs**: If docs reference blocklisted tools, rewrite the sections to be generic or delete them if they're tool-specific.

## Example Session

```
User: /reference-cleaner

Claude: What terms should I remove from this repository?

User: termA, termB, termC, TERMA

Claude:
Original HEAD: a1b2c3d4...
To restore: git reset --hard a1b2c3d4...

Scanning tracked files for: termA, termB, termC, TERMA

Found references in 36 files:
- DELETE: 25 files (orchestration configs, scripts, docs)
- EDIT: 11 files (source comments, identifiers, .gitignore)

Found references in 8 commit messages.

[Table of changes...]

Approve this plan? [Approve / Cancel]
```
