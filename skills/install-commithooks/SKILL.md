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
- Effective `core.hooksPath` value and origin (`git config --show-origin --get core.hooksPath`). Preserve it, including inherited configuration; installation must skip until an explicit routing migration is authorized.
- Existing hooks in `.githooks/` or `scripts/git-hooks/`.

## Installation Steps

### Step 1: Display Current State

Show:
- Current `core.hooksPath` (if set)
- Existing hooks in `.git/hooks/`, `.githooks/`, `scripts/git-hooks/`
- Resolved commithooks source path

### Steps 2–4: Install Without Replacing Existing Hook Routing

Use the Python installer in Step 6 for the initial installation as well as
recurring setup. Set `COMMITHOOKS_DIR` to the resolved source path. Running the
same installer prevents a later setup from undoing initial conflict checks.
For Rust or Node setup, preserve these checks in any native equivalent.

- If effective `core.hooksPath` is configured, preserve it and skip installation.
  Report its origin and value; do not unset local, worktree, global, or inherited
  configuration. A routing change requires an explicitly authorized migration.
- Preserve existing dispatchers, including symlinks. Only an absent hook, a
  regular file identical to the source, or a regular file identical to its
  `.sample` is eligible. Any conflict skips the whole installation before
  copying libraries, since a custom dispatcher may depend on the existing lib.
- Preserve symlinked hook directories and skip installation. Never follow them
  to write outside the intended Git directory.
- Stage library replacement and retain the prior library in a recoverable
  backup; restore it if publication fails.

If initial installation skips, report the conflict and resolve any migration
with the user before scaffolding hooks or wiring setup. Ordinary installation
permission does not authorize replacement of custom hooks or hook routing.

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
import stat
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    commithooks = Path(os.environ.get("COMMITHOOKS_DIR", Path.home() / "Documents" / "commithooks"))
    if not (commithooks / "lib" / "common.sh").is_file():
        print(f"Commithooks not found at {commithooks} (skipping)")
        return

    result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Not in a git repository (skipping)")
        return

    routing = subprocess.run(
        ["git", "config", "--show-origin", "--get", "core.hooksPath"],
        capture_output=True, text=True,
    )
    if routing.returncode == 0:
        print(f"Preserving core.hooksPath: {routing.stdout.strip()} (skipping)")
        return
    if routing.returncode != 1:
        raise RuntimeError(routing.stderr.strip() or "Cannot inspect core.hooksPath")

    git_dir = Path(result.stdout.strip()).resolve()
    if git_dir == Path("/") or not git_dir.is_dir():
        raise RuntimeError(f"Unsafe git directory: {git_dir}")

    if any((git_dir / name).exists() for name in
           ("rebase-merge", "rebase-apply", "MERGE_HEAD")):
        raise RuntimeError("Rebase or merge in progress")

    hooks_dir = git_dir / "hooks"
    if hooks_dir.is_symlink() or (hooks_dir.exists() and not hooks_dir.is_dir()):
        print(f"Preserving custom hooks directory: {hooks_dir} (skipping)")
        return

    def regular_file(path: Path) -> bool:
        return path.exists() and stat.S_ISREG(path.lstat().st_mode)

    copies = []
    for hook in ("pre-commit", "commit-msg", "pre-push", "post-checkout", "post-merge"):
        src = commithooks / hook
        if not regular_file(src):
            continue
        dst = hooks_dir / hook
        sample = hooks_dir / f"{hook}.sample"
        if dst.exists() or dst.is_symlink():
            if regular_file(dst) and dst.read_bytes() == src.read_bytes():
                continue  # Preserve existing contents and permissions.
            if not (regular_file(dst) and regular_file(sample)
                    and dst.read_bytes() == sample.read_bytes()):
                print(f"Preserving custom dispatcher: {dst} (skipping installation)")
                return
        copies.append((src, dst))
    if not any(regular_file(commithooks / hook) for hook in
               ("pre-commit", "commit-msg", "pre-push", "post-checkout", "post-merge")):
        raise RuntimeError("Source contains no regular dispatcher hooks")

    lib_dst = git_dir / "lib"
    if lib_dst.parent.resolve() != git_dir:
        raise RuntimeError(f"Library target escaped git directory: {lib_dst}")

    stage = Path(tempfile.mkdtemp(prefix=".lib-stage-", dir=git_dir))
    shutil.copytree(commithooks / "lib", stage, dirs_exist_ok=True, symlinks=True)

    backup = None
    if lib_dst.exists() or lib_dst.is_symlink():
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
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

    hooks_dir.mkdir(exist_ok=True)
    for src, dst in copies:
        shutil.copy2(src, dst)
        dst.chmod(0o755)

    print(f"Commithooks installed from {commithooks}")


if __name__ == "__main__":
    main()
```

2. Add to `[project.scripts]` in `pyproject.toml`:

```toml
<project-name>-setup-hooks = "<package>.setup_hooks:main"
```

Contributors run `pip install -e .` then `<project-name>-setup-hooks`.

#### Rust projects (`Cargo.toml`)

Add an `xtask` subcommand or use the existing setup path. Apply the same
preflight, preservation, and library transaction as the Python installer;
plain copy commands are insufficient.

#### Node projects (`package.json`)

Create a checked `scripts/install-commithooks` program that performs the same
routing and dispatcher conflict checks and library transaction as the Python
installer. Preserve any existing `prepare` command when wiring this program.
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

Inspect the installed files and compare the effective `core.hooksPath` before
and after setup. Report skipped installation accurately; file existence alone
does not prove that Git uses these dispatchers.

Verify actual dispatch only in a disposable Git repository: install from the
reviewed source, write an executable `.githooks/pre-commit` containing only a
harmless marker write, and use Git to trigger that hook. Repeat setup and check
that dispatch still writes the marker. In separate fixtures, verify custom
hooks and local/inherited `core.hooksPath` survive initial and recurring setup.
Never execute the user's existing hooks just to verify installation.

### Step 9: Summary

```
Commithooks Installation Summary
─────────────────────────────────
Source:     <path>
Method:     Copy into .git/ or skipped with existing routing preserved

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
| Matching dispatchers already installed | Preserve dispatchers; stage and back up library refresh |
| Custom dispatcher or symlink | Preserve it and skip installation before library changes |
| core.hooksPath is set | Preserve configuration and skip; migration needs explicit authorization |
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
