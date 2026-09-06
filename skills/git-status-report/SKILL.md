---
name: git-status-report
description: Report local git working-tree and tracking-ref status for the current repository and submodules. Refresh remotes only within existing explicit authorization.
argument-hint: ""
---

# Git Status Report

## Intent and applicability

Report working-tree, branch and submodule status relative to stored tracking
refs. Default reporting is local-only. Use for repository sync/status questions.

## Inputs and local bindings

Use the requested repository, otherwise the current repository. Resolve its
actual upstreams and initialized submodules; do not assume an `origin` remote or
`main` branch. Distinguish a missing upstream from an unavailable tracking ref.

## Non-goals

Status reporting does not select fetching, checkout, submodule initialization,
history repair, commits or pushing. A broader authorized workflow may select
those separately; necessary local inspection remains autonomous.

## Must not

Do not describe stored tracking refs as current remote evidence, convert a
failed read into a clean/in-sync result, or change repository state to make a
status report easier. Never expose credentials embedded in remote URLs.

## Interaction and authority

Gather local evidence without confirmation. If fresh remote state is requested,
resolve the remotes and refresh effects first; carry valid authorization into
execution. Ask only for an unresolved refresh boundary under active instructions,
not again for the same concrete grant. Continue the local report if refresh is
unavailable or still awaiting authorization.

## Usage

`/git-status-report`

## Trigger Phrases

Use when user says "git status report", "repo sync status", "submodule status", "ahead behind", or asks whether repos are in sync with origin.

## Procedure

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
2. Apply the same local/default versus authorized-refresh branch as the root.
   Fetch only selected remotes covered by valid authority, before collecting
   counts. Do not initialize an uninitialized submodule; report that state.
3. Collect the same 5 data points as the root (branch, upstream, ahead/behind, working tree, stash)
4. Additionally check if the submodule HEAD matches what the parent expects:
   - `git -C <parent> ls-tree HEAD <submodule-path>` gives the expected SHA
   - Compare with the submodule's actual `HEAD`
   - If they differ, flag as **pointer drift** (parent expects a different commit)

### Step 4: Format and Display

Use a compact table in the user's requested format; plain Markdown or ASCII is sufficient. Box drawing and shell formatting tools are optional.

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

  Remote refs: not refreshed (local tracking refs only)

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

- Do not fetch by default. For an authorized refresh, fetch the selected remote before counts and report success/failure per repository. On failure, label counts as stored tracking-ref evidence and continue local inspection.
- If generating an aligned terminal table, `printf` is sufficient; no formatting dependency is required.
- `git rev-list --left-right --count @{upstream}...HEAD` returns **behind first, ahead second**. Preserve this interpretation when labeling columns.
- Repository names should be left-aligned.
- The table must dynamically size columns based on the longest value in each column.
- Keep output compact — no verbose explanations, just the table + summary.
- This skill is project-agnostic — it works on any git repository with or without submodules.

## Error Handling

- **Not a git repo**: Print "Error: not inside a git repository" and stop.
- **Fetch failures**: Print a warning line above the table: "Warning: fetch failed for <repo> — showing cached data" and continue.
- **Detached HEAD**: Show "(detached)" as the branch name.
- **No upstream configured**: Show "none" for upstream, "-" for ahead/behind, "No upstream" for status.

## Completion and evidence

Report branch/upstream, ahead/behind, clean/dirty state, stash count, submodule
pointer drift and coverage limits. Include whether each remote was refreshed.
Report detached, unborn, uninitialized and unreadable states explicitly. A
submodule can match its parent pointer while differing from its own upstream;
these are separate comparisons. Omit irrelevant columns, but do not omit a
failed or unavailable repository from the checked/unchecked accounting.
