# Shared history-rewrite safety contract

Apply this before any skill rewrites commits, paths, messages, tags, or refs.

1. Determine whether affected refs were pushed or shared. Local invocation does
   not authorize rewriting shared history.
2. Require a clean worktree, record original refs, and create a recoverable
   backup ref or bundle before mutation. A printed SHA alone is not a backup.
3. Preview exact commits, refs, and transformations; identify signed objects,
   submodules, LFS, and protection implications; then obtain explicit approval.
4. Prefer deterministic transformations and validate on a disposable ref or
   clone when feasible.
5. Verify refs, commit count, trees, content/message invariants, tests, and the
   working tree after rewriting.
6. Report old/new mappings and rollback. Never force-push, delete backups,
   expire reflogs, or garbage-collect without separate approval.

If `git-filter-repo` is missing, stop. Do not install it implicitly or substitute
an ad hoc destructive workflow.
