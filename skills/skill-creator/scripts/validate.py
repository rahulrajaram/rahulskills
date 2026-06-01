#!/usr/bin/env python3
"""Validate dual-runtime skill files for Claude and Codex agents."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_AGENTS_ROOT = Path.home() / ".agents" / "skills"
DEFAULT_CLAUDE_ROOT = Path.home() / ".claude" / "skills"
SELF_TEST_FIXTURE = "objective-to-dag-decomposition"
RUNTIME_METADATA_KEYS = frozenset({"allowed-tools"})


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    messages: tuple[str, ...]


def skill_file(root: Path, name: str) -> Path:
    return root / name / "SKILL.md"


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    metadata, _ = parse_frontmatter_text(text)
    return metadata


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter marker")

    metadata: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body = "\n".join(lines[index + 1 :])
            if text.endswith("\n"):
                body += "\n"
            return metadata, body
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")

    raise ValueError("missing closing frontmatter marker")


def comparable_skill_parts(path: Path) -> tuple[dict[str, str], str]:
    metadata, body = parse_frontmatter_text(path.read_text(encoding="utf-8"))
    comparable_metadata = {
        key: value for key, value in metadata.items() if key not in RUNTIME_METADATA_KEYS
    }
    return comparable_metadata, body


def only_runtime_metadata_differs(agents_path: Path, claude_path: Path) -> bool:
    return comparable_skill_parts(agents_path) == comparable_skill_parts(claude_path)


def validate_skill(
    name: str,
    agents_root: Path,
    claude_root: Path,
    allow_runtime_metadata_diff: bool = False,
) -> ValidationResult:
    agents_path = skill_file(agents_root, name)
    claude_path = skill_file(claude_root, name)
    errors: list[str] = []

    for label, path in (("agents", agents_path), ("claude", claude_path)):
        if not path.is_file():
            errors.append(f"{label}: missing {path}")
            continue
        try:
            metadata = parse_frontmatter(path)
        except ValueError as exc:
            errors.append(f"{label}: {path}: {exc}")
            continue
        for required_key in ("name", "description"):
            if not metadata.get(required_key):
                errors.append(f"{label}: {path}: missing frontmatter {required_key!r}")

    if agents_path.is_file() and claude_path.is_file():
        if not filecmp.cmp(agents_path, claude_path, shallow=False):
            if not allow_runtime_metadata_diff or not only_runtime_metadata_differs(
                agents_path,
                claude_path,
            ):
                errors.append(
                    "skill files differ; byte-identical SKILL.md files are required "
                    "unless runtime metadata differences are explicitly allowed"
                )

    if errors:
        return ValidationResult(False, tuple(errors))
    return ValidationResult(True, (f"{name}: OK",))


def print_result(result: ValidationResult) -> None:
    stream = sys.stdout if result.ok else sys.stderr
    for message in result.messages:
        print(message, file=stream, flush=True)


def copy_fixture(name: str, agents_root: Path, claude_root: Path, tmp_path: Path) -> tuple[Path, Path]:
    fixture_agents_root = tmp_path / ".agents" / "skills"
    fixture_claude_root = tmp_path / ".claude" / "skills"
    fixture_agents_skill = fixture_agents_root / name
    fixture_claude_skill = fixture_claude_root / name
    fixture_agents_skill.mkdir(parents=True)
    fixture_claude_skill.mkdir(parents=True)
    shutil.copy2(skill_file(agents_root, name), fixture_agents_skill / "SKILL.md")
    shutil.copy2(skill_file(claude_root, name), fixture_claude_skill / "SKILL.md")
    return fixture_agents_root, fixture_claude_root


def run_self_test(agents_root: Path, claude_root: Path) -> bool:
    print(f"self-test: positive fixture {SELF_TEST_FIXTURE}", flush=True)
    positive = validate_skill(SELF_TEST_FIXTURE, agents_root, claude_root)
    print_result(positive)
    if not positive.ok:
        return False

    print("self-test: negative fixture with missing description and divergent content", flush=True)
    with tempfile.TemporaryDirectory(prefix="skill-creator-validate-") as tmp_dir:
        fixture_agents_root, fixture_claude_root = copy_fixture(
            SELF_TEST_FIXTURE,
            agents_root,
            claude_root,
            Path(tmp_dir),
        )
        broken_name = "broken-fixture"
        broken_agents = fixture_agents_root / broken_name
        broken_claude = fixture_claude_root / broken_name
        broken_agents.mkdir(parents=True)
        broken_claude.mkdir(parents=True)
        (broken_agents / "SKILL.md").write_text(
            "---\nname: broken-fixture\n---\n\n# Broken Fixture\n",
            encoding="utf-8",
        )
        (broken_claude / "SKILL.md").write_text(
            "---\nname: broken-fixture\ndescription: Present only here.\n---\n\n# Broken Fixture\n",
            encoding="utf-8",
        )
        negative = validate_skill(broken_name, fixture_agents_root, fixture_claude_root)
        print_result(negative)
        if negative.ok:
            print("negative fixture unexpectedly passed", file=sys.stderr, flush=True)
            return False
        expected_fragments = ("missing frontmatter 'description'", "skill files differ")
        missing = [fragment for fragment in expected_fragments if not any(fragment in msg for msg in negative.messages)]
        if missing:
            print(f"negative fixture did not report expected errors: {missing}", file=sys.stderr, flush=True)
            return False

    print("self-test: OK", flush=True)
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate that a skill has aligned SKILL.md files in ~/.agents and ~/.claude.",
    )
    parser.add_argument("skill", nargs="?", help="Skill directory name to validate.")
    parser.add_argument("--agents-root", type=Path, default=DEFAULT_AGENTS_ROOT)
    parser.add_argument("--claude-root", type=Path, default=DEFAULT_CLAUDE_ROOT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=f"Run validator self-test using {SELF_TEST_FIXTURE} as the positive fixture.",
    )
    parser.add_argument(
        "--allow-runtime-metadata-diff",
        action="store_true",
        help="Allow differences limited to runtime-only frontmatter keys such as allowed-tools.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return 0 if run_self_test(args.agents_root.expanduser(), args.claude_root.expanduser()) else 1

    if not args.skill:
        parser.error("skill is required unless --self-test is used")

    result = validate_skill(
        args.skill,
        args.agents_root.expanduser(),
        args.claude_root.expanduser(),
        args.allow_runtime_metadata_diff,
    )
    print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
