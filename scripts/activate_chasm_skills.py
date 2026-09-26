#!/usr/bin/env python3
"""Compose and atomically activate a Chasm runtime skill snapshot.

The default invocation is a preview. Applying writes only immutable snapshots,
the selected runtime's host-synced link, and (for Pi) an archive of conflicting
selected entries. Unrelated discovery cleanup is explicit opt-in.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time

NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")


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


def prepare(runtime: str, bundle: Path, home: Path, snapshot_root: Path, *, archive_unrelated: bool = False) -> dict:
    if runtime not in ("codex", "pi"):
        raise ValueError("Runtime must be codex or pi")
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
    link = (home / ".codex/skills/host-synced" if runtime == "codex"
            else home / ".pi/agent/skills/host-synced")
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
    selected_names = final_names if archive_unrelated else {p.name for p in skills.iterdir()}
    archive_candidates = (_pi_archive_candidates(pi_root, selected_names, include_broken=archive_unrelated)
                          if runtime == "pi" else [])
    return {"runtime": runtime, "bundle": bundle, "home": home, "snapshot_root": snapshot_root,
            "runtime_root": runtime_root, "link": link, "old": old, "digest": digest,
            "final_names": final_names, "archive_candidates": archive_candidates}


def apply(plan: dict) -> tuple[Path, Path | None, Path | None]:
    runtime = plan["runtime"]
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
        # Restore prior discovery link after an archive failure.
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
    parser.add_argument("--runtime", required=True, choices=("codex", "pi"))
    parser.add_argument("--bundle", required=True, type=Path, help="Bundle root with skills/ and optional references/")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Agent home (default: current user's home)")
    parser.add_argument("--snapshot-root", type=Path, default=Path("/workspace/.agent-skills"))
    parser.add_argument("--apply", action="store_true", help="Write snapshot and atomically activate it")
    parser.add_argument("--archive-unrelated", action="store_true",
                        help="Also archive unrelated Pi duplicate and broken discovery entries")
    args = parser.parse_args(argv)
    try:
        plan = prepare(args.runtime, args.bundle, args.home, args.snapshot_root, archive_unrelated=args.archive_unrelated)
        print(f"runtime: {plan['runtime']}")
        print(f"active link: {plan['link']}")
        print(f"old link target: {plan['old'] if plan['old'] else '(absent)'}")
        print(f"new snapshot: {plan['runtime_root'] / plan['digest']}")
        print(f"skills: {len(plan['final_names'])} total ({len(plan['archive_candidates'])} Pi entries to archive)")
        for candidate in plan["archive_candidates"]:
            print(f"archive Pi entry: {candidate}")
        if not args.apply:
            print("dry run; pass --apply to activate")
            return 0
        final, old, archive = apply(plan)
        print(f"activated: {final / 'skills'}")
        print(f"rollback target: {old if old else '(remove host-synced link)'}")
        if archive:
            print(f"Pi archive: {archive}")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
