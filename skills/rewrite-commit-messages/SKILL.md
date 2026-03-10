---
name: rewrite-commit-messages
description: "Use when the user wants to rewrite existing git commit messages with git filter-repo, rename commit messages in bulk, normalize noisy auto-generated messages, or safely plan a history-wide message-only rewrite."
argument-hint: "[commit-range]"
---

# Rewrite Commit Messages

Safely rewrite existing git commit messages using `git filter-repo`.

Use this skill when the user wants to:
- rename one or more historical commit messages
- normalize repeated generated messages
- replace noisy tranche/merge wording with cleaner summaries
- perform a message-only history rewrite with explicit mappings

Do **not** use this skill for:
- squashing or reordering commits
- changing file contents
- partial staging or creating a new commit from the working tree

Use `/commit` for new commits and `/squash-commits` for rebase-based history cleanup.

## Safety model

This skill rewrites commit SHAs. Treat it as history surgery.

Before making any change:
1. Record and print the full original `HEAD` SHA.
2. Confirm the working tree is clean.
3. Create a backup ref/tag pointing at the original `HEAD`.
4. Require explicit old→new message mappings.
5. Prefer rewriting only commit messages; do not modify trees, authors, or dates unless the user explicitly asks.

Always print:

```text
Original HEAD: <full 40-char SHA>
To restore:    git reset --hard <full 40-char SHA>
Backup tag:    pre-filter-repo-backup
```

## Workflow

### Step 1 — Preflight

Run:

```bash
git rev-parse HEAD
git status --porcelain
git rev-parse --abbrev-ref @{upstream} 2>/dev/null || true
command -v git-filter-repo
```

Rules:
- If the tree is dirty, stop and ask the user to commit or stash first.
- If `git-filter-repo` is unavailable, stop and report it.
- If the branch has pushed commits and the user did not clearly approve rewriting them, warn that a force-push will be required.

### Step 2 — Collect exact rewrite rules

Require explicit mappings in this format:

```text
old: yarli: auto-repair merge conflict for tranche-014-i345
new: yarli: Finalize tranche I345 shell runtime merge
```

Rules:
- Treat `old:` as exact text unless the user explicitly asks for regex behavior.
- Do not infer replacements.
- If multiple old messages map to one new message, list each mapping separately.
- If a mapping is ambiguous, stop and ask.

### Step 3 — Show the rewrite plan

Before running `git filter-repo`, print:
- original HEAD
- backup tag name
- whether the rewrite targets unpushed history only or includes pushed history
- each `old -> new` mapping
- the count of matching commits per mapping when feasible

Example:

```text
Rewrite plan:
  old: yarli: auto-repair merge conflict for tranche-014-i345
  new: yarli: Finalize tranche I345 shell runtime merge
  matches: 1
```

Do not proceed without explicit approval.

### Step 4 — Create a backup ref

Create a recovery tag before rewriting:

```bash
git tag -f pre-filter-repo-backup "$(git rev-parse HEAD)"
```

For repeated passes, prefer unique tags such as:

```bash
pre-filter-repo-backup-YYYYMMDD-HHMMSS
```

### Step 5 — Run git filter-repo in message-only mode

Prefer a message callback that rewrites only exact message matches.

Pattern:

```bash
git filter-repo --force --message-callback '
msg = message.decode("utf-8")
if msg == "OLD MESSAGE":
    return b"NEW MESSAGE"
return message
'
```

For multiple mappings, use a dictionary in the callback.

Rules:
- Rewrite only commit messages.
- Preserve all non-message metadata unless the user explicitly asks otherwise.
- Keep replacements deterministic and exact.
- Avoid regex rewrites by default.

### Step 6 — Verify

After the rewrite, run:

```bash
git log --oneline -N
git rev-parse HEAD
git status --porcelain
```

Also verify that the targeted messages changed and that unrelated messages did not.

If the branch tracks a remote, remind the user that they will need:

```bash
git push --force-with-lease
```

Do not push for them unless explicitly asked.

### Step 7 — Summarize recovery information

Always end with:

```text
Rewrite complete.
  Original HEAD: <full 40-char SHA>
  Current HEAD:  <full 40-char SHA>
  Backup tag:    pre-filter-repo-backup
  To restore:    git reset --hard <original HEAD SHA>
```

## Safety guardrails

- Never run with a dirty working tree.
- Never infer message rewrites from vague intent.
- Never rewrite authors, timestamps, trees, or paths unless explicitly requested.
- Never push after the rewrite unless explicitly asked.
- Prefer exact-string rewrites over regex.
- If the user wants to change commit structure, use `/squash-commits` instead.
- If the user wants only the latest commit message changed, prefer `git commit --amend` rather than `git filter-repo`.
