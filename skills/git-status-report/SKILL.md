---
name: git-status-report
description: Report the sync status of the current git repository and all submodules relative to remote tracking branches.
---

# Git Status Report

Report the sync status of the current git repository and all submodules relative to their remote origins, displayed as a clean ASCII table.

## Usage

`/git-status-report`

## Trigger Phrases

Use when user says "git status report", "repo sync status", "submodule status", "ahead behind", or asks whether repos are in sync with origin.

## Workflow

### Step 1: Detect Root Repository

Confirm the current directory is a git repository:

```bash
git rev-parse --show-toplevel 2>/dev/null
```

If not a git repo, report an error and stop.

### Step 2: Gather Root Status

For the root repository, collect:

1. **Current branch**: `git branch --show-current`
2. **Upstream tracking branch**: `git rev-parse --abbrev-ref @{upstream} 2>/dev/null`
3. **Ahead/behind counts**: `git rev-list --left-right --count @{upstream}...HEAD 2>/dev/null`
4. **Working tree status**: `git status --porcelain` (clean or dirty)
5. **Stash count**: `git stash list | wc -l`

Classify the sync status:
- **In sync**: 0 ahead, 0 behind
- **Ahead**: >0 ahead, 0 behind
- **Behind**: 0 ahead, >0 behind
- **Diverged**: >0 ahead, >0 behind
- **No upstream**: no tracking branch configured

### Step 3: Detect and Gather Submodule Status

Check for submodules:

```bash
git submodule status --recursive 2>/dev/null
```

If submodules exist, for **each submodule**:

1. Enter the submodule directory
2. Run `git fetch origin --quiet` to ensure remote refs are current (skip if offline / fetch fails)
3. Collect the same 5 data points as the root (branch, upstream, ahead/behind, working tree, stash)
4. Additionally check if the submodule HEAD matches what the parent expects:
   - `git -C <parent> ls-tree HEAD <submodule-path>` gives the expected SHA
   - Compare with the submodule's actual `HEAD`
   - If they differ, flag as **pointer drift** (parent expects a different commit)

### Step 4: Format and Display

Display results as an ASCII table. The table MUST use box-drawing characters for clean formatting.

#### Column Definitions

| Column | Description |
|--------|-------------|
| Repository | Name (root = repo name, submodules = relative path) |
| Branch | Current branch name |
| Upstream | Tracking branch (or "none") |
| Ahead | Commits ahead of upstream |
| Behind | Commits behind upstream |
| Status | In sync / Ahead / Behind / Diverged / No upstream |
| Tree | Clean / Dirty |
| Drift | OK / DRIFT (submodule pointer mismatch) |

#### Example Output (with submodules)

```
Git Sync Status Report
======================

  Fetching remote refs... done (3 repos checked)

  +-------------------------------+----------+---------------+-------+--------+-----------+-------+-------+
  | Repository                    | Branch   | Upstream      | Ahead | Behind | Status    | Tree  | Drift |
  +-------------------------------+----------+---------------+-------+--------+-----------+-------+-------+
  | myproject (root)              | master   | origin/master |    69 |      0 | Ahead     | Dirty | -     |
  | myproject_cp/                 | master   | origin/master |    18 |      0 | Ahead     | Clean | OK    |
  | myproject_customer_platform/  | master   | origin/master |    18 |      0 | Ahead     | Clean | DRIFT |
  | myproject-manager/            | master   | origin/master |     0 |      0 | In sync   | Clean | OK    |
  +-------------------------------+----------+---------------+-------+--------+-----------+-------+-------+

  Legend:
    Status: In sync | Ahead | Behind | Diverged | No upstream
    Drift:  OK = submodule HEAD matches parent pointer
            DRIFT = submodule HEAD differs from what parent expects
            - = not applicable (root repo)

  Summary: 4 repos checked, 2 ahead, 1 drifted, 1 dirty
```

#### Example Output (no submodules)

```
Git Sync Status Report
======================

  No submodules detected.

  +----------------------+----------+---------------+-------+--------+---------+-------+
  | Repository           | Branch   | Upstream      | Ahead | Behind | Status  | Tree  |
  +----------------------+----------+---------------+-------+--------+---------+-------+
  | my-project (root)    | main     | origin/main   |     3 |      0 | Ahead   | Clean |
  +----------------------+----------+---------------+-------+--------+---------+-------+

  Summary: 1 repo checked, 1 ahead, 0 dirty
```

When there are no submodules, omit the Drift column entirely.

### Step 5: Summary Line

After the table, print a one-line summary with counts:
- Total repos checked
- How many ahead / behind / diverged / in sync
- How many with dirty working trees
- How many with pointer drift (submodules only)

## Implementation Notes

- Run `git fetch origin --quiet` for each repo before checking ahead/behind. If fetch fails (offline, auth issue), note it but continue with stale data and add a warning line.
- Use `printf` for column alignment — do NOT rely on `column` command (not always available).
- All numeric columns (Ahead, Behind) should be right-aligned.
- Repository names should be left-aligned.
- The table must dynamically size columns based on the longest value in each column.
- Keep output compact — no verbose explanations, just the table + summary.
- This skill is project-agnostic — it works on any git repository with or without submodules.

## Error Handling

- **Not a git repo**: Print "Error: not inside a git repository" and stop.
- **Fetch failures**: Print a warning line above the table: "Warning: fetch failed for <repo> — showing cached data" and continue.
- **Detached HEAD**: Show "(detached)" as the branch name.
- **No upstream configured**: Show "none" for upstream, "-" for ahead/behind, "No upstream" for status.
