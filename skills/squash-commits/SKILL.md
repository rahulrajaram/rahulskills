---
name: squash-commits
description: "Analyze git history, identify contiguous thematic groups, and interactively squash them with clean conventional commit messages. Use when user says /squash-commits, 'squash commits', 'clean up git history', 'compress commits', or asks to tidy commit history."
argument-hint: "[N] [--all] [--batch] [--max-passes M]"
---

# Squash Commits

Analyze a range of git commits, identify contiguous groups that share a theme, and squash them non-interactively with clean commit messages following git conventions.

## Usage

`/squash-commits [N] [--all] [--batch] [--max-passes M]`

- `N`: number of recent commits to analyze (default: 20)
- `--all`: include pushed history (requires force push later)
- `--batch`: run repeated conservative squashes over multiple contiguous groups
- `--max-passes M`: cap batch iterations (default: 5, recommended <= 20)

By default, only **unpushed commits** (ahead of the remote tracking branch) are analyzed. This prevents accidentally proposing to rewrite published history. Pass `--all` to include pushed commits in the scan (will require force push).

## Large History Mode (100+ commits)

For large histories, prefer conservative iterative passes instead of one large rewrite:

1. Use first-parent history (`git log --first-parent --oneline`) to avoid side-branch noise.
2. Pick one small contiguous group per pass.
3. Create a unique backup tag before each pass (for example `pre-big-band-<N>-YYYYMMDD`).
4. Recompute candidates after each pass.
5. Run `git range-diff` plus health checks and tests after every pass.
6. Stop when remaining candidates are tiny or semantically high-value.

### Replay-sensitivity note

Contiguity is necessary for proposing a squash group, but it is **not**
sufficient to guarantee a conflict-free rebase. Interactive rebase rewrites the
selected commits and then replays later commits on top of the rewritten base.
That means a perfectly contiguous `A/B/C` squash can still trigger conflicts in
later `D/E/F` commits if those later commits touch the same regions or depend on
the original parent chain's exact file state.

Practical consequence:
- prefer the smallest contiguous range that achieves the cleanup goal
- avoid crossing multiple tranche waves or repeated hotspot edits in one pass
- be especially conservative around histories containing auto-repairs, reapply
  commits, conflict-fix commits, or repeated edits to the same files

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
- Commits spanning major phase/milestone boundaries unless explicitly approved

## Commit Message Rules

All squashed commit messages MUST follow these conventions:

### Subject Line
- **Imperative mood**: "Add feature" not "Added feature" or "Adds feature"
- **Max 72 characters**
- **Conventional prefix**: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `yarli:`, `handoff:`
- **Capitalize** first word after prefix
- **No trailing period**
- **Be specific**: avoid generic "Consolidate related work" unless requested

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

### Step 1: Determine Scan Range

**Default: unpushed commits only.** Run:

```bash
UPSTREAM=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null)
```

- **If upstream exists and `--all` was NOT passed**: Use `git log --oneline $UPSTREAM..HEAD` to scan only unpushed commits. If user passed N, cap at N. If there are zero unpushed commits, report "No unpushed commits to squash" and stop (suggest `--all` if they want to include pushed history).
- **If upstream exists and `--all` WAS passed**: Use `git log --oneline -N` for the full requested range. Warn prominently: "Including pushed commits — squashing will require `git push --force-with-lease`."
- **If no upstream**: Use `git log --oneline -N` for the requested range (no remote to diverge from).
- **If user specifies a SHA range**: Use `git log --oneline <base>..<tip>` regardless of upstream.

Display the scan range and commit count before proceeding.

Before proposing any groups, also state whether this is a **tip-only cleanup**
or a deeper rewrite that will force many later commits to be replayed. If the
history is large or conflict-prone, bias toward tip-only cleanup first.

### Step 2: Analyze

Identify contiguous squash groups using the rules above. For each group, record:
- The SHAs (first and last in the group)
- The commit count
- A proposed squashed commit message
- Estimated impact using `git diff --shortstat <base>..<tip>`

Present a **table** to the user:

```
| # | Group Label              | Commits | SHA Range          | Proposed Message                        |
|---|--------------------------|---------|--------------------|-----------------------------------------|
| 1 | Yarli YRLI-52 workspace  | 3       | abc1234..def5678   | yarli: Complete YRLI-52 auth middleware  |
| 2 | Handoff docs update      | 2       | 111aaaa..222bbbb   | handoff: Update session handoff docs    |
```

Also show commits that will be **left untouched** (not in any group) so the user can verify nothing was missed or incorrectly excluded.

Flag groups as high risk if any of these are true:
- More than 300 files changed
- More than 20,000 lines touched
- Crosses a named phase or milestone boundary
- Crosses multiple tranche waves or repeated hotspot files

Also explicitly call out:
- whether the group is at the tip of history
- how many later commits would need to be replayed after the rewrite
- whether the range contains Yarli-style `task`, `merge`, `auto-repair`, or
  `reapply` commits, since these are often replay-sensitive

### Step 3: Confirm

Ask the user to approve, modify, or reject the plan. Offer options:
- **Approve as-is**: Proceed with the proposed groups and messages
- **Conservative**: Only squash groups with 3+ commits
- **Custom**: User specifies which groups to keep/drop/edit

Do NOT proceed without explicit user approval.

If `--batch` is used, collect one explicit approval for:
- Maximum passes (`--max-passes`)
- High-risk thresholds
- Per-pass test command

Recommend `Conservative` by default on large branches or replay-sensitive
histories.

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

For batch mode:
- Create a fresh editor script per pass (`/tmp/haake-squash-editor-<pass>.sh`)
- Create a unique backup tag per pass before rebasing
- Recompute groups after each successful pass
- Stop immediately on any failed health check or test failure

For any non-trivial cleanup, prefer running on a dedicated cleanup branch first.

For conflict-heavy batch mode on an isolated branch, enable rerere before passes:

```bash
git config rerere.enabled true
git config rerere.autoupdate true
```

Prefer the merge backend behavior and avoid apply-style workflows for conflict
prone cleanups, because merge-aware replay handles renames and context more
robustly than apply-style patching.

### Step 5: Verify

After rebase completes:
1. Run `git log --oneline -N` to show the cleaned-up history
2. Run `git range-diff` against the pre-pass backup ref to verify what changed
3. Run the project test suite if one exists (`cargo test`, `npm test`, `pytest`, etc.)
4. Report pass/fail status
5. Report per-pass and cumulative commit-count reduction

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

- **Unpushed-only by default**: The scan range is scoped to unpushed commits (`$UPSTREAM..HEAD`) unless `--all` is passed. This prevents accidentally proposing to rewrite published history. When `--all` is used, warn prominently that a force push will be required.
- **Dirty working tree**: If `git status --porcelain` shows uncommitted changes, refuse to proceed. Ask the user to commit or stash first.
- **Never auto-squash**: Always present the plan and wait for approval.
- **Never use --force**: Do not force-push. If the user needs to push after squashing, inform them they'll need `git push --force-with-lease` and let them do it.
- **Original HEAD recorded**: The full 40-char HEAD SHA is captured in Step 0 and printed at both the start and end of the run. This is the authoritative recovery point — it survives even if the backup tag is lost.
- **Backup ref**: Before rebasing, create a backup ref: `git tag -f pre-squash-backup` pointing at the original HEAD so the user can recover with `git reset --hard pre-squash-backup`.
- **Per-pass backup tags in batch mode**: Create `pre-big-band-<N>-YYYYMMDD` before each pass.
- **Prefer small passes**: Rewrite the smallest contiguous group that buys a
  meaningful reduction. Do not squash across multiple tranche waves at once
  unless the user explicitly accepts the replay risk.
- **Replay warning**: Contiguous commits can still cause later conflicts because
  later commits are replayed on the rewritten base during rebase.
- **Use rerere on cleanup branches**: Prefer `git config rerere.enabled true`
  and `git config rerere.autoupdate true` before multi-pass cleanup.
- **Prefer tip-first cleanup**: Start with the newest self-contained group so
  fewer later commits must be replayed.
- **Verify with range-diff**: After each successful pass, compare pre/post
  ranges with `git range-diff` before attempting another pass.
- **Size guard**: If a proposed squash exceeds 300 files or 20,000 touched lines, require explicit user confirmation.
- **Milestone guard**: Avoid squashing across major phase boundaries unless explicitly approved.
- **Conflict policy (default)**: Abort on conflict with `git rebase --abort` and report the recovery SHA.
- **Conflict policy with rerere (explicit opt-in)**:
  - Only on an isolated history-cleanup branch
  - Allow at most one rerere-assisted retry
  - If still conflicted, abort and stop batch mode
- **Diminishing returns stop**: In batch mode, stop when no contiguous group has 3+ commits or expected reduction is <= 1 commit/pass.
- **Post-squash health check**: After completion, verify no rebase state dirs (`.git/rebase-merge`, `.git/rebase-apply`), no stale lock files (`.git/index.lock`, `.git/refs/heads/*.lock`), and working tree is clean. Report any anomalies.

## Example Sessions

### Default (unpushed only)

```
User: /squash-commits

Claude:
Original HEAD: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
To restore:    git reset --hard a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2

Upstream: origin/master (8 commits ahead)
Scanning 8 unpushed commits...

Found 2 squash groups among 8 unpushed commits:

| # | Group Label              | Commits | SHA Range          | Proposed Message                              |
|---|--------------------------|---------|--------------------|-------------------------------------------------|
| 1 | Ideate feature           | 3       | abc1234..def5678   | feat: Add ideate subcommand with pager          |
| 2 | Clippy fix + recovery    | 2       | 333cccc..444dddd   | fix: Resolve clippy warnings in rest.rs          |

3 commits remain untouched (standalone).
Result: 8 commits → 5 commits. No force push needed.

Approve this plan? [Approve / Conservative (3+ only) / Custom / Cancel]
```

### With --all (includes pushed history)

```
User: /squash-commits 30 --all

Claude:
Original HEAD: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
To restore:    git reset --hard a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2

⚠ Including pushed commits — squashing will require force push.
Scanning last 30 commits...

Found 4 squash groups among 30 commits:
...
```

### After squash completes

```
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
