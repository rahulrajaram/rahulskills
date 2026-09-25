#!/usr/bin/env python3
"""Synchronize local Pi or Codex skills into a selected running Chasm guest."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import re
import subprocess
import tempfile
from typing import Any, Iterable

MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024
FORBIDDEN = {".env", ".git", "__pycache__", ".cache", "node_modules", "auth.json", "id_rsa", "id_ed25519"}
SKIP_NAMES = {".git", "__pycache__", ".cache", "node_modules", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
DEFAULT_SOURCE = Path.home() / ".pi/agent/skills"
DEFAULT_ALLOWED = (DEFAULT_SOURCE,)
GUEST_ROOT = Path("/workspace/.agent-skills/pi")
GUEST_LINK = Path("/home/agent/.pi/agent/skills/host-synced")
RUNTIME_PATHS = {
    "pi": (Path("/workspace/.agent-skills/pi"), Path("/home/agent/.pi/agent/skills/host-synced")),
    "codex": (Path("/workspace/.agent-skills/codex"), Path("/home/agent/.codex/skills/host-synced")),
}


def _inside(path: Path, roots: Iterable[Path]) -> bool:
    resolved = path.resolve(strict=True)
    return any(resolved == root or root in resolved.parents for root in roots)


def _safe_name(name: str) -> bool:
    lowered = name.lower()
    return (
        name not in FORBIDDEN
        and not name.startswith("id_")
        and not lowered.endswith((".pem", ".key", ".p12", ".pfx"))
        and not lowered.startswith(("credential", "token", "secret", "auth"))
    )


def _read_regular(path: Path) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE:
            raise ValueError(f"not a bounded regular file: {path}")
        data = stream.read(MAX_FILE + 1)
        if len(data) > MAX_FILE:
            raise ValueError(f"file grew beyond cap: {path}")
        return data


def _walk(source: Path, root_name: str, allowed: tuple[Path, ...], seen: set[Path] | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    total = 0
    seen = set() if seen is None else seen
    queue = [(source, Path(root_name))]
    while queue:
        if len(seen) + len(records) > 10000:
            raise ValueError("source entry cap exceeded")
        path, relative = queue.pop(0)
        if path.name in SKIP_NAMES:
            continue
        if not _safe_name(path.name):
            raise ValueError(f"forbidden path component: {path}")
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            target = path.resolve(strict=True)
            if not _inside(target, allowed):
                raise ValueError(f"symlink escapes allowed roots: {path}")
            if any(not _safe_name(part) for part in target.relative_to(next(root for root in allowed if target.is_relative_to(root))).parts):
                raise ValueError(f"unsafe symlink target: {path}")
            path = target
            info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            resolved_dir = path.resolve()
            if resolved_dir in seen:
                raise ValueError(f"symlink cycle or repeated directory: {path}")
            seen.add(resolved_dir)
            for child in sorted(path.iterdir(), key=lambda item: item.name):
                if child.name in SKIP_NAMES:
                    continue
                if not _safe_name(child.name):
                    raise ValueError(f"forbidden path component: {child}")
                queue.append((child, relative / child.name))
            continue
        data = _read_regular(path)
        total += len(data)
        if total > MAX_TOTAL:
            raise ValueError("total payload size cap exceeded")
        mode = stat.S_IMODE(info.st_mode) & 0o777
        records.append({"path": relative.as_posix(), "mode": mode, "sha256": hashlib.sha256(data).hexdigest(), "data": base64.b64encode(data).decode("ascii")})
    return records


def build_manifest(
    source: Path,
    allowed_roots: Iterable[Path] = DEFAULT_ALLOWED,
    extra_skills: Iterable[Path] = (),
    references: Path | None = None,
) -> dict[str, Any]:
    source = source.expanduser()
    allowed = tuple(root.expanduser().resolve() for root in allowed_roots)
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"skill source must be a real directory: {source}")
    records: list[dict[str, Any]] = []
    for child in sorted(source.iterdir(), key=lambda item: item.name):
        if child.name in SKIP_NAMES:
            continue
        if child.name == ".system":
            continue
        if not _safe_name(child.name):
            raise ValueError(f"forbidden source entry: {child}")
        if child.is_symlink() or child.is_dir():
            records.extend(_walk(child, f"skills/{child.name}", allowed))
        elif child.is_file() and child.suffix == ".md":
            records.extend(_walk(child, f"skills/{child.name}", allowed))
        else:
            raise ValueError(f"unsupported source entry: {child}")
    for extra in extra_skills:
        extra = extra.expanduser()
        if not extra.is_dir() or extra.is_symlink():
            raise ValueError(f"extra skill must be a real directory: {extra}")
        records.extend(_walk(extra, f"skills/{extra.name}", allowed))
    if references is not None:
        references = references.expanduser()
        if not references.is_dir() or references.is_symlink():
            raise ValueError(f"references must be a real directory: {references}")
        records.extend(_walk(references, "references", allowed))
    if sum(len(base64.b64decode(record["data"])) for record in records) > MAX_TOTAL:
        raise ValueError("total payload size cap exceeded")
    if len({record["path"] for record in records}) != len(records):
        raise ValueError("duplicate destination paths")
    records.sort(key=lambda record: record["path"])
    identity = [{key: record[key] for key in ("path", "mode", "sha256")} for record in records]
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    excluded = sorted(str(path.relative_to(source)) for path in source.rglob("*") if path.name in SKIP_NAMES)
    return {"schema": 1, "source": str(source.resolve()), "hash": digest, "files": records, "excluded": excluded}


def _incus_prefix() -> list[str]:
    for prefix in (["incus"], ["sudo", "-n", "incus"]):
        try:
            result = subprocess.run([*prefix, "list", "--format", "json"], capture_output=True, timeout=15, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0:
            return prefix
    raise RuntimeError("Incus unavailable through local or sudo -n access")


def guest_status(sandbox: str = "development", prefix: list[str] | None = None) -> str:
    prefix = prefix or _incus_prefix()
    result = subprocess.run([*prefix, "list", "--format", "json"], capture_output=True, timeout=15, check=True)
    for row in json.loads(result.stdout):
        if row.get("name") == f"sandbox-{sandbox}":
            return "running" if str(row.get("status", "")).upper() == "RUNNING" else "stopped"
    raise RuntimeError("selected sandbox does not exist")


GUEST_APPLY = r'''import base64, hashlib, json, os, pathlib, re, stat, sys, tempfile
payload = json.load(sys.stdin)
runtime_paths = {"pi": ("/workspace/.agent-skills/pi", "/home/agent/.pi/agent/skills/host-synced"), "codex": ("/workspace/.agent-skills/codex", "/home/agent/.codex/skills/host-synced")}
if payload.get("runtime") not in runtime_paths:
    raise SystemExit("invalid runtime")
root = pathlib.Path(payload["root"])
link = pathlib.Path(payload["link"])
if (str(root), str(link)) != runtime_paths[payload["runtime"]]:
    raise SystemExit("invalid managed destination")
if not re.fullmatch("[0-9a-f]{64}", payload["hash"]):
    raise SystemExit("invalid generation hash")
if any(p.is_symlink() for p in [root, *root.parents, link.parent, *link.parent.parents]):
    raise SystemExit("managed destination ancestor is symlink")

def identity(files):
    return [{k: f[k] for k in ("path", "mode", "sha256")} for f in files]

def digest(files):
    return hashlib.sha256(json.dumps(identity(files), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def validate_paths(files):
    paths = []
    for entry in files:
        rel = pathlib.PurePosixPath(entry["path"])
        if rel.is_absolute() or ".." in rel.parts or len(rel.parts) < 2 or rel.parts[0] not in ("skills", "references"):
            raise SystemExit("unsafe relative path")
        if entry["mode"] < 0 or entry["mode"] > 0o777:
            raise SystemExit("unsafe file mode")
        paths.append(str(rel))
    if len(paths) != len(set(paths)):
        raise SystemExit("duplicate paths")

def verify(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise SystemExit("unmanaged generation")
    marker = directory / ".sync-manifest.json"
    if marker.is_symlink() or not marker.is_file():
        raise SystemExit("unmanaged generation marker")
    stored = json.loads(marker.read_text())
    files = stored["files"]
    validate_paths(files)
    if stored["hash"] != directory.name or digest(files) != directory.name:
        raise SystemExit("generation identity changed")
    expected = {".sync-manifest.json", *(f["path"] for f in files)}
    actual = set()
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise SystemExit("managed generation symlink conflict")
        if path.is_file():
            actual.add(str(path.relative_to(directory)))
        elif not path.is_dir():
            raise SystemExit("managed generation special file conflict")
    if actual != expected:
        raise SystemExit("managed generation contains missing or unexpected files")
    for entry in files:
        path = directory / entry["path"]
        if path.stat().st_size > 8 * 1024 * 1024:
            raise SystemExit("managed generation file exceeds cap")
        if stat.S_IMODE(path.stat().st_mode) != entry["mode"] or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise SystemExit("managed generation was edited")

files = payload["files"]
validate_paths(files)
if digest(files) != payload["hash"]:
    raise SystemExit("payload identity mismatch")
generation = root / payload["hash"]
if link.exists() or link.is_symlink():
    if not link.is_symlink():
        raise SystemExit("unmanaged host-synced collision")
    old = pathlib.Path(os.readlink(link))
    if not old.is_absolute() or old.name != "skills" or old.parent.parent != root:
        raise SystemExit("unmanaged host-synced target")
    verify(old.parent)
if generation.exists() or generation.is_symlink():
    verify(generation)
else:
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    stage = pathlib.Path(tempfile.mkdtemp(prefix=".sync-", dir=root))
    total = 0
    for entry in files:
        data = base64.b64decode(entry["data"], validate=True)
        total += len(data)
        if len(data) > 8 * 1024 * 1024 or total > 64 * 1024 * 1024:
            raise SystemExit("payload size limit")
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise SystemExit("payload hash mismatch")
        out = stage / entry["path"]
        out.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        out.write_bytes(data)
        out.chmod(entry["mode"])
    (stage / ".sync-manifest.json").write_text(json.dumps({"hash": payload["hash"], "files": identity(files)}, sort_keys=True))
    os.rename(stage, generation)
    verify(generation)
unchanged = link.is_symlink() and os.readlink(link) == str(generation / "skills")
if not unchanged:
    link.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    temporary = link.with_name(".host-synced." + str(os.getpid()))
    temporary.symlink_to(generation / "skills")
    os.replace(temporary, link)
print(json.dumps({"generation": str(generation), "link": str(link), "hash": payload["hash"], "unchanged": unchanged}))
'''

def apply_manifest(manifest: dict[str, Any], sandbox: str = "development", runtime: str = "pi") -> dict[str, Any]:
    if runtime not in RUNTIME_PATHS:
        raise ValueError("runtime must be pi or codex")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", sandbox):
        raise ValueError("invalid sandbox name")
    prefix = _incus_prefix()
    status = guest_status(sandbox, prefix)
    if status != "running":
        return {"status": "skipped", "reason": f"guest-{status}"}
    guest_root, guest_link = RUNTIME_PATHS[runtime]
    payload = {"runtime": runtime, "root": str(guest_root), "link": str(guest_link), **manifest}
    result = subprocess.run([*prefix, "exec", f"sandbox-{sandbox}", "--user", "1001", "--group", "1001", "--", "/usr/bin/python3", "-I", "-c", "import json,sys;exec(json.loads(sys.stdin.readline()))"], input=(json.dumps(GUEST_APPLY) + "\n" + json.dumps(payload, sort_keys=True)).encode(), capture_output=True, timeout=90, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace")[:1000])
    return {"status": "applied", **json.loads(result.stdout)}


@contextmanager
def _process_lock():
    lock_path = Path.home() / ".local/state/rahulskills/sync_pi_guest.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=tuple(RUNTIME_PATHS), default="pi")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--sandbox", default="development")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--allow-root", type=Path, action="append", default=[])
    parser.add_argument("--extra-skill", type=Path, action="append", default=[])
    parser.add_argument("--references", type=Path)
    args = parser.parse_args(argv)
    try:
        source = args.source or (DEFAULT_SOURCE if args.runtime == "pi" else Path.home() / ".codex/skills")
        allowed = tuple(args.allow_root) or DEFAULT_ALLOWED
        if args.runtime == "codex" and args.source is None:
            allowed = (*allowed, source)
        manifest = build_manifest(source, allowed, args.extra_skill, args.references)
        result = {"status": "check", "runtime": args.runtime, "hash": manifest["hash"], "files": len(manifest["files"])}
        if args.apply:
            with _process_lock():
                result = {**result, **apply_manifest(manifest, args.sandbox, args.runtime)}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"sync refused: {error}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
