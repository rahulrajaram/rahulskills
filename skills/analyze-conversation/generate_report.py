#!/usr/bin/env python3
"""
Generates comprehensive retrospective report from conversation analysis.
Entry point for /analyze-conversation skill.
"""

import sys
import os
import json
import shlex
import tempfile
from datetime import datetime
from pathlib import Path

# Import from analyzer and patterns modules
sys.path.insert(0, os.path.dirname(__file__))
from analyzer import analyze_conversation
from redaction import redact_sensitive_text
from patterns import (
    find_credential_antipatterns,
    find_retry_without_diagnosis,
    find_scope_creep,
    find_missing_verification,
    find_tool_opportunities,
    load_messages,
)


AUTONOMY_USER_MARKERS = (
    "autonom",
    "break and ask",
    "tackle all",
    "tackle these yourself",
    "do it",
    "so what now",
    "what's happening",
    "whats happening",
    "hogging memory",
    "please figure it out",
    "are you going to execute",
    "should we use",
    "should i kick",
)

AUTONOMY_ASSISTANT_MARKERS = (
    "should we use",
    "should i",
    "do you want",
    "would you like",
    "please confirm",
    "approve this",
    "which",
)


def load_diagnostic_taxonomy() -> dict:
    """Read the assembled shared taxonomy, or remain standalone-safe."""
    shared = Path(__file__).resolve().parents[2] / "references" / "diagnostic-taxonomy.json"
    if not shared.exists():
        return {"schema_version": 1, "rules": []}
    with shared.open(encoding="utf-8") as handle:
        return json.load(handle)


def _extract_codex_text(content) -> str:
    """Extract readable text from a Codex message content list."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    texts = []
    for item in content:
        if not isinstance(item, dict):
            if isinstance(item, str):
                texts.append(item)
            continue
        if str(item.get("type", "")).lower() in {"input_text", "output_text", "text"}:
            texts.append(item.get("text", ""))
    return "\n".join(texts)


def _safe_json_loads(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _codex_tool_item(name: str, arguments: str) -> dict:
    """Convert a Codex function call into a Claude-shaped tool item."""
    args = _safe_json_loads(arguments)
    if name == "exec_command":
        return {
            "name": "Bash",
            "input": {
                "command": str(args.get("cmd", "")),
                "description": str(args.get("justification", "")),
            },
        }
    if name in {"apply_patch", "write_stdin", "spawn_agent", "wait_agent"}:
        return {"name": name, "input": args}
    return {"name": name, "input": args}


def _duration_seconds(duration) -> float:
    """Return a Codex duration object as seconds."""
    if not isinstance(duration, dict):
        return 0.0
    return float(duration.get("secs", 0) or 0) + (
        float(duration.get("nanos", 0) or 0) / 1_000_000_000
    )


def _codex_command_text(command) -> str:
    """Recover the user command from Codex's shell argv representation."""
    if not isinstance(command, list):
        return str(command or "")
    if len(command) >= 3 and command[1] in {"-c", "-lc"}:
        return str(command[2])
    return shlex.join(str(part) for part in command)


def _normalized_message(timestamp: str, role: str, content: list) -> dict:
    return {
        "timestamp": timestamp,
        "type": role,
        "message": {"content": content},
    }


def _normalize_completed_item(event: dict) -> dict | None:
    """Normalize one current Codex item_completed event without duplicating it."""
    payload = event.get("payload") or {}
    item = payload.get("item") or {}
    item_type = item.get("type")
    timestamp = event.get("timestamp", "")

    if item_type in {"UserMessage", "AgentMessage"}:
        text = _extract_codex_text(item.get("content"))
        if not text:
            return None
        role = "user" if item_type == "UserMessage" else "assistant"
        return _normalized_message(
            timestamp,
            role,
            [{"type": "text", "text": text}],
        )

    if item_type == "CommandExecution":
        tool_items = [
            {
                "name": "Bash",
                "input": {
                    "command": _codex_command_text(item.get("command")),
                    "description": str(item.get("source", "")),
                    "duration_seconds": _duration_seconds(item.get("duration")),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status", ""),
                },
            }
        ]
        for parsed in item.get("parsed_cmd") or []:
            if not isinstance(parsed, dict):
                continue
            parsed_type = parsed.get("type")
            path = parsed.get("path") or parsed.get("name")
            if parsed_type == "read" and path:
                tool_items.append({"name": "Read", "input": {"file_path": str(path)}})
            elif parsed_type in {"write", "create"} and path:
                tool_items.append({"name": "Write", "input": {"file_path": str(path)}})
        tool_items.append(
            {
                "type": "tool_result",
                "tool_use_id": item.get("id", ""),
                "content": json.dumps(
                    {
                        "status": item.get("status"),
                        "exit_code": item.get("exit_code"),
                        "stderr": redact_sensitive_text(item.get("stderr") or "")[:2000],
                    },
                    sort_keys=True,
                ),
            }
        )
        return _normalized_message(timestamp, "assistant", tool_items)

    if item_type == "FileChange":
        tool_items = []
        for path, change in (item.get("changes") or {}).items():
            change_type = change.get("type") if isinstance(change, dict) else "update"
            tool_name = "Write" if change_type == "add" else "Edit"
            tool_items.append({"name": tool_name, "input": {"file_path": str(path)}})
        if tool_items:
            return _normalized_message(timestamp, "assistant", tool_items)
        return None

    if item_type == "McpToolCall":
        name = f"mcp__{item.get('server', '')}__{item.get('tool', '')}"
        return _normalized_message(
            timestamp,
            "assistant",
            [{"name": name, "input": item.get("arguments") or {}}],
        )

    if item_type == "CollabAgentToolCall":
        name = f"collaboration__{item.get('tool', '')}"
        return _normalized_message(
            timestamp, "assistant", [{"name": name, "input": {}}]
        )

    if item_type == "SubAgentActivity":
        return _normalized_message(
            timestamp,
            "assistant",
            [
                {
                    "name": "subagent_activity",
                    "input": {
                        "kind": item.get("kind", ""),
                        "agent_path": item.get("agent_path", ""),
                    },
                }
            ],
        )

    return None


def is_codex_conversation_file(conversation_file: str) -> bool:
    """Return whether a JSONL transcript appears to use Codex event format."""
    try:
        with open(conversation_file) as handle:
            for line in handle:
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("type") in {
                    "session_meta",
                    "turn_context",
                    "response_item",
                } or (
                    event.get("type") == "event_msg"
                    and (event.get("payload") or {}).get("type") == "item_completed"
                ):
                    return True
    except (OSError, json.JSONDecodeError):
        return False
    return False


def normalize_codex_conversation(conversation_file: str) -> str:
    """Normalize Codex JSONL events into the message shape used by this analyzer."""
    normalized = []
    with open(conversation_file) as handle:
        events = [json.loads(line) for line in handle if line.strip()]

    if not events:
        raise ValueError("empty transcript: no supported conversation events")

    has_completed_item_stream = any(
        event.get("type") == "event_msg"
        and (event.get("payload") or {}).get("type") == "item_completed"
        for event in events
    )

    if has_completed_item_stream:
        for event in events:
            if event.get("type") != "event_msg":
                continue
            payload = event.get("payload") or {}
            if payload.get("type") != "item_completed":
                continue
            message = _normalize_completed_item(event)
            if message:
                normalized.append(message)
    else:
        for event in events:
            if event.get("type") != "response_item":
                continue
            payload = event.get("payload") or {}
            payload_type = payload.get("type")
            timestamp = event.get("timestamp", "")
            if payload_type == "message":
                role = payload.get("role")
                if role not in {"user", "assistant"}:
                    continue
                text = _extract_codex_text(payload.get("content"))
                if not text:
                    continue
                normalized.append(
                    _normalized_message(
                        timestamp,
                        role,
                        [{"type": "text", "text": text}],
                    )
                )
            elif payload_type == "function_call":
                normalized.append(
                    _normalized_message(
                        timestamp,
                        "assistant",
                        [
                            _codex_tool_item(
                                str(payload.get("name", "")),
                                str(payload.get("arguments", "")),
                            )
                        ],
                    )
                )

    if not normalized:
        raise ValueError("unsupported transcript: no supported Codex messages or tool events")

    temp = tempfile.NamedTemporaryFile(
        mode="w",
        prefix="analyze-conversation-codex-",
        suffix=".jsonl",
        delete=False,
    )
    with temp:
        for message in normalized:
            temp.write(json.dumps(message) + "\n")
    return temp.name


def find_current_codex_conversation_file() -> str:
    """Find the most recently updated Codex session JSONL."""
    sessions_dir = Path.home() / ".codex" / "sessions"
    candidates = sorted(
        sessions_dir.glob("**/*.jsonl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError("No Codex JSONL sessions found under ~/.codex/sessions")
    return str(candidates[0])


def find_conversation_file(conversation_id=None):
    """Find conversation JSONL file."""
    if conversation_id == "--current":
        return find_current_codex_conversation_file()
    if conversation_id:
        # Search in .claude/projects/
        projects_dir = Path.home() / ".claude" / "projects"
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                try:
                    is_project_dir = project_dir.is_dir()
                except PermissionError:
                    continue
                if not is_project_dir:
                    continue
                conv_file = project_dir / f"{conversation_id}.jsonl"
                try:
                    if conv_file.exists():
                        return str(conv_file)
                except PermissionError:
                    continue
        # Search Codex sessions by id or filename fragment.
        sessions_dir = Path.home() / ".codex" / "sessions"
        for conv_file in sessions_dir.glob("**/*.jsonl"):
            if conversation_id in conv_file.name:
                return str(conv_file)
        raise FileNotFoundError(f"Conversation {conversation_id} not found")
    else:
        return find_current_codex_conversation_file()


# Commands that are normal development patterns - don't suggest tools for these
NORMAL_DEV_COMMANDS = {
    "git status",
    "git diff",
    "git log",
    "git add",
    "git commit",
    "ls",
    "pwd",
    "cd",
    "cat",
    "echo",
}

# Command prefixes that are normal test-fix-test cycles
NORMAL_TEST_COMMANDS = {
    "pytest",
    "python -m pytest",
    "python -m unittest",
    "python3 -m unittest",
    "npm test",
    "npm run test",
    "go test",
    "cargo test",
    "cargo clippy",
}


def is_normal_dev_command(cmd: str) -> bool:
    """Check if command is a normal development pattern."""
    cmd_lower = cmd.lower().strip()

    # Check exact matches
    for normal_cmd in NORMAL_DEV_COMMANDS:
        if cmd_lower.startswith(normal_cmd):
            return True

    # Check test commands
    for test_cmd in NORMAL_TEST_COMMANDS:
        if cmd_lower.startswith(test_cmd):
            return True

    # Overwatch is a monitor around an underlying development command, not a
    # missing project abstraction merely because a governed gate repeats.
    if cmd_lower.startswith("overwatch run") and any(
        marker in cmd_lower
        for marker in (
            " -- cargo test",
            " -- cargo clippy",
            " -- pytest",
            " -- npm test",
        )
    ):
        return True

    return False


def check_project_context(conversation_file: str) -> dict:
    """Check what tools/docs already exist in the project."""
    context = {
        "has_project_cli": False,
        "has_tools_doc": False,
        "has_claude_md": False,
        "has_agents_md": False,
        "has_operations_md": False,
        "existing_tools": [],
    }

    conv_path = Path(conversation_file)
    project_path = None

    if is_codex_conversation_file(conversation_file):
        try:
            with open(conversation_file) as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    if event.get("type") != "session_meta":
                        continue
                    cwd = (event.get("payload") or {}).get("cwd")
                    if cwd:
                        project_path = Path(cwd)
                    break
        except (OSError, json.JSONDecodeError):
            project_path = None

    if project_path is None:
        # Claude transcripts encode their project root in the parent directory.
        project_dir_name = conv_path.parent.name
        if project_dir_name.startswith("-"):
            project_path = Path("/" + project_dir_name[1:].replace("-", "/"))

    if project_path is not None:
        # Convert back to path: <project-slug> -> ~/Documents/myproject
        # Check for common documentation files
        if (project_path / "CLAUDE.md").exists():
            context["has_claude_md"] = True
        if (project_path / "AGENTS.md").exists():
            context["has_agents_md"] = True
        if (project_path / "OPERATIONS.md").exists():
            context["has_operations_md"] = True
        if (project_path / "TOOLS.md").exists():
            context["has_tools_doc"] = True

        # Check for project CLI
        for subdir in ["myproject_cp", "."]:
            scripts_dir = project_path / subdir / "scripts"
            if scripts_dir.exists():
                context["has_project_cli"] = True
                break

        # Check for bin/myproject or similar
        for pattern in ["bin/myproject", "scripts/myproject", ".local/bin/myproject"]:
            if (project_path / pattern).exists() or (Path.home() / pattern).exists():
                context["has_project_cli"] = True
                break

    return context


def _format_duration(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _timestamp_span_seconds(first: str, last: str) -> float:
    if not first or not last:
        return 0.0
    try:
        start = datetime.fromisoformat(first.replace("Z", "+00:00"))
        end = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    return max(0.0, (end - start).total_seconds())


def generate_markdown_report(conversation_file: str, output_dir: str = None) -> str:
    """Generate comprehensive markdown report."""

    try:
        if not any(line.strip() for line in Path(conversation_file).open(encoding="utf-8")):
            raise ValueError("empty transcript: no supported conversation events")
    except OSError:
        raise

    codex_input = is_codex_conversation_file(conversation_file)

    # Create output directory
    if output_dir is None:
        runtime_dir = ".codex" if codex_input else ".claude"
        output_dir = Path.home() / runtime_dir / "retrospectives"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    original_conversation_file = conversation_file
    analysis_file = conversation_file
    normalized_temp_file = None
    if codex_input:
        normalized_temp_file = normalize_codex_conversation(conversation_file)
        analysis_file = normalized_temp_file

    # Extract conversation ID from filename
    conv_id = Path(original_conversation_file).stem

    # Run analysis
    print(f"Analyzing conversation: {conv_id}...")
    stats = analyze_conversation(analysis_file)
    messages = load_messages(analysis_file)
    if not messages:
        raise ValueError("unsupported transcript: no supported conversation messages")

    # Check project context for existing tools/docs
    project_context = check_project_context(original_conversation_file)

    # Extract detailed patterns
    print("Extracting anti-patterns...")
    cred_patterns = find_credential_antipatterns(messages)
    retry_patterns = find_retry_without_diagnosis(messages)
    scope_patterns = find_scope_creep(messages)
    verify_patterns = find_missing_verification(messages)
    taxonomy = load_diagnostic_taxonomy()
    stable_ids = {item.get("legacy_id"): item.get("id") for item in taxonomy.get("rules", [])}
    tool_opps = find_tool_opportunities(messages)
    autonomy_user_signals = [
        msg
        for msg in stats.user_messages
        if any(marker in msg.lower() for marker in AUTONOMY_USER_MARKERS)
    ]
    autonomy_assistant_signals = [
        msg
        for msg in stats.assistant_messages
        if "?" in msg
        and any(marker in msg.lower() for marker in AUTONOMY_ASSISTANT_MARKERS)
    ]

    # Generate report
    report_lines = []

    # Header
    report_lines.append(f"# Conversation Retrospective: {conv_id}")
    report_lines.append("")
    report_lines.append(
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    report_lines.append(f"**Conversation File:** `{original_conversation_file}`")
    if normalized_temp_file:
        report_lines.append("**Runtime Adapter:** Codex JSONL normalized for analysis")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append(
        "These keyword-derived candidates cite observed transcript evidence, not established violations. "
        "Review the full conversation, prior authorization, and active instructions. Missing keywords "
        "do not prove missing checks. Severity ranks review priority and creates no stop authority. "
        "Continue authorized work; pause an affected action if evidence establishes a current "
        "authority or safety violation under an applicable instruction."
    )
    report_lines.append("")
    report_lines.append("### Top Heuristic Candidates")
    report_lines.append("")
    report_lines.append(
        f"1. **Retry-Without-Diagnosis**: {len(retry_patterns)} candidates"
    )
    report_lines.append(
        f"2. **Credential Assumptions**: {len(cred_patterns)} candidates"
    )
    report_lines.append(f"3. **Scope Expansions**: {len(scope_patterns)} candidates")
    report_lines.append(f"4. **Unverified Values**: {len(verify_patterns)} candidates")
    report_lines.append(
        f"5. **File Creation Events**: {len(stats.file_writes)} "
        "(reported for review; not inherently a tooling gap)"
    )
    report_lines.append(
        f"6. **Autonomy Break Signals**: {len(autonomy_user_signals)} user prompts, "
        f"{len(autonomy_assistant_signals)} assistant routing questions"
    )
    report_lines.append("")

    report_lines.append("### Top Tool Opportunities")
    report_lines.append("")
    tool_opp_count = 0
    for cmd, count in stats.repeated_commands.most_common(10):
        if count >= 3 and not is_normal_dev_command(cmd):
            tool_opp_count += 1
            report_lines.append(
                f"{tool_opp_count}. **Repeated {count}x**: `{redact_sensitive_text(cmd)[:80]}...` → Review whether a project-specific automation helper is warranted"
            )
            if tool_opp_count >= 5:
                break
    if tool_opp_count == 0:
        report_lines.append(
            "- None identified (repeated commands are normal dev patterns)"
        )
    report_lines.append("")

    report_lines.append("### Rule-Related Candidates for Review")
    report_lines.append("")
    if len(retry_patterns) > 0:
        report_lines.append(
            f"- **{stable_ids.get(2, 'DIAG-002')}** (diagnose before retry): {len(retry_patterns)} candidates"
        )
    if len(cred_patterns) > 0:
        report_lines.append(
            f"- **{stable_ids.get(1, 'DIAG-001')}** (credential assumptions): {len(cred_patterns)} candidates"
        )
    if len(scope_patterns) > 0:
        report_lines.append(
            f"- **{stable_ids.get(3, 'DIAG-003')}** (scope authorization): {len(scope_patterns)} candidates"
        )
    if len(verify_patterns) > 0:
        report_lines.append(
            f"- **{stable_ids.get(6, 'DIAG-006')}** (external value verification): {len(verify_patterns)} candidates"
        )
    if not any((retry_patterns, cred_patterns, scope_patterns, verify_patterns)):
        report_lines.append("- None detected by the implemented heuristics")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Autonomy analysis
    report_lines.append("## Autonomy Break Analysis")
    report_lines.append("")
    report_lines.append(
        "This section flags places where long-running autonomous work may have "
        "degraded into workflow selection, user re-prompting, or unnecessary "
        "help requests."
    )
    report_lines.append("")
    report_lines.append(
        f"- **User re-prompt / frustration signals**: {len(autonomy_user_signals)}"
    )
    report_lines.append(
        f"- **Assistant routing questions**: {len(autonomy_assistant_signals)}"
    )
    report_lines.append("")
    if autonomy_user_signals:
        report_lines.append("### User Signals")
        report_lines.append("")
        for signal in autonomy_user_signals[:10]:
            report_lines.append(f"- {redact_sensitive_text(signal).replace(chr(10), ' ')[:220]}")
        report_lines.append("")
    if autonomy_assistant_signals:
        report_lines.append("### Assistant Routing Questions")
        report_lines.append("")
        for signal in autonomy_assistant_signals[:10]:
            report_lines.append(f"- {redact_sensitive_text(signal).replace(chr(10), ' ')[:220]}")
        report_lines.append("")
    if autonomy_user_signals or autonomy_assistant_signals:
        report_lines.append("### Recommended Operating Rule")
        report_lines.append("")
        report_lines.append(
            "When the user requests long-running autonomous work, proceed through "
            "the next authorized concrete task. Pause only when an applicable authority or safety "
            "boundary requires new input, or a real local blocker prevents progress. Treat status updates as progress "
            "reports, not stopping points."
        )
        report_lines.append("")
        report_lines.append(
            "Routing hierarchy: direct request => direct execution; explicit "
            "`$skill` => use that skill; no explicit skill => normal engineering "
            "loop; `/goal` only for narrow multi-step objectives; durable "
            "background runs only when durability or managed scheduling matters."
        )
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

    # Conversation Summary
    report_lines.append("## Conversation Summary")
    report_lines.append("")
    report_lines.append(f"- **Total Turns**: {stats.total_turns}")
    report_lines.append(f"- **User Messages**: {len(stats.user_messages)}")
    report_lines.append(f"- **Assistant Messages**: {len(stats.assistant_messages)}")
    report_lines.append(f"- **Shell Commands**: {len(stats.bash_commands)}")
    report_lines.append(f"- **Failed Shell Commands**: {len(stats.failed_commands)}")
    report_lines.append(
        f"- **Cumulative Shell Runtime**: {_format_duration(stats.command_duration_seconds)}"
    )
    span = _timestamp_span_seconds(stats.first_timestamp, stats.last_timestamp)
    if span:
        report_lines.append(
            f"- **Observed Transcript Span**: {_format_duration(span)} "
            "(includes user/agent idle time)"
        )
    report_lines.append(f"- **Distinct Tool Kinds**: {len(stats.tool_calls)}")
    report_lines.append(f"- **Files Read**: {len(stats.file_reads)}")
    report_lines.append(f"- **Files Written**: {len(stats.file_writes)}")
    report_lines.append(f"- **Files Edited**: {len(stats.file_edits)}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Anti-Patterns Found
    report_lines.append("## Heuristic Candidates")
    report_lines.append("")

    # Retry-without-diagnosis
    if retry_patterns:
        report_lines.append("### 1. Retry-Without-Diagnosis")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(retry_patterns)} candidates")
        report_lines.append("")
        report_lines.append(
            "**Observed**: Commands repeated without recognized diagnostic text between attempts; intent and failure status remain unverified."
        )
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(retry_patterns[:5], 1):
            report_lines.append(f"{i}. Command: `{p['command']}`")
            report_lines.append(f"   - First attempt: Message {p['first_attempt']}")
            report_lines.append(f"   - Retry attempt: Message {p['retry_attempt']}")
            report_lines.append(f"   - Issue: {p['evidence']}")
        report_lines.append("")
        report_lines.append(
            "**Review**: Distinguish intentional repetition and test/fix cycles from blind failure retries. "
            "For a confirmed failure, inspect relevant evidence before repeating the action."
        )
        report_lines.append("")

    # Credential anti-patterns
    if cred_patterns:
        report_lines.append("### 2. Credential Assumptions")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(cred_patterns)} candidates")
        report_lines.append("")
        report_lines.append(
            "**Observed**: Credential-like assignments appeared in assistant text. They may be examples, placeholders, or authorized references; source and exposure require review."
        )
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(cred_patterns[:3], 1):
            report_lines.append(f"{i}. Type: {p['type']}")
            report_lines.append(f"   - Evidence: {p.get('evidence', 'N/A')}")
            report_lines.append(f"   - Context: {p['context'][:150]}...")
        report_lines.append("")
        report_lines.append(
            "**Review**: Establish whether a real credential was exposed or used outside existing "
            "authorization. Use the project's authorized credential mechanism without printing values. "
            "Do not retrieve or decode secrets merely to satisfy this diagnostic."
        )
        report_lines.append("")

    # Scope creep
    if scope_patterns:
        report_lines.append("### 3. Scope Expansions")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(scope_patterns)} candidates")
        report_lines.append("")
        report_lines.append(
            "**Observed**: Scope-related language appeared. The latest request excerpt may omit earlier authorization, and necessary implementation work may already be in scope."
        )
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(scope_patterns[:3], 1):
            report_lines.append(f"{i}. Original request: {p['original_request']}")
            report_lines.append(f"   - Expansion: {p['expansion']}")
        report_lines.append("")
        report_lines.append(
            "**Review**: Compare the proposed work with the full request and existing authorization. "
            "Continue necessary authorized work; ask only when an actual scope or permission boundary "
            "requires new user input. Additional files or scope keywords alone do not establish that boundary."
        )
        report_lines.append("")

    # Unverified values
    if verify_patterns:
        report_lines.append("### 4. Unverified External Values")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(verify_patterns)} candidates")
        report_lines.append("")
        report_lines.append(
            "**Observed**: Address or URL usage appeared without recognized verification text in the same message; verification elsewhere is unobserved."
        )
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(verify_patterns[:3], 1):
            report_lines.append(f"{i}. Type: {p['type']}")
            report_lines.append(f"   - Value: {p.get('evidence', 'N/A')}")
            report_lines.append(f"   - Context: {p['context'][:100]}...")
        report_lines.append("")
        report_lines.append(
            "**Review**: Check whether these are examples, supplied configuration, or values already "
            "verified elsewhere. Verify a value when its uncertainty affects the current task."
        )
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Tool Opportunities
    report_lines.append("## Tool Opportunities")
    report_lines.append("")
    report_lines.append("Commands repeated 3+ times that may benefit from automation:")
    report_lines.append("")

    actionable_tool_opps = []
    for cmd, count in stats.repeated_commands.most_common(10):
        if count >= 3 and not is_normal_dev_command(cmd):
            report_lines.append(f"- **{count}x**: `{redact_sensitive_text(cmd)[:80]}` → Review whether a project-specific automation helper is warranted")
            actionable_tool_opps.append((cmd, count))

    if not actionable_tool_opps:
        report_lines.append(
            "- None identified (all repeated commands are normal dev patterns like git, pytest)"
        )
        report_lines.append("")
        report_lines.append(
            "**Note**: Commands like `git status`, `pytest`, etc. are expected to repeat"
        )
        report_lines.append(
            "during normal development and don't indicate tooling gaps."
        )

    report_lines.append("")
    report_lines.append("**Repeated Command Sequences**:")
    if tool_opps["repeated_sequences"]:
        for seq_info in tool_opps["repeated_sequences"]:
            report_lines.append(
                f"- **{seq_info['count']}x**: `{redact_sensitive_text(seq_info['sequence'])[:100]}`"
            )
            report_lines.append(f"  → Potential tool: `{seq_info['tool_name']}`")
    else:
        report_lines.append("- None found (single commands only)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")

    high_priority_items = []
    medium_priority_items = []

    # HIGH priority - based on actual findings
    if len(retry_patterns) >= 5:
        high_priority_items.append(
            "**Review repeated-action evidence** - Determine whether retries followed failures\n"
            f"   - Candidates to review: {len(retry_patterns)} retry-without-diagnosis candidates"
        )
    if len(cred_patterns) > 0:
        high_priority_items.append(
            "**Review credential handling** - Check existing authorization and exposure without retrieving values\n"
            f"   - Candidates to review: {len(cred_patterns)} credential anti-patterns"
        )
    if len(stats.bash_commands) > 100 and len(stats.errors) > 10:
        high_priority_items.append(
            "**Review failure causes** - Check whether environment validation would help\n"
            "   - Candidates to review: Command volume and error count alone do not establish environment failures"
        )

    # MEDIUM priority - context-aware (only suggest if not already present)
    if (
        not project_context["has_tools_doc"]
        and not project_context["has_claude_md"]
        and not project_context["has_agents_md"]
    ):
        medium_priority_items.append(
            "**Create `TOOLS.md` or `CLAUDE.md`** - Document available tools for discoverability"
        )

    if not project_context["has_project_cli"] and actionable_tool_opps:
        medium_priority_items.append(
            "**Consider unified CLI** - Consolidate repeated command patterns into tools"
        )

    if len(scope_patterns) > 3:
        medium_priority_items.append(
            "**Review scope candidates** - Check prior authorization before proposing checkpoints"
        )

    report_lines.append("### Priority 1 (HIGH) - Review Candidates")
    report_lines.append("")
    if high_priority_items:
        for i, item in enumerate(high_priority_items, 1):
            report_lines.append(f"{i}. {item}")
    else:
        report_lines.append("- No high-priority candidates identified; unobserved behavior is not assessed")
    report_lines.append("")

    report_lines.append("### Priority 2 (MEDIUM) - Short-Term")
    report_lines.append("")
    if medium_priority_items:
        for i, item in enumerate(medium_priority_items, 1):
            report_lines.append(f"{i}. {item}")
    else:
        report_lines.append(
            "- No additional candidates identified from available project context"
        )
    report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Success Metrics
    report_lines.append("## Success Metrics")
    report_lines.append("")
    report_lines.append("| Metric | Current | Target |")
    report_lines.append("|--------|---------|--------|")
    report_lines.append(f"| Retry-without-diagnosis | {len(retry_patterns)} | Contextual review |")
    report_lines.append(f"| Credential-assignment candidates | {len(cred_patterns)} | Contextual review |")
    report_lines.append(
        f"| Scope-language candidates | {len(scope_patterns)} | Contextual review |"
    )
    report_lines.append(f"| Unverified values | {len(verify_patterns)} | Contextual review |")
    report_lines.append(
        f"| Shell commands captured | {len(stats.bash_commands)} | Informational; no universal target |"
    )
    report_lines.append("")

    # This score summarizes only the implemented heuristics. It is not a
    # completeness or policy-compliance proof.
    total_violations = (
        len(retry_patterns)
        + len(cred_patterns)
        + len(scope_patterns)
        + len(verify_patterns)
    )
    total_opportunities = total_violations + 7  # seven implemented shared identities
    compliance_score = (
        int(((total_opportunities - total_violations) / total_opportunities) * 100)
        if total_opportunities > 0
        else 100
    )

    report_lines.append(
        f"**Heuristic Signal Score**: {compliance_score}% ("
        "not a compliance or completeness claim)"
    )
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Footer
    report_lines.append("*Report generated by `/analyze-conversation` skill*")
    report_lines.append(
        "*For real-time anti-pattern detection, use `/check-antipatterns`*"
    )

    # Write report
    report_file = output_dir / f"{conv_id}_retrospective.md"
    with open(report_file, "w") as f:
        f.write(redact_sensitive_text("\n".join(report_lines)))

    if normalized_temp_file:
        try:
            os.unlink(normalized_temp_file)
        except OSError:
            pass

    print(f"\n✅ Report generated: {report_file}")
    return str(report_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        conversation_file = find_conversation_file()

    elif sys.argv[1] == "--current":
        conversation_file = find_conversation_file("--current")
    elif sys.argv[1] == "--id":
        if len(sys.argv) < 3:
            print("Error: Conversation ID required")
            sys.exit(1)
        conversation_file = find_conversation_file(sys.argv[2])
    else:
        conversation_file = sys.argv[1]

    output_file = generate_markdown_report(conversation_file)
    print("\nRetrospective analysis complete!")
    print(f"Report: {output_file}")
