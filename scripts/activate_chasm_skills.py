#!/usr/bin/env python3
"""Compose and atomically activate a Chasm runtime skill snapshot.

The default invocation is a preview. Applying writes only immutable snapshots,
the selected runtime's host-synced link, and (for Pi) an archive of conflicting
selected entries. Unrelated discovery cleanup is explicit opt-in.

Claude discovers skills only at ``<config>/skills/<name>/SKILL.md`` (no nested
``host-synced`` directory), where ``<config>`` is ``$CLAUDE_CONFIG_DIR`` or
``~/.claude``. For ``--runtime claude`` the hashed snapshot is tracked by a
bookkeeping ``active`` link under the snapshot root and then projected as real
copies into ``<config>/skills`` and ``<config>/references``. Projected entries
are recorded in ``<config>/.chasm-skills-ownership.json``; an entry is updated
or removed only while its fingerprint still matches that ledger, so user-created
or locally edited skills are never replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time

NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
RUNTIMES = ("codex", "pi", "claude")
CLAUDE_LEDGER = ".chasm-skills-ownership.json"
CLAUDE_LEDGER_MANAGER = "rahulskills-chasm-skills"


def check_tree(source: Path, boundary: Path, *, skills: bool = False) -> None:
    """Validate bundle contents and reject links, special files, and escapes."""
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"Expected a real bundle directory: {source}")
    boundary = boundary.resolve(strict=True)
    for path in (source, *sorted(source.rglob("*"))):
        if path.is_symlink():
            raise ValueError(f"Bundle symlinks are not allowed: {path}")
        try:
            path.resolve(strict=True).relative_to(boundary)
        except (OSError, ValueError) as error:
            raise ValueError(f"Bundle resource escapes its root: {path}") from error
        if not (path.is_dir() or path.is_file()):
            raise ValueError(f"Unsupported bundle resource: {path}")
    if skills:
        entries = sorted(source.iterdir())
        if not entries:
            raise ValueError("Bundle skills directory is empty")
        for entry in entries:
            if not NAME.fullmatch(entry.name) or not entry.is_dir():
                raise ValueError(f"Invalid skill entry: {entry}")
            manifests = [p for p in (entry / "SKILL.md", entry / "skill.md") if p.is_file()]
            if len(manifests) != 1:
                raise ValueError(f"Skill must contain exactly one SKILL.md manifest: {entry.name}")


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode())
        if path.is_file():
            digest.update(b"\0file\0")
            digest.update(str(path.stat().st_mode & 0o777).encode())
            digest.update(path.read_bytes())
        elif path.is_dir():
            digest.update(b"\0dir\0")
    return digest.hexdigest()


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    shutil.copytree(source, destination, dirs_exist_ok=True, symlinks=False)


def replace_skills(source: Path, destination: Path) -> None:
    """Overlay whole skill packages so stale files cannot survive an update."""
    destination.mkdir(parents=True, exist_ok=True)
    for incoming in sorted(source.iterdir()):
        target = destination / incoming.name
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.copytree(incoming, target, symlinks=False)


def _active_snapshot(link: Path, snapshot_root: Path, runtime: str) -> Path | None:
    if not os.path.lexists(link):
        return None
    if not link.is_symlink():
        raise ValueError(f"Refusing to replace non-symlink discovery root: {link}")
    target_text = os.readlink(link)
    target = (link.parent / target_text).resolve(strict=True)
    expected = (snapshot_root / runtime).resolve(strict=False)
    try:
        relative = target.relative_to(expected)
    except ValueError as error:
        raise ValueError(f"Active link is outside managed snapshot root: {link} -> {target_text}") from error
    if len(relative.parts) != 2 or relative.parts[1] != "skills" or not re.fullmatch(r"[0-9a-f]{64}", relative.parts[0]):
        raise ValueError(f"Active link does not target a managed hashed snapshot: {link} -> {target_text}")
    if not target.is_dir():
        raise ValueError(f"Active skill snapshot is not a directory: {target}")
    return target


def claude_config_dir(home: Path, explicit: Path | None = None) -> Path:
    """Resolve Claude's configuration root: explicit, then $CLAUDE_CONFIG_DIR, then ~/.claude."""
    if explicit is not None:
        return explicit.expanduser().absolute()
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(configured).expanduser().absolute() if configured else home / ".claude"


def runtime_link(runtime: str, home: Path, snapshot_root: Path) -> Path:
    match runtime:
        case "codex":
            return home / ".codex/skills/host-synced"
        case "pi":
            return home / ".pi/agent/skills/host-synced"
        case "claude":
            # Bookkeeping pointer only; Claude never scans the snapshot root.
            return snapshot_root / "claude" / "active"
    raise ValueError("Runtime must be codex, pi, or claude")


def tree_fingerprint(path: Path) -> str | None:
    """Content identity of a projected entry (file modes and bytes; dir modes excluded)."""
    if path.is_symlink():
        return "symlink:" + os.readlink(path)
    if not path.exists():
        return None
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(b"file\0" + str(path.stat().st_mode & 0o777).encode() + b"\0")
        digest.update(path.read_bytes())
        return "sha256:" + digest.hexdigest()
    if not path.is_dir():
        return "special"
    for child in sorted(path.rglob("*")):
        digest.update(child.relative_to(path).as_posix().encode() + b"\0")
        if child.is_symlink():
            digest.update(b"link\0" + os.readlink(child).encode() + b"\0")
        elif child.is_file():
            digest.update(b"file\0" + str(child.stat().st_mode & 0o777).encode() + b"\0")
            digest.update(hashlib.sha256(child.read_bytes()).digest())
        elif child.is_dir():
            digest.update(b"dir\0")
        else:
            digest.update(b"special\0")
    return "sha256:" + digest.hexdigest()


def _projection_keys(generation: Path) -> list[str]:
    keys = [f"skills/{p.name}" for p in sorted((generation / "skills").iterdir()) if p.is_dir()]
    refs = generation / "references"
    if refs.is_dir():
        keys += [f"references/{p.relative_to(refs).as_posix()}" for p in sorted(refs.rglob("*")) if p.is_file()]
    return keys


def load_claude_ledger(config: Path) -> dict[str, str]:
    path = config / CLAUDE_LEDGER
    if path.is_symlink():
        raise ValueError(f"Refusing symlink ownership ledger: {path}")
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if data.get("version") != 1 or data.get("manager") != CLAUDE_LEDGER_MANAGER:
        raise ValueError(f"Ownership ledger belongs to another manager/version: {path}")
    entries = data.get("entries", {})
    for key in entries:
        parts = Path(key).parts
        if Path(key).is_absolute() or ".." in parts or len(parts) < 2 or parts[0] not in ("skills", "references"):
            raise ValueError(f"Unsafe ownership entry: {key}")
    return dict(entries)


def write_claude_ledger(config: Path, entries: dict[str, str]) -> None:
    descriptor, raw = tempfile.mkstemp(prefix=".chasm-ownership-", dir=config)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump({"version": 1, "manager": CLAUDE_LEDGER_MANAGER, "entries": entries}, stream,
                      indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(raw, config / CLAUDE_LEDGER)
    finally:
        Path(raw).unlink(missing_ok=True)


def plan_claude_projection(generation: Path, config: Path) -> list[tuple[str, str, str | None]]:
    """Return (key, action, desired fingerprint); actions: add/update/unchanged/remove/retain/forget/blocked."""
    for path in (config, *config.parents):
        if path.is_symlink():
            raise ValueError(f"Refusing Claude config path through symlink: {path}")
    for sub in ("skills", "references"):
        if (config / sub).is_symlink() or ((config / sub).exists() and not (config / sub).is_dir()):
            raise ValueError(f"Claude discovery root must be a real directory: {config / sub}")
    owned = load_claude_ledger(config)
    plan: list[tuple[str, str, str | None]] = []
    desired_keys = _projection_keys(generation)
    for key in desired_keys:
        want = tree_fingerprint(generation / key)
        current = tree_fingerprint(config / key)
        if current is None:
            action = "add"
        elif owned.get(key) == current:
            action = "unchanged" if current == want else "update"
        else:
            # Includes identical-but-unowned copies: ownership is never inferred.
            action = "blocked"
        plan.append((key, action, want))
    for key in sorted(set(owned) - set(desired_keys)):
        current = tree_fingerprint(config / key)
        if current is None:
            plan.append((key, "forget", None))
        elif current == owned[key]:
            plan.append((key, "remove", None))
        else:
            plan.append((key, "retain", None))
    return plan


def _remove_entry(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def apply_claude_projection(generation: Path, config: Path, plan: list[tuple[str, str, str | None]]) -> None:
    blocked = [key for key, action, _ in plan if action == "blocked"]
    if blocked:
        raise ValueError("Claude projection conflicts with unmanaged or locally edited entries: " + ", ".join(blocked))
    owned = load_claude_ledger(config)
    config.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".chasm-skills-staging-", dir=config))
    try:
        for index, (key, action, want) in enumerate(plan):
            target = config / key
            current = tree_fingerprint(target)
            if action in ("unchanged", "retain"):
                continue
            if action == "forget":
                owned.pop(key, None)
                write_claude_ledger(config, owned)
                continue
            # Recheck ownership immediately before touching the entry.
            if action == "add" and current is not None:
                raise ValueError(f"Claude entry appeared after preview: {target}")
            if action in ("update", "remove") and owned.get(key) != current:
                raise ValueError(f"Claude entry ownership changed after preview: {target}")
            if action == "remove":
                _remove_entry(target)
                owned.pop(key, None)
                write_claude_ledger(config, owned)
                continue
            source = generation / key
            staged = staging / str(index)
            if source.is_dir():
                shutil.copytree(source, staged, symlinks=False)
            else:
                shutil.copy2(source, staged)
            if tree_fingerprint(staged) != want:
                raise ValueError(f"Snapshot changed while projecting: {source}")
            target.parent.mkdir(parents=True, exist_ok=True)
            retired = staging / f"{index}.old"
            if current is not None:
                os.replace(target, retired)
            try:
                os.replace(staged, target)
            except OSError:
                if os.path.lexists(retired) and not os.path.lexists(target):
                    os.replace(retired, target)
                raise
            owned[key] = want
            write_claude_ledger(config, owned)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _pi_archive_candidates(pi_root: Path, final_names: set[str], *, include_broken: bool = False) -> list[Path]:
    if not pi_root.exists():
        return []
    if pi_root.is_symlink() or not pi_root.is_dir():
        raise ValueError(f"Pi skill discovery root must be a real directory: {pi_root}")
    result = []
    for entry in sorted(pi_root.iterdir()):
        if entry.name == "host-synced":
            continue
        if entry.is_symlink() and not entry.exists():
            if include_broken or entry.name in final_names:
                result.append(entry)
        elif entry.name in final_names:
            result.append(entry)
    return result


def prepare(runtime: str, bundle: Path, home: Path, snapshot_root: Path, *, archive_unrelated: bool = False,
            claude_config: Path | None = None) -> dict:
    if runtime not in RUNTIMES:
        raise ValueError("Runtime must be codex, pi, or claude")
    bundle = bundle.absolute()
    check_tree(bundle, bundle)
    skills = bundle / "skills"
    check_tree(skills, bundle, skills=True)
    refs = bundle / "references"
    if refs.exists() or refs.is_symlink():
        check_tree(refs, bundle)
    home = home.absolute()
    snapshot_root = snapshot_root.absolute()
    runtime_root = snapshot_root / runtime
    link = runtime_link(runtime, home, snapshot_root)
    config = claude_config_dir(home, claude_config) if runtime == "claude" else None
    pi_root = home / ".pi/agent/skills"
    old = _active_snapshot(link, snapshot_root, runtime)
    if old:
        # Never follow legacy snapshot links while composing a new generation.
        check_tree(old, old.parent)
        old_refs = old.parent / "references"
        if old_refs.exists() or old_refs.is_symlink():
            check_tree(old_refs, old.parent)
    # A destination's ancestor chain must not redirect writes elsewhere.
    for path in (home, *home.parents, *link.parents, snapshot_root, *snapshot_root.parents):
        if path.is_symlink():
            raise ValueError(f"Refusing path through symlink: {path}")
    with tempfile.TemporaryDirectory(prefix="chasm-skills-preview-") as temp:
        composed = Path(temp) / "snapshot" / "skills"
        composed.mkdir(parents=True)
        if old:
            old_root = old.parent
            copy_tree(old, composed)
            copy_tree(old_root / "references", composed.parent / "references")
        replace_skills(skills, composed)
        if refs.is_dir():
            copy_tree(refs, composed.parent / "references")
        digest = digest_tree(composed.parent)
        final_names = {p.name for p in composed.iterdir() if p.is_dir()}
        projection = plan_claude_projection(composed.parent, config) if config else []
    selected_names = final_names if archive_unrelated else {p.name for p in skills.iterdir()}
    archive_candidates = (_pi_archive_candidates(pi_root, selected_names, include_broken=archive_unrelated)
                          if runtime == "pi" else [])
    return {"runtime": runtime, "bundle": bundle, "home": home, "snapshot_root": snapshot_root,
            "runtime_root": runtime_root, "link": link, "old": old, "digest": digest,
            "final_names": final_names, "archive_candidates": archive_candidates,
            "claude_config": config, "projection": projection}


def apply(plan: dict) -> tuple[Path, Path | None, Path | None]:
    runtime = plan["runtime"]
    if any(action == "blocked" for _, action, _ in plan["projection"]):
        blocked = [key for key, action, _ in plan["projection"] if action == "blocked"]
        raise ValueError("Claude projection conflicts with unmanaged or locally edited entries: " + ", ".join(blocked))
    bundle: Path = plan["bundle"]
    runtime_root: Path = plan["runtime_root"]
    snapshot_root: Path = plan["snapshot_root"]
    link: Path = plan["link"]
    final = runtime_root / plan["digest"]
    if final.exists():
        if final.is_symlink() or not (final / "skills").is_dir():
            raise ValueError(f"Hashed snapshot path is occupied by invalid content: {final}")
        if digest_tree(final) != plan["digest"]:
            raise ValueError(f"Hashed snapshot content does not match its digest: {final}")
    else:
        runtime_root.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=runtime_root))
        try:
            skills_out = staging / "skills"
            skills_out.mkdir()
            old = plan["old"]
            if old:
                copy_tree(old, skills_out)
                copy_tree(old.parent / "references", staging / "references")
            replace_skills(bundle / "skills", skills_out)
            refs = bundle / "references"
            if refs.is_dir():
                copy_tree(refs, staging / "references")
            if digest_tree(staging) != plan["digest"]:
                raise ValueError("Bundle or active snapshot changed while staging")
            staging.rename(final)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    link.parent.mkdir(parents=True, exist_ok=True)
    # Revalidate just before switching; replace is atomic within the directory.
    current = _active_snapshot(link, snapshot_root, runtime)
    expected_old = plan["old"]
    if current != expected_old:
        raise ValueError("Active link changed after preview; refusing activation")
    temp_link = link.parent / f".host-synced-{os.getpid()}-{time.time_ns()}"
    os.symlink(str(final / "skills"), temp_link)
    try:
        os.replace(temp_link, link)
    finally:
        if os.path.lexists(temp_link):
            temp_link.unlink()

    archive_path = None
    moved: list[tuple[Path, Path]] = []
    try:
        if plan["claude_config"] is not None:
            apply_claude_projection(final, plan["claude_config"], plan["projection"])
        if plan["archive_candidates"]:
            pi_root = plan["home"] / ".pi/agent/skills"
            archive_base = plan["home"] / ".pi/agent/skill-archives"
            archive_base.mkdir(parents=True, exist_ok=True)
            archive_path = archive_base / f"chasm-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}"
            archive_path.mkdir()
            for entry in plan["archive_candidates"]:
                if not os.path.lexists(entry):
                    continue
                target = archive_path / entry.name
                os.replace(entry, target)
                moved.append((entry, target))
    except Exception:
        for source, target in reversed(moved):
            if os.path.lexists(target) and not os.path.lexists(source):
                os.replace(target, source)
        if archive_path and archive_path.exists() and not any(archive_path.iterdir()):
            archive_path.rmdir()
        # Restore the prior discovery link after an archive or projection failure.
        if expected_old:
            rollback_link = link.parent / f".rollback-{os.getpid()}-{time.time_ns()}"
            os.symlink(str(expected_old), rollback_link)
            os.replace(rollback_link, link)
        else:
            link.unlink(missing_ok=True)
        raise
    return final, expected_old, archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, choices=RUNTIMES)
    parser.add_argument("--bundle", required=True, type=Path, help="Bundle root with skills/ and optional references/")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Agent home (default: current user's home)")
    parser.add_argument("--snapshot-root", type=Path, default=Path("/workspace/.agent-skills"))
    parser.add_argument("--apply", action="store_true", help="Write snapshot and atomically activate it")
    parser.add_argument("--archive-unrelated", action="store_true",
                        help="Also archive unrelated Pi duplicate and broken discovery entries")
    parser.add_argument("--claude-config-dir", type=Path,
                        help="Claude config root (default: $CLAUDE_CONFIG_DIR, else HOME/.claude)")
    args = parser.parse_args(argv)
    try:
        plan = prepare(args.runtime, args.bundle, args.home, args.snapshot_root, archive_unrelated=args.archive_unrelated,
                       claude_config=args.claude_config_dir)
        print(f"runtime: {plan['runtime']}")
        print(f"active link: {plan['link']}")
        print(f"old link target: {plan['old'] if plan['old'] else '(absent)'}")
        print(f"new snapshot: {plan['runtime_root'] / plan['digest']}")
        print(f"skills: {len(plan['final_names'])} total ({len(plan['archive_candidates'])} Pi entries to archive)")
        for candidate in plan["archive_candidates"]:
            print(f"archive Pi entry: {candidate}")
        if plan["claude_config"] is not None:
            print(f"claude config: {plan['claude_config']}")
            for key, action, _ in plan["projection"]:
                if action != "unchanged":
                    print(f"claude {action}: {key}")
        if not args.apply:
            print("dry run; pass --apply to activate")
            return 0
        final, old, archive = apply(plan)
        print(f"activated: {final / 'skills'}")
        print(f"rollback target: {old if old else '(remove active link)'}")
        if archive:
            print(f"Pi archive: {archive}")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
