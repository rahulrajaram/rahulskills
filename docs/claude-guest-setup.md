# Claude Code in a development guest

This document describes the Claude Code profile for a Chasm development guest
(guest user `agent`, home `/home/agent`). The skill synchronizer does not
install Claude, its runtime, or any credential. Chasm's guest installer is
responsible for those; verify them in the target guest before relying on the
commands below.

## Install check

Inside the guest:

```sh
chasm shell development
command -v claude            # expected: /home/agent/.local/bin/claude
claude --version
command -v claude-openrouter # installed by the Chasm Claude layer; usable only under --with claude
claude mcp list              # shows `jev` when the installer registered it
```

A present binary proves only that Claude starts. It does not prove that a model
request succeeds before sign-in or relay access is configured.

## Sign-in options

- **Relay-mediated OpenRouter.** Open the session with
  `chasm shell development --with claude` and start Claude with
  `claude-openrouter`. The wrapper routes requests through the Chasm relay; the
  guest never holds the OpenRouter key.
- **Personal account.** In a plain `chasm shell development`, run
  `claude`, then `/login` and follow the displayed instructions. The resulting
  credentials stay in the guest's Claude config directory.

Then run `claude` (or `claude-openrouter`) from the project or worktree you want
to develop. Primary projects belong under `/workspace/<project>` and task
worktrees under `/workspace/.worktrees/<project>/<task>`; follow
`/workspace/AGENTS.md`.

## Credential rules

- Never copy host `~/.claude/.credentials.json`, host Claude settings, or any
  other host auth material into a guest, `/shared`, a repository, or a chat.
  Sealed guest templates are scrubbed of `.credentials.json`; do not
  reintroduce it.
- The synchronizer refuses credential-like file names (`auth*`, `credential*`,
  `token*`, `secret*`, keys) and copies skill instructions and support files
  only.
- Authentication is performed by the user inside the guest. Host provider
  configuration is not copied.

## Jev MCP registration

The Chasm guest installer registers the Jev MCP server at user scope with
`claude mcp add --scope user jev ...`. Confirm it with `claude mcp list` or
`claude mcp get jev`. If it is missing, report that installer gap; do not copy
a host MCP configuration into the guest. Registration does not prove the server
responds; exercise a Jev tool from a Claude session to check that.

## Skill synchronization

Claude discovers skills only at `<config>/skills/<name>/SKILL.md`, where
`<config>` is `$CLAUDE_CONFIG_DIR` or `~/.claude`. There is no nested
`host-synced` discovery directory, so the Claude runtime differs from Pi and
Codex:

1. The host source is the host's installed Claude catalog,
   `$CLAUDE_CONFIG_DIR/skills` or `~/.claude/skills`. That catalog is the
   stitched `build/claude` output installed by `./stitch-skills.sh`, so Chasm
   profile overlays and Claude runtime exclusions are already applied; raw
   `skills/` sources are not synchronized. Shared references come from
   `--references`.
2. `scripts/sync_pi_guest.py --runtime claude` publishes a verified, immutable
   generation under `/workspace/.agent-skills/claude/<hash>` and points the
   bookkeeping link `/workspace/.agent-skills/claude/active` at it. Claude does
   not read that directory.
3. The generation is then projected as real copies into
   `/home/agent/.claude/skills/<name>` and `/home/agent/.claude/references/`,
   so `../../references/<file>` links in a skill resolve. Use
   `--guest-claude-config-dir` when the guest uses another `CLAUDE_CONFIG_DIR`;
   it must be a normalized path under `/home/agent`.
4. Every projected entry is recorded with a content fingerprint in
   `<config>/.chasm-skills-ownership.json`. An entry is updated or removed only
   while it still matches that ledger. Skills you create in the guest are
   never touched. A same-named unmanaged skill, or a managed skill edited in
   the guest, is a conflict: the sync refuses before switching generations and
   leaves every entry in place. Move or reconcile the conflicting entry, then
   sync again. A managed entry that no longer exists on the host is removed
   only if unedited; an edited one is retained and dropped from management
   only after you remove it.

Preview first, then apply:

```sh
python3 scripts/sync_pi_guest.py --runtime claude --sandbox development \
  --allow-root "$HOME/Documents/rahulskills" \
  --references "$HOME/Documents/rahulskills/references"

python3 scripts/sync_pi_guest.py --runtime claude --sandbox development \
  --allow-root "$HOME/Documents/rahulskills" \
  --references "$HOME/Documents/rahulskills/references" --apply
```

Inside a guest, `scripts/activate_chasm_skills.py --runtime claude --bundle
BUNDLE` composes and activates a local bundle the same way (preview by
default, `--apply` to write). It uses the same ledger, honors
`$CLAUDE_CONFIG_DIR` or `--claude-config-dir`, and keeps its bookkeeping link
at `<snapshot-root>/claude/active`.

Start a new Claude session after a refresh so the updated catalog is loaded.

## Host timer

The host user timer `rahulskills-development-claude-sync.timer` can refresh the
catalog periodically while the user service manager is running. It skips
stopped guests and refuses conflicts as described above. Install the script and
Claude units using the procedure in [`pi-guest-sync.md`](pi-guest-sync.md),
substituting `rahulskills-development-claude-sync.service` and
`rahulskills-development-claude-sync.timer`. The units assume the checkout is
at `$HOME/Documents/rahulskills`; edit their repository paths for another
checkout. If the host uses `CLAUDE_CONFIG_DIR`, set it in the user manager
environment (or pass `--source`) so the service reads the right catalog.
Installation does not enable or start the timer.

```sh
systemctl --user status rahulskills-development-claude-sync.timer
systemctl --user start rahulskills-development-claude-sync.service
journalctl --user -u rahulskills-development-claude-sync.service -n 30
systemctl --user disable --now rahulskills-development-claude-sync.timer
```

Disabling the timer preserves the projected skills. To stop using the managed
catalog, remove the entries listed in the ledger and then the ledger itself;
retained generations under `/workspace/.agent-skills/claude` hold the recovery
data. Synchronization grants skills no new authority: guest tools, credentials,
approvals, and MCP servers still determine what can execute.

After installation, verify the guest's Claude version, native skill discovery
(for example `/skills` in a session), the Jev MCP registration, and the service
journal on the target host. Those results vary with the guest image and host
configuration.
