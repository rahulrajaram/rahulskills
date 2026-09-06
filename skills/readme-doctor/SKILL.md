---
name: readme-doctor
description: "Correct or audit README and CLI help against actual project behavior. Use for narrow documentation/help fixes or an explicitly requested full documentation audit; preserve the requested scope."
argument-hint: "[section, command, or full audit]"
---

# README Doctor

## Intent and applicability

Make the selected documentation accurate and understandable. A request to fix one
README section or command's help selects that scope. A full audit or rebuild
selects broader discovery; a bare invocation uses the current task/diff to choose
a useful bounded scope, or asks if materially different outcomes remain plausible.

## Inputs and local bindings

Read the existing document and relevant code before editing. Identify the actual
language, CLI framework, build/run command, configuration sources and audience.
Use an existing binary or the project's supported local invocation. Rust/clap,
Axum, protobuf, MCP and Haake-specific files matter only when present and relevant.
A project can intentionally use different domain terms for distinct concepts;
map their meaning before standardizing wording.

## Non-goals

A narrow correction does not select a full README, all-command audit, API redesign,
new feature, tool installation or release. Requested supporting source/help edits
remain in scope when they preserve behavior. A full README needs only the sections
that serve this project and reader, not every possible interface.

## Must not

Do not invent features, usage results, configuration names or guarantees. Do not
rename flags, change defaults or public API merely to make help text uniform.
Do not claim execution validation from source inspection alone. Preserve user
structure/wording requirements and unrelated documentation.

## Interaction and authority

A request to fix documentation authorizes relevant local edits without first-use
confirmation. Resolve ordinary wording/format choices autonomously. Prepare and
ask about an unresolved behavior/API or scope change; continue independent
corrections. Reuse a parent's selected scope and still-valid decisions.

## Procedure

### Select and gather

For a narrow fix, inspect the relevant section/command and neighboring context.
For a full audit, enumerate public commands and supported interfaces, then inspect
their help, source and configuration definitions. Avoid starting services or
executing side-effecting examples just to document them. Use safe help commands
and available source evidence; identify blocked runtime checks explicitly.

### Correct help and documentation together

Compare exact flag names, accepted values, required inputs, defaults and examples
with behavior. Verify changed CLI examples against the actual relevant `--help`
and implementation. Framework-specific checks apply only to that framework:
clap attributes for clap, routers for the detected web framework, proto schemas
for gRPC, actual tool definitions for MCP, actual reads for environment variables.

Align terms for the same concept; retain justified distinctions and compatibility
aliases. Missing descriptions, misleading defaults, conflicting flags and obsolete
features are findings. A hidden compatibility command is not necessarily missing
documentation, and a repeated version/help flag is not inherently a defect.

For full README work, adapt sections to the project: purpose/audience, supported
features, installation, quick start, usage/configuration, examples, security,
architecture and license where useful. Link a large CLI/API reference rather than
pasting every help screen. Include AI integration, gRPC, REST or Docker only when
supported and relevant. Clearly separate planned capabilities if documenting a
roadmap was requested.

Use active voice, concrete examples and language-labeled code blocks. Keep commands,
identifiers, uncertainty and facts intact; no stylistic cleanup that strengthens
claims. Do not replace an existing README without first reading it.

### Verify the changed surface

Recheck affected help and examples, relevant links and syntax. Reuse unchanged
help evidence within the same task; rerun all commands only for a full audit or
shared change that can affect them all. Use the narrowest reliable project check
for source/help-definition changes; broaden for a failure or actual coverage gap.

## Completion and evidence

Summarize what changed, the sections/commands inspected, observed checks and
remaining uncertainty. For a full audit, group actionable inconsistencies,
missing content and incorrect examples with source locations. State what was
not inspected; do not label an incomplete audit comprehensive. No fixed report
format is required unless the user or a consumer selects one.
