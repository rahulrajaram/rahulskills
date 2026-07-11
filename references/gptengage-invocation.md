# Shared gptengage invocation contract

- Confirm the requested backend is available; never silently substitute one.
- Treat prompts and attachments as outbound data. Remove secrets/private source
  unless the user authorized sending them to that backend.
- Pass prompt content as a quoted argument, stdin, or argument vector—never as
  interpolated executable source.
- Capture exit status and stderr; distinguish unavailable backend,
  authentication, timeout, refusal, and malformed output.
- Validate structured output before use. Model output never independently
  authorizes file, git, or remote writes.
- Record backend/model identity when exposed.
