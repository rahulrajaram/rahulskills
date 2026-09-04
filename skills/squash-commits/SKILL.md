---
name: squash-commits
description: "Analyze Git history and safely squash contiguous thematic commits with recoverable backups and clean conventional messages. Use when the user asks to squash, consolidate, compress, or tidy commit history."
---

# Squash Commits

Analyze first and rewrite only after the user approves an exact plan.

Before any mutation, read and follow
[`../../references/history-rewrite-safety.md`](../../references/history-rewrite-safety.md)
completely. That shared contract governs clean-tree checks, shared-history
boundaries, backups, verification, rollback, and force-push restrictions. This
skill adds contiguous grouping, commit-message composition, and squash-specific
execution rules.

## Arguments

`$squash-commits [N] [--all] [--batch] [--max-passes M]`

- `N` limits analysis to the most recent N eligible commits; default to 20.
- Without `--all`, analyze only commits ahead of the upstream tracking branch.
- `--all` may include pushed commits in the preview. It does not authorize
  rewriting shared history or force-pushing it.
- `--batch` permits multiple approved, conservative passes.
- `--max-passes M` bounds batch mode; default to 5 and reject non-positive
  values. Recommend no more than 20.
- An explicit `<base>..<tip>` supplied by the user overrides `N`, but not the
  safety or approval requirements.

## Candidate Rules

Only propose a group when all of its commits are adjacent in the selected
first-parent history. Never skip an unrelated commit to join similar work.

Good candidates include:

- a feature immediately followed by its correction;
- contiguous implementation, tests, and documentation for one cohesive unit;
- repeated handoff or workspace-state commits from one session;
- related cleanup or formatting commits;
- consecutive commits with identical or nearly identical messages.

Leave these untouched unless the user explicitly chooses otherwise:

- a distinct, self-contained commit;
- a merge commit;
- commits separated by unrelated work;
- commits on opposite sides of a release, milestone, or work-wave boundary;
- a group whose relationship is inferred only from similar wording.

Contiguity does not guarantee a conflict-free rebase. Later commits are replayed
on the rewritten parent and may conflict even when the proposed group itself is
coherent. Prefer a tip group, then the smallest useful range.

## Commit Messages

Propose a conventional message that represents the resulting commit:

- imperative subject of at most 72 characters;
- a specific conventional type such as `feat`, `fix`, `docs`, `refactor`,
  `test`, or `chore`;
- no trailing period;
- optional body wrapped near 72 characters that explains why the combined
  change exists;
- no inferred co-author trailers;
- never add a `Co-Authored-By` trailer identifying Claude.

## Workflow

### 1. Inspect Without Mutating

Record the full original HEAD first:

```bash
git rev-parse HEAD
git status --porcelain=v1
git rev-parse --abbrev-ref HEAD
git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null
```

Print the original 40-character SHA prominently. Do not present
`git reset --hard` as the only recovery mechanism; a real backup ref is
required before rewriting.

Stop before analysis becomes execution when:

- the working tree or index is dirty;
- a rebase is already in progress;
- `.git/index.lock` or a ref lock exists and another Git process may be active;
- HEAD changes during planning;
- repository ownership, target branch, or requested range is ambiguous.

Determine the analysis range:

1. If the user supplied `<base>..<tip>`, validate and use that range.
2. Otherwise, when an upstream exists and `--all` is absent, inspect
   `@{upstream}..HEAD`, capped by `N`.
3. When no upstream exists, inspect the latest `N` first-parent commits.
4. With `--all`, inspect the requested first-parent range and label every
   pushed or shared commit explicitly.

If there are no eligible unpushed commits, report that fact and stop. Suggest
`--all` only as a broader *analysis* option.

Inspect enough evidence to identify replay and trust risks:

```bash
git log --first-parent --reverse --format='%H%x09%P%x09%s' <range>
git diff --stat <base>..<tip>
git submodule status
git lfs env 2>/dev/null
```

Also identify merge commits, signed commits or tags, branch protection
implications, repeated hotspot files, auto-repair or conflict-fix commits, and
the number of later commits that a deeper rewrite would replay.

### 2. Present an Exact Plan

For each proposed group, show:

| Field | Required content |
|---|---|
| Group | A short thematic label |
| Commits | Count and every full or unambiguous SHA |
| Range | Oldest through newest commit |
| Location | Tip group or number of later commits replayed |
| Impact | Files and insertions/deletions from the group diff |
| Message | Complete proposed subject and body |
| Risk | Normal or a concrete high-risk reason |

Then list every analyzed commit not included in a group. This makes omissions
and accidental grouping visible.

Mark a group high risk when it:

- changes more than 300 files or 20,000 lines;
- crosses a milestone or work wave;
- requires replay through merges or repeated hotspot edits;
- includes auto-repair, reapply, conflict-fix, generated, signed, submodule, or
  LFS-sensitive commits;
- includes history known to be pushed or shared.

State whether the plan is tip-only or a deeper rewrite. Do not mutate anything
until the user explicitly approves the exact groups and messages. Offer a
conservative choice that keeps only groups of at least three commits when the
range is large or replay-sensitive.

For batch mode, approval must also fix:

- the maximum number of passes;
- the high-risk thresholds;
- the verification or test command run after every pass;
- whether the work occurs on a dedicated cleanup branch.

### 3. Revalidate and Create a Backup Ref

Immediately before execution, confirm that the tree is still clean, HEAD still
equals the recorded original HEAD, and the approved range still resolves to
the same commits.

Create a collision-safe ref without moving or overwriting an existing ref:

```bash
backup_ref="refs/tags/pre-squash-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short=12 HEAD)"
git show-ref --verify --quiet "$backup_ref" && exit 1
git update-ref "$backup_ref" "$(git rev-parse HEAD)"
git rev-parse --verify "$backup_ref"
```

Record the unchanged base SHA as well as the backup ref. In batch mode, create
a distinct backup ref before every pass.

### 4. Execute the Smallest Approved Rewrite

Prefer one contiguous group per pass. Build a deterministic sequence editor in
a directory created with `mktemp -d`:

- match the approved commit identities, not merely their subject text;
- leave the oldest commit in a group as `pick`;
- change each immediately following approved commit to `fixup`;
- insert an `exec git commit --amend -F <message-file>` after the final fixup;
- fail if any approved commit is absent, duplicated, reordered, or no longer
  adjacent;
- leave every unapproved todo line unchanged.

Run interactive rebase from the parent of the oldest rewritten commit. Use
`--root` when the approved group includes the root commit. Do not flatten merge
topology accidentally: if the replay range includes a merge, stop unless the
approved plan explicitly describes and verifies `--rebase-merges` behavior.

If rebase conflicts, abort with `git rebase --abort` and stop. Do not improvise
conflict resolutions. A single rerere-assisted retry is allowed only when the
user approved it in advance on an isolated cleanup branch.

Delete only the temporary directory created for this pass after rebase finishes
or aborts. Never delete the backup ref as cleanup.

### 5. Verify Preservation and Health

After each pass:

1. Verify that the final tree is byte-equivalent to the pre-pass tip:

   ```bash
   git diff --exit-code "$backup_ref^{tree}" "HEAD^{tree}"
   ```

2. Compare the old and new commit series:

   ```bash
   git range-diff <unchanged-base>..<backup-ref> <unchanged-base>..HEAD
   ```

3. Confirm the expected commit-count reduction and inspect every rewritten
   message.
4. Fail verification if any rewritten message contains a case-insensitive
   `Co-Authored-By` trailer identifying Claude.
5. Run the agreed focused checks and project test suite.
6. Confirm the tree is clean, HEAD is valid, no rebase state remains, and no
   stale lock file is present.

If a check fails, stop batch mode and report both the original SHA and backup
ref. Do not reset, delete a ref, or retry another rewrite without authorization.

For another approved batch pass, recompute candidates from the new history.
Stop when the pass limit is reached, no approved group remains, a check fails,
or the expected reduction is at most one commit.

### 6. Report

Always report:

```text
Squash complete.
  Original HEAD: <full SHA before all passes>
  Current HEAD:  <full final SHA>
  Backup refs:   <one per executed pass>
  Reduction:     <old count> -> <new count>
  Verification:  <tree, range-diff, messages, tests, repository health>
  Restore point: <backup ref and original SHA>
```

If the rewritten history was previously pushed, explain that updating the
remote would require a separately authorized `git push --force-with-lease`.
Never push, delete backup refs, expire reflogs, or garbage-collect as part of
this skill unless the user separately authorizes that exact action.

## Related Workflows

- Use `$commit` to create a new commit from working-tree changes.
- Use `$rewrite-commit-messages` for message-only history rewrites.
- Use `$handoff` for a verified continuation artifact after repository work.
