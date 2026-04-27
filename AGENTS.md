# Agent Instructions

## Selfimprove

This repository uses the global `selfimprovemeta` MCP. While working here,
record concrete tool friction with `record_friction` as it happens. Include
`caller_agent`, `project_slug = "rahulskills"`, and a run/session id when one
is available.

When creating or updating skills that invoke other agents or CLIs, preserve
`SELFIMPROVE_*` environment variables and set sensible defaults for wrapped
agent calls.

If the MCP is unavailable, append the same record shape to
`~/.selfimprovemeta/friction.md`.
