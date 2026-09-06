---
name: rewrite-commit-messages
description: "Use when the user wants to rewrite existing git commit messages with git filter-repo, rename commit messages in bulk, normalize noisy auto-generated messages, or safely plan a history-wide message-only rewrite."
argument-hint: "[commit-range]"
---

# Rewrite Commit Messages

Before mutation, read and follow
[`../../references/history-rewrite-safety.md`](../../references/history-rewrite-safety.md).
This skill adds message-specific transformations and verification.

Rewrite historical messages without changing file content or commit topology.
For creating a commit use `/commit`; for squashing or reordering use
`/squash-commits`. For only the latest message, prefer `git commit --amend`
with the same scope, recovery and content checks.

## Preflight and preview

Inspect HEAD, worktree status, selected refs, upstream tracking and locally
available `git-filter-repo`. Local tracking evidence can be stale; do not infer
that shared history is unpushed merely because it is ahead of a tracking ref.
Follow the shared preflight and create the independently verified backup before
mutation.

Collect exact old/new message mappings, including full bodies and trailing
newlines. Resolve them to full original commit IDs in the reviewed history.
If asked to propose better wording, prepare replacements from commit evidence
for review; do not treat vague intent as approval for invented replacements.
Show original HEAD, selected refs, matched commit IDs/counts, message changes,
necessary descendant rewrites, signature implications and backup location.
Proceed on still-valid authorization for that concrete plan; ask only when the
mapping, affected refs or effect authority remains unresolved.

## Execute the message-only transformation

Use a commit callback so annotated-tag messages are not implicitly rewritten.
In Bash, use the `rewrite_refs` and `backup_dir` prepared by the shared contract.
Populate the callback with the reviewed full IDs and exact message bytes
before executing. The placeholders below are deliberately not real mappings.

```bash
git filter-repo --force --partial \
  --preserve-commit-hashes --preserve-commit-encoding \
  --prune-empty never --prune-degenerate never \
  --commit-callback '
rules = {
    b"FULL_ORIGINAL_COMMIT_ID": (b"EXACT OLD MESSAGE\n", b"EXACT NEW MESSAGE\n"),
}
rule = rules.get(commit.original_id)
if rule is not None:
    old, new = rule
    if commit.message != old:
        raise ValueError("Reviewed message no longer matches")
    commit.message = new
' --refs "${rewrite_refs[@]}"
```

For many rules, keep the reviewed callback in a private file and pass its
absolute path to `--commit-callback`. Do not interpolate arbitrary message text
into shell code. Do not add file, author, date or path callbacks. Do not omit
partial mode or the selected ref array on retries.

## Verify and report

Preserve the commit map and compare rewritten objects against the independent
backup, not against an in-repository backup ref that could have moved.

- Every selected old commit maps to exactly one surviving new commit; commit
  counts and ordered parents correspond through the map. No squashing/pruning.
- For every mapped commit, `git rev-parse <old>^{tree}` in the recovery repo
  equals `git rev-parse <new>^{tree}` in the rewritten repo. This proves file
  names, modes and blob contents are unchanged across historical trees.
- Read raw commits with `git cat-file commit`: messages equal the approved
  replacement for targeted IDs and the original bytes for all other commits.
  Author/committer identities and dates, encoding and other headers remain
  unchanged except reviewed signature effects and mapped parent IDs.
- All unselected refs retain their original IDs; selected refs point to the
  expected mapped objects. Check annotated tags separately if selected.
- Worktree is clean and relevant verification succeeds. Tree equality is the
  primary proof of message-only behavior; running a build alone is not.

Report original/current HEAD, changed refs and messages, verified invariants,
and the actual external bundle/recovery path. If verification fails, preserve
recovery evidence and report the failed property instead of declaring success.
Explain any remaining separately authorized publication step; do not push as an
implicit consequence of rewriting locally.
