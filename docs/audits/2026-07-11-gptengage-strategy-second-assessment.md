# GPTEngage strategy second assessment and source-only plan

Date: 2026-07-11

Scope: independently reassess the three GPTEngage-facing skills against a
single router and an MCP, verify Codex invocation compatibility and MCP tool
loading, and prepare a compatibility-preserving source-only implementation
plan. This assessment made no GPTEngage model call, skill deployment, MCP
configuration change, service restart, backup change, or remote write.

## Revised decision

Keep `invokellm`, `debate`, and `ideate` as three concise intent manifests with
shared common policy and progressively loaded per-operation references.

The recommendation survives, but one premise of the first assessment does not.
Codex CLI 0.144.1 deferred the configured MCP operation schemas behind
`tool_search`; it did **not** inject every Haake, selfimprove, GPTQueue, and
Cultivar schema into the captured model request. An MCP is therefore
context-competitive in this runtime. It still loses for this migration because
it would replace three established explicit skill names with a service that
needs a new lifecycle, structured error and safety contracts, deployment, and
configuration. Those costs do not buy a needed capability over the existing
local CLI.

Do not use the first report's eager-schema measurement as a reason to reject an
MCP. Treat the MCP as a future architecture option, not the current migration
target.

## Independent evidence

### Explicit skill invocation and aliases

Current OpenAI documentation says Codex explicitly invokes skills with
`$skill`, or through the `/skills` picker. It does not document arbitrary
`/<skill>` aliases. OpenAI Codex issue 11817 records `/<skill>` as unrecognized
while `$<skill>` works; the request was closed as not planned.

Consequences:

- A single `gptengage` manifest cannot preserve explicit `$invokellm`,
  `$debate`, and `$ideate` invocation. A skill has one required `name`; no skill
  alias field is documented.
- The three current directory/frontmatter names are compatibility surfaces even
  though their bodies share a backend.
- Retain the existing `/invokellm`, `/debate`, and `/ideate` wording for clients
  that support it, but add the documented Codex `$...` spelling. Do not claim
  that a bare Codex `/<skill>` command is supported.
- `argument-hint` is useful UI metadata but does not create aliases.

Sources:

- <https://developers.openai.com/codex/skills>
- <https://github.com/openai/codex/issues/11817>

### Bounded MCP request capture

The installed client was `codex-cli 0.144.1`. A local loopback HTTP stub was
used as an ephemeral Responses provider while the normal configured MCP set was
initialized. `codex exec --ephemeral`, read-only sandboxing, and approval
policy `never` ensured no model provider or GPTEngage backend was contacted.
The stub returned an error after recording the request, so no model response or
tool execution occurred.

The captured request contained 11 model-visible tools:

- nine direct built-in/client tools;
- one `tool_search` tool; and
- one web-search tool.

No configured MCP operation appeared as a direct function schema. The
`tool_search` description was 1,511 characters and named the available sources
with short server-wide guidance. Its parameters were only `query` and optional
`limit`. The client-side deferred inventory remained searchable, but the full
MCP schemas were absent from the initial model request.

This aligns with the installed feature report and current OpenAI Codex source:
tool search is active, and the compatibility flag named `tool_search` no longer
means that all tools are directly injected. It also explains why runtime tool
metadata can be discoverable to the client without being eagerly sent to the
model.

Limits:

- This verifies Codex CLI 0.144.1 with the current model/provider feature
  selection. It is not a claim about every Codex surface or older client.
- The capture reused the configured MCP set but did not add a GPTEngage MCP.
  A future server would add client-side index metadata and a short source entry;
  selected tool schemas would load after search.
- Server initialization and `tools/list` discovery may still be eager at the
  **client/server protocol** layer. That is distinct from eager model-context
  injection. The first report combined those two questions.

Sources:

- <https://github.com/openai/codex/blob/main/codex-rs/features/src/lib.rs>
- <https://developers.openai.com/codex/mcp>

### GPTEngage contract check

Local `gptengage` 1.1.2 help confirms that the operations remain semantically
different:

- `invoke` selects one CLI per command and supports model, session, topic,
  context file, images, stdin policy, timeout, and explicit write access. The
  skill's default three-way consultation is wrapper behavior, not one CLI
  invocation.
- `debate` owns participants or agent instances, rounds, templates, output,
  synthesis, and a per-invocation timeout. Synthesis is another backend call.
- `ideate` owns sigma, ternary-tree depth, selection, output, and `--force` for
  limits above sigma 3 or depth 5. Its current skill prompt is stale because it
  describes only depth 1-2 and omits `--force`.

`gptengage status` was local-only and reported Claude, Codex, Gemini, and the
Ollama plugin available. No backend invocation was made.

## Option comparison

| Option | Compatibility | Initial model context in Codex 0.144.1 | Engineering/effect cost | Disposition |
|---|---|---|---|---|
| Current three full wrappers | Preserves all names and intent triggers | Three descriptions in the progressive skill list; one full body after selection | Repeated option tables and policy drift | Replace bodies, not surfaces. |
| Three concise manifests plus references | Preserves exact names and argument hints | Short descriptions; only selected common/operation text loads | Small source-only change; no new runtime | **Choose.** |
| One `gptengage` skill | Loses three explicit `$name` entry points unless forwarding manifests remain | One description and selected router body | Adds dispatch ambiguity; forwarding manifests recreate three surfaces | Reject for compatibility, not token cost. |
| GPTEngage MCP | Loses explicit skill names unless manifests remain; tool search can discover operations | Full operation schemas are deferred in the verified CLI; one shared tool-search/source summary is eager | New service, config, lifecycle, typed safety/error contract, deployment, and rollback | Defer until service value justifies migration. |

The MCP may become preferable if GPTEngage gains a stable structured API used
by several clients, needs centralized policy enforcement, or benefits from
long-lived service state. Before reconsideration, measure a real candidate MCP
request and validate typed errors, outbound-data disclosure, write semantics,
call/cost estimates, cancellation, and session persistence.

## Compatibility-preserving source-only implementation plan

This plan deliberately excludes `ecosystem-borrow-audit`; changing its
automatic multi-sigma calls requires separate approval.

1. Expand `references/gptengage-invocation.md` into a concise common contract.
   Keep backend availability, outbound-data screening, argument-vector command
   construction, result validation, error classes, model/backend identity,
   session persistence, write authority, and inner-versus-outer timeout rules.
2. Add three operation references:
   `references/gptengage-invoke.md`, `references/gptengage-debate.md`, and
   `references/gptengage-ideate.md`. Each owns only its command syntax, valid
   option combinations, cost/call shape, operation-specific failures, and one
   minimal example.
3. Reduce each `skills/{invokellm,debate,ideate}/SKILL.md` to:
   intent/output boundary, the unchanged frontmatter `name` and
   `argument-hint`, both `$name` and existing `/name` discovery wording, the
   common contract link, the selected operation link, and a short workflow.
   Keep `invokellm`'s default ordered trio and 600-second inner timeout as
   explicit wrapper behavior.
4. Correct existing drift while preserving behavior. In particular, document
   `ideate` depth 1-5 and `--force`, distinguish debate's per-invocation timeout
   from any outer watchdog, and do not tell callers to pass unvalidated user
   arguments “directly” through a shell.
5. Add the three references to the source assembly/install inventory and its
   parity tests. Do not deploy them in this source-only tranche.
6. Add static contract tests that assert exact skill names and argument hints,
   required reference existence, preserved invocation defaults, documented
   write/session/outbound boundaries, and absence of duplicated option tables.
7. Run the catalog audit and all packaging/reference tests. Use
   `codex debug prompt-input` to verify the three names and concise
   descriptions are present in a fresh read-only prompt. Treat implicit
   selection quality and a successful backend smoke call as separate,
   approval-gated verification.

Suggested acceptance thresholds:

- all three exact names and argument hints remain unchanged;
- no GPTEngage backend call occurs in source-only tests;
- each manifest is at most 60 lines and contains no full option table;
- common policy exists in one authoritative reference;
- each operation reference can be loaded independently;
- catalog, packaging, reference-closure, and byte-parity tests pass; and
- no MCP, installed skill, retained rollback backup, or GPTEngage repository is
  modified.

## Approval boundaries retained

Ask before any GPTEngage model invocation, change to automatic ideation,
deployment/install, MCP addition or configuration, service restart, rollback
backup change, dependency change, branch push, or upstream issue/PR write.
