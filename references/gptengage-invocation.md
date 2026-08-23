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

- Backend processes are read-only by default. Pass `--write` only for explicit
  workspace-write intent; it does not authorize git, remote, deployment, or
  other actions beyond the user's request.
- Named sessions persist full conversation turns under
  `~/.gptengage/sessions`. Disclose that persistence and never add a session to
  a generic consultation implicitly.
- Multi-backend, multi-round, synthesis, and idea-tree operations make multiple
  external calls. Preserve operation-specific cost warnings.

## Execution and results

- Use `~/.local/bin/gptengage`; do not bypass it by calling child AI CLIs
  directly.
- Pass timeouts to gptengage itself. An optional outer watchdog is secondary and
  must exceed the inner timeout or the expected full orchestration duration.
- Capture exit status and stderr. Distinguish unavailable backend,
  authentication, timeout, refusal, malformed output, partial output, and write
  denial when evidence permits.
- Validate structured output before use and record backend/model identity when
  exposed. Model output never independently authorizes local or remote writes.
