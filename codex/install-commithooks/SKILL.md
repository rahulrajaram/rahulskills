---
name: install-commithooks
description: "Install shared commithooks framework into a project. Copies dispatchers and lib into .git/, scaffolds .githooks/ stubs, and creates setup.sh for contributors. Use when user says /install-commithooks, 'install hooks', 'setup git hooks', 'add commit hooks', or asks to wire up shared commithooks."
allowed-tools: Bash, Read, Write, Grep, Glob
---

# Install Commithooks

Install the shared commithooks framework into the current git repository. Copies dispatchers into `.git/hooks/`, library modules into `.git/lib/`, scaffolds `.githooks/` stubs, and creates a `setup.sh` so contributors can bootstrap after cloning.

## Usage

`/install-commithooks [hooks-source-path]`

If no path is provided, the source is resolved automatically (see below).

## Source Resolution Order

1. **Explicit argument**: If a path is passed, use it.
2. **Local default**: `~/Documents/commithooks/`
3. **GitHub clone**: Clone `https://github.com/rahulrajaram/commithooks.git` to `~/Documents/commithooks/`.

Validate the resolved directory contains `lib/` with at least `common.sh`. Abort with a clear error if not.

## Pre-flight Checks

Abort if any of these fail:

1. **Inside a git repo**: `git rev-parse --show-toplevel` must succeed.
2. **Source directory valid**: Must contain `lib/` and dispatcher hooks.
3. **No active rebase/merge**: No `.git/rebase-merge`, `.git/rebase-apply`, or `.git/MERGE_HEAD`.

Report but do not abort:
- Current `core.hooksPath` value (will be unset during install).
- Existing hooks in `.githooks/` or `scripts/git-hooks/`.

## Installation Steps

### Step 1: Display Current State

Show:
- Current `core.hooksPath` (if set)
- Existing hooks in `.git/hooks/`, `.githooks/`, `scripts/git-hooks/`
- Resolved commithooks source path

### Step 2: Copy Dispatchers into `.git/hooks/`

For each hook (`pre-commit`, `commit-msg`, `pre-push`, `post-checkout`, `post-merge`):

- **Conflict**: hook exists AND differs from the default `.sample` file — skip with warning.
- **No conflict**: copy from source, `chmod +x`.

```bash
for hook in pre-commit commit-msg pre-push post-checkout post-merge; do
  src="$SOURCE/$hook"
  dst="$GIT_DIR/hooks/$hook"
  [ -f "$src" ] || continue
  if [ -f "$dst" ] && [ "$(cat "$dst")" != "$(cat "$dst.sample" 2>/dev/null || true)" ]; then
    echo "[skip] $hook (existing custom hook)"
    continue
  fi
  cp "$src" "$dst"
  chmod +x "$dst"
  echo "[ok]   $hook"
done
```

### Step 3: Copy Library into `.git/lib/`

```bash
rm -rf "$GIT_DIR/lib"
cp -r "$SOURCE/lib" "$GIT_DIR/lib"
```

Always safe — `.git/lib/` is our namespace and is not tracked by git.

### Step 4: Unset `core.hooksPath`

If set, unset it. We use `.git/hooks/` directly.

### Step 5: Scaffold Repo-Local Hook Stubs

For each hook type:

- **If `.githooks/<hook-name>` exists** (file or symlink): Skip.
- **If `scripts/git-hooks/<hook-name>` exists**: Skip.
- **Otherwise**: Detect project type and create appropriate stub.

**Project type detection**:
- `Cargo.toml` → `lib/lint-rust.sh`
- `package.json` → `lib/lint-js.sh`
- `pyproject.toml` / `setup.py` / `setup.cfg` → `lib/lint-python.sh`
- Multiple → source multiple lint modules

Stubs source from `$(git rev-parse --git-dir)/lib/<module>.sh`.

Make all scaffolded hooks executable.

### Step 6: Create or Update `setup.sh`

If the repo does not have a `setup.sh`, copy the canonical template from the commithooks source:

```bash
cp "$SOURCE/setup-template.sh" "$REPO_ROOT/setup.sh"
chmod +x "$REPO_ROOT/setup.sh"
```

If `setup-template.sh` is not available in the source (older commithooks version), generate a minimal setup.sh that clones commithooks and runs the dispatcher/lib copy logic.

If `setup.sh` already exists, do not overwrite — note it in summary.

### Step 7: Check .gitignore

- If `.githooks` appears in `.gitignore`, warn that stubs won't be tracked.
- Otherwise, note that `.githooks/` should be committed for team sharing.

### Step 8: Verify

```bash
ls -la "$GIT_DIR/hooks/pre-commit"
ls "$GIT_DIR/lib/"
```

### Step 9: Summary

```
Commithooks Installation Summary
─────────────────────────────────
Source:     <path>
Method:     Copy into .git/ (no core.hooksPath)

Dispatchers (.git/hooks/):
  pre-commit    [ok/skip]
  commit-msg    [ok/skip]
  pre-push      [ok/skip]
  post-checkout [ok/skip]
  post-merge    [ok/skip]

Library (.git/lib/):
  N modules copied

Hook Stubs (.githooks/):
  pre-commit    [created/skipped/exists]
  commit-msg    [created/skipped/exists]

setup.sh:       [created/exists]

Next steps:
  - Customize .githooks/pre-commit for project-specific checks
  - Commit .githooks/ and setup.sh
  - Tell contributors: git clone && ./setup.sh
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Dispatchers already installed | Skip individual hooks, refresh lib/ |
| core.hooksPath is set | Unset it, switch to .git/hooks/ method |
| Symlinked hooks in .githooks/ | Treat as existing, do not overwrite |
| GitHub clone needed | Clone to ~/Documents/commithooks/ (persistent) |
| Not in a git repo | Clear error, do not git init |
| Active rebase/merge | Abort with explanation |
| .githooks in .gitignore | Warn that stubs won't be tracked |
| setup.sh already exists | Do not overwrite, note in summary |

## Related Skills

- `/squash-commits`: Clean up git history
- `/handoff`: Session handoff with commit
