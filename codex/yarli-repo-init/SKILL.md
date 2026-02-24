---
name: yarli-repo-init
description: "Initialize and validate Yarli orchestration in a repository. Use when the user asks to set up yarli.toml, bootstrap run/prompt/plan files, configure CLI backend and durability, enable optional Haake memory integration, or verify a new repo can execute `yarli run` safely."
---

# Yarli Repository Initialization

Initialize a repository for reliable Yarli operation.

## Outcomes

Produce a working setup with:
- `yarli.toml` generated and tuned for the target CLI backend
- Prompt/plan authority files in place (when the workflow uses them)
- Optional Haake memory integration configured
- A verified smoke run and status/triage commands confirmed

## Step 1: Discover Environment

1. Resolve repository root.
Run `pwd` and `git rev-parse --show-toplevel` (if Git exists).

2. Detect tools.
Run:
- `command -v yarli`
- `command -v codex || command -v claude || command -v gemini`
- `command -v haake` (optional)

3. Inspect existing Yarli artifacts.
Check for:
- `yarli.toml`
- `PROMPT.md`
- `IMPLEMENTATION_PLAN.md`
- `bin/yarli-sanitize-continuation.sh`
- `bin/yarli-run-verification.sh`

If `yarli` is missing, stop and report prerequisite installation is required.

## Step 2: Generate `yarli.toml`

1. Choose backend preset.
- If `codex` exists: use `--backend codex`.
- Else if `claude` exists: use `--backend claude`.
- Else if `gemini` exists: use `--backend gemini`.
- Else run plain `yarli init` and require manual `[cli]` configuration.

2. Generate config.
Preferred command:

```bash
yarli init --backend <codex|claude|gemini> --path yarli.toml --force
```

Fallback:

```bash
yarli init --path yarli.toml --force
```

3. Apply durability baseline.
Prefer Postgres for non-throwaway usage:
- `core.backend = "postgres"`
- `postgres.database_url = "postgres://USER:PASS@HOST:5432/yarli"`

For temporary local-only testing only:
- `core.backend = "in-memory"`
- `core.allow_in_memory_writes = true`

4. Confirm execution defaults.
Ensure:
- `[execution].working_dir = "."`
- `[execution].runner = "native"` (unless user requests overwatch)
- `[ui].mode` is set intentionally (`auto|stream|tui`)

## Step 3: Bootstrap Prompt + Plan Authority (If Missing)

Use this authority model when repository uses the Yarli plan workflow:
- `yarli.toml` controls runtime behavior.
- `PROMPT.md` is intent/objective context.
- `IMPLEMENTATION_PLAN.md` is tranche scope/state authority.

If absent, create minimal bootstraps:

### Minimal `PROMPT.md`
- Objective statement.
- Current scope and constraints.
- No operator runbook commands.

### Minimal `IMPLEMENTATION_PLAN.md`
- Ordered tranches with explicit status.
- Clear exit criteria per tranche.
- Required verification sequence section.

If repository already has canonical equivalents, preserve existing files.

## Step 4: Optional Haake Memory Integration

If user requests memory integration and `haake` is available:

1. Enable in `yarli.toml`:
- `[memory.haake].enabled = true`
- `[memory.haake].command = "haake"`
- Optional `[memory.haake].project_dir = "."`

2. Validate command path.
Run:

```bash
haake --help
```

3. Keep fallback behavior.
If Haake is unavailable later, preserve local fallback memory logging behavior and do not block Yarli startup.

## Step 5: Repository-Specific Hooks

If repository provides helper scripts, wire/validate them:

1. If `bin/yarli-sanitize-continuation.sh` exists, run it before first run.
2. If `bin/yarli-run-verification.sh` exists, keep or add:
- `[run.paces.verification].cmds = ["./bin/yarli-run-verification.sh"]`
3. If a wrapper binary exists in `bin/`, preserve wrapper flow as canonical entrypoint.

Do not invent scripts that repository does not use.

## Step 6: Validation Pass

Run non-destructive checks first:

```bash
yarli info
yarli run --help
yarli run list
```

Run initialization smoke:

```bash
yarli run start "yarli bootstrap smoke" --cmd "echo YARLI_INIT_OK"
```

Then inspect:

```bash
yarli run status <run-id>
yarli run explain-exit <run-id>
```

If repository has verification chain script:

```bash
./bin/yarli-run-verification.sh --print-commands
```

## Step 7: Report

Return:
1. Backend chosen and why.
2. Files created/updated.
3. Validation commands run and outcomes.
4. Remaining manual inputs required (for example Postgres URL, CLI auth, optional Haake).

## Guardrails

- Prefer repository conventions over generic defaults.
- Keep `PROMPT.md` intent-only when using plan workflow.
- Avoid destructive git operations during initialization.
- Do not claim setup is complete without running at least one `yarli run` smoke path.
