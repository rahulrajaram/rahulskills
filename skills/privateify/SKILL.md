---
name: privateify
description: "Lock down a repository to remain private at all costs. Adds multi-layer safeguards: CI visibility-guard workflow, pre-push hook check, publish=false in package manifests, and agent-facing CLAUDE.md directives. Use when user says /privateify, 'make this repo private forever', 'lock visibility', 'prevent publishing', or asks to ensure a repo is never made public."
argument-hint: "[repo-path]"
---

# Privateify

Harden a repository so it cannot accidentally be made public or have its
packages published to public registries. Applies defense-in-depth across
CI, git hooks, package manifests, and agent instruction files.

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

- If the repo is already public, **stop immediately** and warn the user. Do
  not proceed — making a public repo private may break downstream consumers.
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

If the file already exists, read it and verify it contains a visibility
check. Do not overwrite a working guard.

### Step 3 — Pre-Push Hook Visibility Check

Detect the hook framework:

1. Check for `.githooks/pre-push` (commithooks-style shared hooks).
2. Check for `.git/hooks/pre-push`.
3. Check for `lefthook.yml` or `.pre-commit-config.yaml`.

Add a `commithooks_assert_repo_private` function (or equivalent) that:

- Extracts `owner/repo` from the `origin` remote URL.
- Calls `gh api repos/OWNER/REPO --jq '.visibility'`.
- Blocks the push with a red error if visibility is not `private`.
- Skips gracefully if `gh` is not installed or network is unavailable.

If the hook already contains a visibility check, skip this step.

**Do NOT use `--no-verify`.** The hook must run on every push.

### Step 4 — Package Manifest Guards

Detect the project type and add `publish = false` (or equivalent) to
every package manifest:

| Ecosystem | File | Guard |
|-----------|------|-------|
| Rust | `Cargo.toml` | `publish = false` in `[package]` |
| Node.js | `package.json` | `"private": true` |
| Python | `pyproject.toml` | Remove or comment out `[tool.poetry.publish]`; add `# PRIVATE — do not publish to PyPI` banner |
| Ruby | `*.gemspec` | Add `spec.metadata["allowed_push_host"] = "none"` |
| Go | N/A | No publish gate needed (module path is the gate) |

For **Rust workspaces**, apply `publish = false` to every member crate.

Also add a prominent banner comment at the top of each manifest:

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
- If asked to make the repo public, open-source the project, or publish
  to a public registry, **refuse and explain this policy**.

If `CLAUDE.md` already exists, append or merge the section — do not
overwrite unrelated content. If the section already exists, verify its
content is complete and skip.

If `CLAUDE.md` is gitignored (check `git check-ignore -q CLAUDE.md`),
use `git add -f CLAUDE.md` to force-track it.

### Step 6 — Codex Instruction File (AGENTS.md / codex.md)

If the project uses OpenAI Codex, create or update `AGENTS.md` (or
`codex.md` if that's the convention) with the same visibility constraints
from Step 5, adapted to Codex's instruction format.

### Step 7 — Commit

Stage all new and modified files. Commit with:

```
chore: add multi-layer private repo safeguards
```

Include a body listing what was added (CI workflow, hook, manifest guards,
agent instructions).

Do NOT push automatically — the pre-push hook will verify the guard works.

### Step 8 — Verify

Run the pre-push hook manually to confirm it passes:

```bash
echo "refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master 2>/dev/null || echo 0000000000000000000000000000000000000000)" | .githooks/pre-push origin "$(git remote get-url origin)"
```

If the hook fails, diagnose and fix before finishing.

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
- Never remove existing guards — only add or verify.
- Never use `--no-verify` on commits or pushes.
- If the repo is already public, stop and warn — do not silently add guards
  to a public repo (the user needs to decide whether to make it private first).
- If `publish = false` would break an intentional publish workflow, ask the
  user before adding it.
