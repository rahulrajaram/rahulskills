# Independent Skills and MCP Second Review

Date: 2026-07-10

Scope: the currently loaded Codex skill and MCP surfaces, their canonical local
sources, and the four repository-owned MCP implementations. This review rebuilt
the inventory from current files and runtime metadata. It did not treat
`capabilities/skills.toml` or the first audit as authoritative.

No recommendation in this report has been implemented. No dependency was
installed, no capability was activated, and no MCP binary or process was
rebuilt, restarted, or pruned.

## Executive conclusion

The first audit correctly removed name collisions from the *resolved loaded
catalog*, but its clean 46/46 summary is not a complete source inventory and its
metadata still contains material behavioral errors. The explicit four-root
inventory contains 86 manifests with 46 unique names: 39 repository manifests
are byte-identical deployment mirrors under `~/.agents/skills`, the repository's
`skill-creator` is source-only for Codex, and the system `skill-creator` wins at
runtime. Treating mirrors as distinct capabilities would be wrong; treating the
fourth root as absent would also be wrong.

The independent prompt review did not affirm the catalog wholesale. It found
critical hidden or under-disclosed effects in `handoff`, `commit`,
`yarli-execution-loop`, `next-todos`, `pr-lifecycle`, and system Figma setup;
command-construction risks in `speak`, `tui-web-design-orchestrator`, and history
rewriters; technically unsound diagnostic claims in `memleak-investigate` and
`system-memory-audit`; stale implementation contracts in the conversation
analysis skills; and several useful composer skills that restate rather than
consume their primitives.

The MCP source/runtime comparison found 66 repository-owned runtime tools (26
Haake, 27 selfimprove, 7 GPTQueue, 6 Cultivar), plus the system-owned
`image_gen.imagegen`. Current runtime metadata is stale relative to three source
HEADs. Most visibly, every loaded Haake tool repeats a 1,165-character
initialize/recent-memory prefix: 30,290 duplicated characters, 71.1% of Haake's
42,631 runtime-description characters. Current Haake source has already made
that ambient preview opt-in, but the loaded process has not picked up the fix.

## Method and inventory

The requested commands were run from the `rahulskills` repository root.
`audit_catalog.py` reported 46 loaded definitions, 46 unique names, and no
divergent collisions. Running the same audit with the repository source root
explicitly added reported 86 definitions, 46 names, and one divergent collision:
the system and repository `skill-creator` prompts. Direct SHA-256 comparison
showed all 39 `~/.agents/skills` manifests are byte-identical to their repository
counterparts; only repository `skill-creator` lacks a `~/.agents` mirror.

Repository HEADs matched the handoff exactly:

| Repository | Branch / HEAD | Working state |
|---|---|---|
| rahulskills | `master` / `1e6a411` | clean at start; ahead 2 |
| haake | `master` / `59e9e33` | clean |
| selfimprove | `master` / `1cbe63d` | clean; ahead 25 |
| gptqueue | `feat/session-aware-architecture` / `8f51dd3` | clean; ahead 1 |
| cultivar | `master` / `d29ee59` | clean; pre-existing stash untouched |

The MCP source and loaded inventories are:

| Namespace | Source advertised | Source dispatchable | Runtime | Runtime description chars | Role |
|---|---:|---:|---:|---:|---|
| `haake_memory` | 26 | 26 | 26 | 42,631 | durable memory, retrieval, checkpointing, durable coordination |
| `selfimprovemeta` | 27 | 27 | 27 | 18,255 | tool-ecosystem graph and friction governance |
| `gptqueue_shared` | 7 | 7 | 7 | 3,524 | Redis-backed external/shared agent mailboxes and sessions |
| `cultivar` | 6 | 22 | 6 | 3,021 | repository source/index context; 16 compatibility tools remain hidden |
| `image_gen` | system-owned | system-owned | 1 | 1,993 | raster generation/editing backend |

Evidence: [Haake tool list](../../../haake/src/mcp.rs:282),
[selfimprove registry](../../../selfimprove/_tool_registry.py:52),
[GPTQueue setup](../../../gptqueue/src/transports/setup-tools.ts:24), and
[Cultivar list/dispatch](../../../cultivar/crates/cultivar-mcp/src/main.rs:218).

## Ranked recommendations

Legend: `I` impact, `C` confidence, `R` migration risk, `E` effort. Values are
Critical/High/Medium/Low. The ordering within each group is priority order.

### Remove or merge

| ID | Recommendation | I/C/R/E | Evidence |
|---|---|---|---|
| RM-1 | Upstream: merge `figma-implement-design` into a concise `figma` router plus implementation reference. Both currently encode the same context → metadata fallback → screenshot → assets → translation → parity workflow. | H/H/M/M | [figma:13](~/.codex/skills/figma/SKILL.md:13), [figma-implement-design:22](~/.codex/skills/figma-implement-design/SKILL.md:22) |
| RM-2 | Deprecate Cultivar's hidden `slice` alias in favor of hidden `query.neighborhood`; both call the same renderer. Preserve a compatibility window rather than deleting abruptly. | L/H/M/L | [dispatch](../../../cultivar/crates/cultivar-mcp/src/main.rs:237), [shared implementation](../../../cultivar/crates/cultivar-mcp/src/slice_tool.rs:248) |
| RM-3 | Split `readme-doctor` into a generic README/CLI accuracy workflow and a Haake-specific profile. Do not merge the generic capability away. | H/H/M/M | [project-specific requirements](../../skills/readme-doctor/SKILL.md:20), [workflow](../../skills/readme-doctor/SKILL.md:110) |
| RM-4 | Keep the repository and system `skill-creator` as different ownership surfaces, but make source/deployment resolution explicit so the 86-manifest source audit cannot be misread as 86 loaded skills. Do not edit the system copy locally. | M/H/L/L | [repository skill](../../skills/skill-creator/SKILL.md:11), [system skill](~/.codex/skills/.system/skill-creator/SKILL.md:8) |

### Clarify routing

| ID | Recommendation | I/C/R/E | Evidence |
|---|---|---|---|
| CR-1 | Make `next-todos` read-only by default. Mere presence of `yarli.toml` must not turn a list request into durable enqueueing; require explicit enqueue intent. | H/H/L/L | [trigger](../../skills/next-todos/SKILL.md:20), [hidden enqueue](../../skills/next-todos/SKILL.md:25), [output](../../skills/next-todos/SKILL.md:54) |
| CR-2 | Route `autonomous-execution-contract` to one bounded objective and `autonomy-loop` to multi-task epic selection. Remove overlapping “keep going/continue” ambiguity from frontmatter. | M/H/L/L | [contract](../../skills/autonomous-execution-contract/SKILL.md:11), [loop boundary](../../skills/autonomy-loop/SKILL.md:14) |
| CR-3 | Keep `yarli-introspect` read-only and make `yarli-execution-loop` consume it. Monitoring/supervision must not imply cancellation or relaunch authority. | C/H/M/M | [auto-cancel path](../../skills/yarli-execution-loop/SKILL.md:157), [introspection workflow](../../skills/yarli-introspect/SKILL.md:45) |
| CR-4 | Add one control-plane routing matrix: native collaboration for local in-session work, GPTQueue for external/shared mailboxes, Haake coordination for durable memory-backed work state. | H/H/L/L | [Haake coordination schemas](../../../haake/src/mcp.rs:424), [GPTQueue policy](../../../gptqueue/src/transports/setup-tools.ts:25) |
| CR-5 | Preserve planning layers: `objective-to-dag-decomposition` (hierarchical planning), `next-todos` (short list), `vision-plan-tranche-sync` (artifact sync), and `yarli-tranche-expander` (broad research). Route by output and mutation, not shared vocabulary. | M/H/L/L | [DAG boundary](../../skills/objective-to-dag-decomposition/SKILL.md:23), [sync rules](../../skills/vision-plan-tranche-sync/SKILL.md:96), [expander routing](../../skills/yarli-tranche-expander/SKILL.md:11) |
| CR-6 | Clarify `archdiagram` versus `imagegen`: code-native/deterministic architecture diagrams versus illustrative raster infographics. | M/H/L/L | [archdiagram formats](../../skills/archdiagram/SKILL.md:45), [imagegen negative route](~/.codex/skills/.system/imagegen/SKILL.md:62) |
| CR-7 | Keep system-wide memory audit separate from per-process leak investigation, but tighten frontmatter so OOM/swap symptoms route first by requested scope. | M/H/L/L | [system scope](../../skills/system-memory-audit/SKILL.md:11), [process scope](../../skills/memleak-investigate/SKILL.md:11) |
| CR-8 | Keep live `check-antipatterns` separate from retrospective `analyze-conversation`; this is legitimate temporal layering and should remain explicit. | M/H/L/L | [live trigger](../../skills/check-antipatterns/SKILL.md:3), [retrospective trigger](../../skills/analyze-conversation/SKILL.md:3) |

### Extract shared primitive

| ID | Recommendation | I/C/R/E | Evidence |
|---|---|---|---|
| EP-1 | Extract a history-surgery safety primitive for clean-tree/range selection, external backup, approval, scoped rewrite, verification, origin restoration, and recovery. Keep message rewrite, squash, and reference scrub as distinct user intents. | H/H/M/M | [rewrite safety](../../skills/rewrite-commit-messages/SKILL.md:24), [squash preflight](../../skills/squash-commits/SKILL.md:101), [cleaner state capture](../../skills/reference-cleaner/SKILL.md:28) |
| EP-2 | Extract a `gptengage` execution primitive for availability, safe argument construction, timeout, privacy/cost disclosure, write mode, and result integration. Keep `invokellm`, `debate`, and `ideate` as intent wrappers. | H/H/L/M | [debate workflow](../../skills/debate/SKILL.md:11), [ideate workflow](../../skills/ideate/SKILL.md:11), [invokellm workflow](../../skills/invokellm/SKILL.md:20) |
| EP-3 | Make `handoff` compose `commit`; reconcile canonical docs before the final commit and remove embedded `git add -A`. | C/H/M/M | [handoff commit](../../skills/handoff/SKILL.md:39), [post-commit edits](../../skills/handoff/SKILL.md:45), [commit explicit paths](../../skills/commit/SKILL.md:188) |
| EP-4 | Extract one Yarli inspect primitive and one enqueue/dedupe primitive. Reuse them from execution-loop, next-todos, tranche-expander, and vision sync instead of repeating shell/state policy. | H/H/M/M | [execution inspect](../../skills/yarli-execution-loop/SKILL.md:76), [introspect data](../../skills/yarli-introspect/SKILL.md:32), [expander writing](../../skills/yarli-tranche-expander/SKILL.md:107) |
| EP-5 | Reuse the resolved multi-root skill inventory in selfimprove discovery. Current discovery claims broad tool population but only searches Claude paths and leaves `CODEX_CONFIG` unused. | H/H/M/M | [discovery implementation](../../../selfimprove/_registry_discovery.py:127), [server config](../../../selfimprove/server.py:105) |
| EP-6 | Extract or conditionally expose selfimprove `list_directory` as a generic filesystem primitive; it is not tool-ecosystem domain logic. | M/H/M/M | [list_directory](../../../selfimprove/_registry_discovery.py:256) |

### Reduce prompt or context size

| ID | Recommendation | I/C/R/E | Evidence |
|---|---|---|---|
| PC-1 | After explicit operational authorization, restart/reload the Haake MCP built from current source. The loaded runtime repeats 30,290 ambient-prefix characters; source now opts previews out. Do not rebuild/restart as part of this audit. | C/H/L/L | [source opt-in](../../../haake/src/mcp.rs:89), [initialize](../../../haake/src/mcp.rs:257) |
| PC-2 | Move selfimprove-wide disposition and enum policy to server instructions/schemas. Remove ticket genealogy and long examples from `record_friction`, `friction_clusters`, `query_graph`, and `list_directory`. | M/H/L/M | [record_friction docs](../../../selfimprove/_registry_friction.py:43), [clusters](../../../selfimprove/_registry_friction.py:421), [query_graph](../../../selfimprove/_registry_graph.py:76) |
| PC-3 | Shrink `autonomy-loop` to ranking, chaining, checkpointing, and stop policy; delegate its full executor template to `autonomous-execution-contract`. | M/H/L/M | [composition map](../../skills/autonomy-loop/SKILL.md:136), [duplicated template](../../skills/autonomy-loop/SKILL.md:231) |
| PC-4 | Convert `memleak-investigate`, `squash-commits`, `check-antipatterns`, `postmortem`, and system `imagegen` into concise routers with recipes/examples in references. | H/H/M/M | [419-line leak prompt](../../skills/memleak-investigate/SKILL.md:26), [squash workflow](../../skills/squash-commits/SKILL.md:99), [check examples](../../skills/check-antipatterns/SKILL.md:106), [imagegen](~/.codex/skills/.system/imagegen/SKILL.md:1) |
| PC-5 | Make external multi-sigma ideation optional in `ecosystem-borrow-audit`, require an explicit scope, and compose `ideate` rather than embedding a shell loop. | M/H/L/M | [scope](../../skills/ecosystem-borrow-audit/SKILL.md:11), [loop](../../skills/ecosystem-borrow-audit/SKILL.md:59) |

### Correct safety or dependency metadata

| ID | Recommendation | I/C/R/E | Evidence |
|---|---|---|---|
| SD-1 | Redesign `commit`: remove the global artifact blacklist and automatic writes to global gitignore/index. Repository policy and explicit user approval must govern tracked docs and global state. | C/H/M/M | [blacklist](../../skills/commit/SKILL.md:74), [global/index writes](../../skills/commit/SKILL.md:150) |
| SD-2 | Require approval/dry-run before Yarli cancellation/relaunch. A supervise or monitor request does not authorize destructive run repair. | C/H/M/L | [continuation routing](../../skills/yarli-execution-loop/SKILL.md:63), [intervention](../../skills/yarli-execution-loop/SKILL.md:189) |
| SD-3 | Make `pr-lifecycle` obey global push approval and ask before SemVer decisions. Explicit skill invocation cannot override repository/global release policy. | C/H/L/L | [claimed approval](../../skills/pr-lifecycle/SKILL.md:13), [version choice](../../skills/pr-lifecycle/SKILL.md:86), [push](../../skills/pr-lifecycle/SKILL.md:116) |
| SD-4 | Replace `speak`'s interpolated `python3 -c` command with a bundled helper receiving text via a non-code channel; disclose audio/Kokoro dependencies and secret/code-content negative triggers. | H/H/L/L | [unsafe interpolation](../../skills/speak/SKILL.md:11) |
| SD-5 | Correct selfimprove effects: `prune_friction` is destructive; `discover_tools` is both privileged and writable. Replace one-dimensional tags with permission/effect/idempotency axes. | H/H/L/M | [hard delete](../../../selfimprove/_registry_friction.py:398), [discovery writes](../../../selfimprove/_registry_discovery.py:127) |
| SD-6 | Add bound confirmation and recovery semantics to Haake `forget_all`, `delete_memory`, and `restore_scope`. Empty arguments are inadequate for irreversible scope deletion. | H/H/M/M | [forget schema](../../../haake/src/mcp.rs:372), [restore schema](../../../haake/src/mcp.rs:709) |
| SD-7 | Fix Haake schema/handler drift: persist or remove `importance`; align `update_memory`'s “and/or” promise with its required content; advertise accepted query fields. | H/H/M/M | [importance schema](../../../haake/src/mcp.rs:300), [store handler](../../../haake/src/mcp.rs:844), [update schema](../../../haake/src/mcp.rs:632), [query handler](../../../haake/src/mcp.rs:939) |
| SD-8 | Upstream: remove automatic Figma MCP add/feature enable/login and token echo/persistence instructions. Setup requires approval and secret-safe verification. | C/H/L/L | [activation](~/.codex/skills/figma-implement-design/SKILL.md:26), [token handling](~/.codex/skills/figma/references/figma-mcp-config.md:18) |
| SD-9 | Make `git-status-report` fetch opt-in; without fetch it is read-only and may report cached remote-tracking state explicitly. | H/H/L/L | [fetch](../../skills/git-status-report/SKILL.md:58), [implementation note](../../skills/git-status-report/SKILL.md:138) |
| SD-10 | Redesign `install-commithooks` around ownership checks, backup/rollback, and approval before deleting `.git/lib`, unsetting `core.hooksPath`, or changing setup/build files. | H/H/M/H | [library deletion](../../skills/install-commithooks/SKILL.md:68), [config](../../skills/install-commithooks/SKILL.md:77), [setup changes](../../skills/install-commithooks/SKILL.md:147) |
| SD-11 | Make `yarli-repo-init` preview and back up before `--force`, ignore/untrack changes, or smoke-run writes. Align backend arguments with actual Gemini support. | H/H/M/M | [force](../../skills/yarli-repo-init/SKILL.md:40), [ignore mutation](../../skills/yarli-repo-init/SKILL.md:76), [smoke run](../../skills/yarli-repo-init/SKILL.md:135) |
| SD-12 | Reframe `privateify` as best-effort defense in depth, not an irrevocable guarantee. Its pre-push check fails open; CI detects after the fact; agent instruction files cannot override later explicit authority. | H/H/M/M | [fail-open hook](../../skills/privateify/SKILL.md:80), [agent policy writes](../../skills/privateify/SKILL.md:133) |
| SD-13 | Correct `pythonpackagesevere`'s effect boundary: Phase 0 writes reports, Phase 4 creates environments/installs packages, and those dependency installs need approval. | H/H/L/M | [setup/report writes](../../skills/pythonpackagesevere/SKILL.md:11), [environment/install](../../skills/pythonpackagesevere/SKILL.md:244) |
| SD-14 | Make PDF conversion atomic and check `pdfinfo`; never delete the last good output before conversion succeeds. | H/H/L/L | [pre-delete](../../skills/markdown-to-pdf/SKILL.md:26), [verification](../../skills/markdown-to-pdf/SKILL.md:34) |

### Improve failure recovery and verification

| ID | Recommendation | I/C/R/E | Evidence |
|---|---|---|---|
| FV-1 | Correct `memleak-investigate` before use as diagnostic authority: high-water RSS is not proof of a leak, `/proc/PID/net/sockstat` is namespace-wide, and the BPF allocation arithmetic is concurrency/instrumentation unsafe. Add permission, exited-process, container, allocator, and missing-tool recovery. | H/H/L/M | [high-water claim](../../skills/memleak-investigate/SKILL.md:58), [sockstat](../../skills/memleak-investigate/SKILL.md:187), [BPF logic](../../skills/memleak-investigate/SKILL.md:249) |
| FV-2 | Correct `system-memory-audit`: sort actual RSS, inspect all PIDs or disclose sampling, and condition tunables on RAM/kernel/workload. Keep privileged apply/persistence separate from read-only audit. | H/H/L/M | [consumer commands](../../skills/system-memory-audit/SKILL.md:72), [tunables](../../skills/system-memory-audit/SKILL.md:49), [apply script](../../skills/system-memory-audit/SKILL.md:105) |
| FV-3 | Fix `analyze-conversation` and `check-antipatterns` documentation to match real scripts, paths, required inputs, and output filenames; add missing/unreadable transcript recovery. | H/H/L/M | [stale analyzer path](../../skills/analyze-conversation/SKILL.md:138), [actual output](../../skills/analyze-conversation/generate_report.py:680), [stale checker implementation](../../skills/check-antipatterns/SKILL.md:156), [required input](../../skills/check-antipatterns/checker.py:441) |
| FV-4 | Fix `yore-vocabulary-llm-filter`: send the full promised schema prompt, honor `--scope`/`--dry-run`, validate JSON, expose backend choice, and gate repository/global writes on review. | H/H/L/M | [schema prompt](../../skills/yore-vocabulary-llm-filter/SKILL.md:33), [broken invocation](../../skills/yore-vocabulary-llm-filter/SKILL.md:87), [writes/review](../../skills/yore-vocabulary-llm-filter/SKILL.md:97) |
| FV-5 | Make `test` degrade gracefully when Overwatch is missing/unhealthy or has PATH mismatch; document exit/result semantics and avoid fragile cancel-on-output defaults. | H/H/L/M | [cancel patterns](../../skills/test/SKILL.md:40), [prerequisite](../../skills/test/SKILL.md:80) |
| FV-6 | Add structured content/output schemas and stable errors to Haake, GPTQueue, and selfimprove. Preserve text for compatibility. Cultivar's `structuredContent` and error data are the local positive pattern. | H/H/M/H | [Haake text envelope](../../../haake/src/mcp.rs:780), [selfimprove Result conversion](../../../selfimprove/server.py:486), [Cultivar envelope](../../../cultivar/crates/cultivar-mcp/src/main.rs:187) |
| FV-7 | Repair Cultivar schema generation: avoid `anyOf` degradation for `query.resolve`, and add required/one-of routing for preview/expand. Split single/batch resolve if necessary. | H/H/M/M | [resolve schema](../../../cultivar/crates/cultivar-mcp/src/main.rs:252), [preview/expand schemas](../../../cultivar/crates/cultivar-mcp/src/main.rs:284) |
| FV-8 | Add cursor/nextCursor pagination and stable ordering to selfimprove lists, Haake list/search resources, and any capped retrieval surface. | M/H/M/M | [selfimprove graph lists](../../../selfimprove/_registry_graph.py:76), [Haake capped list](../../../haake/src/mcp.rs:1398), [resource paging](../../../haake/src/mcp.rs:2089) |
| FV-9 | Add GPTQueue timeout bounds, caller idempotency keys, registration non-idempotency disclosure, and stable Redis/session unavailable errors. | M/H/M/M | [timeout](../../../gptqueue/src/mcp-server/tools/receive-message.ts:5), [message UUID](../../../gptqueue/src/mcp-server/tools/send-message.ts:7), [registration](../../../gptqueue/src/mcp-server/redis-client.ts:80) |
| FV-10 | Centralize Cultivar's registry so list, dispatch, docs, and deprecation state agree. Current docs say four advertised tools while source/runtime expose six and dispatch 22. | M/H/L/M | [docs](../../../cultivar/docs/mcp-integration-contract.md:10), [list](../../../cultivar/crates/cultivar-mcp/src/main.rs:248) |
| FV-11 | Add real smoke verification and rollback to `install-commithooks`; listing copied files is not evidence that dispatch or setup wiring works. | H/H/M/M | [current verify](../../skills/install-commithooks/SKILL.md:223) |
| FV-12 | Make `postmortem` permit explicit unknowns and evidence confidence. A rigid five-link chain plus mandatory-looking metrics/owners encourages invented causality. | M/H/L/M | [five-whys template](../../skills/postmortem/SKILL.md:55), [evidence process](../../skills/postmortem/SKILL.md:125) |

### Keep separate with justification

| Surfaces | Justification |
|---|---|
| `analyze-conversation` / `check-antipatterns` | Retrospective report versus live course correction. |
| `system-memory-audit` / `memleak-investigate` | System/kernel snapshot versus per-process longitudinal/tracing investigation. |
| `objective-to-dag-decomposition` / `next-todos` / `vision-plan-tranche-sync` / `yarli-tranche-expander` | Hierarchical plan, concise list, artifact synchronization, and broad research/backlog expansion. Share enqueue only. |
| `reference-cleaner` / `rewrite-commit-messages` / `squash-commits` | Content/path scrub, message-only rewrite, and topology rewrite. Share safety substrate only. |
| `yore-vocabulary-harvest` / `yore-vocabulary-llm-filter` | Deterministic candidate extraction versus heuristic, human-gated semantic curation. |
| `yarli-introspect` / `yarli-execution-loop` | Read-only diagnostics versus mutating supervisor. Current prompts blur but do not erase the distinction. |
| Haake `query_memories` / `assemble_context` / `list_memories` | Search primitive, context composer, chronological browse. |
| Cultivar `query.resolve` / `context.preview` / `context.expand` | Symbol primitive, compact context composer, explicit progressive expansion. |
| selfimprove `find_similar_frictions` / promotion enqueue tools | Read-only retrieval, writable primitive, convenience composer. |
| GPTQueue `close_session` / `unregister_agent` | Mailbox-preserving lifecycle close versus destructive deletion. |

### Upstream or system-owned findings

Do not patch these in `rahulskills`:

| ID | Recommendation | I/C/R/E |
|---|---|---|
| UP-1 | Merge the Figma prompts and remove automatic activation/token exposure. | C/H/M/M |
| UP-2 | Reduce `imagegen` default context and resolve its post-generation output-contract conflict. | H/H/L/M |
| UP-3 | Keep system `skill-creator` authoritative; add plugin precedence, correct frontmatter rules, and extract examples/references. | M/H/L/M |
| UP-4 | Make `openai-docs` fallback-capable without auto-install/escalation and deduplicate fallback policy. | C/H/L/M |
| UP-5 | Gate `plugin-creator` external/marketplace/reinstall writes and resolve its `hooks` schema contradiction. | H/H/M/M |
| UP-6 | Add provenance approval, pinning, validation, rollback/removal, and system-skill protection to `skill-installer`. | C/H/L/M |
| UP-7 | Reload stale Haake/GPTQueue/Cultivar runtime metadata only after explicit lifecycle authorization. | C/H/L/L |

- Merge the overlapping system Figma prompts and remove unauthorized activation
  and unsafe token-verification instructions (RM-1, SD-8).
- Reduce system `imagegen` default context and resolve its instruction to report
  after generation against the runtime tool contract that forbids post-generation
  text: [imagegen:117](~/.codex/skills/.system/imagegen/SKILL.md:117).
- Keep Codex's system `skill-creator` authoritative. The short repository copy is
  a cross-runtime source artifact, not the loaded Codex skill.
- `openai-docs` is fallback-capable, not truly dormant: it has a local manual
  helper and official-domain web fallback. Remove its automatic MCP-install and
  escalation path, which violates the workspace approval policy:
  [openai-docs:41](~/.codex/skills/.system/openai-docs/SKILL.md:41),
  [openai-docs:112](~/.codex/skills/.system/openai-docs/SKILL.md:112).
- `plugin-creator` is a legitimate plugin composer, but its default external
  paths, marketplace writes, cachebuster/reinstall flow, and `codex plugin add`
  need explicit approval. Resolve its contradictory top-level `hooks` rules and
  move duplicated marketplace/spec material to references:
  [plugin-creator:71](~/.codex/skills/.system/plugin-creator/SKILL.md:71),
  [plugin-creator:183](~/.codex/skills/.system/plugin-creator/SKILL.md:183).
- Shrink system `skill-creator` and route plugin bundles to `plugin-creator`.
  Its 416-line prompt contradicts its own concision principle and its claim that
  frontmatter may contain only `name` and `description` conflicts with its own
  metadata: [skill-creator:26](~/.codex/skills/.system/skill-creator/SKILL.md:26),
  [skill-creator:342](~/.codex/skills/.system/skill-creator/SKILL.md:342).
- Keep `skill-installer` distinct, but require exact-source/provenance approval,
  ref pinning, manifest review, validation, transactional cleanup, and removal
  guidance. Do not allow local overwrite of system skills:
  [skill-installer:8](~/.codex/skills/.system/skill-installer/SKILL.md:8),
  [skill-installer:43](~/.codex/skills/.system/skill-installer/SKILL.md:43).
- The stale loaded MCP metadata is an operational/runtime finding. Source changes
  exist, but rebuilding or restarting remains explicitly out of scope.

## Per-skill prompt-quality matrix

Score is 1–5. It summarizes current prompt safety, correctness, routing,
recovery, verification, portability, and token value; it is not a capability
importance score.

| Skill | Score | Disposition and main quality flags |
|---|---:|---|
| analyze-conversation | 3.5 | Keep retrospective workflow; stale paths/output, missing transcript recovery, oversized example. |
| archdiagram | 4.0 | Keep; precise output routing. Add diagram syntax validation and raster boundary. |
| autonomous-execution-contract | 4.0 | Keep bounded executor; strong stop/verification contract, clarify precedence. |
| autonomy-loop | 3.0 | Keep epic composer; remove executor duplication and overlapping trigger language. |
| check-antipatterns | 2.5 | Keep live checker; implementation tree/config claims are stale and invocation is incomplete. |
| commit | 2.0 | Redesign safety policy; global ignore/index mutation and universal artifact blacklist are unsafe. |
| debate | 3.0 | Keep intent wrapper; share backend primitive and disclose cost/privacy/write semantics. |
| ecosystem-borrow-audit | 2.5 | Keep composer; explicit scope, optional external ideation, no embedded backend loop. |
| figma | 3.5 | Prefer as sole Figma router; setup reference violates approval/secret hygiene. Upstream-owned. |
| figma-implement-design | 2.0 | Merge upstream into `figma`; duplicated workflow and unauthorized activation. |
| fp-refine | 4.5 | Keep; excellent compact router, progressive disclosure, behavior preservation, verification. |
| git-status-report | 2.5 | Keep with opt-in fetch; current read-only metadata is false. |
| handoff | 1.5 | Keep workflow name; compose commit and fix post-commit doc edits/dirty final state. |
| ideate | 3.0 | Keep intent wrapper; shared external backend primitive and disclosure needed. |
| imagegen | 3.0 | Keep system-owned raster capability; strong routing, excessive context, runtime-contract conflict. |
| install-commithooks | 1.5 | Major reversibility/ownership rewrite and smoke verification required. |
| invokellm | 3.5 | Keep general primitive; disclose default three-call cost and context/session persistence. |
| markdown-to-pdf | 2.5 | Keep; atomic output, complete dependency checks, conversion recovery. |
| max-columns | 3.5 | Keep; high token value. Clarify invocation without width and duration of constraint. |
| memleak-investigate | 2.0 | Keep specialist only after technical correction, recovery paths, and recipe extraction. |
| next-todos | 2.0 | Keep concise list primitive; remove hidden enqueue/write behavior. |
| objective-to-dag-decomposition | 4.5 | Keep planning primitive; strong taxonomy/verification; compact mode controls bulk. |
| openai-docs | 3.0 | Keep system-owned; strong source routing, but auto-install/escalation violates approval and repeated fallback text is costly. |
| plugin-creator | 2.5 | Keep system composer; gate external/marketplace/reinstall writes, resolve `hooks` contradiction, shrink duplicated spec. |
| postmortem | 3.0 | Keep incident RCA; support unknown/confidence, reduce rigid template/project examples. |
| pr-lifecycle | 2.5 | Keep composer after push/version approval fixes; do not squash every PR by default. |
| privateify | 2.0 | Keep unique defense intent; correct unenforceable guarantees and policy overreach. |
| pythonpackagesevere | 3.0 | Keep specialist workflow; correct effect/install boundaries and layout assumptions. |
| readme-doctor | 2.0 | Split generic workflow from Haake profile; clarify audit versus mutate mode. |
| reference-cleaner | 2.5 | Keep distinct destructive intent; shared rewrite safety, escaping, scope, recovery. |
| repo-topics | 3.5 | Keep; disambiguate GitHub topics from issue labels, add auth/rate-limit/final reread. |
| rewrite-commit-messages | 3.0 | Keep message-only intent; fix filter-repo scope/newline/origin/backup semantics. |
| skill-creator | 3.5 | Keep loaded system authority; add plugin precedence, correct frontmatter claims, shrink examples, strengthen semantic validation/output. |
| skill-installer | 2.0 | Keep install backend; critical provenance/approval, pinning, rollback, validation, removal, and system-overwrite gaps. |
| speak | 1.5 | Keep backend skill after eliminating code interpolation and adding dependency/recovery rules. |
| squash-commits | 2.0 | Keep topology intent; drastically shrink and fix temp paths, injection, config cleanup, attribution. |
| system-memory-audit | 2.0 | Keep system scope; measurements/tunables and privileged boundary need correction. |
| test | 2.5 | Keep backend or shared test primitive; add Overwatch health/PATH fallback and result contract. |
| tui-web-design-orchestrator | 2.5 | Keep generator; fix nonexistent `~/.claude` path and unquoted arguments. |
| vision-plan-tranche-sync | 3.5 | Keep artifact sync; remove stale agent routing and improve title-only dedupe recovery. |
| yarli-execution-loop | 2.0 | Keep mutating composer after approval boundary and introspection extraction. |
| yarli-introspect | 3.5 | Keep read-only diagnostic; clarify `.yarli`/`.yarl`, PID matching, heuristic confidence. |
| yarli-repo-init | 2.5 | Keep setup workflow; preview/backup before force/config/repo-state changes. |
| yarli-tranche-expander | 3.5 | Keep broad research composer; move global Hulista assumptions to conditional profile. |
| yore-vocabulary-harvest | 3.0 | Keep deterministic primitive; honor args, avoid fixed `/tmp`, disclose build/index writes. |
| yore-vocabulary-llm-filter | 2.0 | Keep human-gated filter after fixing broken prompt, args, validation, and scope writes. |

## MCP prompt/schema matrix

| Surface | Strengths | Material deficiencies | Disposition |
|---|---|---|---|
| Haake initialize/runtime | Current source uses concise instructions and opt-in ambient previews. | Loaded runtime is stale and repeats 30,290 chars; source safety tags are absent at runtime. | Keep server; operationally reload only with authorization. |
| Haake memory CRUD/search | Retrieval modes are legitimately distinct. | `importance` no-op, schema/handler drift, destructive tools lack bound confirmation, numeric/time constraints weak, text-only results, capped lists. | Correct schemas/effects/recovery; do not merge retrieval modes. |
| Haake coordination | Durable channels/items/checkpoints are coherent. | Boundary against native collaboration/GPTQueue is absent; single safety axis hides telemetry writes. | Keep as durable coordination; add global routing/effect axes. |
| selfimprove initialize/tools | Domain is coherent and runtime safety tags are visible. | Bare initialize; disposition repeated per tool; destructive/privileged effects misclassified; string enums; success-shaped errors; partial discovery and no cursors. | Keep governance plane; shrink and type schemas; share inventory primitive. |
| GPTQueue initialize/tools | Seven-tool lifecycle is small; close versus unregister is meaningful. | Loaded safety text stale; policy repeated per tool; timeout/idempotency/error contracts incomplete; text-only JSON. | Keep external/shared plane; move policy server-level and harden contracts. |
| Cultivar initialize/tools | Compact six-tool progressive context surface; structured results/errors are strongest of four. | Runtime safety tags stale; `anyOf` client degradation; missing required routes; 16 hidden callable tools and docs/list drift. | Keep six advertised tools; centralize registry and deprecate exact alias. |
| image_gen | Clear bitmap backend role. | System-owned; not sourced in the five repositories. | Keep separate; report upstream prompt conflict only. |

## Catalog metadata corrections implied by evidence

The current `capabilities/skills.toml` is useful but not yet truthful enough:

- `next-todos` is not read-only while it auto-enqueues.
- `git-status-report` performs network access and updates remote-tracking refs.
- `handoff`/`commit` can mutate more state than `local-write` suggests, including
  global Git configuration/index state in `commit`.
- `yarli-execution-loop` can cross from write to destructive cancellation.
- `pythonpackagesevere` can install dependencies.
- selfimprove needs multi-axis MCP effects; `prune_friction` is destructive and
  `discover_tools` is privileged plus writable.
- Runtime safety metadata for Haake, GPTQueue, and Cultivar does not match source
  until an authorized lifecycle operation reloads it.

## Verification and boundaries

This was a source/runtime metadata review, not a modification wave. The existing
catalog and capability-health commands completed successfully. All five starting
HEADs were verified. The explicit-root catalog result and SHA comparisons were
recomputed independently. Runtime namespace counts and description sizes came
from the currently exposed tool registry. No release binaries were rebuilt, no
servers restarted, no old MCP processes pruned, no dependency installed, no
branch pushed, and the Cultivar stash was untouched.

The existing friction `f-1634` already names the core tooling gap encountered
here: there is no first-class resolved source/deployment skill and MCP audit.
This review did not create a duplicate friction record. The source/runtime drift
and lifecycle visibility findings also corroborate existing `f-1636`; Overwatch
recovery findings corroborate `f-1635`.
