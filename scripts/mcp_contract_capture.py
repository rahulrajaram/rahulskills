#!/usr/bin/env python3
"""Capture and compare an MCP stdio server contract without activating it."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import selectors
import shutil
import subprocess
import time
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import Any, Iterable


VOLATILE_KEYS = frozenset(
    {"captured_at", "created_at", "pid", "started_at", "timestamp"}
)


@dataclass(frozen=True)
class Artifact:
    label: str
    path: Path


@dataclass(frozen=True)
class Capture:
    initialize: dict[str, Any]
    tools_list: dict[str, Any]
    transcript: tuple[dict[str, Any], ...]
    stderr: str
    returncode: int


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in sorted(value.items())
            if key not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(path: Path) -> dict[str, str]:
    if path.is_symlink():
        return {"@symlink": f"symlink:{os.readlink(path)}"}
    if path.is_file():
        return {"@file": sha256_file(path)}
    if not path.is_dir():
        raise FileNotFoundError(path)
    return {
        str(item.relative_to(path)): (
            f"symlink:{os.readlink(item)}" if item.is_symlink() else sha256_file(item)
        )
        for item in sorted(path.rglob("*"))
        if item.is_file() or item.is_symlink()
    }


def parse_artifact(raw: str) -> Artifact:
    label, separator, path = raw.partition("=")
    if not separator or not label or not path:
        raise argparse.ArgumentTypeError("expected LABEL=PATH")
    return Artifact(label=label, path=Path(path).expanduser().absolute())


def _send(process: subprocess.Popen[str], message: dict[str, Any]) -> None:
    assert process.stdin is not None
    process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
    process.stdin.flush()


def capture_session(command: list[str], timeout: float) -> Capture:
    if not command:
        raise ValueError("MCP command must not be empty")
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None and process.stderr is not None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    transcript: list[dict[str, Any]] = []
    stderr_lines: list[str] = []
    responses: dict[int, dict[str, Any]] = {}
    try:
        _send(
            process,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-contract-capture", "version": "1"},
                },
            },
        )
        deadline = time.monotonic() + timeout
        initialized_sent = False
        while len(responses) < 2:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"MCP capture exceeded {timeout:g}s")
            events = selector.select(remaining)
            if not events and process.poll() is not None:
                raise RuntimeError(
                    f"MCP process exited before capture completed ({process.returncode})"
                )
            for key, _ in events:
                line = key.fileobj.readline()
                if not line:
                    selector.unregister(key.fileobj)
                    continue
                if key.data == "stderr":
                    stderr_lines.append(line)
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as error:
                    raise RuntimeError(f"invalid JSON-RPC output: {line.rstrip()}") from error
                transcript.append(message)
                message_id = message.get("id")
                if message_id in (1, 2):
                    if "error" in message:
                        raise RuntimeError(
                            f"MCP request {message_id} failed: {message['error']}"
                        )
                    responses[message_id] = message
                if message_id == 1 and not initialized_sent:
                    _send(
                        process,
                        {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    )
                    _send(
                        process,
                        {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/list",
                            "params": {},
                        },
                    )
                    initialized_sent = True
    finally:
        selector.close()
        if process.stdin:
            process.stdin.close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        stderr_lines.extend(process.stderr.readlines())
    return Capture(
        initialize=responses[1],
        tools_list=responses[2],
        transcript=tuple(transcript),
        stderr="".join(stderr_lines),
        returncode=process.returncode,
    )


def _read_text(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return None


def compare_artifacts(source: Artifact, runtime: Artifact) -> dict[str, Any]:
    source_inventory = inventory(source.path)
    runtime_inventory = inventory(runtime.path)
    keys = sorted(set(source_inventory) | set(runtime_inventory))
    changed = [
        key for key in keys if source_inventory.get(key) != runtime_inventory.get(key)
    ]
    text_diffs: dict[str, str] = {}
    if source.path.is_file() and runtime.path.is_file() and changed:
        source_text = _read_text(source.path)
        runtime_text = _read_text(runtime.path)
        if source_text is not None and runtime_text is not None:
            text_diffs[source.path.name] = "".join(
                unified_diff(
                    runtime_text,
                    source_text,
                    fromfile=f"runtime/{runtime.label}",
                    tofile=f"source/{source.label}",
                )
            )
    elif source.path.is_dir() and runtime.path.is_dir():
        for key in changed:
            source_file = source.path / key
            runtime_file = runtime.path / key
            if not source_file.is_file() or not runtime_file.is_file():
                continue
            source_text = _read_text(source_file)
            runtime_text = _read_text(runtime_file)
            if source_text is not None and runtime_text is not None:
                text_diffs[key] = "".join(
                    unified_diff(
                        runtime_text,
                        source_text,
                        fromfile=f"runtime/{runtime.label}/{key}",
                        tofile=f"source/{source.label}/{key}",
                    )
                )
    return {
        "equal": not changed,
        "changed_paths": changed,
        "source": {"path": str(source.path), "sha256": source_inventory},
        "runtime": {"path": str(runtime.path), "sha256": runtime_inventory},
        "text_diffs": text_diffs,
    }


def copy_rollback_artifact(artifact: Artifact, root: Path) -> Path:
    destination = root / artifact.label
    if artifact.path.is_symlink():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(os.readlink(artifact.path))
    elif artifact.path.is_dir():
        shutil.copytree(artifact.path, destination, symlinks=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact.path, destination)
    return destination


def paired_artifacts(
    sources: Iterable[Artifact], runtimes: Iterable[Artifact]
) -> list[tuple[Artifact, Artifact]]:
    source_by_label = {artifact.label: artifact for artifact in sources}
    runtime_by_label = {artifact.label: artifact for artifact in runtimes}
    if source_by_label.keys() != runtime_by_label.keys():
        missing_runtime = sorted(source_by_label.keys() - runtime_by_label.keys())
        missing_source = sorted(runtime_by_label.keys() - source_by_label.keys())
        raise ValueError(
            f"artifact labels differ; missing runtime={missing_runtime}, "
            f"missing source={missing_source}"
        )
    return [(source_by_label[label], runtime_by_label[label]) for label in sorted(source_by_label)]


def write_report(
    output_dir: Path,
    name: str,
    command: list[str],
    capture: Capture,
    comparisons: dict[str, dict[str, Any]],
    rollback_paths: dict[str, str],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "initialize.json").write_text(
        canonical_json(normalize(capture.initialize)), encoding="utf-8"
    )
    (output_dir / "tools-list.json").write_text(
        canonical_json(normalize(capture.tools_list)), encoding="utf-8"
    )
    (output_dir / "transcript.jsonl").write_text(
        "".join(json.dumps(normalize(item), sort_keys=True) + "\n" for item in capture.transcript),
        encoding="utf-8",
    )
    (output_dir / "stderr.log").write_text(capture.stderr, encoding="utf-8")
    for label, comparison in comparisons.items():
        diff_dir = output_dir / "diffs" / label
        diff_dir.mkdir(parents=True, exist_ok=True)
        for relative, content in comparison["text_diffs"].items():
            safe_name = relative.replace("/", "__") + ".diff"
            (diff_dir / safe_name).write_text(content, encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "name": name,
        "command": command,
        "process_returncode_after_capture": capture.returncode,
        "protocol": {
            "initialize": "initialize.json",
            "tools_list": "tools-list.json",
            "transcript": "transcript.jsonl",
            "stderr": "stderr.log",
        },
        "comparisons": comparisons,
        "rollback_artifacts": rollback_paths,
    }
    (output_dir / "manifest.json").write_text(canonical_json(manifest), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--source", action="append", default=[], type=parse_artifact)
    parser.add_argument("--runtime", action="append", default=[], type=parse_artifact)
    parser.add_argument("--fail-on-diff", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    pairs = paired_artifacts(args.source, args.runtime)
    if args.output_dir.exists():
        parser.error(f"output directory already exists: {args.output_dir}")

    capture = capture_session(command, args.timeout)
    comparisons = {
        source.label: compare_artifacts(source, runtime)
        for source, runtime in pairs
    }
    staging = args.output_dir.with_name(args.output_dir.name + ".staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    try:
        rollback_paths = {
            runtime.label: str(
                copy_rollback_artifact(runtime, staging / "rollback").relative_to(staging)
            )
            for _, runtime in pairs
        }
        write_report(
            staging / "report",
            args.name,
            command,
            capture,
            comparisons,
            rollback_paths,
        )
        shutil.move(str(staging / "report"), args.output_dir)
        if (staging / "rollback").exists():
            shutil.move(str(staging / "rollback"), args.output_dir / "rollback")
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return int(args.fail_on_diff and any(not item["equal"] for item in comparisons.values()))


if __name__ == "__main__":
    raise SystemExit(main())
