# Cross-Repository Remediation Release Review

Date: 2026-07-11
Remote observation time: 2026-07-11
Status: local review complete; no push or PR mutation performed

Remote branch tips were read with `git ls-remote`; visibility and GPTQueue PR
state were read through GitHub. All five local histories are strict descendants
of the observed remote branch tip (zero remote-only commits), so no integration
is currently required before publication. A fresh check is still mandatory at
approval time.

| Repository | Visibility | Local branch / HEAD | Observed remote tip | Ahead | Remediation evidence |
|---|---|---|---|---:|---|
| Rahulskills | public | `master` / documentation commits | `master` / `1e8c7fb` | 9 | packaging/catalog wave plus 3 harness tests, 39/40 assembly, and activation evidence |
| Haake | private | `master` / `d014325` | `master` / `bd41e3b` | 38 | full commit hook, including 44 MCP and 75 REST tests |
| Selfimprove | private | `master` / `2551eb3` | `master` / `1c6ce86` | 26 | Ruff/focused hardening evidence; known unrelated full-suite import inventory failure |
| GPTQueue | public | `feat/session-aware-architecture` / `44e9156` | same branch / `22ca428` | 2 | typecheck, 29 tests, fresh service contract verification |
| Cultivar | private | `master` / `ae835ed` | `master` / `c252e1a` | 79 | 42 unit tests, 4 stdio smokes, warning-free Clippy |

## Review findings

- Rahulskills' four commits are cohesive but public. Before push, ensure the new
  audit documents contain no private evidence or host-specific material that is
  unsuitable for publication. The install packet intentionally contains local
  paths and should be reviewed as operational documentation before publication.
- Haake's remediation is four commits at the tip of a much larger 38-commit
  private branch. A direct push publishes all 38 commits. If only remediation
  should move, create a new branch from the observed remote tip and cherry-pick
  `59e9e33`, `fbd3411`, `297ccde`, and `d014325`, then rerun the hook.
- Selfimprove's remediation is the newest of 26 private commits. The same
  direct-push-versus-curated-branch decision applies; a remediation-only branch
  would cherry-pick `2551eb3`, while preserving any dependencies it actually
  needs from `1cbe63d` after a clean cherry-pick test.
- GPTQueue already has open, non-draft PR #2 from
  `feat/session-aware-architecture` to `master`, currently reported clean.
  Pushing the two commits updates that existing PR; opening another PR would be
  duplicative.
- Cultivar's remediation is the newest of 79 private commits. Direct push has
  the broadest publication scope. A remediation-only branch from the remote tip
  should cherry-pick `d29ee59` and `ae835ed` and rerun Rust/unit/stdio checks;
  preserve `stash@{0}` and do not rewrite or prune history.

## Approval-gated options

For each repository, choose exactly one independently approved action:

1. **Hold local:** no remote mutation; safest default.
2. **Push current branch:** allowed only after showing the exact remote, branch,
   ahead range, visibility, and verification evidence. This publishes every
   ahead commit in the table.
3. **Publish a curated remediation branch:** create locally from the freshly
   observed remote tip, cherry-pick the reviewed remediation commits, verify,
   then request a separate approval to push and another approval to open a PR.

For GPTQueue, option 2 updates PR #2 and no PR-create approval is needed unless
the target changes. For every other repository, pushing a branch and creating a
PR are distinct external writes. No approval may be inferred across repositories.

## Final preflight at approval time

Re-read visibility and remote tip without pruning, verify the worktree and
index, display `remote..HEAD`, rerun the repository's narrow authoritative
checks, scan public-bound commits for secrets/local-only evidence, and show the
exact `git push <remote> <local>:<remote>` command. Stop on remote drift,
verification failure, unexpected hooks, or any change to the reviewed range.
