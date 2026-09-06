#!/usr/bin/env python3
"""Read-only live anti-pattern checks for active Claude and Codex conversations."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from collections import defaultdict
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from typing import Any, Iterable, Sequence

from redaction import redact_sensitive_text


DIAGNOSTIC_COMMANDS = (
    "git status",
    "git diff",
    "git log",
    "kubectl get",
    "kubectl describe",
    "kubectl logs",
    "kubectl get events",
    "curl",
    "docker ps",
    "docker images",
    "journalctl",
    "lsof",
)

ACTION_COMMANDS = (
    "pytest",
    "python -m pytest",
    "python3 -m pytest",
    "npm test",
    "npm run test",
    "npx playwright",
    "helm install",
    "helm upgrade",
    "kubectl apply",
    "kubectl create",
    "kubectl delete",
    "docker build",
    "docker push",
    "git commit",
    "git push",
    "bootstrap",
    "deploy",
    "make",
)

NORMAL_REPEAT_COMMANDS = (
    "pytest",
    "python -m pytest",
    "python3 -m pytest",
    "python -m unittest",
    "python3 -m unittest",
    "npm test",
    "npm run test",
    "go test",
    "cargo test",
    "cargo clippy",
    "git status",
    "git diff",
    "git log",
)

CREDENTIAL_NAME = re.compile(
    r"(?:^|_)(?:password|secret|token|api_?key|credential)(?:_|$)",
    re.IGNORECASE,
)

E2E_TEST_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"pytest.*e2e",
        r"pytest.*integration",
        r"npx\s+playwright",
        r"npm.*test.*e2e",
        r"npm.*test.*integration",
        r"npm\s+run\s+test:e2e",
        r"npm\s+run\s+test:integration",
    )
)

IMPLEMENTED_CHECKS = frozenset(
    {
        "RETRY_WITHOUT_DIAGNOSIS",
        "CREDENTIAL_ASSUMPTION",
        "MISSING_PREFLIGHT",
        "TOOL_DISCOVERY_GAP",
        "DESTRUCTIVE_OPERATION_WITHOUT_EXACT_GUARD",
    }
)

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
SHELL_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
SHELL_BUILTINS_WITH_ASSIGNMENTS = frozenset(
    {"declare", "export", "local", "readonly", "typeset"}
)
PYTHON_EXECUTABLES = frozenset({"python", "python2", "python3", "py", "pypy", "pypy3"})


@dataclass(frozen=True)
class ConversationData:
    messages: tuple[dict[str, Any], ...]
    event_count: int
    source_format: str


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str
    message_range: str
    command: str
    suggestion: str


@dataclass(frozen=True)
class GoodPractice:
    kind: str
    message_index: int
    rule: int
    description: str


def load_rules() -> dict[str, Any]:
    """Load the human-facing rule taxonomy."""
    rules_file = Path(__file__).parent / "rules.json"
    return json.loads(rules_file.read_text(encoding="utf-8"))


def extract_text(content: Any) -> str:
    """Extract text from Claude- or Codex-shaped message content."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        str(item.get("text", ""))
        for item in content
        if isinstance(item, dict)
        and str(item.get("type", "")).lower() in {"text", "input_text", "output_text"}
        and item.get("text")
    )


def _message(
    timestamp: str, role: str, content: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "timestamp": timestamp,
        "type": role,
        "message": {"content": content},
    }


def _codex_command_text(command: Any) -> str:
    if not isinstance(command, list):
        return str(command or "")
    if len(command) >= 3 and command[1] in {"-c", "-lc"}:
        return str(command[2])
    return shlex.join(str(part) for part in command)


def _safe_arguments(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    try:
        value = json.loads(str(raw or ""))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _normalized_tool(name: str, arguments: Any) -> dict[str, Any]:
    values = _safe_arguments(arguments)
    if name == "exec_command":
        return {
            "name": "Bash",
            "input": {
                "command": str(values.get("cmd", "")),
                "description": str(values.get("justification", "")),
            },
        }
    return {"name": name, "input": values}


def _completed_item_message(event: dict[str, Any]) -> dict[str, Any] | None:
    payload = event.get("payload") or {}
    item = payload.get("item") or {}
    item_type = re.sub(r"[^a-z]", "", str(item.get("type", "")).lower())
    timestamp = str(event.get("timestamp", ""))

    if item_type in {"usermessage", "agentmessage"}:
        text = extract_text(item.get("content"))
        if not text:
            return None
        role = "user" if item_type == "usermessage" else "assistant"
        return _message(timestamp, role, [{"type": "text", "text": text}])

    if item_type == "commandexecution":
        return _message(
            timestamp,
            "assistant",
            [
                {
                    "name": "Bash",
                    "input": {
                        "command": _codex_command_text(item.get("command")),
                        "description": str(item.get("source", "")),
                    },
                }
            ],
        )

    if item_type == "filechange":
        changes = item.get("changes") or {}
        if not isinstance(changes, dict):
            return None
        tool_items = []
        for path, change in changes.items():
            change_type = change.get("type") if isinstance(change, dict) else "update"
            tool_items.append(
                {
                    "name": "Write" if change_type == "add" else "Edit",
                    "input": {"file_path": str(path)},
                }
            )
        return _message(timestamp, "assistant", tool_items) if tool_items else None

    if item_type == "mcptoolcall":
        name = f"mcp__{item.get('server', '')}__{item.get('tool', '')}"
        return _message(
            timestamp,
            "assistant",
            [{"name": name, "input": _safe_arguments(item.get("arguments"))}],
        )

    if item_type == "collabagenttoolcall":
        name = f"collaboration__{item.get('tool', '')}"
        return _message(timestamp, "assistant", [{"name": name, "input": {}}])

    return None


def _legacy_codex_message(event: dict[str, Any]) -> dict[str, Any] | None:
    if event.get("type") != "response_item":
        return None
    payload = event.get("payload") or {}
    payload_type = payload.get("type")
    timestamp = str(event.get("timestamp", ""))

    if payload_type == "message":
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            return None
        text = extract_text(payload.get("content"))
        return (
            _message(timestamp, role, [{"type": "text", "text": text}])
            if text
            else None
        )

    if payload_type == "function_call":
        return _message(
            timestamp,
            "assistant",
            [
                _normalized_tool(
                    str(payload.get("name", "")),
                    payload.get("arguments"),
                )
            ],
        )

    return None


def normalize_events(events: Sequence[dict[str, Any]]) -> ConversationData:
    """Normalize supported transcript formats before applying heuristics."""
    has_completed_stream = any(
        event.get("type") == "event_msg"
        and (event.get("payload") or {}).get("type") == "item_completed"
        for event in events
    )
    if has_completed_stream:
        messages = tuple(
            message
            for event in events
            if event.get("type") == "event_msg"
            and (event.get("payload") or {}).get("type") == "item_completed"
            for message in [_completed_item_message(event)]
            if message is not None
        )
        return ConversationData(messages, len(events), "codex-item-completed")

    if any(event.get("type") == "response_item" for event in events):
        messages = tuple(
            message
            for event in events
            for message in [_legacy_codex_message(event)]
            if message is not None
        )
        return ConversationData(messages, len(events), "codex-response-item")

    messages = tuple(
        event for event in events if event.get("type") in {"user", "assistant"}
    )
    return ConversationData(messages, len(events), "claude-message")


def read_conversation(filepath: str | Path) -> ConversationData:
    events = []
    with Path(filepath).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid JSON on transcript line {line_number}: {error.msg}"
                ) from error
            if isinstance(value, dict):
                events.append(value)
    return normalize_events(events)


def extract_tool_calls(
    messages: Sequence[dict[str, Any]],
) -> tuple[tuple[int, str, dict[str, Any]], ...]:
    calls = []
    for index, message in enumerate(messages):
        if message.get("type") != "assistant":
            continue
        content = message.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            tool_input = item.get("input")
            calls.append(
                (
                    index,
                    str(item["name"]),
                    tool_input if isinstance(tool_input, dict) else {},
                )
            )
    return tuple(calls)


def extract_bash_commands(
    messages: Sequence[dict[str, Any]],
) -> tuple[tuple[int, str], ...]:
    commands = []
    for index, name, tool_input in extract_tool_calls(messages):
        if name == "Bash":
            commands.append(
                (
                    index,
                    str(tool_input.get("command") or tool_input.get("cmd") or ""),
                )
            )
    return tuple(commands)


def is_action_command(command: str) -> bool:
    normalized = command.lower().strip()
    return any(normalized.startswith(prefix) for prefix in ACTION_COMMANDS)


def is_diagnostic_command(command: str) -> bool:
    normalized = command.lower().strip()
    return any(normalized.startswith(prefix) for prefix in DIAGNOSTIC_COMMANDS)


def is_normal_repeat_command(command: str) -> bool:
    normalized = command.lower().strip()
    return any(normalized.startswith(prefix) for prefix in NORMAL_REPEAT_COMMANDS)


def _message_text(message: dict[str, Any]) -> str:
    return extract_text(message.get("message", {}).get("content", ""))


def _diagnostic_between(
    messages: Sequence[dict[str, Any]],
    commands: Sequence[tuple[int, str]],
    first_index: int,
    second_index: int,
) -> bool:
    if any(
        first_index < index < second_index and is_diagnostic_command(command)
        for index, command in commands
    ):
        return True
    markers = (
        "error",
        "failed",
        "traceback",
        "diagnos",
        "root cause",
        "logs",
    )
    return any(
        any(marker in _message_text(messages[index]).lower() for marker in markers)
        for index in range(first_index + 1, second_index)
    )


def check_retry_without_diagnosis(
    messages: Sequence[dict[str, Any]],
) -> tuple[Finding, ...]:
    commands = extract_bash_commands(messages)
    occurrences: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for index, command in commands:
        if is_action_command(command) and not is_normal_repeat_command(command):
            occurrences[" ".join(command.split()[:3])].append((index, command))

    findings = []
    for repeated in occurrences.values():
        for (first_index, first), (second_index, _) in zip(repeated, repeated[1:]):
            if not _diagnostic_between(messages, commands, first_index, second_index):
                findings.append(
                    Finding(
                        "RETRY_WITHOUT_DIAGNOSIS",
                        "MEDIUM",
                        f"{first_index}-{second_index}",
                        first,
                        "Inspect the complete failure evidence before repeating the action.",
                    )
                )
    return tuple(findings)


def check_credential_usage(
    messages: Sequence[dict[str, Any]],
) -> tuple[Finding, ...]:
    commands = extract_bash_commands(messages)
    secret_reads = tuple(
        index for index, command in commands if "kubectl get secret" in command.lower()
    )
    findings = []
    for index, command in commands:
        if not _credential_assignment_tokens(command):
            continue
        has_prior_read = any(
            0 <= index - secret_index <= 20 for secret_index in secret_reads
        )
        if not has_prior_read:
            findings.append(
                Finding(
                    "CREDENTIAL_ASSUMPTION",
                    "HIGH",
                    str(index),
                    "Credential assignment detected (value redacted)",
                    "Use the authorized secret source and never print the credential value.",
                )
            )
    return tuple(findings)


def check_preflight_missing(
    messages: Sequence[dict[str, Any]],
) -> tuple[Finding, ...]:
    commands = extract_bash_commands(messages)
    preflight_indices = tuple(
        index
        for index, command in commands
        if any(
            marker in command.lower()
            for marker in (
                "kubectl get pods",
                "kubectl get svc",
                "docker ps",
                "curl ",
                "health",
                "preflight",
            )
        )
    )
    findings = []
    for index, command in commands:
        if not any(pattern.search(command) for pattern in E2E_TEST_PATTERNS):
            continue
        has_preflight = any(
            0 < index - check_index <= 10 for check_index in preflight_indices
        )
        if not has_preflight:
            findings.append(
                Finding(
                    "MISSING_PREFLIGHT",
                    "HIGH",
                    str(index),
                    command,
                    "Verify the relevant services and dependencies before the integration run.",
                )
            )
    return tuple(findings)


def check_tool_discovery(
    messages: Sequence[dict[str, Any]],
) -> tuple[Finding, ...]:
    if len(messages) < 50:
        return ()
    commands = "\n".join(
        command.lower() for _, command in extract_bash_commands(messages)
    )
    prose = "\n".join(_message_text(message).lower() for message in messages)
    discovered = any(
        marker in commands or marker in prose
        for marker in (
            "command -v ",
            "type -a ",
            "which ",
            "rg --files",
            "ls ~/.local/bin",
            "ls ./scripts",
            "cat tools.md",
        )
    )
    return (
        ()
        if discovered
        else (
            Finding(
                "TOOL_DISCOVERY_GAP",
                "LOW",
                f"0-{len(messages)}",
                "N/A",
                "Inspect already-present project and local tools before building a replacement.",
            ),
        )
    )


@dataclass(frozen=True)
class ShellWord:
    text: str
    is_assignment: bool


# Split operators while quotes/escapes are still present, then decode words.
# This is a bounded lexer for simple commands, not a shell evaluator.
_SHELL_TOKENS = re.compile(
    r"""(?P<space>[^\S\n]+)|(?P<comment>\#[^\n]*)|(?P<operator>[;&|\n]+)"""
    r"""|(?P<word>(?:'[^']*'|"(?:\\[\s\S]|[^"\\])*"|\\[\s\S]|[^\s;&|'"\\])+)"""
    r"""|(?P<invalid>[\s\S])"""
)


def _command_clauses(command: str) -> tuple[tuple[ShellWord, ...], ...]:
    tokens = tuple(
        token
        for token in _SHELL_TOKENS.finditer(command)
        if token.lastgroup not in {"space", "comment"}
    )
    if any(token.lastgroup == "invalid" for token in tokens):
        return ()
    return tuple(
        tuple(
            ShellWord(
                shlex.split(token.group())[0],
                bool(SHELL_ASSIGNMENT.match(token.group())),
            )
            for token in group
        )
        for kind, group in groupby(tokens, key=lambda token: token.lastgroup)
        if kind == "word"
    )


@dataclass(frozen=True)
class CommandPrefix:
    start: int | None
    assignments: tuple[str, ...]


def _command_prefix(clause: Sequence[ShellWord]) -> CommandPrefix:
    index = 0
    assignments: tuple[str, ...] = ()
    while index < len(clause):
        token = clause[index].text
        if clause[index].is_assignment:
            assignments += (token,)
            index += 1
            continue
        if token == "command":
            index += 1
            if index < len(clause) and clause[index].text in {"-v", "-V"}:
                return CommandPrefix(None, assignments)
            while index < len(clause) and clause[index].text.startswith("-"):
                if clause[index].text == "--":
                    index += 1
                    break
                index += 1
            continue
        if Path(token).name == "env":
            index += 1
            options = True
            while index < len(clause):
                option = clause[index].text
                if options and option == "--":
                    options = False
                    index += 1
                    continue
                if SHELL_ASSIGNMENT.match(option):
                    assignments += (option,)
                    options = False
                    index += 1
                    continue
                if options and option in {"-u", "--unset", "-C", "--chdir"}:
                    index += 2
                    continue
                if options and option.startswith("-"):
                    index += 1
                    continue
                break
            continue
        if Path(token).name == "sudo":
            index += 1
            while index < len(clause):
                option = clause[index].text
                if option == "--":
                    index += 1
                    break
                if option in {
                    "-C",
                    "-D",
                    "-g",
                    "-h",
                    "-p",
                    "-R",
                    "-r",
                    "-T",
                    "-t",
                    "-u",
                    "--chdir",
                    "--close-from",
                    "--group",
                    "--host",
                    "--prompt",
                    "--role",
                    "--type",
                    "--user",
                }:
                    index += 2
                    continue
                if option.startswith("-"):
                    index += 1
                    continue
                break
            continue
        return CommandPrefix(index, assignments)
    return CommandPrefix(None, assignments)


def _command_start(clause: Sequence[ShellWord]) -> int | None:
    return _command_prefix(clause).start


def _credential_assignment_tokens(command: str) -> tuple[str, ...]:
    assignments = []
    for clause in _command_clauses(command):
        prefix = _command_prefix(clause)
        start = prefix.start
        executable = Path(clause[start].text).name if start is not None else None
        candidates = prefix.assignments
        if executable in SHELL_BUILTINS_WITH_ASSIGNMENTS:
            candidates += tuple(word.text for word in clause[start + 1 :])
        assignments.extend(
            token
            for token in candidates
            if SHELL_ASSIGNMENT.match(token)
            and CREDENTIAL_NAME.search(token.partition("=")[0])
        )
    return tuple(assignments)


def _destructive_clause(
    clause: Sequence[ShellWord],
) -> tuple[str, tuple[str, ...]] | None:
    start = _command_start(clause)
    if start is None:
        return None
    executable = Path(clause[start].text).name
    arguments = tuple(word.text for word in clause[start + 1 :])

    if executable == "rm":
        recursive = any(
            argument == "--recursive"
            or (
                argument.startswith("-")
                and not argument.startswith("--")
                and "r" in argument.lower()
            )
            for argument in arguments
        )
        if recursive:
            targets = tuple(
                argument for argument in arguments if not argument.startswith("-")
            )
            return "recursive remove", targets

    if executable == "find" and "-delete" in arguments:
        return "find delete", arguments[:1]

    if executable == "git" and arguments[:1] == ("clean",):
        if any(
            "f" in argument and argument.startswith("-") for argument in arguments[1:]
        ):
            return "git clean", arguments[1:]

    if executable == "git" and arguments[:2] == ("reset", "--hard"):
        return "hard reset", arguments[2:]

    if executable in PYTHON_EXECUTABLES and "shutil.rmtree" in " ".join(arguments):
        return "recursive Python remove", ()

    return None


def _broad_target(targets: Iterable[str]) -> bool:
    broad = {"/", ".", "..", "~", "$HOME", "${HOME}"}
    return any(
        target in broad
        or "*" in target
        or target.endswith("/*")
        or target.startswith(("$HOME/", "${HOME}/", "~/"))
        for target in targets
    )


def check_destructive_command_safety(
    messages: Sequence[dict[str, Any]],
) -> tuple[Finding, ...]:
    findings = []
    for index, command in extract_bash_commands(messages):
        for clause in _command_clauses(command):
            destructive = _destructive_clause(clause)
            if destructive is None:
                continue
            operation, targets = destructive
            severity = "HIGH" if _broad_target(targets) else "MEDIUM"
            findings.append(
                Finding(
                    "DESTRUCTIVE_OPERATION_WITHOUT_EXACT_GUARD",
                    severity,
                    str(index),
                    f"{operation}: {' '.join(targets) or 'target not recoverable from command'}",
                    (
                        "Resolve the exact target, prove its expected identity and containment, "
                        "reject roots/symlinks, and prefer a recoverable move or backup."
                    ),
                )
            )
    return tuple(findings)


def identify_good_practices(
    messages: Sequence[dict[str, Any]],
) -> tuple[GoodPractice, ...]:
    commands = extract_bash_commands(messages)
    practices = []

    for index, command in commands:
        lowered = command.lower()
        if "kubectl get secret" in lowered and "base64 -d" in lowered:
            practices.append(
                GoodPractice(
                    "CREDENTIAL_FROM_SECRET",
                    index,
                    1,
                    "Used an authorized secret read instead of hardcoding.",
                )
            )
        if is_diagnostic_command(command):
            practices.append(
                GoodPractice(
                    "DIAGNOSTIC_BEFORE_RETRY",
                    index,
                    2,
                    "Ran a diagnostic command before deciding on another action.",
                )
            )

    for index, message in enumerate(messages):
        text = _message_text(message).lower()
        if any(
            marker in text
            for marker in ("this expands", "requires approval", "before i push")
        ):
            practices.append(
                GoodPractice(
                    "SCOPE_CONFIRMATION",
                    index,
                    3,
                    "Made an authority or scope boundary explicit.",
                )
            )

    return tuple(practices)


def heuristic_signal_score(findings: Sequence[Finding]) -> int:
    violated_checks = len({finding.kind for finding in findings} & IMPLEMENTED_CHECKS)
    return round(
        100 * (len(IMPLEMENTED_CHECKS) - violated_checks) / len(IMPLEMENTED_CHECKS)
    )


def generate_report(
    findings: Sequence[Finding],
    good_practices: Sequence[GoodPractice],
    rules: dict[str, Any],
) -> str:
    lines = ["Analyzing current conversation for anti-patterns...", ""]

    if findings:
        lines.extend((f"WARNINGS ({len(findings)} found):", ""))
        for number, finding in enumerate(
            sorted(findings, key=lambda item: SEVERITY_ORDER.get(item.severity, 3)),
            1,
        ):
            lines.append(
                f"{number}. {finding.severity}: "
                f"{finding.kind.replace('_', ' ').title()} "
                f"(Message {finding.message_range})"
            )
            if finding.command != "N/A":
                safe_evidence = redact_sensitive_text(finding.command)
                if len(safe_evidence) > 160:
                    safe_evidence = safe_evidence[:157] + "..."
                lines.append(f"   - Evidence: {safe_evidence}")
            lines.append(f"   - Correction: {finding.suggestion}")
            lines.append("")
    else:
        lines.extend(("No heuristic warnings found.", ""))

    unique_practices = {practice.kind: practice for practice in good_practices}
    if unique_practices:
        lines.extend((f"GOOD PRACTICES ({len(unique_practices)} observed):", ""))
        for number, practice in enumerate(unique_practices.values(), 1):
            rule = next(
                (
                    item
                    for item in rules.get("universal_rules", [])
                    if item.get("id") == practice.rule
                ),
                None,
            )
            lines.append(
                f"{number}. {practice.kind.replace('_', ' ').title()} "
                f"(Message {practice.message_index})"
            )
            lines.append(f"   - {practice.description}")
            if rule:
                lines.append(f"   - Related rule {practice.rule}: {rule['rule']}")
            lines.append("")

    severities = {finding.severity for finding in findings}
    lines.append("COURSE CORRECTION:")
    if "HIGH" in severities:
        lines.append(
            "  - Stop the affected action until the high-severity finding is resolved."
        )
    elif "MEDIUM" in severities:
        lines.append(
            "  - Correct or explicitly adjudicate medium-severity findings before continuing."
        )
    elif findings:
        lines.append(
            "  - Low-severity findings do not automatically block continued work."
        )
    else:
        lines.append(
            "  - No transcript-level correction is required by these heuristics."
        )
    lines.append(
        f"  - Heuristic signal score: {heuristic_signal_score(findings)}% "
        f"across {len(IMPLEMENTED_CHECKS)} implemented checks"
    )
    lines.append("")
    lines.append(
        "This score is a bounded heuristic signal, not proof of policy compliance "
        "or review completeness."
    )
    return "\n".join(lines)


def analyze(
    data: ConversationData, lookback: int = 50
) -> tuple[tuple[Finding, ...], tuple[GoodPractice, ...]]:
    recent = (
        data.messages[-lookback:] if len(data.messages) > lookback else data.messages
    )
    findings = (
        *check_retry_without_diagnosis(recent),
        *check_preflight_missing(recent),
        *check_credential_usage(data.messages),
        *check_tool_discovery(data.messages),
        *check_destructive_command_safety(data.messages),
    )
    return tuple(findings), identify_good_practices(recent)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conversation_file", type=Path)
    parser.add_argument("--lookback", type=int, default=50)
    args = parser.parse_args(argv)
    if args.lookback <= 0:
        parser.error("--lookback must be positive")

    try:
        data = read_conversation(args.conversation_file)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(
        f"Loaded {data.event_count} events as {len(data.messages)} normalized "
        f"messages ({data.source_format})."
    )
    findings, good_practices = analyze(data, args.lookback)
    print()
    print(generate_report(findings, good_practices, load_rules()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
