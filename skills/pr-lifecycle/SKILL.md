---
name: pr-lifecycle
description: "Prepare and open a GitHub pull request and follow required CI through success. Use for an end-to-end PR workflow; select commit, history cleanup, documentation and release steps only when needed and authorized."
argument-hint: "[pr hint]"
---

# PR Lifecycle

## Intent and applicability

Take the requested change to an open GitHub PR with passing required CI. A
local-preparation-only request ends with a reviewable branch and PR draft.

## Inputs and local bindings

Resolve the requested change, current branch, actual base/upstream, remote and
repository contribution/release policy. Read existing validation/setup commands;
filenames below are examples, not proof that a command or flag is supported.
Use locally available Git/gh or an already authorized equivalent. Missing remote
authentication does not prevent independent local preparation.

## Non-goals

A PR request does not select squashing, hook installation, full README rebuilding,
a package release, merge or deployment by default. Necessary local fixes and
verification are within the requested preparation. Explicit broader scope can
select the other operations under their own applicable boundaries.

## Must not

Do not bypass hooks with `--no-verify`, commit unrelated work, change shared
history without authority, or claim CI success from stale/skipped/unknown required
checks. Do not install tools/hooks or change release policy just to run this skill.
Do not treat local tracking refs as proof that commits have never been shared.

## Interaction and authority

An explicit PR lifecycle request selects local preparation, relevant commits,
review and validation. Carry still-valid approvals into composed skills; do not
ask again merely because a new phase starts. Push/PR creation/version changes
must be covered by the request and active repository rules. Prepare the exact
branch, diff, validation evidence, title/body and outbound action before asking
about an unresolved boundary. Push approval alone does not authorize PR creation.

Diagnose and fix ordinary local failures within scope, then rerun the affected
check. Do not stop at the first failing test, fixable review finding or missing
authentication when useful local work remains. Wait for genuinely missing access,
a material release/scope decision or unsafe unresolved history effects; never
loop blindly, weaken gates or expand the task to avoid the blocker.

## Procedure

### 1. Select the branch before mutation

Inspect repository state and preserve unrelated files. Determine the base from
repository evidence (`origin/HEAD` if applicable, then actual local branches).
If detached or on the default branch, create a suitable feature branch at the
intended starting commit before committing or rewriting history. Preserve an
existing appropriate feature branch. Resolve ambiguity that would change the PR
contents; do not reset or discard work to make the branch clean.

### 2. Prepare only the necessary changes

- Invoke `commit` when relevant changes need committing; reuse existing selected
  files and preserve its secret/artifact triage. Unrelated untracked files alone
  do not require abandoning the task.
- Invoke `squash-commits` only when requested or required by repository policy
  and covered by concrete history authority. Clean history needs no rewrite.
- Use `readme-doctor` for documentation/help affected by this diff. A full audit
  applies only when selected; a small help fix does not require rebuilding README.
- Resolve local review findings within scope and commit resulting intended edits.

### 3. Verify the resulting change

Inspect the patch, `git diff --check <base>...HEAD`, secrets exposure, behavior,
relevant tests and documentation. Determine which checks already ran against
unchanged relevant content, and run missing/stale required checks. A message-only
rewrite need not rerun an unchanged build; required history checks still apply.
Do not infer that all hooks ran merely from installed files. Preserve effective
hook routing and inspect the commands it actually invokes.

If repository policy uses `scripts/run_ci_mirror.sh`, inspect its supported
interface and run required gates. Do not assume `--list` or `--no-pytest` exists,
or that a partial run meets the full gate. Broaden tests only for changed risk,
insufficient coverage, a failure or an actual required check.

### 4. Resolve release requirements when applicable

Skip release work for private/non-published packages and when the repository
releases separately from PR preparation. For selected public-package versioning,
read [references/version-registries.md](references/version-registries.md) and the
actual release policy. Check the relevant registry only if needed to resolve the
version decision. Propose a supported bump when required; edit it only under
valid authority. An unpublished version alone does not settle compatibility or
release policy. After authorized edits, rerun only affected checks and commit.

### 5. Prepare and perform authorized external actions

Confirm remote access when needed. Present the concrete branch, remote, commits,
push command and PR title/body before an unresolved approval. Once covered, push
with appropriate upstream tracking and create the PR (or use the existing PR).
Do not force-push as a routine fallback. On failure, inspect whether an action
partially succeeded before retrying so duplicate PRs are not created.

Write title/body from the actual diff and validation evidence; `--fill` is useful
only when commit history accurately describes the final change. Capture the PR
number and URL. Missing access leaves a completed local branch and draft with
the smallest remaining user action, not a claim that the PR was opened.

### 6. Follow required CI

Use `gh pr checks <pr-number> --watch` or the available CI interface. Verify the
checks correspond to current HEAD and all required checks succeeded; skipped,
neutral and missing checks are not automatically green. Use an existing
repository CI gate when required, checking its supported arguments first.
Diagnose and repair relevant failures within scope. Further pushes still require
applicable authority, reusing an existing grant when it covers the correction.
Finish at green required CI; review/merge remains with the user unless selected.

## Completion and evidence

End with this plain-text block:

```text
PR_LIFECYCLE_V1
status: prepared-local|stopped-on-issue|opened-pr|ci-passed
branch: <branch-name>
pr_url: <url-or-none>
version_action: none|checked-no-bump|bumped-to-<version>
next_action: user-review|await-authorization|resolve-access|fix-issue|monitor-ci
```
