---
name: new-worktree-feature
description: Start subsequent feature or bounded work in a new Git worktree under the prescribed project worktree root, preserving the current checkout and checking branch and path safety first.
---

# New Worktree Feature

Use this skill when beginning a new feature, fix, experiment, or review that
should be isolated from the current checkout. On the host, the target is
`~/Documents/worktrees/<project-name>/<branch-name>`. Inside a Chasm guest,
the target is `/workspace/.worktrees/<project-name>/<task-name>` and the
primary checkout remains `/workspace/<project-name>`. Select the environment
from verified runtime context; never silently use a host path in the guest or
a guest path on the host.

## Before creation

Inspect the current repository root, default branch, remotes, current branch,
and worktree registry. Preserve existing changes in the current checkout; do
not stash, reset, clean, or commit them merely to create the new worktree.
Choose a lowercase hyphenated branch name with a `feat/`, `fix/`, `chore/`, or
`review/` prefix that reflects the requested work. Check that both the branch
name and destination path are unused, and report an existing collision instead
of reusing it.

Derive the project directory from the repository name, sanitize only characters
that are invalid or unsafe in a path, and show the exact branch and destination
before creation. In a guest, require project and task names to match
`[A-Za-z0-9][A-Za-z0-9._-]{0,127}` as single components; the branch name may
still contain `/`. Reject traversal, symlinked parents, and paths outside
`/workspace/.worktrees`. The new worktree should normally start from the
current default branch or another explicitly requested base. Do not silently
base it on the dirty current branch.

## Create and verify

Create the parent directory under the selected environment's root and use
`git worktree add -b <branch> <destination> <base>` (or an equivalent
existing-branch form only when explicitly requested). In a Chasm guest,
`<destination>` must be
`/workspace/.worktrees/<project-name>/<task-name>`. Verify that:

- the destination is registered by `git worktree list`;
- it is on the intended branch and base commit;
- its initial tree is clean;
- the original checkout still has exactly its prior status.

For guest worktrees, verify that the primary checkout is
`/workspace/<project-name>`, the task path is inside `/workspace/.worktrees`,
and the worktree registry records the intended branch and base. Do not copy
host `.git/config`, credentials, or authentication directories into the guest;
rebuild the worktree from the guest checkout and a reviewed history/status
payload when migration recovery is involved.

Do not install dependencies, run migrations, push branches, or open a pull
request as part of worktree creation. Those are separate actions requiring
their own scope and approvals.

## Handoff

Report the new worktree path, branch, base commit, verification results, and
the original checkout status. If creation fails, leave existing work untouched
and explain the smallest corrective action.
