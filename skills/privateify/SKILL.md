---
name: privateify
description: "Add reviewed safeguards against accidental public visibility and package publication. Adds multi-layer safeguards: CI visibility-guard workflow, pre-push hook check, publish=false in package manifests, and agent-facing CLAUDE.md directives. Use when user says /privateify, 'make this repo private forever', 'lock visibility', 'prevent publishing', or asks to ensure a repo is never made public."
argument-hint: "[repo-path]"
---

# Privateify

Reduce accidental visibility/publication risk with supported local guards and
explicitly scoped checks; these do not make publication impossible. Applies defense-in-depth across
CI, git hooks, package manifests, and agent instruction files.

## Intent, inputs and local bindings

Resolve the requested repository, actual push remote, effective hook routing,
package ecosystems and current privacy policy. Prefer relevant existing tools;
missing GitHub access need not block a reviewable local proposal.

## Non-goals

This workflow does not change remote visibility, publish, install tooling, erase
history or override a future authoritative privacy-policy decision. Necessary
local safeguard preparation remains autonomous within the requested scope.

## Must not

Do not promise prevention from a scheduled detector, present comments as enforced
package controls, bypass hooks, stage unrelated files or force-track ignored agent
instructions without an explicit policy decision. No local guard controls all
copies, administrators or publication mechanisms.

## Interaction and authority

A safeguard request authorizes relevant local edits. Prepare material routing,
offline-blocking or tracking-policy changes for unresolved user decisions, reusing
valid grants. Preserve existing hooks. A later authorized policy change requires
an explicit migration, not refusal based solely on this older skill.

## Usage

```
/privateify
/privateify /path/to/repo
```

If no path is given, operates on the current working directory.

## Preconditions

- Must be inside a git repository.
- `gh` CLI should be installed and authenticated (for CI and API checks).
- Repository should already be private on GitHub (the skill guards against
  accidental changes, it does not change current visibility).

## Workflow

### Step 1 — Verify Current Visibility

If `gh` is available and a GitHub remote exists:

```bash
gh api repos/OWNER/REPO --jq '.visibility'
```

- If already public, report that privacy is not established and prepare local
  safeguards independently. Do not change visibility; resolve that separate
  policy/action with the user before claiming the requested privacy outcome.
- If private, continue.
- If no remote or `gh` unavailable, warn and continue (offline mode).

### Step 2 — CI Visibility Guard Workflow

Create `.github/workflows/visibility-guard.yml` if it does not exist:

```yaml
name: Visibility Guard

on:
  repository_dispatch:
    types: [visibility_changed]
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  check-visibility:
    name: Ensure repo is private
    runs-on: ubuntu-latest
    steps:
      - name: Check repository visibility
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          VISIBILITY=$(gh api repos/${{ github.repository }} --jq '.visibility')
          echo "Repository visibility: $VISIBILITY"
          if [ "$VISIBILITY" != "private" ]; then
            echo "::error::CRITICAL: Repository is $VISIBILITY — must be private!"
            echo "::error::Revert immediately: gh api -X PATCH repos/${{ github.repository }} --field private=true"
            exit 1
          fi
          echo "Visibility check passed: private"
```

This schedule detects visibility after exposure; it cannot prevent a change.
`repository_dispatch` requires an actual sender and is not a built-in visibility
change event. Do not claim immediate detection without that integration.

If the file already exists, read it and verify it contains a visibility
check. Do not overwrite a working guard.

### Step 3 — Pre-Push Hook Visibility Check

Resolve effective `core.hooksPath` and the actual project hook framework first.
Preserve routing/custom dispatchers. Inspect the following only when relevant:

1. Check for `.githooks/pre-push` (commithooks-style shared hooks).
2. Check for `.git/hooks/pre-push`.
3. Check for `lefthook.yml` or `.pre-commit-config.yaml`.

Add a `commithooks_assert_repo_private` function (or equivalent) that:

- Resolves the actual push destination from hook arguments/configuration; does
  not assume `origin` or expose embedded credentials.
- Calls `gh api repos/OWNER/REPO --jq '.visibility'`.
- Blocks the push with a red error if visibility is not `private`.
- Preserves the selected offline policy. If it skips on missing `gh`/network,
  report that as a fail-open gap; a new fail-closed policy needs a material
  decision because it blocks offline pushes.

If the hook already contains a visibility check, skip this step.

**Do NOT use `--no-verify`.** The hook must run on every push.

### Step 4 — Package Manifest Guards

Detect the project type and add `publish = false` (or equivalent) to
every package manifest:

| Ecosystem | File | Guard |
|-----------|------|-------|
| Rust | `Cargo.toml` | `publish = false` in `[package]` |
| Node.js | `package.json` | `"private": true` |
| Python | Actual packaging/release configuration | Inspect supported publisher controls; a comment or removal of a guessed table is not an enforced publication block |
| Ruby | `*.gemspec` and release tooling | Verify supported push-host restrictions against the actual tooling; document bypass limits |
| Go | Repository/module distribution | Private path/access policy is not a universal publication gate; identify the actual distribution controls |

For **Rust workspaces**, apply `publish = false` to every member crate.

Where useful, add a concise privacy-policy notice using valid file syntax.
The following is an optional policy notice, not an enforcement mechanism:

```
# ╔════════════════════════════════════════════════════════════════╗
# ║  PRIVATE REPOSITORY — DO NOT PUBLISH TO <registry>            ║
# ║                                                                ║
# ║  This package is distributed exclusively via private channels. ║
# ║  It must NEVER be published to a public registry or made       ║
# ║  available in a public repository. Any agent, CI job, or       ║
# ║  human seeing this comment must treat this as a hard           ║
# ║  constraint.                                                   ║
# ╚════════════════════════════════════════════════════════════════╝
```

Adapt comment syntax for JSON (`package.json` cannot have comments — use
the `"private": true` field and add a `"_privateify_notice"` key instead).

If the guard is already present, skip.

### Step 5 — Agent Instruction File (CLAUDE.md)

Create or update `CLAUDE.md` at the repository root with a
`## CRITICAL: Repository Visibility` section containing:

- Do NOT run `gh repo edit --visibility public` or any equivalent.
- Do NOT publish packages to public registries.
- Do NOT remove `publish = false` (or equivalent) from any manifest.
- Do NOT remove or weaken the visibility-guard CI workflow.
- Do NOT remove or weaken the pre-push visibility hook.
- If later asked to change privacy/publication policy, identify this policy
  and prepare the concrete migration for the authorized owner; do not silently
  weaken guards or treat an old instruction as irrevocable authority.

If `CLAUDE.md` already exists, append or merge the section — do not
overwrite unrelated content. If the section already exists, verify its
content is complete and skip.

If `CLAUDE.md` is gitignored (check `git check-ignore -q CLAUDE.md`),
preserve the ignore policy. Present any needed tracking change for a concrete
decision; do not force-add it merely because this template mentions the file.

### Step 6 — Codex Instruction File (AGENTS.md / codex.md)

If the project uses OpenAI Codex, create or update `AGENTS.md` (or
`codex.md` if that's the convention) with the same visibility constraints
from Step 5, adapted to Codex's instruction format.

### Step 7 — Commit

When committing is selected, use `commit` to triage and stage only the intended
safeguards by explicit path, preserving unrelated changes. Suggested subject:

```
chore: add multi-layer private repo safeguards
```

Include a body listing what was added (CI workflow, hook, manifest guards,
agent instructions).

Do NOT push automatically — the pre-push hook will verify the guard works.

### Step 8 — Verify

Verify the changed guard logic using disposable repositories and mocked visibility
responses (private, public, unavailable), including the chosen offline behavior.
Do not execute the user's entire pre-push hook merely as a test; it can perform
unrelated external work. Inspect manifest/workflow syntax and report which checks
were exercised versus only reviewed. A local passing guard is not proof that
GitHub visibility cannot change.

## Output Contract

End with this plain-text block:

```text
PRIVATEIFY_V1
status: applied|already-guarded|stopped-on-issue
guards_added:
  ci_workflow: yes|no|already-present
  pre_push_hook: yes|no|already-present
  manifest_publish_false: yes|no|already-present
  agent_instructions: yes|no|already-present
commit: <sha-or-none>
```

## Safety

- Never change repository visibility (do not call `gh repo edit --visibility`).
- Preserve existing guards unless a concrete authoritative migration selects a change.
- Never use `--no-verify` on commits or pushes.
- If the repo is already public, stop and warn — do not silently add guards
  to a public repo (the user needs to decide whether to make it private first).
- If `publish = false` would break an intentional publish workflow, ask the
  user before adding it.
