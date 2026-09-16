#!/usr/bin/env python3
"""Shared skill selection and conservative package migration inspection.

No discovery, download, or dependency activation occurs here. Existing entries
are owned only when their saved package fingerprint still matches disk.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ".rahulskills-ownership.json"
NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")


def exclusions(root: Path, runtime: str) -> set[str]:
    paths = [root / ".exclude-skills", root / "runtime-exclusions" / f"{runtime}.txt"]
    return {line.split("#", 1)[0].strip() for path in paths if path.is_file()
            for line in path.read_text().splitlines() if line.split("#", 1)[0].strip()}


def select(root: Path, runtime: str, profiles: list[str], skills: list[str]) -> tuple[str, ...]:
    config = tomllib.loads((root / "capabilities/install-profiles.toml").read_text())
    inventory = config["profiles"]

    def expand(profile: str, stack: tuple[str, ...] = ()) -> set[str]:
        if profile not in inventory or profile in stack:
            raise ValueError(f"Unknown or cyclic profile: {profile}")
        return set().union(*(expand(name[1:], (*stack, profile)) if name.startswith("@")
                             else {name} for name in inventory[profile]))

    chosen = set(skills)
    for profile in profiles or ([] if skills else [config["default"]]):
        chosen |= expand(profile)
    for name in chosen:
        if not NAME.fullmatch(name):
            raise ValueError(f"Invalid skill name: {name}")
        directory = root / "skills" / name
        if not any((directory / manifest).is_file() for manifest in ("SKILL.md", "skill.md")):
            raise ValueError(f"Skill has no canonical manifest: {name}")
    return tuple(sorted(chosen - exclusions(root, runtime)))


def fingerprint(path: Path) -> str | None:
    if path.is_symlink():
        return "symlink:" + os.readlink(path)
    if not path.exists():
        return None
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(str(path.stat().st_mode & 0o7777).encode())
        digest.update(path.read_bytes())
    elif path.is_dir():
        digest.update(str(path.stat().st_mode & 0o7777).encode())
        for child in sorted(path.rglob("*")):
            if "__pycache__" in child.parts or child.suffix in (".pyc", ".pyo"):
                continue
            digest.update(child.relative_to(path).as_posix().encode())
            digest.update(str(child.lstat().st_mode & 0o7777).encode())
            digest.update((fingerprint(child) if not child.is_dir() or child.is_symlink() else "directory").encode())
    else:
        raise ValueError(f"Unsupported installed entry: {path}")
    return "sha256:" + digest.hexdigest()


def load_ownership(destination: Path, root: Path) -> dict[str, str]:
    path = destination / LEDGER
    if path.is_symlink():
        raise ValueError(f"Refusing symlink ownership ledger: {path}")
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if data.get("source") != str(root.resolve()) or data.get("version") != 1:
        raise ValueError(f"Ownership ledger belongs to another source/version: {path}")
    entries = data.get("entries", {})
    for key in entries:
        if Path(key).is_absolute() or ".." in Path(key).parts or not key.startswith(("skills/", "references/")):
            raise ValueError(f"Unsafe ownership entry: {key}")
    return entries


def safe_parent(destination: Path, relative: str) -> None:
    target = destination / relative
    # Do not write through any existing ancestor symlink, including the root.
    for parent in (destination, *destination.parents, *target.parents):
        if parent.is_symlink():
            raise ValueError(f"Refusing destination ancestor symlink: {parent}")


@dataclass(frozen=True)
class Change:
    path: str
    action: str
    reason: str


def migration(root: Path, source: Path, destination: Path, names: tuple[str, ...],
              *, links: bool = False, remove: tuple[str, ...] = ()) -> tuple[Change, ...]:
    owned = load_ownership(destination, root)
    selected = {f"skills/{name}" for name in names}
    reference_root = source / "references"
    if reference_root.exists():
        selected |= {f"references/{p.relative_to(reference_root).as_posix()}"
                     for p in reference_root.rglob("*") if p.is_file()}
    changes = []
    for key in sorted(selected):
        safe_parent(destination, key)
        current = fingerprint(destination / key)
        desired = "symlink:" + str((source / key).resolve()) if links else fingerprint(source / key)
        if desired is None:
            raise ValueError(f"Missing selected package entry: {source / key}")
        if current is None:
            changes.append(Change(key, "add", "absent"))
        elif current == desired:
            changes.append(Change(key, "unchanged", "matches selected package; ownership unchanged"))
        elif owned.get(key) == current:
            changes.append(Change(key, "update", "unchanged package-owned entry"))
        elif links and current == "symlink:" + str((root / key).resolve()):
            changes.append(Change(key, "unchanged", "existing canonical repository link"))
        else:
            changes.append(Change(key, "blocked", "unmanaged or locally modified entry; preserved"))
    for name in remove:
        if not NAME.fullmatch(name):
            raise ValueError(f"Invalid removal name: {name}")
        key = f"skills/{name}"
        if key in selected:
            raise ValueError(f"Cannot remove selected skill: {name}")
        safe_parent(destination, key)
        current = fingerprint(destination / key)
        canonical_link = links and current == "symlink:" + str(root.resolve() / key)
        action = "remove" if current is not None and (owned.get(key) == current or canonical_link) else "blocked"
        changes.append(Change(key, action, "explicit removal of verified package entry" if action == "remove"
                              else "removal ownership not established; preserved"))
    for key in sorted(set(owned) - selected - {f"skills/{name}" for name in remove}):
        if key.startswith("skills/") and fingerprint(destination / key) is not None:
            changes.append(Change(key, "retain", "outside selection; removal requires explicit --remove"))
    # Legacy optional copies are visible in previews but never adopted or removed.
    skills_dir = destination / "skills"
    if skills_dir.is_dir():
        listed = {change.path for change in changes}
        for entry in sorted(skills_dir.iterdir()):
            key = f"skills/{entry.name}"
            if key not in listed and not entry.name.startswith("."):
                changes.append(Change(key, "retain", "outside selection; ownership not inferred"))
    return tuple(changes)


def apply(root: Path, source: Path, destination: Path, changes: tuple[Change, ...], *, links: bool = False) -> None:
    if any(change.action == "blocked" for change in changes):
        raise ValueError("Migration has ownership conflicts; no installed entries were changed")
    owned = load_ownership(destination, root)
    for change in changes:
        if change.action not in ("add", "update", "remove"):
            continue
        safe_parent(destination, change.path)
        target = destination / change.path
        current = fingerprint(target)
        # Recheck ownership immediately before touching the entry.
        canonical_link = links and current == "symlink:" + str(root.resolve() / change.path)
        if change.action == "add" and current is not None:
            raise ValueError(f"Destination changed after preview: {target}")
        if change.action != "add" and owned.get(change.path) != current and not canonical_link:
            raise ValueError(f"Ownership changed after preview: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        backup = None
        stage_dir = None
        replacement_installed = False
        try:
            if change.action != "remove":
                stage_dir = Path(tempfile.mkdtemp(prefix="migration-stage-", dir=_backup_dir(destination)))
                staged = stage_dir / target.name
                if links:
                    staged.symlink_to((source / change.path).resolve(), target_is_directory=True)
                elif (source / change.path).is_dir():
                    shutil.copytree(source / change.path, staged, symlinks=True,
                                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
                else:
                    shutil.copy2(source / change.path, staged)
            if current is not None:
                backup = Path(tempfile.mkdtemp(prefix="migration-", dir=_backup_dir(destination))) / target.name
                target.rename(backup)
            if change.action == "remove":
                owned.pop(change.path, None)
            else:
                staged.rename(target)
                replacement_installed = True
                owned[change.path] = fingerprint(target)
            write_ownership(destination, root, owned)
        except Exception:
            failed_target = None
            if replacement_installed and (target.exists() or target.is_symlink()):
                failed_target = stage_dir / "failed-replacement"
                target.rename(failed_target)
            if backup is not None and (backup.exists() or backup.is_symlink()) and not target.exists() and not target.is_symlink():
                backup.rename(target)
            if failed_target is not None and (failed_target.exists() or failed_target.is_symlink()):
                if failed_target.is_dir() and not failed_target.is_symlink():
                    shutil.rmtree(failed_target)
                else:
                    failed_target.unlink()
            raise
        finally:
            if stage_dir is not None and stage_dir.exists():
                shutil.rmtree(stage_dir)


def write_ownership(destination: Path, root: Path, owned: dict[str, str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    descriptor, raw = tempfile.mkstemp(prefix=".ownership-", dir=destination)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump({"version": 1, "source": str(root.resolve()), "entries": owned}, stream, indent=2)
            stream.write("\n")
        os.replace(raw, destination / LEDGER)
    finally:
        Path(raw).unlink(missing_ok=True)


def _backup_dir(destination: Path) -> Path:
    path = destination / "skill-backups"
    if path.is_symlink():
        raise ValueError(f"Refusing symlink backup directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("select", "preview", "apply"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--runtime", choices=("codex", "claude", "pi", "opencode"), required=True)
    parser.add_argument("--profile", action="append", default=[])
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--source", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--links", action="store_true")
    parser.add_argument("--require-safe", action="store_true", help="Fail preview on ownership conflicts")
    parser.add_argument("--remove", action="append", default=[])
    args = parser.parse_args()
    try:
        names = select(args.root, args.runtime, args.profile, args.skill)
        if args.command == "select":
            print("\n".join(names))
            return 0
        if args.source is None or args.destination is None:
            parser.error("preview/apply require --source and --destination")
        changes = migration(args.root, args.source, args.destination, names,
                            links=args.links, remove=tuple(args.remove))
        print(json.dumps({"runtime": args.runtime, "selection": names,
                          "changes": [asdict(change) for change in changes]}, indent=2))
        if args.require_safe and any(change.action == "blocked" for change in changes):
            raise ValueError("Migration has ownership conflicts")
        if args.command == "apply":
            apply(args.root, args.source, args.destination, changes, links=args.links)
        return 0
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
