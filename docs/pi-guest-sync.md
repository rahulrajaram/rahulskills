# Pi skills in the development sandbox

The host's installed Pi skill catalog is authoritative for the managed guest
copy. `scripts/sync_pi_guest.py` copies local skill instructions and support
files into a versioned guest snapshot. It does not install remote packages,
agent extensions, MCP servers, providers, or dependencies used by the skills.
It never copies Pi credentials or settings, starts a sandbox, or changes Chasm
binaries.

The main source is `~/.pi/agent/skills`. A package-specific source, such as the
optional `pi-mcp-adapter` `mcp-scripting` skill, can be added explicitly to the
service configuration when installed. New skills under the main source are included
automatically. Links into explicitly allowed local checkouts are materialized
so that host absolute links do not break inside the guest. Unsupported paths
fail rather than being silently omitted.
Guest-local skills remain separate from the `host-synced` managed directory.
Do not edit that directory in the guest: edit the host source instead. A
changed managed snapshot is a conflict, and must be preserved and reconciled
before further synchronization.

## Synchronization

Preview first, then apply:

```sh
python3 scripts/sync_pi_guest.py \
  --source "$HOME/.pi/agent/skills" --sandbox development \
  --allow-root "$HOME/Documents/rahulskills" \
  --references "$HOME/Documents/rahulskills/references"

python3 scripts/sync_pi_guest.py \
  --source "$HOME/.pi/agent/skills" --sandbox development \
  --allow-root "$HOME/Documents/rahulskills" \
  --references "$HOME/Documents/rahulskills/references" --apply
```

The host timer runs the deployed script every two minutes while the user's
systemd manager is running. A stopped development sandbox is skipped. It
catches up after the sandbox starts; it does not boot the guest itself. Source
updates become a new verified generation with an atomic pointer change. Old
generations remain available for recovery. Guest sessions already running may
need Pi's `/reload` or a restart to see the new catalog.

The timer targets `development` only. New sandbox targets must be explicitly
configured; installing Pi through Chasm alone does not install these personal
skills. Chasm provisioning can call the same sync command after a selected
sandbox starts, rather than implementing a second copy mechanism.

If `pi-mcp-adapter` is installed and you want its `mcp-scripting` skill, add
`--allow-root "$HOME/.pi/agent/npm/node_modules/pi-mcp-adapter/skills"` and
`--extra-skill "$HOME/.pi/agent/npm/node_modules/pi-mcp-adapter/skills/mcp-scripting"`
to the command or user service. Without that package, leave those options out.

## Operations

The source units are under `deployment/systemd/`. Install the script and user
units explicitly; merely checking out this repository does not provision them.
The preview commands above and the units assume the checkout is at
`$HOME/Documents/rahulskills`. Replace their repository paths and set `REPO`
to the actual checkout path when it differs:

```sh
REPO="$HOME/Documents/rahulskills"
install -D -m 0755 "$REPO/scripts/sync_pi_guest.py" \
  "$HOME/.local/lib/rahulskills/sync_pi_guest.py"
install -D -m 0644 "$REPO/deployment/systemd/rahulskills-development-sync.service" \
  "$HOME/.config/systemd/user/rahulskills-development-sync.service"
install -D -m 0644 "$REPO/deployment/systemd/rahulskills-development-sync.timer" \
  "$HOME/.config/systemd/user/rahulskills-development-sync.timer"
```

Before starting the service, update each installed unit's `Documents/rahulskills`
arguments if `REPO` is elsewhere. Then inspect the generated manifest with the
preview command above. Reloading the user manager and enabling or starting the
timer are separate operator actions; this repository does not activate them
automatically.

```sh
systemctl --user status rahulskills-development-sync.timer
systemctl --user start rahulskills-development-sync.service
journalctl --user -u rahulskills-development-sync.service -n 30
systemctl --user disable --now rahulskills-development-sync.timer
```

Disabling the timer leaves the current guest skills in place. Removing the
managed guest discovery link disables the copied catalog; retained generation
directories hold the recovery data. This synchronization grants skills no new
authority: guest tools, credentials, approvals, and available runtime adapters
still determine which instructions can actually execute.

The synchronizer copies instruction files only. It does not install the
`pi-mcp-adapter` extension, `selfimprove-host-triage`, MCP servers, or any other
runtime dependency. After installation, verify the guest's loader and the
service journal on the target host; those results depend on that host's
installed skills and guest configuration.
