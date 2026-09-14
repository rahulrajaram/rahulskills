#!/usr/bin/env python3
"""Export an opencode session (SQLite) into normalized analysis JSONL.

opencode stores sessions in ~/.local/share/opencode/opencode.db:
  - message(id, session_id, time_created, data{role, agent, tokens, ...})
  - part(id, message_id, session_id, time_created, data{type: text|reasoning|
    tool|step-start|step-finish, ...})

The export emits the same normalized shape generate_report.py's Codex
normalizer produces, so analyze_conversation()/patterns.py can consume it:

  {"timestamp": ISO, "type": "user"|"assistant",
   "message": {"role": ..., "content": [...]}}

Text parts become {"type": "text"} items. Tool parts become tool-call items
({"name": "Bash", "input": {"command": ...}} etc.) so the analyzer's tool
stats work. reasoning/step-* parts are skipped (parity with Codex
normalization, which also omits hidden reasoning).
"""

import argparse
import datetime
import json
import sqlite3
import sys
from pathlib import Path


def default_db() -> Path:
    return Path.home() / ".local" / "share" / "opencode" / "opencode.db"


def _iso(ms: int) -> str:
    if not ms:
        return ""
    return (
        datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        + "Z"
    )


def resolve_session(conn: sqlite3.Connection, selector: str | None):
    """Resolve selector (None = most recently updated) to (id, slug, title)."""
    if selector is None:
        row = conn.execute(
            "SELECT id, slug, title FROM session ORDER BY time_updated DESC LIMIT 1"
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id, slug, title FROM session WHERE id = ? OR slug = ?",
            (selector, selector),
        ).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT id, slug, title FROM session "
                "WHERE title LIKE ? OR slug LIKE ? ORDER BY time_updated DESC LIMIT 1",
                (f"%{selector}%", f"%{selector}%"),
            ).fetchone()
    if row is None:
        raise SystemExit(f"no opencode session matches selector {selector!r}")
    return row


def list_sessions(conn: sqlite3.Connection, limit: int = 15):
    return conn.execute(
        "SELECT id, slug, substr(title, 1, 60), "
        "datetime(time_created / 1000, 'unixepoch'), "
        "datetime(time_updated / 1000, 'unixepoch') "
        "FROM session ORDER BY time_updated DESC LIMIT ?",
        (limit,),
    ).fetchall()


_TOOL_NAME_MAP = {
    "bash": "Bash",
    "read": "Read",
    "write": "Write",
    "edit": "Edit",
    "glob": "Glob",
    "grep": "Grep",
    "task": "Task",
    "todowrite": "TodoWrite",
    "webfetch": "WebFetch",
}


def _tool_item(tool_name: str, state: dict) -> dict | None:
    name = _TOOL_NAME_MAP.get((tool_name or "").lower(), (tool_name or "tool").title())
    input_data = (state or {}).get("input") or {}
    if name == "Bash":
        command = input_data.get("command")
        if not command:
            return None
        return {"name": "Bash", "input": {"command": str(command)}}
    for key in ("filePath", "file_path", "path"):
        if input_data.get(key):
            return {"name": name, "input": {"file_path": str(input_data[key])}}
    return {"name": name, "input": {}}


def export_session(db_path: Path, selector: str | None, out_path: Path) -> dict:
    """Export one session to normalized JSONL. Returns session identity dict."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        session_id, slug, title = resolve_session(conn, selector)
        rows = conn.execute(
            "SELECT m.id AS mid, m.data AS mdata, p.data AS pdata "
            "FROM message m LEFT JOIN part p ON p.message_id = m.id "
            "WHERE m.session_id = ? "
            "ORDER BY m.time_created, p.time_created, p.id",
            (session_id,),
        ).fetchall()
    finally:
        conn.close()

    # Group parts under their message, preserving role.
    messages: list[dict] = []
    current: dict | None = None
    for mid, mdata_raw, pdata_raw in rows:
        mdata = json.loads(mdata_raw)
        role = mdata.get("role")
        if role not in ("user", "assistant"):
            continue
        if current is None or current["mid"] != mid:
            current = {
                "mid": mid,
                "role": role,
                "created": mdata.get("time", {}).get("created"),
                "parts": [],
            }
            messages.append(current)
        if pdata_raw:
            current["parts"].append(json.loads(pdata_raw))

    exported = 0
    with out_path.open("w", encoding="utf-8") as handle:
        for entry in messages:
            content: list[dict] = []
            for part in entry["parts"]:
                ptype = part.get("type")
                if ptype == "text":
                    text = part.get("text") or ""
                    if text.strip():
                        content.append({"type": "text", "text": text})
                elif ptype == "tool":
                    item = _tool_item(part.get("tool"), part.get("state"))
                    if item:
                        content.append(item)
            if not content:
                continue
            record = {
                "timestamp": _iso(entry["created"]),
                "type": entry["role"],
                "message": {"role": entry["role"], "content": content},
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            exported += 1

    identity = {"id": session_id, "slug": slug, "title": title, "messages": exported}
    return identity


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=default_db(), help="opencode.db path")
    parser.add_argument("--list", action="store_true", help="list recent sessions")
    parser.add_argument("--session", help="session id or slug (default: most recently updated)")
    parser.add_argument("--out", type=Path, required=False, help="output JSONL path")
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"error: opencode.db not found at {args.db}", file=sys.stderr)
        return 1
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    if args.list:
        for sid, slug, title, created, updated in list_sessions(conn):
            print(f"{sid}  {updated}  {slug:20s}  {title}")
        conn.close()
        return 0
    conn.close()

    if not args.out:
        print("error: --out is required with --session", file=sys.stderr)
        return 1
    identity = export_session(args.db, args.session, args.out)
    print(
        f"exported session {identity['id']} ({identity['slug']}): "
        f"{identity['messages']} messages -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
