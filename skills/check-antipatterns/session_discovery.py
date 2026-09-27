#!/usr/bin/env python3
"""Runtime-aware discovery and normalization of agent session transcripts.

Shared, byte-identical copy lives in both ``analyze-conversation`` and
``check-antipatterns`` so each skill stays independently installable.

Supported JSONL layouts (read-only; contents are never printed here):

- Claude Code: ``${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/<session>.jsonl``
  where ``<slug>`` is the absolute cwd with every non-alphanumeric character
  replaced by ``-``. Subagent transcripts live beside it under
  ``<session>/subagents/*.jsonl``.
- Codex: ``${CODEX_HOME:-~/.codex}/sessions/**/*.jsonl``.
- Pi: ``${PI_CODING_AGENT_DIR:-~/.pi/agent}/sessions/--<cwd with / as ->--/*.jsonl``.

opencode stores sessions in SQLite and is handled by ``opencode_adapter.py``
in ``analyze-conversation`` rather than here.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

RUNTIMES = ("claude", "codex", "pi")
CLAUDE_SESSION_ENV = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID")
# Codex-home configuration alone does not mean the caller is inside Codex.
CODEX_NON_SESSION_ENV = frozenset({"CODEX_HOME"})


@dataclass(frozen=True)
class Candidate:
    runtime: str
    path: Path
    mtime: float


class SessionNotFound(LookupError):
    """No transcript matched; ``candidates`` lists nearby choices (never contents)."""

    def __init__(self, message: str, candidates: tuple[Candidate, ...] = ()):
        super().__init__(message)
        self.candidates = candidates


def claude_slug(cwd: str | os.PathLike[str]) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(cwd))


def pi_slug(cwd: str | os.PathLike[str]) -> str:
    return "--" + str(cwd).strip("/").replace("/", "-") + "--"


def _home(env: Mapping[str, str]) -> Path:
    # An explicit mapping may carry its own HOME; the process environment
    # defers to Path.home() so callers that patch it stay consistent.
    if env is not os.environ and env.get("HOME"):
        return Path(env["HOME"])
    return Path.home()


def runtime_root(runtime: str, env: Mapping[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    match runtime:
        case "claude":
            return Path(env.get("CLAUDE_CONFIG_DIR") or _home(env) / ".claude") / "projects"
        case "codex":
            return Path(env.get("CODEX_HOME") or _home(env) / ".codex") / "sessions"
        case "pi":
            return Path(env.get("PI_CODING_AGENT_DIR") or _home(env) / ".pi" / "agent") / "sessions"
    raise ValueError(f"unsupported runtime {runtime!r}; expected one of {', '.join(RUNTIMES)}")


def runtime_home(runtime: str, env: Mapping[str, str] | None = None) -> Path:
    """Directory that owns a runtime's local state (parent of its session root)."""
    root = runtime_root(runtime, env)
    return root.parent


def detect_runtime(env: Mapping[str, str] | None = None) -> str | None:
    """Best-effort identification of the runtime hosting this process."""
    env = os.environ if env is None else env
    if env.get("CLAUDECODE") or any(env.get(name) for name in CLAUDE_SESSION_ENV):
        return "claude"
    if any(key.startswith("CODEX_") and key not in CODEX_NON_SESSION_ENV for key in env):
        return "codex"
    if env.get("PI_CODING_AGENT"):
        return "pi"
    return None


def _jsonl_candidates(runtime: str, paths: Iterable[Path]) -> tuple[Candidate, ...]:
    found = []
    for path in paths:
        try:
            if path.is_file():
                found.append(Candidate(runtime, path, path.stat().st_mtime))
        except OSError:
            continue
    return tuple(sorted(found, key=lambda item: item.mtime, reverse=True))


def _safe_glob(directory: Path, pattern: str) -> Iterable[Path]:
    try:
        return tuple(directory.glob(pattern)) if directory.is_dir() else ()
    except OSError:
        return ()


def candidates(
    runtime: str,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[Candidate, ...]:
    """Newest-first transcripts for one runtime, scoped to ``cwd`` where the layout allows."""
    cwd = os.getcwd() if cwd is None else cwd
    root = runtime_root(runtime, env)
    match runtime:
        case "claude":
            return _jsonl_candidates(runtime, _safe_glob(root / claude_slug(cwd), "*.jsonl"))
        case "codex":
            return _jsonl_candidates(runtime, _safe_glob(root, "**/*.jsonl"))
        case "pi":
            return _jsonl_candidates(runtime, _safe_glob(root / pi_slug(cwd), "*.jsonl"))
    raise ValueError(f"unsupported runtime {runtime!r}")


def all_candidates(
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[Candidate, ...]:
    merged = (item for runtime in RUNTIMES for item in candidates(runtime, cwd, env))
    return tuple(sorted(merged, key=lambda item: item.mtime, reverse=True))


def _claude_session_by_id(session_id: str, cwd, env) -> Path | None:
    root = runtime_root("claude", env)
    preferred = root / claude_slug(cwd) / f"{session_id}.jsonl"
    if preferred.is_file():
        return preferred
    for path in _safe_glob(root, f"*/{session_id}.jsonl"):
        if path.is_file():
            return path
    return None


def current_session(
    runtime: str | None = None,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> Candidate:
    """Resolve the current session transcript.

    ``runtime=None`` auto-detects: Claude Code (``CLAUDECODE``), then Codex
    (``CODEX_*``), then Pi (``PI_CODING_AGENT``), else the newest transcript
    across all known roots. Claude prefers ``$CLAUDE_CODE_SESSION_ID``.
    """
    env = os.environ if env is None else env
    cwd = os.getcwd() if cwd is None else cwd
    selected = runtime or detect_runtime(env)
    if selected == "claude":
        session_id = next((env[name] for name in CLAUDE_SESSION_ENV if env.get(name)), None)
        if session_id:
            path = _claude_session_by_id(session_id, cwd, env)
            if path is not None:
                return Candidate("claude", path, path.stat().st_mtime)
    found = candidates(selected, cwd, env) if selected else all_candidates(cwd, env)
    if found:
        return found[0]
    scope = selected or "any known runtime"
    raise SessionNotFound(
        f"no {scope} session transcript found for cwd {cwd}",
        all_candidates(cwd, env)[:10],
    )


def find_session_by_id(
    conversation_id: str,
    runtime: str | None = None,
    env: Mapping[str, str] | None = None,
) -> Candidate:
    """Select one exact transcript by session id (Claude) or filename fragment (Codex, Pi)."""
    runtimes = (runtime,) if runtime else RUNTIMES
    for name in runtimes:
        root = runtime_root(name, env)
        pattern = f"*/{conversation_id}.jsonl" if name == "claude" else f"**/*{conversation_id}*.jsonl"
        matches = _jsonl_candidates(name, _safe_glob(root, pattern))
        if name != "claude":
            matches = tuple(item for item in matches if "/subagents/" not in item.path.as_posix())
        if len(matches) > 1:
            raise SessionNotFound(
                f"conversation id {conversation_id!r} is ambiguous in {name}", matches[:10]
            )
        if matches:
            return matches[0]
    raise SessionNotFound(f"conversation {conversation_id} not found")


def subagent_transcripts(session_path: str | os.PathLike[str]) -> tuple[Path, ...]:
    """Claude subagent transcripts recorded for one top-level session."""
    path = Path(session_path)
    directory = path.parent / path.stem / "subagents"
    return tuple(sorted(item for item in _safe_glob(directory, "*.jsonl") if item.is_file()))


def transcript_cwd(transcript: str | os.PathLike[str], max_records: int = 200) -> Path | None:
    """Recorded working directory: Claude ``cwd``, Codex ``session_meta``, or Pi ``session`` header."""
    try:
        with open(transcript, encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= max_records:
                    break
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                payload = record.get("payload")
                if record.get("type") == "session_meta" and isinstance(payload, dict):
                    cwd = payload.get("cwd")
                else:
                    cwd = record.get("cwd")
                if isinstance(cwd, str) and cwd.startswith("/"):
                    return Path(cwd)
    except OSError:
        return None
    return None


def describe(candidates_: Iterable[Candidate]) -> str:
    """Path-and-runtime listing for a chooser; never includes transcript contents."""
    return "\n".join(f"  [{item.runtime}] {item.path}" for item in candidates_)


# ---------------------------------------------------------------------------
# Transcript normalization into the shared analyzer message shape:
#   {"type": "user"|"assistant", "timestamp": str, "message": {"content": ...}}
# Tool calls are content items carrying "name" and "input"; tool results are
# assistant-typed messages holding only "tool_result" items so they never count
# as human turns.
# ---------------------------------------------------------------------------

CODEX_EVENT_TYPES = frozenset({"session_meta", "turn_context", "response_item"})
PI_TOOL_NAMES = {"bash": "Bash", "read": "Read", "write": "Write", "edit": "Edit", "grep": "Grep"}


def detect_format(records: Iterable[Mapping]) -> str:
    """Return ``codex``, ``pi``, ``claude``, or ``unknown`` for parsed JSONL records."""
    saw_message = False
    for record in records:
        kind = record.get("type")
        payload = record.get("payload")
        if kind in CODEX_EVENT_TYPES or (
            kind == "event_msg" and isinstance(payload, dict) and payload.get("type") == "item_completed"
        ):
            return "codex"
        if kind == "session" and "version" in record:
            return "pi"
        if kind == "message" and isinstance(record.get("message"), dict) and "role" in record["message"]:
            return "pi"
        if kind in {"user", "assistant"}:
            saw_message = True
    return "claude" if saw_message else "unknown"


def _normalized(timestamp: str, role: str, content, **extra) -> dict:
    return {"type": role, "timestamp": timestamp, "message": {"content": content}, **extra}


def normalize_claude_records(records: Iterable[Mapping], sidechain: bool = False) -> list[dict]:
    """Normalize Claude Code records; ``sidechain`` drops parent-authored subagent prompts."""
    normalized: list[dict] = []
    for record in records:
        role = record.get("type")
        if role not in {"user", "assistant"} or record.get("isMeta"):
            continue
        timestamp = str(record.get("timestamp", ""))
        extra = {"isSidechain": True} if sidechain or record.get("isSidechain") else {}
        content = (record.get("message") or {}).get("content", "")
        if role == "assistant":
            normalized.append(_normalized(timestamp, "assistant", content, **extra))
            continue
        items = content if isinstance(content, list) else [content]
        results = [item for item in items if isinstance(item, dict) and item.get("type") == "tool_result"]
        human = [item for item in items if not (isinstance(item, dict) and item.get("type") == "tool_result")]
        if human and not (sidechain or record.get("isSidechain")):
            normalized.append(
                _normalized(timestamp, "user", content if isinstance(content, str) else human, **extra)
            )
        if results:
            normalized.append(_normalized(timestamp, "assistant", results, toolResult=True, **extra))
    return normalized


def _pi_text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        str(item.get("text", ""))
        for item in content
        if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
    )


def _pi_tool(item: Mapping) -> dict:
    name = str(item.get("name", ""))
    arguments = item.get("arguments")
    arguments = arguments if isinstance(arguments, dict) else {}
    mapped = PI_TOOL_NAMES.get(name, name)
    match mapped:
        case "Bash":
            tool_input = {"command": str(arguments.get("command", "")), "description": ""}
        case "Read" | "Write" | "Edit":
            tool_input = {"file_path": str(arguments.get("path", ""))}
        case "Grep":
            tool_input = {"pattern": str(arguments.get("pattern", ""))}
        case _:
            tool_input = dict(arguments)
    return {"type": "tool_use", "id": item.get("id", ""), "name": mapped, "input": tool_input}


def normalize_pi_records(records: Iterable[Mapping]) -> list[dict]:
    """Normalize Pi session ``message`` records (user, assistant, toolResult roles)."""
    normalized: list[dict] = []
    for record in records:
        message = record.get("message")
        if record.get("type") != "message" or not isinstance(message, dict):
            continue
        timestamp = str(record.get("timestamp", ""))
        role = message.get("role")
        content = message.get("content")
        if role == "user":
            text = _pi_text(content)
            if text:
                normalized.append(_normalized(timestamp, "user", [{"type": "text", "text": text}]))
        elif role == "assistant" and isinstance(content, list):
            items = [
                {"type": "text", "text": str(item.get("text", ""))}
                if item.get("type") == "text"
                else _pi_tool(item)
                for item in content
                if isinstance(item, dict) and item.get("type") in {"text", "toolCall"}
            ]
            if items:
                normalized.append(_normalized(timestamp, "assistant", items))
        elif role == "toolResult":
            result = {
                "type": "tool_result",
                "tool_use_id": message.get("toolCallId", ""),
                "content": _pi_text(content),
                "is_error": bool(message.get("isError")),
            }
            normalized.append(_normalized(timestamp, "assistant", [result], toolResult=True))
    return normalized


def load_records(transcript: str | os.PathLike[str]) -> list[dict]:
    """Parse JSONL objects, failing loudly with the offending line number."""
    records = []
    with open(transcript, encoding="utf-8") as handle:
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
                records.append(value)
    return records


def merge_claude_subagents(
    main: list[dict], session_path: str | os.PathLike[str]
) -> tuple[list[dict], tuple[Path, ...]]:
    """Interleave subagent activity (assistant actions and tool results) by timestamp."""
    paths = subagent_transcripts(session_path)
    side = [
        message
        for path in paths
        for message in normalize_claude_records(load_records(path), sidechain=True)
    ]
    combined = main + side
    if not all(message.get("timestamp") for message in combined):
        return combined, paths  # cannot interleave reliably; keep main order, append subagents
    ordered = sorted(enumerate(combined), key=lambda pair: (pair[1]["timestamp"], pair[0]))
    return [message for _, message in ordered], paths
