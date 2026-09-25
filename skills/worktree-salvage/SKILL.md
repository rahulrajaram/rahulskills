---
name: worktree-salvage
description: Audit a repository and its related Git worktrees, identify recoverable and unsalvaged work, and produce a status table with evidence-based recommendations for dormant or merged worktrees.
---

# Worktree Salvage

Use this skill when work may be stranded across checkouts, detached heads,
stale branches, temporary directories, or the prescribed host
`~/Documents/worktrees` area. In a Chasm guest, include the primary checkout
and task worktrees under `/workspace/.worktrees/<project-name>/<task-name>`.
The default deliverable is an evidence-backed report about the present project
only. Do not delete, reset, clean, prune, or rewrite history as part of the
audit.

The optional `--all` argument changes the scope to a machine-wide inventory of
project worktrees. With `--all`, discover repositories and their worktrees
under the user's home and configured worktree roots, group rows by repository,
and clearly separate the present project from unrelated projects. Without
`--all`, do not report unrelated repositories merely because they happen to be
under `~/Documents/worktrees`.

## Audit boundaries

### Default project scope

Start at the current or requested repository and inspect:

- `git worktree list --porcelain` for registered worktrees;
- sibling worktree roots explicitly named by repository guidance, especially
  `~/Documents/worktrees/<project>/`;
- current branch or detached HEAD, upstream, local changes, untracked files,
  ignored files that may contain work, and latest commit for each checkout;
- whether each branch is merged into the default branch or its configured
  upstream, whether its upstream is gone, and whether its commits remain
  reachable from any local ref, remote-tracking ref, tag, or worktree HEAD.

Identify the repository root for each candidate. A registered worktree is in
scope even when it is outside the conventional worktree directory.

When the repository is inside a Chasm guest, inspect the registered worktrees
and the bounded guest roots `/workspace/<project-name>` and
`/workspace/.worktrees/<project-name>/`. Do not crawl the host's
`~/Documents/worktrees` from the guest, and do not treat a guest path as a host
worktree. Report whether each dirty or untracked state has a reviewed bundle,
patch, deletion list, or payload recovery record; a tar copy without Git
history is not sufficient recovery evidence.

### Machine-wide `--all` scope

When `--all` is present, inspect all discoverable Git repositories and
worktrees in the current environment: on the host use `~/Documents/worktrees`
and configured project roots; in a confirmed Chasm guest use `/workspace` and
`/workspace/.worktrees`. Include registered worktrees outside those defaults
without treating a guest path as a host path. Use bounded filesystem
discovery; do not crawl system directories or follow arbitrary mounts. Report
the discovery roots and any unreadable or skipped locations so the inventory's
coverage is honest.

## Salvage classification

Classify evidence before recommending cleanup:

- **Unsalvaged**: uncommitted tracked changes, untracked files, or ignored files
  that may contain work and have no verified recovery path.
- **Recoverable**: committed work reachable from a branch, tag, remote-tracking
  ref, or a registered worktree HEAD, even if the checkout is detached.
- **Dormant**: clean worktree or branch with no recent activity and no current
  worktree-local changes; dormancy alone is not permission to delete.
- **Merged**: branch tip is an ancestor of the relevant base branch. Check for
  uncommitted files before treating the checkout as disposable.
- **Blocked**: unreadable, missing, corrupt, or ambiguous state that prevents a
  safe conclusion.

For detached committed work, recommend creating a descriptive branch at the
exact HEAD before any cleanup. For uncommitted work, recommend a patch or
commit-based capture only after inspecting its contents; do not silently stage,
commit, or overwrite it.

## Required report

Report local evidence and its limits, then provide a Markdown table with at
least these columns:

| Worktree | Repository | Branch/HEAD | Tree | Local work | Reachability | Merge state | Recommendation |
|---|---|---|---|---|---|---|---|

Use concise values and link each recommendation to the evidence that supports
it. In default mode, state which work is genuinely unsalvaged and which is
recoverable within the present project. In `--all` mode, also identify
unrelated projects and summarize them separately. Include a separate “safe
next actions” list ordered as capture, verify, then cleanup.

## Cleanup recommendations

A deletion recommendation is allowed only when the checkout is clean, its
commits are recoverable from a verified ref or no unique commits exist, and it
is merged or demonstrably obsolete. Say `recommend delete after capture` when
capture is still needed. Never execute deletion from this skill unless the user
explicitly authorizes the exact worktree paths after reviewing the report.
