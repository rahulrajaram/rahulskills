# Shared history-rewrite safety contract

Apply before rewriting commits, paths, messages, tags, or refs. Carry forward
still-valid authorization for the concrete refs and transformations; do not ask
again merely because a child skill was loaded. Prepare the exact scope and
preview before asking about an unresolved history rewrite or external effect.

## Scope and recovery

- Record the original HEAD, every ref and its object ID, and the selected refs.
  Distinguish local changes from publication: rewriting locally does not itself
  authorize a force-push or changes to other shared copies.
- Require a clean worktree, including untracked files. Inspect linked worktrees,
  shallow history, replace refs/grafts, signed commits/tags, submodules and LFS.
  Resolve relevant limitations before mutation. The recipes below assume a
  complete ordinary repository without replace refs/grafts and no other worktree
  checking out an affected branch. Git bundles do not contain LFS payloads or
  submodule repositories; preserve those separately when the requested operation
  affects them. Signatures on rewritten objects cannot be preserved as valid.
- Bind `rewrite_refs` to the reviewed, fully qualified refs, never an implicit
  all-ref selection. Resolve any commit range separately from destination refs;
  for message edits, an exact commit-ID callback can limit changed messages while
  necessary descendants receive new parent IDs. For cleaning, scope verification
  to everything reachable from the selected refs.
- Before mutation, create an independent private bundle outside the repository.
  An in-repository tag or a printed SHA is only an additional recovery handle.
  Protect the originals: cleaning deliberately leaves prohibited terms in this
  private recovery copy and in unselected refs. Never publish the backup.

The following Bash setup is a template: bind the reviewed refs and an existing
private backup parent directory first. Do not run placeholder values. Reading
all refs into a backup does not select all refs for rewriting.

```bash
set -euo pipefail
rewrite_refs=(refs/heads/REVIEWED_BRANCH)
backup_parent=/ABSOLUTE/PRIVATE/BACKUP/DIRECTORY
[[ ${#rewrite_refs[@]} -gt 0 ]]
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]]
for ref in "${rewrite_refs[@]}"; do
  [[ "$ref" == refs/* ]]
  git show-ref --verify "$ref"
done
# backup_parent must resolve outside this repository and its linked worktrees.
umask 077
backup_dir=$(mktemp -d "$backup_parent/history-rewrite.XXXXXXXX")
git rev-parse HEAD > "$backup_dir/original-head"
git for-each-ref --format='%(refname) %(objectname)' > "$backup_dir/refs-before"
printf '%s\n' "${rewrite_refs[@]}" > "$backup_dir/rewrite-refs"
git bundle create "$backup_dir/original.bundle" --all HEAD
git bundle verify "$backup_dir/original.bundle"
# Prove recovery does not depend on objects remaining in the source repository.
git init --bare --template= "$backup_dir/recovery.git"
git -C "$backup_dir/recovery.git" -c core.hooksPath=/dev/null fetch "$backup_dir/original.bundle" \
  'refs/*:refs/*' 'HEAD:refs/recovery/original-head'
git -C "$backup_dir/recovery.git" fsck --full
```

Recovery verification suppresses template and inherited hooks so creating the
backup does not execute unrelated user hooks. Preserve the source repository's
hook configuration.

If `git-filter-repo` is missing, report the blocker. Do not install it implicitly.
Use explicit `--partial --refs "${rewrite_refs[@]}"` on **every** filter-repo
invocation. Partial mode disables automatic reflog expiry/GC, origin removal,
and deletion of unexported refs. `--force` only bypasses the fresh-clone check;
it is not approval or a recovery mechanism. Never fall back to an unscoped
command. Disable empty/degenerate commit pruning unless removing commits is
explicitly part of the agreed transformation. Preserve hash text and encoding
unless their changes are selected. Keep transformation inputs outside the
worktree, inspect them before running, and preserve them with the evidence.

## Verification and rollback

Compare all ref names and IDs before/after: only reviewed refs may change.
Preserve filter-repo's `commit-map` (and `ref-map` when available) outside its
working metadata immediately after each run; later runs can replace/compose it.
Compare selected reachability, commit counts and parent mappings against the
independent originals. Any removed commits or signature/header loss must match
the reviewed effects. Apply the skill-specific content/message checks and
relevant tests; a clean worktree or successful filter command is insufficient.

Report original/current HEAD, changed refs, transformation results, verification
coverage and backup path. For recovery, the independent `recovery.git` contains
the old refs and objects. To restore in place, first preserve any new work,
fetch a specific original ref from `original.bundle` into a fresh recovery ref,
then restore the affected ref(s) to the recorded original IDs under valid
rollback authority. A single `reset --hard` restores only the checked-out branch
and discards working files; it is not a general rollback recipe. Do not perform
rollback automatically after a failed check or claim completion; report the
failure with intact recovery handles.

Never force-push, delete backups, expire reflogs, or garbage-collect without
explicit authorization covering that effect. A request to sanitize selected
published refs is not authorization to erase private recovery copies or
unselected refs. If full erasure is requested, prepare that additional scope
and its loss of recovery separately.
