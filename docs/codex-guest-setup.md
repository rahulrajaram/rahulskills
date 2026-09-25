# Codex in a development guest

This document describes the Codex skill synchronization profile for a
development guest. The synchronizer does not install Codex, its Node runtime,
or host credentials. Verify those prerequisites in the target guest before
using the commands below.

Sign in interactively inside the guest:

```sh
chasm shell development
codex login --device-auth
```

Follow the displayed instructions, then run `codex` from the project or
worktree you want to develop. Primary projects belong under
`/workspace/<project>` and task worktrees under
`/workspace/.worktrees/<project>/<task>`; follow `/workspace/AGENTS.md`.

If the guest is configured with a selfimprove stdio MCP, its settings are
environment-specific. A typical profile uses:

- Interpreter: `/workspace/.venvs/selfimprove/bin/python`
- Server: `/workspace/selfimprove/server.py`
- State root: `/workspace/.selfimprove-state`
- Automatic external tool discovery disabled (`SELFIMPROVE_NO_AUTO_DISCOVER=1`).

The skill synchronizer supports `--runtime codex` and uses the host's installed
`~/.codex/skills`, including explicitly supplied shared references. It publishes under
`/workspace/.agent-skills/codex` and exposes the active snapshot through
`~/.codex/skills/host-synced` in the guest. Existing runtime-provided `.system`
skills are kept separate. The Pi and Codex destinations are independent.

The host user timer `rahulskills-development-codex-sync.timer` can refresh this
catalog periodically while the user service manager is running. It skips
stopped guests and refuses to replace locally edited snapshots. Start a fresh
Codex session after a refresh to ensure the new skill catalog is loaded.

Install the script and Codex units using the procedure in
[`pi-guest-sync.md`](pi-guest-sync.md), substituting
`rahulskills-development-codex-sync.service` and
`rahulskills-development-codex-sync.timer`. The units assume the checkout is
at `$HOME/Documents/rahulskills`; edit their repository paths for another
checkout. Installation does not enable or start the timer.

```sh
systemctl --user status rahulskills-development-codex-sync.timer
systemctl --user start rahulskills-development-codex-sync.service
systemctl --user disable --now rahulskills-development-codex-sync.timer
```

Disabling the timer preserves the installed skills. Authentication is performed
by the user inside the guest; host credentials and provider configuration are
not copied. CLI startup and native skill discovery do not prove that a model
request succeeds before sign-in is complete.

After installation, verify the target guest's Codex version, native skill
discovery, and service journal on that host. Those results vary with the guest
image and host configuration. An authenticated model request is not required
to verify file synchronization.
