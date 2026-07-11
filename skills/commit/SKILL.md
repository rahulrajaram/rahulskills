---
name: commit
description: "Create a well-formed commit after intelligently triaging every changed file to determine whether it should actually be committed. Filters planning artifacts, agent state, spurious docs, and secrets. Supports human-controlled overrides via .githooks/commit-allow. Use when the user says /commit, 'commit changes', 'make a commit', or asks to commit work."
argument-hint: "[message hint]"
---

# Commit

Create a single well-formed commit after assessing every visible changed file
to determine whether it should actually be committed.

## Autonomy Routing

A commit request is approval to triage, stage repository-appropriate files, compose a
conventional commit message, and create the commit without turning the routine
path into an approval loop. Ask only when the assessment contains REVIEW items,
ALLOWED overrides, secrets, destructive cleanup, ignore-policy changes, or a
message/scope decision that materially affects user intent. Do not ask whether
to use another workflow wrapper unless the user is really requesting history
cleanup, PR creation, or handoff.

## Usage

```
/commit
/commit "message hint"
```

`message hint` is optional seed text for the commit message subject.

---

## Workflow

### Step 1 — Survey the working tree

```bash
git status --short
git stash list | head -3
```

Collect:
- Staged files (will appear in next commit as-is unless you unstage)
- Unstaged modifications to tracked files
- Untracked files
- Whether the branch has unpushed commits

Read repository policy before classifying: applicable `AGENTS.md`/`CLAUDE.md`,
`.gitignore`, contribution docs, tracked-file status, and recent history for
ambiguous generated or planning files. Repository policy outranks the generic
heuristics below unless it would expose a secret or violate an active safety
instruction.

Also check for a human-maintained override file:

```bash
cat .githooks/commit-allow 2>/dev/null
```

This file lists patterns that are explicitly permitted to be committed even
though they would normally be ignored. It is maintained by humans only —
agents must never write to it.

### Step 2 — Triage every file

For every file visible in `git status`, assign one of four verdicts:

| Verdict | Meaning |
|---------|---------|
| **COMMIT** | Clearly part of the work; stage and commit |
| **ALLOWED** | Normally ignored, but explicitly permitted by `.githooks/commit-allow` |
| **SKIP** | Should never be in version control; do not stage |
| **REVIEW** | Ambiguous; present to user before deciding |

**Check `.githooks/commit-allow` first.** If a file matches a pattern in that
file, assign ALLOWED before applying any SKIP rule. ALLOWED always wins over
SKIP. Never assign ALLOWED based on your own judgement — only based on what
is written in the allow file by the human.

#### Default SKIP heuristics for untracked files

Apply these defaults when repository policy and history do not establish that a
file belongs in version control. A tracked file modified by the requested work
is normally COMMIT; do not untrack it merely because its name matches a generic
pattern. Contradictions between repository policy and these heuristics are
REVIEW, not silent SKIP.

**Untracked planning / AI session artifacts**
- `VISION.md`, `IMPLEMENTATION_PLAN.md`, `PROMPT.md`, `RALPH_PROMPT.md`
- `IDEAS.md`, `DECISIONS_LOG.txt`, `RFC_INSTRUCTIONS.md`, `ISSUES_FOUND.md`
- `PHASE_*_SUMMARY.md`, `PHASE_*_IMPLEMENTATION.md`
- `*VALIDATION*.md`, `*VALIDATION*.txt`, `UNDOCUMENTED_APIS*.md`

**Untracked agent runtime state**
- `.yarli/`, `.yarl/`, `.yore/`, `.yore-test/`, `.yore-audit/`
- `.cultivar/`, `.claude/` (session state only), `.codex/`, `.agent/`
- `.ralph/`, `.haake/`, `.workmerge/`, `.worktrees/`, `.playwright-mcp/`
- `artifacts/`, `agent_reports/`, `yarli.toml`

**Untracked build / cache / generated output**
- `__pycache__/`, `*.pyc`, `*.pyo`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`
- `target/` (Rust), `node_modules/`, `dist/`, `out/`, `.next/`, `.nuxt/`
- `*.egg-info/`, `.tox/`, `htmlcov/`, `coverage/`, `.nyc_output/`
- `*.tsbuildinfo`, `.eslintcache`, `.parcel-cache`

**Secrets / credentials**
- `.env`, `.env.*` (any variant), `*.pem`, `*.key`, `*.p12`, `*.pfx`
- Files matching `*credentials*.json`, `*service_account*.json`
- `id_rsa`, `id_ed25519`, `id_ecdsa`, `*.keystore`, `*.secret`

**Note:** Secrets must never receive ALLOWED verdict regardless of what is in
the allow file. Flag them as SKIP and warn the user explicitly.

**Newly created `.md` files** that are not in this explicit allow-list:
`README.md`, `CHANGELOG.md`, `CHANGES.md`, `LICENSE.md`, `CONTRIBUTING.md`,
`SECURITY.md`, `CODE_OF_CONDUCT.md`

#### Default COMMIT heuristics

- Source files: `.py`, `.rs`, `.ts`, `.js`, `.tsx`, `.jsx`, `.go`, `.hs`,
  `.sh`, `.bash`, `.css`, `.scss`, `.html`, `.sql`
- Project config that clearly belongs: `Cargo.toml`, `pyproject.toml`,
  `package.json`, `tsconfig.json`, `.gitignore`, `Makefile`, `*.yaml` / `*.toml`
  when they are project-owned config (not agent state)
- Test files (`.test.ts`, `*_test.go`, `test_*.py`, `*_spec.rb`, etc.)

#### REVIEW — ask the user

- Any `.md` file not covered by the auto-skip, auto-commit, or ALLOWED rules
- Lock files (`Cargo.lock`, `package-lock.json`, `yarn.lock`, `poetry.lock`,
  `go.sum`) — confirm whether this repo commits them
- Large generated files (>500 lines, clearly machine-written)
- New top-level files with an unusual extension

### Step 3 — Present the assessment

Print a verdict table **before touching the index**:

```
File assessment:
  COMMIT   lib/staged-guard.sh              (modified — new function)
  COMMIT   .githooks/pre-commit             (modified — wired new check)
  ALLOWED  VISION.md                        (normally ignored — permitted by .githooks/commit-allow)
  SKIP     IMPLEMENTATION_PLAN.md           (planning artifact — will not stage)
  SKIP     .claude/session.json             (agent state — will not stage)
  REVIEW   Cargo.lock                       (lock file — commit in this repo?)
```

**ALLOWED files must be shown distinctly** — never buried in COMMIT.
The user needs to see at a glance that an override is in play.

**Never silently skip a SKIP file.** Name every one so the user can override.

If the table contains REVIEW items, ALLOWED files, secrets, destructive cleanup,
or an ignore-location choice, ask:
> Resolve REVIEW/ALLOWED/SKIP decisions before staging. Proceed? (y/n)

If all staged files are ordinary COMMIT verdicts and all SKIP handling is
unambiguous, continue without a second approval; the user's commit request is
the approval.

### Step 3b — Respect repository ignore policy

SKIP means "leave unstaged" for this invocation. It does not authorize changing
global Git configuration, writing `~/.config/git/ignore`, editing `.gitignore`,
deleting files, or removing tracked files from the index. Never run
`git rm --cached` as commit housekeeping.

If ignored noise is recurring, report the exact paths and recommend a
repository-local policy change for separate approval. Only edit `.gitignore`
when the user explicitly requests that change and it belongs to this repository.
Never write `.githooks/commit-allow`; it is human-maintained.

### Step 4 — Stage approved files

```bash
git add path/to/file1 path/to/file2 ...
```

Include both COMMIT and ALLOWED files. **Never use `git add .` or `git add -A`**
— always name explicit paths.

### Step 5 — Read the diff and compose the commit message

```bash
git diff --cached --stat
git diff --cached
```

Compose a **conventional commit** message:

```
<type>(<scope>): <subject>

<body — optional, explain WHY not WHAT, wrap at 72 chars>
```

**Types**: `feat` · `fix` · `chore` · `docs` · `refactor` · `test` · `style` · `ci` · `build`

Rules:
- Subject ≤ 72 characters, imperative mood ("Add", not "Added" or "Adds")
- No trailing period on the subject line
- Scope = primary module, directory, or subsystem (omit if changes are repo-wide)
- If changes span multiple types, use the dominant one; list secondary changes in body
- Body only when the "why" is not obvious from the subject
- If any ALLOWED files are staged, note them in the body:
  `Permitted overrides: VISION.md (see .githooks/commit-allow)`
- If the user provided a message hint, incorporate it

Use the proposed message without asking for approval unless the user requested
interactive review, supplied conflicting message guidance, or the correct
subject/scope is materially ambiguous. Include the final message in the summary.

### Step 6 — Commit

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <subject>

<body if needed>
EOF
)"
```

### Step 7 — Confirm and summarise

```bash
git show --stat HEAD
```

Print:
```
✓ <short-sha>: <subject>
  N files changed, X insertions(+), Y deletions(-)
```

If ALLOWED files were committed, call them out again here so the audit trail
is visible even if the user wasn't watching:
```
⚠ Permitted overrides committed: VISION.md
```

### Step 8 — If the user is really asking for history cleanup, switch skills

If the user asks to squash, tidy, compress, clean up, or rewrite commit
history, do **not** improvise with ad-hoc `git rebase` from this skill.
Use the `/squash-commits` skill instead.

History cleanup requires a different safety model: recording original HEAD,
backup refs, rerere, per-pass health checks, and conflict abort policies.
This skill is for staging and creating a commit from the current working
tree, not for rewriting existing history.

---

## Safety rules

- **Never pass `--no-verify`**. If a hook fails, diagnose and fix — don't bypass.
- **Never amend a pushed commit** without explicit user instruction.
- **Never push** unless the user explicitly asks after the commit is done.
- **Never write to `.githooks/commit-allow`** — only humans maintain that file.
- **Never grant ALLOWED to secrets** regardless of the allow file.
- **Never casually rewrite history from this skill** — route to `/squash-commits`.
- If `staged-guard` fires during the commit hook, treat it as a signal:
  unstage the flagged file, re-examine it, and proceed only after resolution.
- If after SKIP filtering there is nothing left to commit, report:
  > Nothing to commit after filtering artifacts. Working tree is clean or only artifacts remain.
  and stop.
- If you are unsure whether a file is an artifact, bias toward REVIEW, not COMMIT.

---

## The `.githooks/commit-allow` file

This file is the human-controlled override mechanism. Format:

```
# Allow VISION.md to be committed — this project tracks vision in git
VISION.md

# Allow the phase summary for the current sprint
PHASE_3_SUMMARY.md
```

- One gitignore-style pattern per line
- `#` comments supported
- Agents **read** this file during triage but **never write to it**
- An agent that wants to commit a normally-ignored file must tell the human
  and ask them to add the pattern here first
- Secrets (`*.key`, `.env`, etc.) are never honoured even if listed here
