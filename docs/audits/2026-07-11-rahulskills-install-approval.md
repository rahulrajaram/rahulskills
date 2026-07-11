# Rahulskills Installation Approval Packet

Date: 2026-07-11
Status: approved, executed, and verified

## Requested operation

Activate the committed Rahulskills bundle in the two configured runtime roots,
after creating an external backup of every managed destination that will be
replaced. This is a capability installation, not ordinary repository copying,
and requires explicit approval.

## Exact reviewed source

- Repository: `$HOME/Documents/rahulskills`
- Commit containing the remediated skill content: `39523bd98331f0bb4e7e206b335c5eddd1615782`
- `skills/` Git tree: `907115b580acedfae3fea78bf207453bb79dc053`
- `references/` Git tree: `2bd0bc4e860be7520156c34d5aa06cf4e6b8ab5d`
- `overlays/` Git tree: `9dcbef0b6825eec9c28d855a73de3435ebf9f97f`
- `runtime-exclusions/` Git tree: `e6ba74524e9020972d360c2880ced799be97bd09`
- installer script blob: `1fb0d2bf54cde43487f6c9b69f4778095ae77af5`

The assembly produces 39 Codex repository skills and 40 Claude skills. The
repository `skill-creator` is excluded from Codex so the system-owned version
continues to win. Together with the seven system-owned Codex skills observed in
the reviewed catalog, the runtime resolves to 46 unique skill names.

## Destinations and expected effects

| Source | Destination | Effect |
|---|---|---|
| `build/codex/skills/<name>` | `$HOME/.agents/skills/<name>` | replace 39 managed skill directories |
| `build/claude/skills/<name>` | `$HOME/.claude/skills/<name>` | replace 40 managed skill directories |
| `build/codex/references/*` | `$HOME/.agents/references/` | add/update 3 shared primitive files |
| `build/claude/references/*` | `$HOME/.claude/references/` | add/update the same 3 files |

Unmanaged sibling skills are left in place. Current read-only comparison shows
24 managed manifests differ in each runtime; `speak/scripts` is newly deployed;
two Yarli helper scripts change; and neither reference destination exists.
Assembly excludes `__pycache__`, `.pyc`, and `.pyo` artifacts.

## Approved execution sequence

Only after explicit approval:

1. Require Rahulskills HEAD and the five source/tree hashes above to match this
   packet; abort on drift.
2. Re-run all packaging, frontmatter, reference, catalog, and capture-harness
   tests, then assemble without installing.
3. Create
   `${XDG_STATE_HOME:-$HOME/.local/state}/rahulskills/backups/<UTC>-39523bd/`
   with byte-preserving copies of the 39 Codex destinations, 40 Claude
   destinations, both reference destinations (or an absence marker), and a
   SHA-256 inventory.
4. Re-run the source-versus-installed diff and present the final changed-path
   summary. Stop if it exceeds the reviewed destinations.
5. Run `./stitch-skills.sh install` from the reviewed commit.
6. Verify 39/40 installed repository skills, 46 unique resolved names, zero
   divergent collisions, all three references in both roots, no Python caches,
   and byte parity with assembled output.
7. Start a fresh Codex process and verify `next-todos` is planning-only unless
   enqueue intent is explicit. Do not kill or mutate the current process.

## Rollback

If any post-install check fails, stop new client launches and restore only the
managed destinations from the timestamped backup. Remove a destination only
when its absence marker proves it did not exist before installation. Re-run the
same inventory and catalog checks after restoration. Retain the backup until a
fresh client has passed smoke verification and the user separately approves
deletion.

## Execution result

Explicit approval was received and the bounded operation completed on
2026-07-11. The retained backup is:

`$HOME/.local/state/rahulskills/backups/20260711T185810Z-39523bd/`

Its SHA-256 inventory passed in full and contains 39 prior Codex skill
directories, 40 prior Claude skill directories, and absence markers for both
previously missing reference roots. Post-install verification reported:

- byte parity between assembled and installed managed skills;
- 39 Codex and 40 Claude repository skills;
- 46 resolved definitions, 46 unique names, and zero divergent collisions;
- all three shared references present in both roots;
- no deployed `__pycache__`, `.pyc`, or `.pyo` artifacts; and
- a fresh ephemeral, read-only Codex process loaded the installed `next-todos`
  manifest, returned only the requested numbered plan, and performed no Yarli
  enqueue.

Rollback was not required. The backup remains retained and was not deleted.

## Approval boundary

Approval must name this commit and all four destination roots. It authorizes the
bounded backup/install/verify/rollback sequence only. It does not authorize a
push, dependency installation, system-skill replacement, MCP restart, process
pruning, marketplace/plugin activation, or backup deletion.
