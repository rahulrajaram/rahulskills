---
name: chasm-migrate
description: >
  Migrate a project into a chasm sandbox: copy (never move) the code into the
  sandbox's own workspace volume, install the project's requirements inside
  the guest, and verify the build plus the pinned rahulrajaram/dotfiles
  artifacts. Use when the user asks to migrate/copy a project into a chasm
  sandbox, give a project its own sandbox workspace, or set up a new sandbox
  for existing work.
metadata:
  short-description: Migrate a project into a chasm sandbox
---

# Chasm project migration

Migrate host-side work into a chasm sandbox VM: copy the code into the
sandbox's own workspace, make the project's requirements true inside the
guest, and prove it. Copying is one-way: the host tree stays the source of
truth, and the sandbox workspace is a working copy.

## Model (verified on a live chasm site, 2026-09-19)

- A sandbox named `<name>` is Incus instance `sandbox-<name>`; its
  `/workspace` is the host-side btrfs volume
  `/var/lib/incus/storage-pools/chasm/custom/default_agent-sandbox-workspace-sandbox-<name>`
  (Incus prefixes the project name `default_`). Writes on either side appear
  on the other instantly (virtiofs).
- The guest agent user is uid/gid 1001 (host group `harbinger` has gid 1001;
  operator `rahul` is a member). Population from the host must map ownership
  to 1001:1001 or the agent cannot write its own files.
- The site runs **one sandbox VM at a time**; `chasm create/start` refuses
  while another VM runs. Stop the other sandbox first (`chasm stop <name>`);
  its state persists.
- Dotfiles: new sandboxes inherit `rahulrajaram/dotfiles` from the sealed
  template at the revision pinned in `guest-config/dotfiles/SOURCE` —
  `.zshrc`, `.vimrc`, `.tmux.conf` are symlinks into
  `/usr/local/share/agent-sandbox/dotfiles/<sha256>/` in the guest, and the
  login shell is zsh. `.gitconfig` is a template, not auto-installed.
- Guest egress reaches the internet (DNS + non-RFC1918); apt works in-guest.

## Procedure

### 1. Site and sandbox preparation

```sh
cd ~/Documents/chasm && sudo scripts/install-chasm.sh --verify   # expect 0 drift
chasm create <name> <budget-mib>   # 512-16384; give Lisp/C++ builds 4096+
chasm start <name>
```

If another sandbox is running, `chasm stop <other>` first. Give each project
its own sandbox: the name is the workspace identity.

### 2. Copy the code (never move)

The pool's `custom/` directory is root-only, so population runs under sudo.
Map ownership to the guest agent and keep files group-accessible:

```sh
WS=/var/lib/incus/storage-pools/chasm/custom/default_agent-sandbox-workspace-sandbox-<name>
sudo rsync -a --chown=1001:1001 --chmod=Du=rwx,Fu=rw \
  --exclude=/.git/ --exclude=__pycache__/ --exclude='*.pyc' \
  --exclude=/dist/ --exclude=/tmp/ --exclude=/.venv/ --exclude=/node_modules/ \
  <host-project>/ "$WS/"
```

Defaults: exclude machine-local agent state (dot-directories like `.agent/`,
`.cache/`, project tool state) and regenerable build output (`dist/`, `tmp/`,
`__pycache__`). Keep anything the build needs vendored (for example a
checked-in dependency toolchain such as a bundled Quicklisp, node_modules
with a lockfile, or a Cargo vendor dir). Re-run the same command to re-sync
later; add `--delete` only when the sandbox copy is meant to mirror the host
exactly.

### 3. Install the project's requirements in the guest

Inspect the project (manifests, Makefile, install.sh), then install into the
guest as root:

```sh
sudo incus exec sandbox-<name> -- bash -c \
  'export DEBIAN_FRONTEND=noninteractive; apt-get update -qq && apt-get install -y <packages>'
```

Record per-project requirement notes as projects migrate (guest packages,
version quirks, the build/test command that proves it). Two patterns seen so
far: interpreted-language projects usually need only their runtime plus the
build tool; compiled/Lisp projects may additionally need `-dev` packages when
a vendored dependency probes unversioned shared libraries that the distro
ships only versioned (e.g. cl+ssl probing `libcrypto.so` on a release that
installs only `libcrypto.so.3` — install the matching `libssl-dev`).

### 4. Verify

```sh
# build/test proof (as the agent user, from the workspace):
sudo incus exec sandbox-<name> -- su - agent -c 'cd /workspace && <build-or-test-command>'
# dotfiles proof:
sudo incus exec sandbox-<name> -- su - agent -c \
  'ls -la ~/.zshrc ~/.vimrc ~/.tmux.conf; echo $SHELL'
```

Migration is done when the build (and, where cheap, the fast test target)
exits 0 in the guest and the dotfile symlinks resolve.

### 4b. Personalizing the environment (E166)

`.zshrc`, `.vimrc`, `.tmux.conf` are symlinks into the root-owned, read-only
pinned store, so vim fails with E166 if pointed at them directly. That is the
integrity design, not a bug: personal overrides belong in `~/.zshrc.local` and
`~/.vimrc.local`, which the pinned files source at the end. Create them
agent-owned:

```sh
sudo incus exec sandbox-<name> -- su - agent -c \
  'echo "# Personal overrides" > ~/.zshrc.local; echo "\" Personal overrides" > ~/.vimrc.local'
```

Only changes that belong in the dotfiles themselves go through section 5.

### 5. Refreshing the dotfiles pin (when rahulrajaram/dotfiles moves)

The pin lives in three places that must move together:
`guest-config/dotfiles/SOURCE` (revision + per-file sha256 pins),
`scripts/install-guest-dotfiles.sh` (the same constants), and the bootstrap
profile manifests (`dotfiles_revision`). Update all three, run
`scripts/check-carve-equivalence.sh` and `scripts/check-site-profiles.sh`,
then rebuild the template — the identity digests the dotfiles layer, so
`build-sandbox-template.sh` creates a coexisting new template and
`install-chasm.sh --provision` picks it up. Never hand-edit dotfiles inside
an existing sandbox; refresh the pin and rebuild instead.

## Symlink boundary (verified)

A symlink stored in a share resolves in whichever kernel walks the path.
Guest processes resolve against the guest root: a sandbox can NEVER reach
host files through a symlink in /shared or /workspace (proven: host-written
and guest-written links both resolved to the guest's own /etc/hostname).
Host processes resolve against the HOST root: a sandbox-written symlink
redirects a host reader to host files. Therefore never dereference paths in
the volume directories blindly (no `cat <ws>/...`, `cp -L`, or backup jobs
that follow links), and run the standing audit:

```sh
cd ~/Documents/chasm && sudo scripts/audit-workspace-symlinks.sh        # exit 1 if any exist
sudo scripts/audit-workspace-symlinks.sh --prune                        # remove them
```

## Gotchas

- `chasm shell <name>` needs no sudo (built-in passwordless allowlist) and
  REFUSES to run as root. It is interactive only — automation goes through
  `sudo incus exec sandbox-<name> -- …`.
- Host-side writes into the volume need sudo (the `custom/` dir is 0700
  root). Without `--chown=1001:1001` the agent cannot write its own files.
- First `make`-style runs compile from scratch (fresh guest HOME); budget
  tens of minutes for Lisp builds, not seconds.
- The workspace volume is uncapped and shares the 64G pool with VM disks;
  check `sudo incus storage volume list chasm` and host `df` before big
  copies.
