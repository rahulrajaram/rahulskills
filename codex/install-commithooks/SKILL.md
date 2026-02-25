---
name: install-commithooks
description: "Install shared commithooks framework into a project. Copies dispatchers and lib into .git/, scaffolds .githooks/ stubs, and wires hook installation into the project's dev setup path. Use when user says /install-commithooks, 'install hooks', 'setup git hooks', 'add commit hooks', or asks to wire up shared commithooks."
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Install Commithooks

Install the shared commithooks framework into the current git repository. Copies dispatchers into `.git/hooks/`, library modules into `.git/lib/`, scaffolds `.githooks/` stubs, and wires hook installation into the project's dev setup path so contributors get hooks automatically.

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
rm -rf "${GIT_DIR:?}/lib"
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

Stubs must use the `COMMITHOOKS_DIR` variable to locate library modules:

```bash
COMMITHOOKS_DIR="${COMMITHOOKS_DIR:-$(git rev-parse --git-dir)}"
source "$COMMITHOOKS_DIR/lib/common.sh"
```

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

    git_dir = Path(result.stdout.strip())

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    for hook in ("pre-commit", "commit-msg", "pre-push", "post-checkout", "post-merge"):
        src = commithooks / hook
        if src.exists():
            shutil.copy2(src, hooks_dir / hook)
            (hooks_dir / hook).chmod(0o755)

    lib_dst = git_dir / "lib"
    if lib_dst.exists():
        shutil.rmtree(lib_dst)
    shutil.copytree(commithooks / "lib", lib_dst)

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

Add a `"prepare"` script:

```json
"scripts": {
  "prepare": "bash -c 'COMMITHOOKS=${COMMITHOOKS_DIR:-$HOME/Documents/commithooks}; GIT_DIR=$(git rev-parse --git-dir); [ -d $COMMITHOOKS/lib ] && for h in pre-commit commit-msg pre-push post-checkout post-merge; do [ -f $COMMITHOOKS/$h ] && cp $COMMITHOOKS/$h $GIT_DIR/hooks/$h && chmod +x $GIT_DIR/hooks/$h; done && rm -rf ${GIT_DIR}/lib && cp -r $COMMITHOOKS/lib $GIT_DIR/lib || true'"
}
```

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
| GitHub clone needed | Clone to ~/Documents/commithooks/ (persistent) |
| Not in a git repo | Clear error, do not git init |
| Active rebase/merge | Abort with explanation |
| .githooks in .gitignore | Warn that stubs won't be tracked |
| setup_hooks module already exists | Do not overwrite, note in summary |
| pyproject.toml script entry exists | Do not duplicate, note in summary |

## Related Skills

- `/squash-commits`: Clean up git history
- `/handoff`: Session handoff with commit
