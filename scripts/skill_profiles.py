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
from urllib.parse import urldefrag, unquote

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ".rahulskills-ownership.json"
NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
MARKDOWN_LINK = re.compile(r"!?(?:\[[^]]*\])\(([^)]+)\)")
PORTABLE_VERSION = 1


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


@dataclass(frozen=True)
class PortabilityFinding:
    path: str
    kind: str
    detail: str


def _ignored_portable(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo")


def _assert_portable_path(root: Path, path: Path) -> None:
    """Reject symlink ancestors and paths that resolve outside the source root."""
    root = root.resolve()
    candidate = path.absolute()
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ValueError(f"Portable resource escapes source root: {path}") from error
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Portable bundles reject symlink path component: {current.relative_to(root)}")
    if not candidate.resolve().is_relative_to(root):
        raise ValueError(f"Portable resource escapes source root: {path}")


def _relative_target(source: Path, owner: Path, raw_target: str) -> Path | None:
    target, _fragment = urldefrag(unquote(raw_target.strip().strip("<>")))
    if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    if Path(target).is_absolute():
        return Path(target)
    candidate = (owner.parent / target).resolve()
    try:
        candidate.relative_to(source.resolve())
    except ValueError:
        return candidate
    return candidate


def referenced_resources(
    root: Path, names: tuple[str, ...], payloads: tuple[str, ...] = ()
) -> tuple[set[Path], tuple[PortabilityFinding, ...]]:
    """Resolve Markdown links from selected skills to repo-local resources.

    Complete selected skill directories and explicitly declared payloads are
    included. Markdown links outside those roots are audit findings only; prose
    path examples therefore cannot silently enlarge a bundle.
    """
    root = root.resolve()
    for name in names:
        if not NAME.fullmatch(name):
            raise ValueError(f"Invalid skill name: {name}")
    resources = {root / "skills" / name for name in names}
    declared = set()
    for payload in payloads:
        if Path(payload).is_absolute() or ".." in Path(payload).parts:
            raise ValueError(f"Portable payload must be repo-relative: {payload}")
        candidate = root / payload
        _assert_portable_path(root, candidate)
        if not candidate.exists():
            raise ValueError(f"Missing portable payload: {payload}")
        declared.add(candidate)
    resources |= declared
    allowed_roots = tuple(resources)
    queue = list(resources)
    findings: list[PortabilityFinding] = []
    seen: set[Path] = set()
    root_resolved = root.resolve()
    while queue:
        current = queue.pop()
        if current in seen or _ignored_portable(current):
            continue
        if current.is_symlink():
            raise ValueError(f"Portable bundles reject symlinks: {current.relative_to(root)}")
        _assert_portable_path(root, current)
        if not current.exists():
            raise ValueError(f"Missing selected portable resource: {current.relative_to(root)}")
        seen.add(current)
        if current.is_dir():
            children = [path for path in current.iterdir() if not _ignored_portable(path)]
            resources.update(children)
            queue.extend(children)
            continue
        if current.suffix.lower() not in (".md", ".markdown"):
            continue
        try:
            text = current.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for raw_target in MARKDOWN_LINK.findall(text):
            target = _relative_target(root, current, raw_target)
            if target is None:
                continue
            try:
                relative = target.relative_to(root_resolved)
            except ValueError:
                findings.append(PortabilityFinding(str(target), "host_only", f"reference escapes repository: {raw_target}"))
                continue
            if not target.exists():
                findings.append(PortabilityFinding(relative.as_posix(), "required_missing", f"declared/reference missing from {current.relative_to(root)}"))
                continue
            if target.is_symlink():
                findings.append(PortabilityFinding(relative.as_posix(), "host_only", "referenced resource is a symlink"))
                continue
            if not any(target == allowed or allowed in target.parents for allowed in allowed_roots):
                findings.append(PortabilityFinding(relative.as_posix(), "unlisted_reference", f"referenced by {current.relative_to(root)}; declare with portable_payloads"))
                continue
            resources.add(target)
            queue.append(target)
    return resources, tuple(sorted(findings, key=lambda item: (item.path, item.kind, item.detail)))


def bundle(
    root: Path,
    output: Path,
    runtime: str,
    names: tuple[str, ...],
    payloads: tuple[str, ...] = (),
) -> dict[str, object]:
    """Create a self-contained, offline bundle without touching runtime installs."""
    root = root.resolve()
    for payload in payloads:
        if Path(payload).is_absolute() or ".." in Path(payload).parts:
            raise ValueError(f"Portable payload escapes source root: {payload}")
        candidate = root / payload
        if not candidate.exists():
            raise ValueError(f"Missing portable payload: {payload}")
    resources, findings = referenced_resources(root, names, payloads)
    required = [item for item in findings if item.kind in ("required_missing", "host_only", "unlisted_reference")]
    if required:
        details = ", ".join(f"{item.kind}:{item.path}" for item in required)
        raise ValueError("Bundle has required portability findings: " + details)
    if output.is_symlink():
        raise ValueError(f"Bundle output must not be a symlink: {output}")
    for ancestor in (output, *output.parents):
        if ancestor.is_symlink():
            raise ValueError(f"Bundle output has symlink ancestor: {ancestor}")
    output = output.resolve()
    if output == root or root in output.parents:
        raise ValueError("Bundle output must be outside the source repository")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Bundle output must be absent or empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    directories: list[str] = []
    hashes: dict[str, str] = {}
    for path in sorted(resources):
        if not path.exists() or _ignored_portable(path):
            continue
        relative = path.relative_to(root)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            target.mkdir(exist_ok=True)
        elif path.is_file():
            shutil.copy2(path, target)
        else:
            raise ValueError(f"Portable bundle rejects non-regular resource: {relative}")
        if target.is_file():
            copied.append(relative.as_posix())
            hashes[relative.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
        else:
            directories.append(relative.as_posix())
    manifest = {
        "schema_version": PORTABLE_VERSION,
        "kind": "rahulskills-portable-bundle",
        "runtime": runtime,
        "selection": list(names),
        "files": copied,
        "directories": directories,
        "sha256": hashes,
        "findings": [asdict(item) for item in findings],
        "offline": True,
        "mcp_functionality_verified": False,
    }
    (output / "portable-bundle.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def declared_payloads(root: Path, names: tuple[str, ...]) -> tuple[str, ...]:
    config = tomllib.loads((root / "capabilities/skills.toml").read_text())
    result: set[str] = set()
    for name in names:
        item = config.get("skills", {}).get(name, {})
        if isinstance(item, dict):
            result.update(str(path) for path in item.get("portable_payloads", []))
    return tuple(sorted(result))


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
    parser.add_argument("command", choices=("select", "preview", "apply", "bundle"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--runtime", choices=("codex", "claude", "pi", "opencode"), required=True)
    parser.add_argument("--profile", action="append", default=[])
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--source", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--output", type=Path, help="Empty directory for an offline portable bundle")
    parser.add_argument("--payload", action="append", default=[], help="Repo-relative shared payload (repeatable)")
    parser.add_argument("--links", action="store_true")
    parser.add_argument("--require-safe", action="store_true", help="Fail preview on ownership conflicts")
    parser.add_argument("--remove", action="append", default=[])
    args = parser.parse_args()
    try:
        names = select(args.root, args.runtime, args.profile, args.skill)
        if args.command == "select":
            print("\n".join(names))
            return 0
        if args.command == "bundle":
            if args.output is None:
                parser.error("bundle requires --output")
            payloads = tuple(sorted(set(args.payload) | set(declared_payloads(args.root, names))))
            print(json.dumps(bundle(args.root, args.output, args.runtime, names, payloads), indent=2, sort_keys=True))
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
