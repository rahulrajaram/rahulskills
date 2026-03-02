---
name: repo-topics
description: "Analyze a GitHub repository and apply relevant topic labels under repository details. Use when user says /repo-topics, 'add topics', 'add labels to repo', 'tag the repo', or asks to set GitHub repository topics."
allowed-tools: Bash, Read, Glob, Grep
---

# Repo Topics

Analyze a GitHub repository's content, tech stack, and purpose, then apply relevant topic labels via the GitHub API.

## Prerequisites

- `gh` CLI authenticated with repo access
- Repository must be hosted on GitHub

## Usage

`/repo-topics [owner/repo]`

- If `owner/repo` is provided, use that.
- If omitted, detect from the current git remote: `gh repo view --json nameWithOwner -q .nameWithOwner`

## Workflow

### Step 1: Identify the repository

```bash
REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
```

If detection fails, ask the user for the repository.

### Step 2: Read existing topics

```bash
gh api repos/$REPO/topics -q '.names[]'
```

Report current topics (if any) to the user.

### Step 3: Analyze the repository

Gather signals to determine relevant topics:

1. **Languages**: `gh api repos/$REPO/languages -q 'keys[]'`
2. **Description**: `gh repo view $REPO --json description -q .description`
3. **File markers** (check for presence via the API or local checkout):
   - `Cargo.toml` → `rust`
   - `package.json` → `nodejs`, `javascript` or `typescript`
   - `pyproject.toml` / `setup.py` / `requirements.txt` → `python`
   - `go.mod` → `golang`
   - `Dockerfile` / `docker-compose.yml` → `docker`
   - `kubernetes/` / `k8s/` / `helm/` → `kubernetes`
   - `.github/workflows/` → `github-actions`, `ci-cd`
   - `terraform/` / `*.tf` → `terraform`, `infrastructure-as-code`
   - `SKILL.md` / skills directory → `ai-agents`, `skills`
   - `yarli.toml` → `orchestration`
   - CLI entry points (`cli.py`, `main.rs`, `bin/`) → `cli-tools`
4. **README content**: Scan for keywords that suggest domains:
   - "machine learning" / "ML" / "model" → `machine-learning`
   - "API" / "REST" / "GraphQL" → `api`
   - "web" / "frontend" / "React" / "Vue" → `web`, framework name
   - "database" / "SQL" / "postgres" → `database`
   - "security" / "auth" / "encryption" → `security`
   - "testing" / "test framework" → `testing`
   - "automation" / "workflow" → `automation`
   - "devops" / "deploy" / "infrastructure" → `devops`
   - "prompt" / "LLM" / "AI" / "agent" → `ai`, `llm`, relevant terms

### Step 4: Propose topics

Combine signals into a deduplicated, sorted list of topic slugs. Topics must:
- Be lowercase
- Use hyphens (no spaces or underscores)
- Be specific enough to be useful (avoid overly generic tags like `code` or `project`)
- Cap at 20 topics (GitHub's limit)

Present the proposed topics to the user as a table:

```
Current topics: (none)

Proposed topics (14):
  ai-agents, automation, cli-tools, claude-code, developer-tools,
  devops, git-hooks, multi-agent, openai-codex, prompt-engineering,
  python, shell-scripts, skills, workflow-automation

New:     14 topics to add
Kept:    0 existing topics preserved
Removed: 0 existing topics dropped
```

### Step 5: Confirm

Ask the user to approve, edit, or cancel. Do NOT apply without confirmation.

### Step 6: Apply

```bash
gh api repos/$REPO/topics -X PUT \
  -f "names[]=topic-1" \
  -f "names[]=topic-2" \
  ...
```

Report the final applied topics.

## Guardrails

- Never remove existing topics without explicit user approval.
- Always merge new topics with existing ones unless the user asks to replace.
- Respect GitHub's 20-topic limit. If the combined list exceeds 20, ask the user to prioritize.
- Do not invent topics unrelated to the repository's actual content.
- If the repository is private, warn that topics are still publicly visible on GitHub.
