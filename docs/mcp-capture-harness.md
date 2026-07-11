# MCP Contract Capture Harness

`scripts/mcp_contract_capture.py` captures a fresh stdio MCP process without
installing, registering, restarting, or pruning any runtime. It records the
initialize response, tool schemas, normalized JSON-RPC transcript, stderr,
source/runtime SHA-256 inventories, text diffs, and copies of compared runtime
artifacts suitable for rollback.

## Usage

Source and runtime artifacts are paired by label. The command after `--` must
start a new stdio MCP server and may point directly at a repository build or an
already-configured executable:

```sh
python3 scripts/mcp_contract_capture.py \
  --name example \
  --output-dir /tmp/mcp-capture-example \
  --source server=/path/to/source/server \
  --runtime server=/path/to/configured/server \
  --fail-on-diff \
  -- /path/to/configured/server mcp
```

Each label may refer to a file, directory, or symlink. Repeat `--source` and
`--runtime` for multiple artifacts. Labels must match exactly. The output
directory must not already exist, preventing accidental evidence overwrite.

## Output contract

- `manifest.json` identifies the command, protocol captures, comparisons,
  hashes, changed paths, and rollback artifact locations.
- `initialize.json` preserves server instructions and capabilities after
  removing known volatile timestamp/process fields.
- `tools-list.json` preserves advertised descriptions, safety labels, input
  schemas, output schemas, and annotations.
- `transcript.jsonl` contains normalized server messages in observed order.
- `stderr.log` preserves diagnostic output from the fresh child.
- `diffs/<label>/` contains unified diffs for comparable UTF-8 files.
- `rollback/<label>/` is a byte-preserving copy of each runtime artifact (or a
  preserved symlink) from before any later operational change.

The harness returns nonzero on protocol failure or timeout. With
`--fail-on-diff`, it also returns nonzero when any source/runtime artifact
differs. A difference is evidence, not authorization to copy, install, reload,
restart, or clean up a process.

## Operational boundary

Running the harness starts and terminates only the fresh child command it owns.
It does not inspect or signal existing Codex-owned stdio children. Capture into
a durable evidence directory when the artifacts must survive reboot; `/tmp`
captures are intentionally ephemeral. Review the exact command and all artifact
paths before execution, especially when a server can write to a database during
initialization. Do not place secrets in command-line arguments because the exact
command is recorded in `manifest.json`.
