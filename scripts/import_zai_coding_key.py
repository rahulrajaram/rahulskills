#!/usr/bin/env python3
"""Install a Z.ai Coding Plan key into Pi's private guest auth store."""

from __future__ import annotations

import getpass
import json
import os
from pathlib import Path
import sys
import tempfile


def install_key(agent_dir: Path, key: str) -> None:
    if not key or key != key.strip() or any(char.isspace() for char in key):
        raise ValueError("The key must be nonempty and contain no whitespace")
    auth = agent_dir / "auth.json"
    for path in (agent_dir, auth, *agent_dir.parents):
        if path.is_symlink():
            raise ValueError(f"Refusing symlinked auth path: {path}")
    if not agent_dir.is_dir():
        raise ValueError(f"Pi agent directory is missing: {agent_dir}")
    if auth.exists():
        if auth.stat().st_mode & 0o077:
            raise ValueError("Pi auth.json is not private; fix its permissions first")
        data = json.loads(auth.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Pi auth.json must contain an object")
        if "zai" in data:
            raise ValueError("A Z.ai credential already exists; inspect it before replacement")
    else:
        data = {}
    data["zai"] = {"type": "api_key", "key": key}
    descriptor, staged = tempfile.mkstemp(prefix=".auth-zai-", dir=agent_dir)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(staged, 0o600)
        os.replace(staged, auth)
    finally:
        Path(staged).unlink(missing_ok=True)


def main() -> int:
    if not sys.stdin.isatty():
        print("Run this command in an interactive guest terminal; input is hidden.", file=sys.stderr)
        return 2
    try:
        key = getpass.getpass("Z.ai Coding Plan API key (hidden input): ")
        install_key(Path.home() / ".pi/agent", key)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Could not install Z.ai credential: {error}", file=sys.stderr)
        return 2
    print("Z.ai Coding Plan credential installed for Pi; run a functional GLM check next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
