---
name: reference-cleaner
description: "Remove references to blocklisted terms from git history and source files. Use when user says /reference-cleaner, 'clean references', 'remove mentions of X', 'scrub project names from history', or asks to sanitize a repo before publishing."
argument-hint: "<term> [<term>...]"
---

# Reference Cleaner

Before history mutation, read and follow
[`../../references/history-rewrite-safety.md`](../../references/history-rewrite-safety.md).
The shared scope, independent backup and recovery contract applies to every
filter-repo invocation below.

Remove agreed terms from current files or selected reachable history. Establish
which outcome the user requested: current-only cleanup does not promise
historical sanitization. A full historical cleanup must cover retained files'
old blobs as well as deleted paths and complete commit messages.

## Scan and prepare the transformation

Obtain the blocklist and any whitelist. Treat terms as literal strings unless
regex was requested; specify case sensitivity, byte/text encoding and the
whitelist's context rules. Escape regex metacharacters when using literal terms.
Do not silently narrow full history scope to the current branch or current tree.
Bind the selected refs as described in the shared contract.

Scan tracked current paths/content using NUL-delimited filenames or structured
Git plumbing. Inspect full commit messages, historical paths, and blob contents
reachable from **each selected ref**, including old versions of files still
present today. `git log --name-only` does not inspect file content. Report
binary, LFS, submodule and encoding limitations during preparation.

Prepare a concrete table of DELETE, EDIT, RENAME and historical purge/replacement
operations, with exact paths, replacement rules, whitelist exceptions and
message before/after examples. Deleting a current file does not select its
entire history for purging. Path purges must include reviewed historical names;
Git does not automatically follow renames for filtering.

Carry existing valid approval for the selected plan into execution. If scope,
transformations or authority are unresolved, finish the preview and ask about
that decision before its dependent mutation. Local source edits, commits,
history rewriting and publication have distinct effects; perform the effects
covered by the user's request and existing authorization.

## Current files

Apply approved edits, deletions and renames. Whitelisted occurrences stay intact.
Rename code identifiers coherently and run relevant build/tests. If committing
these edits is in scope, commit only the intended changes before rewriting;
otherwise leave the reviewed current-only result or resolve how to obtain the
clean worktree required for history mutation. Do not auto-stash unrelated work.

## Historical content, paths and messages

Prepare and independently verify the external backup before history mutation.
For retained historical text files, use reviewed `--replace-text` rules or a
blob callback. A source edit at HEAD cannot replace those historical blobs.
The following Bash template combines the selected operations in one pass to
avoid losing intermediate mapping evidence. Bind `rewrite_refs` from the
reviewed scope and prepare the referenced files first. Omit options for effects
that are not selected; the paths shown are placeholders, not a purge policy.

```bash
replacement_file="$backup_dir/reviewed-replacements.txt"
message_callback="$backup_dir/reviewed-message-callback.py"
git filter-repo --force --partial \
  --preserve-commit-hashes --preserve-commit-encoding \
  --prune-empty never --prune-degenerate never \
  --replace-text "$replacement_file" \
  --commit-callback "$message_callback" \
  --invert-paths --path 'REVIEWED/PURGED/PATH' \
  --refs "${rewrite_refs[@]}"
```

For a simple literal rule the replacement file can contain
`literal:BLOCKED_TEXT==>REVIEWED_REPLACEMENT`. Inspect filter-repo's expression
syntax before representing terms that contain delimiters or newlines. Literal
replacement is case-sensitive; explicit variants or reviewed regex rules are
needed for a case-insensitive policy. The commit callback operates on
`commit.message`; use exact reviewed transformations and preserve other metadata.
If selected annotated-tag messages also contain terms, handle and verify those
explicitly rather than implying that a commit callback covers them.

A global replacement is unsuitable when an occurrence is whitelisted by file
or context. Use a transformation that can honor that context (for example,
reviewed file-specific processing); do not apply a blanket replacement and
claim whitelist support. Binary contents, encodings and external LFS/submodule
payloads require an explicit supported treatment. Keep unresolved matches
visible; do not silently delete them or claim they were sanitized.

## Verify the actual reachable content

Verify against the independent originals and preserve the commit map. Scan
**the selected refs**, not `--all`: private originals and unselected refs are
intentionally retained. To enumerate actual historical contents, use this
procedure in Python or equivalent structured tooling:

1. Obtain unique commits with `git rev-list <selected-ref>...`.
2. For each commit, read `git ls-tree -r -z --full-tree <commit>` and split on
   NUL, then split each record once at TAB. Check the raw path against the
   agreed term/whitelist policy. This handles spaces and newlines in filenames.
3. For each entry whose type is `blob`, read bytes with `git cat-file blob <oid>`
   and check the full contents. Cache by blob ID, but apply path-dependent
   whitelist rules at each occurrence. This checks retained files at every
   historical version, not only their latest content. Include symlink blobs.
4. Read each raw commit with `git cat-file commit <oid>` and scan its entire
   message after the first blank line. Inspect selected annotated-tag names and
   messages separately. Record gitlink entries (submodules) and LFS pointers
   as coverage limits unless their external contents were also checked.
5. Compare intended transformations against original paths/blobs/messages;
   ensure whitelist matches and unrelated content are preserved. Check parent
   mappings and commit counts, all unselected ref IDs, and clean worktree state.
   Run relevant build/tests on the resulting current files.

A nonmatching search is evidence only if traversal completed successfully. A
read/decode error, unsupported binary or absent external payload is incomplete
coverage, not “zero matches.” A byte-level scan can detect literal byte terms
in binary blobs, but does not establish absence in compressed/encoded payloads.
Report the term semantics, selected refs, commits/blobs checked, residual matches,
whitelist exceptions and coverage limitations. Claim full selected-history
sanitization only when those checks support it. Current-file tests alone cannot.

Report original/current HEAD, changed refs, transformation evidence and actual
backup/recovery paths. Explain that original private backups, unselected refs,
reflogs, remote copies and caches are outside a selected-reachability claim.
Retain recovery evidence. Publication and permanent erasure require authority
covering those effects; do not add cleanup or force-push commands implicitly.
