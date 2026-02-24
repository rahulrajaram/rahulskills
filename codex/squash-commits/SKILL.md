---
name: squash-commits
description: "Analyze git history, identify contiguous thematic groups, and interactively squash them with clean conventional commit messages. Use when user says /squash-commits, 'squash commits', 'clean up git history', 'compress commits', or asks to tidy commit history."
allowed-tools: Bash, Read, Write, Grep, Glob
---

# Squash Commits

Analyze a range of git commits, identify contiguous groups that share a theme, and squash them non-interactively with clean commit messages following git conventions.

## Usage

`/squash-commits [N]` where N is the number of recent commits to analyze (default: 20).

## Squash Candidate Rules

### Contiguity Rule (MANDATORY)

Only commits that are **adjacent** in `git log` order are candidates. If commit A and C share a theme but commit B (unrelated) sits between them, A and C are **NOT** candidates. Never skip over unrelated commits to form a group.

### Thematic Grouping Patterns

These contiguous sequences should be squashed:

1. **Yarli workspace merges + reapplies**: A `yarli: merge workspace result for tranche-XXX` followed by `yarli: reapply pre-existing workspace state after merge` (and any intermediate yarli bookkeeping commits for the same run).

2. **Handoff sequences**: Multiple `handoff:` commits updating docs in the same session.

3. **Fix + recovery pairs**: A commit that broke something followed immediately by its fix (e.g., `feat: add X` then `fix: correct X` where X is the same feature).

4. **Multi-step feature work**: Implementation commit + its test commit + its doc commit, **only if contiguous** and clearly part of the same unit of work.

5. **Identical repeated messages**: Multiple commits with the same or near-identical message (e.g., repeated `yarli: reapply pre-existing workspace state after merge`).

6. **Chore batches**: Contiguous `chore:` commits doing related cleanup (e.g., lint fixes, formatting, dependency bumps in one session).

### NOT Candidates

- Standalone commits with a distinct, self-contained purpose
- Commits from different logical batches even if they look similar
- Anything where contiguity is broken by an unrelated commit
- Merge commits (skip these; do not include in groups)

## Commit Message Rules

All squashed commit messages MUST follow these conventions:

### Subject Line
- **Imperative mood**: "Add feature" not "Added feature" or "Adds feature"
- **Max 72 characters**
- **Conventional prefix**: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `yarli:`, `handoff:`
- **Capitalize** first word after prefix
- **No trailing period**

### Body (optional, separated by blank line)
- Wrap at 72 characters
- Explain *what* and *why*, not *how*
- Reference tranche IDs (YRLI-XX) when applicable
- Use bullet points for multi-item changes

### Trailer
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` when AI-assisted

## Workflow

### Step 0: Record Original HEAD

Before anything else, capture and display the full HEAD commit hash:

```bash
ORIGINAL_HEAD=$(git rev-parse HEAD)
```

**Always print this prominently** at the start of output:

```
Original HEAD: <full 40-char SHA>
To restore: git reset --hard <full 40-char SHA>
```

This is the single source of truth for recovery. The backup tag (Step 4) is a convenience alias, but the SHA is authoritative because tags can be accidentally deleted or moved.

### Step 1: Scan

Run `git log --oneline -N` for the requested range. Also run `git log --oneline -N --format="%h %s"` for a clean list to analyze.

If user specifies a SHA range instead of a count, use `git log --oneline <base>..<tip>`.

### Step 2: Analyze

Identify contiguous squash groups using the rules above. For each group, record:
- The SHAs (first and last in the group)
- The commit count
- A proposed squashed commit message

Present a **table** to the user:

```
| # | Group Label              | Commits | SHA Range          | Proposed Message                        |
|---|--------------------------|---------|--------------------|-----------------------------------------|
| 1 | Yarli YRLI-52 workspace  | 3       | abc1234..def5678   | yarli: Complete YRLI-52 auth middleware  |
| 2 | Handoff docs update      | 2       | 111aaaa..222bbbb   | handoff: Update session handoff docs    |
```

Also show commits that will be **left untouched** (not in any group) so the user can verify nothing was missed or incorrectly excluded.

### Step 3: Confirm

Ask the user to approve, modify, or reject the plan. Offer options:
- **Approve as-is**: Proceed with the proposed groups and messages
- **Conservative**: Only squash groups with 3+ commits
- **Custom**: User specifies which groups to keep/drop/edit

Do NOT proceed without explicit user approval.

### Step 4: Execute

Build a `GIT_SEQUENCE_EDITOR` shell script:

```bash
#!/bin/bash
# Auto-generated squash editor
sed -i '
  # For each group: keep first as "pick", change rest to "fixup"
  # Then use "exec" to amend the message
  <sed commands here>
' "$1"
```

Save it to `/tmp/haake-squash-editor.sh`, make it executable, then run:

```bash
GIT_SEQUENCE_EDITOR=/tmp/haake-squash-editor.sh git rebase -i <base-sha>^
```

For the commit message amendments, use `exec git commit --amend -m "..."` lines in the rebase todo.

### Step 5: Verify

After rebase completes:
1. Run `git log --oneline -N` to show the cleaned-up history
2. Run the project test suite if one exists (`cargo test`, `npm test`, `pytest`, etc.)
3. Report pass/fail status

If tests fail, warn the user and suggest `git rebase --abort` or `git reflog` to recover.

### Step 6: Cleanup and Health Check

Remove the temp script and verify the repository is in a healthy state:

```bash
# Remove temp files
rm -f /tmp/haake-squash-editor.sh

# Ensure no rebase is in progress
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  echo "WARNING: Rebase state directory still exists!"
fi

# Ensure no stale lock files
if [ -f .git/index.lock ]; then
  echo "WARNING: .git/index.lock exists — git may be locked!"
fi
if [ -f .git/refs/heads/*.lock ] 2>/dev/null; then
  echo "WARNING: Stale ref lock files found!"
fi

# Verify working tree is clean
git status --porcelain

# Verify HEAD is valid
git rev-parse --verify HEAD
```

Run all of the above checks. If any warnings fire:
- **Rebase state directories**: Attempt `git rebase --abort`. If that fails, inform the user.
- **Lock files**: Warn the user and suggest `rm .git/index.lock` only after confirming no other git process is running (`ps aux | grep git`).
- **Dirty working tree**: Warn the user — the rebase may have left uncommitted changes.

**Always print the final summary** including the original HEAD for recovery:

```
Squash complete.
  Original HEAD: <full 40-char SHA>
  Current HEAD:  <full 40-char SHA>
  Backup tag:    pre-squash-backup
  To restore:    git reset --hard <original HEAD SHA>
  Repo health:   OK (clean tree, no locks, no dangling rebase)
```

## Safety Guardrails

- **Remote tracking check**: Before rebasing, run `git rev-parse --abbrev-ref @{upstream} 2>/dev/null`. If a remote tracking branch exists, **warn the user** that squashing will diverge from remote and require a force push. Ask for explicit confirmation before proceeding.
- **Dirty working tree**: If `git status --porcelain` shows uncommitted changes, refuse to proceed. Ask the user to commit or stash first.
- **Never auto-squash**: Always present the plan and wait for approval.
- **Never use --force**: Do not force-push. If the user needs to push after squashing, inform them they'll need `git push --force-with-lease` and let them do it.
- **Original HEAD recorded**: The full 40-char HEAD SHA is captured in Step 0 and printed at both the start and end of the run. This is the authoritative recovery point — it survives even if the backup tag is lost.
- **Backup ref**: Before rebasing, create a backup ref: `git tag -f pre-squash-backup` pointing at the original HEAD so the user can recover with `git reset --hard pre-squash-backup`.
- **Abort on conflict**: If the rebase hits a conflict, do not attempt to resolve it. Abort with `git rebase --abort`, print the original HEAD SHA for manual recovery, and report the issue.
- **Post-squash health check**: After completion, verify no rebase state dirs (`.git/rebase-merge`, `.git/rebase-apply`), no stale lock files (`.git/index.lock`, `.git/refs/heads/*.lock`), and working tree is clean. Report any anomalies.

## Example Session

```
User: /squash-commits 30

Claude:
Original HEAD: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
To restore:    git reset --hard a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2

Scanning last 30 commits...

Found 4 squash groups among 30 commits:

| # | Group Label              | Commits | SHA Range          | Proposed Message                              |
|---|--------------------------|---------|--------------------|-------------------------------------------------|
| 1 | Yarli YRLI-52..55 auth   | 6       | abc1234..def5678   | feat: Add per-project API key auth (YRLI-52..55) |
| 2 | Handoff session 3        | 2       | 111aaaa..222bbbb   | handoff: Update session 3 handoff docs           |
| 3 | Clippy fix + recovery    | 2       | 333cccc..444dddd   | fix: Resolve clippy warnings in rest.rs          |
| 4 | Yarli workspace reapply  | 4       | 555eeee..666ffff   | yarli: Reapply workspace state after merge       |

22 commits remain untouched (standalone).
Result: 30 commits → 22 commits.

Approve this plan? [Approve / Conservative (3+ only) / Custom / Cancel]

--- after user approves and squash completes ---

Squash complete.
  Original HEAD: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
  Current HEAD:  f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5
  Backup tag:    pre-squash-backup
  To restore:    git reset --hard a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
  Repo health:   OK (clean tree, no locks, no dangling rebase)
  Tests:         67 passed, 0 failed
```

## Related Skills

- `/handoff`: Session handoff with commit and docs update
