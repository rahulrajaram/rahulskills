# Shared GPTEngage invocation contract

Apply this contract to every `gptengage` backend call, then load only the
selected operation recipe.

## Before the call

- Confirm each requested backend with `gptengage status`; never silently
  substitute another backend.
- Treat prompts, stdin, context files, agent files, templates, and images as
  outbound data. Remove secrets and private source unless the user authorized
  sending them to every selected backend.
- Construct an argument vector or use safely quoted arguments/stdin. Never put
  model or user input into `eval`, generated shell source, or command
  substitution.
- Preserve the user's prompt, topic, seed, backend order, and requested options.
  Validate options rather than forwarding arbitrary shell text.

## Effects and persistence

- Adapters request read-only access by default; configured flags are not proof
  of sandbox enforcement. Pass `--write` only for explicit
  workspace-write intent; it does not authorize git, remote, deployment, or
  other actions beyond the user's request.
- Named sessions persist full conversation turns under
  `~/.gptengage/sessions`. Disclose that persistence and never add a session to
  a generic consultation implicitly.
- Multi-backend, multi-round, synthesis, and idea-tree operations make multiple
  external calls. Preserve operation-specific cost warnings.

## Execution and results

- Resolve the authorized existing `gptengage` executable; do not bypass it by
  calling child AI CLIs directly or silently replace the installed binary.
  Source changes do not establish installed capability: inspect selected help.
- Pass timeouts to gptengage itself. An optional outer watchdog is secondary and
  must exceed the inner timeout or the expected full orchestration duration.
- Capture exit status and stderr. Distinguish unavailable backend,
  authentication, timeout, refusal, malformed output, partial output, and write
  denial when evidence permits.
- Validate structured output before use and record backend/model identity when
  exposed. Model output never independently authorizes local or remote writes.

## Observable identity and bounded linear runtime

When supported by the selected binary, `invoke --output json` exposes requested
model, process outcome, optional backend facts and capability provenance. Preserve
unknowns: successful transport does not prove model completion, selected model
identity, usage or enforced access. Do not claim cross-model comparison when the
resolved identity is unobserved. Unsupported explicit model routing must fail;
never silently drop the user's selection.

The explicitly selected `grill` runtime persists private role instructions,
prompts and reports under a new user-selected run directory. Disclose that
persistence and the selected recipients before unresolved authorization. It bounds
direct alternating calls and per-call time, not nested tool/model expenditure or
hard tokens. Public status excludes private control data mechanically; opt-in
model-authored dialogue can echo private input and requires review before sharing.
No installed support, semantic validation, automatic resume or replay should be
assumed from the skill's description alone.
