---
name: chasm-migrate
description: "Copy a project into a Chasm sandbox's persistent /workspace, install only the project's required dependencies in the guest, and verify the result. Use when a user asks to migrate or copy existing project work into Chasm."
metadata:
  short-description: "Migrate a project into a Chasm sandbox"
---

# Chasm project migration

Copy a host project into a named Chasm sandbox and make it usable in the
sandbox's persistent `/workspace`. Record which checkout is authoritative.
Honor an existing sandbox-primary designation; for a new Chasm-first project,
use the guest checkout as primary when that is the user's selected workflow.
Retain host-primary operation when explicitly selected, and preserve the host
copy in either case. Recover dirty and untracked work before re-import or deletion.

## Intent and boundaries

This skill covers one project copy, project-local dependency installation,
build/test proof, and export or recovery of guest changes. It does not upgrade
dotfiles, refresh a site profile, prune old sandboxes, or change host policy.
The contract is runtime-neutral and applies to Pi, Codex, Claude, and OpenCode;
each runtime must still be admitted through its own reviewed discovery root and
instruction/profile binding before claiming that runtime is ready.

The sandbox owner chooses the logical sandbox name and whether an existing
sandbox is the migration target. Preserve the selected authoritative checkout;
do not infer source authority from the fact that a copy was migrated. A guest
checkout becomes primary only after that authority is explicitly designated.
If Chasm refuses admission because available resources are insufficient,
report the refusal; do not stop another guest automatically.

## Inputs and authority

Bind these values before mutating anything:

- `PROJECT`: one existing host project directory, resolved to an absolute path;
- `SANDBOX`: one logical Chasm name (the CLI derives `sandbox-$SANDBOX`);
- `PROJECT_NAME`: one safe path component for the guest project directory;
- `BUDGET_MIB`: a declared memory budget within Chasm's supported 512–16384 MiB range;
- `WORKSPACE`: `/workspace/$PROJECT_NAME`, the persistent guest path;
- `TASK_WORKTREE`: `/workspace/.worktrees/$PROJECT_NAME/$TASK_NAME` for an
  additional guest worktree; the project checkout remains authoritative at
  `WORKSPACE`;
- `SOURCE_COMMIT`: the host Git commit being copied, when `PROJECT` is a Git repository;
  for a multi-repository project, record a commit and working state for every
  required repository, not only the umbrella.
- `AUTHORITY`: the designated host or guest checkout and the approved integration route.
- `CHASM_DIR`: the verified local Chasm source checkout when source helpers are needed.

Project and task names must match `[A-Za-z0-9][A-Za-z0-9._-]{0,127}` as one
path component. The bare `/workspace` root and `.worktrees` are not projects.

Use the Chasm CLI for lifecycle operations. The source CLI documents
`create NAME [BUDGET_MEMORY_MIB]`, `start [NAME]`, `show NAME --layout`, `stop
[NAME]`, `delete NAME`, and `shell [NAME]` (`chasm/cmd/chasm/help.go`). Chasm
creates a persistent per-sandbox `/workspace` and a global `/shared`; do not
mistake `/shared` for the project workspace.

## Safety gate

Run this from the host before lifecycle, copy, install, or build work:

```sh
if mountpoint -q /workspace && [ "$(stat -c '%u:%g:%a' /workspace 2>/dev/null)" = '1001:1001:770' ]; then
  echo 'already inside a Chasm guest; start migration from the host' >&2
  exit 1
fi
[ -f /etc/agent-sandbox/site-host-id ] || {
  echo 'Chasm host identity marker is unavailable' >&2
  exit 1
}
```

If the context is ambiguous, stop without side effects. Run the read-only
preflight and record its output:

```sh
cd "$CHASM_DIR"
scripts/install-chasm.sh --verify
chasm list
chasm show "$SANDBOX" --layout 2>/dev/null || true
```

Do not expose `/etc/agent-sandbox/openrouter.env` or any credential material.
Provider access is a separate, explicitly approved route; migration does not
copy host credentials into the guest.

## Procedure

### 1. Select or create the sandbox

Use the existing owner-selected sandbox when it exists. Otherwise, after the
owner authorizes creation:

```sh
chasm create "$SANDBOX" "$BUDGET_MIB"
chasm start "$SANDBOX"
chasm show "$SANDBOX" --layout
```

Chasm's documented default budget is 3072 MiB; use that unless the owner has a
measured reason to choose another value. Creation leaves the sandbox stopped;
start waits for the guest agent. Do not change `default_sandbox` or stop
another guest as an implicit prerequisite.

Before claiming Pi HEAD behavior, read the installed `bootstrap_profile` from
the site descriptor and the corresponding profile. `minimal.profile` pins the
vendored Pi release with `pi_head_resolution=none`; `chasm.profile` resolves
site Pi HEAD at create time. A source manifest alone does not prove which path
the installed site will take.

### 2. Check the destination and recover guest work

Before deciding what to copy, inventory the task's **source closure**: the
umbrella repository, recursively required submodules, separate companion
repositories, selected task worktrees, and any non-Git inputs the project
actually reads. Use the project's dependency or question scope to decide what
is required; do not assume every nearby repository belongs in the closure.
For each required Git repository, record its path, HEAD, branch or detached
state, staged and unstaged changes, relevant untracked files, and whether its
working tree contains source. `git submodule status --recursive` identifies
pins but does not prove that the submodule working files exist. Record missing
or empty checkouts as gaps, and never silently replace a missing pin with a
remote branch tip. Identify indexes and other derived stores separately from
source; list their owning module, language or data scope, and source identity.

Inspect `/workspace/$PROJECT_NAME` before copying. If it exists, verify its Git
status, source metadata, and base commit. Preserve any dirty or untracked work
through the recovery procedure below before re-importing. A clean, matching
destination may be reused; a mismatched destination requires an owner decision
before replacement. Never mirror destructively by default. Additional guest
worktrees belong under `/workspace/.worktrees/$PROJECT_NAME/$TASK_NAME`; do not
put them beside the primary checkout or under the host worktree root.

Inspect the installed import/export helper versions and capabilities before
using them. For clean executor deployment, the selected helper must accept
`/workspace/<PROJECT_NAME>` with the same name, commit, clean-tree, and
credential-filter checks. If it still accepts only `/home/agent/workspaces/*`,
record that path capability gap; do not silently substitute `/home/agent`.

An owner-authorized local host-to-guest migration may use the existing
configured Incus guest interface when the host, instance, destination path,
guest UID, and source identity are verified. Clean executor deployment is not a
prerequisite. Use guest-side unprivileged commands or the approved import
adapter; never access Incus storage directly. A helper's path check does not
prove dirty-state recovery. If a helper or credential filter rejects the
source, destination, or payload, stop and preserve that rejection; do not
bypass it with an unreviewed copy route.

Dirty or untracked recovery is a separate approved transfer: capture the bundle
and status payloads below before replacement, and use a helper or verified guest
interface that explicitly supports their import/export modes.

### 3. Copy without moving

Copy only after the destination and recovery decision are recorded. Do not tar
the source with `.git` excluded: that destroys the repository's actual history
and index needed for recovery. Instead, transfer a reviewed Git bundle (or
rebuild a guest clone from the pinned source commit), then apply separate
status-preserving payloads for the source's dirty state:

- `git diff --cached --binary --full-index HEAD` for staged changes;
- `git diff --binary --full-index` for unstaged tracked changes;
- an explicit deletion list; and
- a reviewed archive of untracked files after secret and credential filtering.

Make a separate history and working-state payload for each required submodule,
companion repository, or independently dirty task worktree. Materialize each
submodule at its recorded relative path and HEAD before applying its working
state. An umbrella Git bundle contains gitlinks, not the submodules' objects or
working files. Include task-relevant ignored or generated
inputs only when the project actually needs them and they pass the same review;
the standard untracked payload does not capture ignored files.

Never bulk-copy `.git/config`, credential helpers, authentication directories,
or other host-local configuration. Rebuild guest worktrees from the transferred
history and record their branch/base bindings. Preserve machine-local state and
regenerable output by default (`.agent/`, `.cache/`, `__pycache__/`, `dist/`,
`tmp/`, `.venv/`, and `node_modules/`), while retaining checked-in vendored
inputs required by the project's build. Preserve file ownership for the guest
agent (the site normally uses uid/gid 1001). Use the approved Chasm import adapter or the verified configured Incus guest
interface once the `/workspace` path contract is resolved; do not access Incus
storage directly or bypass a real source, path, or credential rejection.

For a Git source, bind `SOURCE_COMMIT` and record the guest base commit. The
guest import must be idempotent: a retry is allowed only when the existing
destination has the same source identity, base commit, and clean status. If the
user selects a task worktree, create it with `git worktree add` at
`TASK_WORKTREE` after the primary checkout is verified; task worktree creation
does not change the authority of the primary checkout.

### 3b. Recover Git state without transferring host configuration

Before replacement, capture the source repository's complete history in a
reviewed bundle and capture its working state separately. A recovery record must
name the source commit, bundle digest, staged and unstaged patch digests,
deletions, untracked payload digest, and any intentionally omitted files. Apply
the staged patch first with `git apply --index`, then apply the unstaged patch,
and finally restore the reviewed untracked/deletion payload. Verify
`git status --short`, the index distinction, and the resulting content. If a
bundle or patch cannot be produced safely, stop before replacement and report
the exact recovery gap. A tar stream is a payload transport only; without the
bundle and status payloads it does not preserve Git history or the index, and it
is not a reason to copy host `.git` configuration.

### 4. Install project requirements inside the guest

Inspect the copied project's manifests and documented build entry point. Install
only the missing project requirements inside the guest, using the project's
native package manager and the guest's unprivileged environment where possible.
Package installation is an external mutation and may require separate approval.
Do not upgrade Chasm's pinned dotfiles or profile as part of project migration.

Record the package command, versions, and any approved provider route in the
task evidence. Never record secrets.

### 5. Verify the migrated project

For a multi-repository or index-backed project, first verify the source closure
in the guest before claiming the workload is ready. Compare each required
repository's selected source entries with a host manifest made from a stable
source view: relative path, regular-file size and SHA-256, executable mode when
relevant, or symlink target. Include dirty and relevant untracked content. In
the guest, re-enumerate the same selection and report missing, extra, or
changed paths by repository. If either checkout changes during capture or
verification, repeat the affected comparison. Matching umbrella HEADs,
submodule pins, or a copied manifest alone do not prove source parity. A
missing required submodule is a failed closure, not a partial success silently
treated as complete.

Admit each needed index or derived store separately. For an index copied from
the host, bind its owning module, source snapshot, language/data scope,
metadata, tool version, and stable snapshot digest; quiesce or snapshot active
stores before hashing or transfer. Validate the guest copy and run a
task-specific retrieval or read smoke test. If the guest builds a new index,
record its own identity and validate it against the verified guest source;
never claim byte identity with the host index. Source parity, index readiness,
and permission or harness readiness are distinct gates. Continue independent
work while a gate is pending, but do not run the dependent evaluation or claim
full migration readiness until it passes.

Run the project's build and fast test/check target from `/workspace/$PROJECT_NAME`
as the guest agent. If a task worktree was selected, repeat the relevant checks
from `/workspace/.worktrees/$PROJECT_NAME/$TASK_NAME`. Also verify the guest
working style relevant to the request:

- inspect the repository and status;
- edit a fixture file;
- run the project's relevant test or check;
- produce and inspect the requested review/evidence output;
- make a local commit when the task requires commit capability;
- verify the pinned dotfile links and shell without modifying the pinned store.

Static manifests and a successful `chasm show` do not establish project
functionality. Report command lines, exit status, commit IDs, and non-secret
artifacts separately from inferences.

### 6. Stop, export, and recover

The `/workspace` volume persists across stop/start. Before an approved delete,
export clean metadata and any intended patch/mbox/diffstat, and separately
preserve dirty or untracked work. Verify the export's source/base/head binding
and credential-filter result. If the requested lifecycle includes stopping the
target, stop through the Chasm CLI; an ongoing primary workspace may stay running:

```sh
chasm stop "$SANDBOX"
chasm show "$SANDBOX"
```

Deletion is a separate destructive action. Request or reuse explicit approval
only after recovery and export are verified, then use `chasm delete "$SANDBOX"`.
The global `/shared` volume must remain untouched. If a Pi/OpenRouter capability
was explicitly enabled and a shell ended uncleanly, use `chasm revoke "$SANDBOX"`
before stopping; otherwise do not invoke capability controls.

## Dotfiles and symlink boundary

New sandboxes inherit the pinned dotfiles layer from the sealed profile. Verify
the links and shell as evidence; do not hand-edit the root-owned pinned store.
Personal overrides belong in the guest user's local override files when the
dotfiles contract supports them. A host reader can resolve guest-created
symlinks against the host root, so host-side inspection and export must not
blindly dereference links (`cp -L`, recursive readers, or backup jobs).

## Completion and evidence

Migration is complete only when the copied project is in
`/workspace/$PROJECT_NAME`, any selected task worktree is under
`/workspace/.worktrees/$PROJECT_NAME/$TASK_NAME`, required dependencies are
installed with their approval recorded, the relevant build/test/review/commit
checks pass, any required multi-repository source closure and index gates pass,
and guest changes are either intentionally retained or exported
for recovery. Update the bound project plan or checkpoint with the actual
transfer, test, persistence, and exclusion evidence plus remaining gates before
returning, so `continue-work` does not repeat completed migration work. Report
unresolved path-adapter, provider, package, or existing-destination gaps instead
of claiming migration success.
