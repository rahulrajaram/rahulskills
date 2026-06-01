---
name: pr-lifecycle
description: "Create and manage a GitHub pull request from local branch prep through green CI. Use when the user wants an agent to run the commit skill, run the squash-commits skill, ensure it is on a feature branch, verify hooks and fast local checks, do a quick PR review, run readme-doctor before versioning, decide whether a public package needs a version bump, push the branch, open a PR, wait for build success, then stop."
argument-hint: "[pr hint]"
---

# PR Lifecycle

Take a local worktree to an open GitHub PR with passing CI, then stop.

## Autonomy Routing

An explicit PR lifecycle request is approval to run the local preparation
workflow through branch preparation, commits, validation, push, PR creation, and
CI watching, subject to the safety stops below. Do not ask whether to use
`/goal`, Yarli, commit, or squash workflows; invoke the required sub-skills and
continue. Still stop for push/auth failures, risky history rewrites, failing
checks, unresolved review findings, visibility risk, or any user-visible release
decision that cannot be inferred from repo policy.

## Preconditions

- Work inside a git repository with a GitHub remote.
- `gh` must be installed and authenticated.
- Stop immediately on glaring issues: hook failures, unresolved review findings,
  risky squash plans, dirty tree after a major step, unclear versioning, push
  failure, PR creation failure, or failing CI.

## Workflow

### 1. Preflight

- Detect repo root, current branch, default branch, and upstream status.
- Confirm `gh auth status` succeeds before doing PR work.
- Derive a short hint from the argument, current top commit subject, or user
  request for branch/PR naming.

### 2. Run `/commit`

- Use the `commit` skill first.
- If it surfaces REVIEW or ALLOWED items, hook failures, or leaves material
  changes uncommitted, stop and report instead of pushing ahead.

### 3. Run `/squash-commits`

- Use `squash-commits` on unpushed commits only.
- If it needs user approval, proposes a risky rewrite, hits conflicts, fails
  tests, or leaves the repo dirty, stop and report.

### 4. Ensure Feature Branch

- Detect the default branch from `origin/HEAD`, then fall back to `main` or
  `master` if needed.
- If HEAD is detached or the current branch is still the default branch, create
  and switch to `feature/<slug>` derived from the hint.
- If already on a non-default branch, keep it.

### 5. Ensure Hooks And Fast Validation Ran

- Never use `--no-verify`.
- Inspect `.githooks/`, `.git/hooks/`, `lefthook.yml`,
  `.pre-commit-config.yaml`, `package.json`, `pyproject.toml`, `Cargo.toml`,
  and other obvious project files to identify the concrete validation commands
  behind the hooks.
- Re-run those concrete validations against the current HEAD after commit and
  squash.
- If you cannot determine hook coverage confidently, stop and say so rather
  than pretending all hooks ran.

### 6. Quick Local PR Review

- Review `git diff --stat <base>...HEAD`, `git diff --check <base>...HEAD`, and
  a skim of the patch itself.
- Look for secrets, debug prints, stale TODO/FIXME markers, missing tests for
  risky behavior, broken docs, or obviously noisy changes.
- Stop on glaring issues.

### 7. Run `/readme-doctor`

- Run `readme-doctor` after the quick local PR review and before any version
  decision.
- Stop if it finds glaring README, help-text, or packaging-documentation drift.
- If `readme-doctor` makes material doc changes, commit them normally so hooks
  run before continuing.

### 8. Check Public Package Versioning

- Detect whether the repo publishes a public package by inspecting
  `package.json`, `pyproject.toml`, `Cargo.toml`, `*.gemspec`, or other release
  metadata.
- If the repo is private or has no publish target, skip this step.
- If the repo publishes publicly, read
  [references/version-registries.md](references/version-registries.md) and use
  the matching registry check.
- Compare the local package version with the currently published version.
- Use the PR diff to decide whether the shipped package behavior or artifact
  changed enough to warrant a release.
- If the local version is already published and the PR changes shipped package
  behavior or artifacts, make the smallest correct SemVer bump.
- If the local version has not been published yet, do not bump the version.
- If you make a version bump, commit it normally so hooks run, then rerun the
  quick local review and `readme-doctor`.

### 9. Run Repo-Local CI Mirror

- If `scripts/run_ci_mirror.sh` exists, run `scripts/run_ci_mirror.sh --list`
  to record the available local mirror gates.
- Then run `scripts/run_ci_mirror.sh` before pushing.
- If the mirror fails, stop and report the failing gate names instead of
  pushing.
- For faster iteration before the final pre-push check, you may run
  `scripts/run_ci_mirror.sh --no-pytest`, but treat it as a partial mirror that
  skips the top-level `pytest+ratchet+ruff+complexity` gate.
- If no `scripts/run_ci_mirror.sh` exists, skip this step.

### 10. Push The Feature Branch

- Push the current feature branch with upstream tracking.
- Stop on any push rejection or auth failure.

### 11. Open The PR

- Use `gh pr create`.
- Prefer `--fill` when the existing commit history is already clean; otherwise
  provide an explicit title and body built from the branch diff.
- Capture the PR number and URL.

### 12. Wait For Build Success

- Use `gh pr checks <pr-number> --watch` when available, otherwise watch the
  corresponding GitHub Actions run.
- After the watch reports green, run `bash scripts/ci_gate.sh --commit $(git rev-parse HEAD)`
  from the repo root when that script exists so skipped, neutral, or stale
  required checks still stop the flow.
- If CI fails, notify the user and stop.
- If CI passes, notify the user and stop. The user owns review, merge, and all
  follow-up after that point.

## Output Contract

End with this plain-text block:

```text
PR_LIFECYCLE_V1
status: stopped-on-issue|opened-pr|ci-passed
branch: <branch-name>
pr_url: <url-or-none>
version_action: none|checked-no-bump|bumped-to-<version>
next_action: user-review|fix-issue|monitor-ci
```
