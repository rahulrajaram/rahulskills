---
name: install-commithooks
description: "Install shared commithooks framework into a project. Copies dispatchers and lib into .git/, scaffolds .githooks/ stubs, and wires hook installation into the project's dev setup path. Use when user says /install-commithooks, 'install hooks', 'setup git hooks', 'add commit hooks', or asks to wire up shared commithooks."
argument-hint: "[hooks-source-path]"
---

# Install Commithooks

Install the shared commithooks framework into the current git repository. Copies dispatchers into `.git/hooks/`, library modules into `.git/lib/`, scaffolds `.githooks/` stubs, and wires hook installation into the project's dev setup path so contributors get hooks automatically.

## Usage

`/install-commithooks [hooks-source-path]`

If no path is provided, the source is resolved automatically (see below).

## Source Resolution Order

1. **Explicit argument**: If a path is passed, use it.
2. **Local default**: `${COMMITHOOKS_DIR:-$HOME/Documents/commithooks}`
3. **GitHub clone**: Clone `https://github.com/rahulrajaram/commithooks.git` to `$COMMITHOOKS_DIR` after user approval.

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
  cp "$src" "$dst" || { echo "Failed to copy $hook" >&2; exit 1; }
  chmod +x "$dst" || { echo "Failed to make $hook executable" >&2; exit 1; }
  echo "[ok]   $hook"
done
```

### Step 3: Copy Library into `.git/lib/`

```bash
(
git_dir_real="$(realpath -e -- "$GIT_DIR")" || exit 1
target="$git_dir_real/lib"

[[ -d "$git_dir_real" && "$git_dir_real" != "/" && ! -L "$GIT_DIR" ]] || exit 1
[[ "$(realpath -e -- "$(dirname -- "$target")")" == "$git_dir_real" ]] || exit 1
[[ -f "$SOURCE/lib/common.sh" ]] || { echo "Missing source lib/common.sh" >&2; exit 1; }

stage="$(mktemp -d "$git_dir_real/.lib-stage.XXXXXX")" || exit 1
cp -a "$SOURCE/lib/." "$stage/" || {
  echo "Copy failed; staged tree retained at $stage" >&2
  exit 1
}

backup=""
if [[ -e "$target" || -L "$target" ]]; then
  mkdir -p "$git_dir_real/commithooks-backups" || exit 1
  backup_root="$(mktemp -d "$git_dir_real/commithooks-backups/lib.XXXXXX")" || exit 1
  backup="$backup_root/lib"
  mv -T -- "$target" "$backup" || { echo "Backup failed; live library preserved" >&2; exit 1; }
fi

if ! mv -T -- "$stage" "$target"; then
  if [[ -n "$backup" && ! -e "$target" && ! -L "$target" ]]; then
    mv -T -- "$backup" "$target" || echo "Restore failed; prior library retained at $backup" >&2
  fi
  echo "Install failed; staged tree retained at $stage" >&2
  exit 1
fi
)
```

The exact target must be proven even though `.git/lib/` is an untracked
namespace. Never use a nonempty-variable check as the only guard for recursive
deletion. Stage the replacement, move the prior tree to a recoverable backup,
and restore it if publication fails.

The example uses GNU `realpath` and `mv -T` so publication cannot nest the
stage inside an existing target directory. Every failure exits the transaction
explicitly; do not rely on the calling shell's `set -e` setting.

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

Stubs MUST source the library modules AND call the validation functions. A stub that only sources without calling is a no-op bug.

**Scaffold `.githooks/pre-commit`** (example for Rust project):

```bash
#!/usr/bin/env bash
set -euo pipefail
COMMITHOOKS_DIR="$(git rev-parse --git-dir)"
source "$COMMITHOOKS_DIR/lib/common.sh"
source "$COMMITHOOKS_DIR/lib/lint-rust.sh"
source "$COMMITHOOKS_DIR/lib/secrets.sh"

commithooks_skip_during_rebase && exit 0
commithooks_rust_fmt
commithooks_rust_clippy
commithooks_block_sensitive_files
commithooks_scan_secrets_in_diff
```

**Scaffold `.githooks/commit-msg`**:

```bash
#!/usr/bin/env bash
set -euo pipefail
COMMITHOOKS_DIR="$(git rev-parse --git-dir)"
source "$COMMITHOOKS_DIR/lib/common.sh"
source "$COMMITHOOKS_DIR/lib/commit-msg.sh"

commithooks_validate_conventional_commit "$1"
commithooks_validate_subject_line "$1"
```

**Scaffold `.githooks/pre-push`**:

```bash
#!/usr/bin/env bash
set -euo pipefail
COMMITHOOKS_DIR="$(git rev-parse --git-dir)"
source "$COMMITHOOKS_DIR/lib/common.sh"
source "$COMMITHOOKS_DIR/lib/pre-push.sh"

commithooks_reject_wip_commits "$@"
commithooks_check_branch_name
```

Adapt the `pre-commit` stub based on detected project type:
- `Cargo.toml` → `lint-rust.sh` with `commithooks_rust_fmt`, `commithooks_rust_clippy`
- `package.json` → `lint-js.sh` with `commithooks_js_oxlint` or `commithooks_js_eslint`
- `pyproject.toml` → `lint-python.sh` with `commithooks_python_syntax`, `commithooks_python_ruff`

Make all scaffolded hooks executable.

### Step 6: Wire Hook Installation into Dev Setup Path

The goal: after `git clone` + normal project setup, contributors get dispatchers and lib in `.git/` automatically. The approach depends on project type. **Do NOT create Makefiles for Python projects. Do NOT create standalone `setup.sh` scripts.**

#### Python projects (`pyproject.toml`)

Create a `setup_hooks.py` module inside the package and add a console script entry to `pyproject.toml`:

1. Create `<package>/setup_hooks.py`:

```python
"""Install commithooks dispatchers and lib into .git/."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    commithooks = Path(os.environ.get("COMMITHOOKS_DIR", Path.home() / "Documents" / "commithooks"))
    if not (commithooks / "lib").is_dir():
        print(f"Commithooks not found at {commithooks} (skipping)")
        return

    result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Not in a git repository (skipping)")
        return

    git_dir = Path(result.stdout.strip()).resolve()
    if git_dir == Path("/") or not git_dir.is_dir():
        raise RuntimeError(f"Unsafe git directory: {git_dir}")

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    for hook in ("pre-commit", "commit-msg", "pre-push", "post-checkout", "post-merge"):
        src = commithooks / hook
        if src.exists():
            shutil.copy2(src, hooks_dir / hook)
            (hooks_dir / hook).chmod(0o755)

    lib_dst = git_dir / "lib"
    if lib_dst.parent.resolve() != git_dir:
        raise RuntimeError(f"Library target escaped git directory: {lib_dst}")

    stage = Path(tempfile.mkdtemp(prefix=".lib-stage-", dir=git_dir))
    shutil.copytree(commithooks / "lib", stage, dirs_exist_ok=True, symlinks=True)

    backup = None
    if lib_dst.exists() or lib_dst.is_symlink():
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup = git_dir / "commithooks-backups" / stamp / "lib"
        backup.parent.mkdir(parents=True, exist_ok=False)
        lib_dst.rename(backup)

    try:
        stage.rename(lib_dst)
    except OSError:
        if backup is not None and not lib_dst.exists() and not lib_dst.is_symlink():
            backup.rename(lib_dst)
        print(f"Install failed; staged tree retained at {stage}")
        raise

    print(f"Commithooks installed from {commithooks}")
```

2. Add to `[project.scripts]` in `pyproject.toml`:

```toml
<project-name>-setup-hooks = "<package>.setup_hooks:main"
```

Contributors run `pip install -e .` then `<project-name>-setup-hooks`.

#### Rust projects (`Cargo.toml`)

Add a `build.rs` that runs the copy, or add a `xtask` subcommand.

#### Node projects (`package.json`)

Create a checked `scripts/install-commithooks` program that performs the same
resolve, validate, stage, backup, publish, and rollback transaction as Step 3.
Then make `prepare` invoke that program:

```json
"scripts": {
  "prepare": "scripts/install-commithooks"
}
```

Do not embed an unquoted shell pipeline or destructive tree replacement in
`package.json`. Do not append `|| true`; installation failures must remain
visible.

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

Dev setup wiring:
  <what was done — e.g., "Added <pkg>/setup_hooks.py + pyproject.toml script entry">

Next steps:
  - Customize .githooks/pre-commit for project-specific checks
  - Commit .githooks/ and the setup_hooks module
  - Tell contributors: pip install -e . && <project>-setup-hooks
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Dispatchers already installed | Skip individual hooks, refresh lib/ |
| core.hooksPath is set | Unset it, switch to .git/hooks/ method |
| Symlinked hooks in .githooks/ | Treat as existing, do not overwrite |
| GitHub clone needed | Clone to `$COMMITHOOKS_DIR` after user approval |
| Not in a git repo | Clear error, do not git init |
| Active rebase/merge | Abort with explanation |
| .githooks in .gitignore | Warn that stubs won't be tracked |
| setup_hooks module already exists | Do not overwrite, note in summary |
| pyproject.toml script entry exists | Do not duplicate, note in summary |

## Related Skills

- `/squash-commits`: Clean up git history
- `/handoff`: Session handoff with commit
