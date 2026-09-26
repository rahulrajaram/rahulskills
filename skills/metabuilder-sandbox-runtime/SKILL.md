---
name: metabuilder-sandbox-runtime
description: "Historical playbook for executing Harness Module command actions inside the MetaBuilder sandboxed command adapter: the exact bwrap/systemd-run confinement profile, its consequences (no network, 4 GiB address space, read-only workspace, tmpfs /tmp, fixed env), and the working patterns for network-less deterministic scenarios (Unix-socket HTTP transports, in-sandbox redis-server, node:http clients, digest-bound auxiliary directories). Use when authoring or debugging actions that must actually run under `metabuilder run workflow apply`."
---

# MetaBuilder sandbox runtime playbook

## Harness state diagrams

When work in this skill concerns a harness's states or transitions, follow [harness state diagrams](../metabuilder/references/harness-state-diagrams.md) and include the required Mermaid and ASCII diagrams in the final response.

The observations below came from a prior communication-harness run against the
confinement profile in
`metabuilder/crates/mb-core/src/campaign_step_fs.rs`
(`run_sandboxed_command` → `run_bounded_sandboxed_command_observed_at`) and its governed run. They are historical evidence, not proof of the current
runtime. Before relying on a limit or command, inspect the installed CLI and
matching source. Prefer the current `metabuilder qualify guide` when supported;
older builds used `harness qualification guide`. Do not install or activate a
different runtime to make these examples work.

## The confinement profile (what an action actually gets)

`run workflow apply --workspace PATH` dispatches command actions through:

```
systemd-run --user --scope --collect --quiet
  --property RuntimeMaxSec=<timeout+1s>ms
  --property MemoryMax=4GiB --property TasksMax=128
  -- /usr/bin/bwrap --die-with-parent --new-session --unshare-all
    --ro-bind /usr /usr  (+ /bin,/lib,/lib64,/sbin symlinks)
    --tmpfs /usr/local  --tmpfs /etc
    --tmpfs /tmp  (512 MiB)
    --proc /proc --dev /dev
    --ro-bind <source-snapshot> /workspace   (READ-ONLY)
    --ro-bind <aux-snapshot> /workspace/<aux-path>
    --chdir /workspace
    --setenv HOME /tmp/metabuilder-home --setenv TMPDIR /tmp
    --setenv METABUILDER_OUTPUT_DIR /outputs ...
    -- PATH/prlimit --as=4GiB --cpu=<timeout+1> --fsize=1GiB -- <argv>
```

Consequences, each verified:

1. **No network at all.** `--unshare-all` includes `--unshare-net`; the new
   netns has `lo` DOWN and nothing raises it. TCP loopback is dead. Any
   action needing localhost services must use **Unix domain sockets under
   `/tmp`** (tmpfs, shared by all children of the action).
2. **Child processes are allowed and see the same confinement.** A runner may
   spawn servers, Redis, and clients. They inherit the 4 GiB address-space
   rlimit.
3. **Node 18’s bundled `fetch()` failed under the observed 4 GiB AS limit.**
   Node 18's bundled undici eagerly instantiates its llhttp WASM at module
   load, and the trap-handler memory reservation does not fit — the promise
   rejects with `WebAssembly.instantiate(): Out of memory: wasm memory`, and
   an unhandled rejection kills the process. Write MCP/HTTP clients with
   `node:http` (`socketPath`) or `net`. Verified crash and verified workaround.
4. **A server that itself loads undici can survive** with
   `node --unhandled-rejections=warn` when it never calls `fetch`: constructing
   `Request`/`Response` objects needs no WASM. This is exactly how the GPTQueue
   HTTP server runs in-sandbox (see `harness/lifecycle/server-fixture.mjs`
   in the gptqueue repository for the working spawn).
5. **Only `/usr`/`/bin` system executables and bare rustup names are
   admissible** as `argv[0]`/toolchain executables (enforced in
   `command.rs`: `executable.starts_with("/usr/") || starts_with("/bin/")`).
   A user-home interpreter (e.g. a Node 24 under `/home/...`) can NEVER be a
   harness action. Do not try `env`, symlinks, or wrappers to smuggle one —
   that is an admission bypass, and the guide says to stop and report instead.
6. **The workspace is read-only.** Builds (`tsc` emit, `npm run build`) cannot
   run as actions. Run them controller-side before authoring the run and bind
   the built output (e.g. `dist/`) as an **auxiliary directory**.
7. **No environment passthrough.** The action env is fixed
   (HOME/TMPDIR/METABUILDER_*). A runner controls its children's env itself.
8. **Declared outputs only under `/outputs`.** stdout/stderr are bounded,
   content-addressed diagnostics — a single-line JSON summary on stdout is a
   perfectly good evidence artifact and avoids the artifact-port catalog.
9. **A filesystem-source-write confinement probe runs before the command**
   and fails the apply if the source tree is dirty. Source identity must be
   exact (clean tracked tree at the bound revision).

## Auxiliary directories: the rules that bite

- Digests are content digests of the directory — recompute with the CURRENT
  binary immediately before `harness author`; `node_modules` drifts silently
  (observed twice in one campaign).
- An auxiliary directory may NOT overlap committed source. Once your runner
  code is committed, remove its aux declaration — the source binding carries
  it. Only ignored/untracked dependencies (node_modules, dist) belong there.
- Aux snapshots are mounted read-only at `/workspace/<path>`.
- `harness author` requires a **clean worktree** — including untracked files.
  Put the run root OUTSIDE the repository (`<authorized-artifact-root>/<project>-mb-runs/<id>`),
  otherwise the run's own journal dirties the tree and authoring fails with a
  confusing "requires a clean worktree" error listing the journal files.

## Proven in-sandbox architecture for communication harnesses

The gptqueue `harness/metabuilder/communication-lifecycle-v1` campaign ran the
full lifecycle inside this profile. Reuse its shape:

- In-sandbox `redis-server`: `/usr/bin/redis-server --unixsocket <tmp>/redis.sock
  --unixsocketperm 700 --port 0 --save "" --appendonly no --dir <tmp>`.
  ioredis accepts the socket path directly via `REDIS_URL=<path>`.
- GPTQueue HTTP server over UDS via the opt-in `GPTQUEUE_HTTP_SOCKET`
  (src/transports/http.ts), spawned with `--unhandled-rejections=warn`.
- Deterministic MCP clients over `node:http` `socketPath` (no `fetch`), a
  single-line JSON result summary on stdout, deadline polling (no fixed
  sleeps), unique per-edge idempotency keys embedded in `metadata.edge_key`,
  and expected-edge multiset comparison via pure helpers.

## Operating gotchas (each cost a real cycle once)

- The apply envelope for a bundle-backed run needs the bundle:
  `run workflow apply --run-root R --workspace . --bundle BUNDLE` — otherwise
  "no frozen intent origin".
- Each worker action is followed by a `retrospective_required` blocker; the
  workflow is idle until `run retrospectives scaffold` → fill → `record`.
  **`actor_id` must be a valid tranche id** (lowercase-hyphen slug, e.g.
  `gptqueue-controller`); an empty string fails with
  "invalid retrospective id: invalid tranche identifier".
- `run workflow review inspect|apply` is the self-hosting BlindReview flow —
  not the consumer path. A finished consumer run rests at campaign state
  `awaiting_assessment` with workflow selection `status: "complete"`; that is
  the normal resting state.
- Attestation `verdict` values are `meets` / `does_not_meet` / `uncertain`
  (not "pass"), and `consumer_evidence[].digest` entries must be real SHA-256
  digests (use the journaled action evidence digests).
- Tool results that serialize a legacy payload (e.g. `list_agents`,
  `get_queue_status`, `receive_message` in GPTQueue) return a bare array or
  the message object as `content[0].text` — normalize shapes in clients.
- The historical CLI used `metabuilder harness qualification`; current builds
  may expose `metabuilder qualify`. Inspect help and preserve the verified
  executable identity rather than copying a command family from this playbook.

## Stop boundaries to preserve

Paid generation dispatch (`harness generate`), pushes, deploys, live-server
contact (port 8101 / Redis db0), dependency changes, secret access, and
admission bypasses all remain stop-for-principal-direction events. The
sandbox exists so that none of those are ever tempting.
