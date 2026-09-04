#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import json
import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_FRONTMATTER_PROPERTIES = frozenset(
    {
        "name",
        "description",
        "license",
        "allowed-tools",
        "metadata",
        "argument-hint",
        "disable-model-invocation",
        "author",
        "version",
    }
)


class FrontmatterError(ValueError):
    """Raised when skill frontmatter is outside the supported YAML subset."""


def parse_scalar(raw_value):
    """Parse a strict YAML subset; ambiguous/unsupported values must be quoted."""
    value = raw_value.strip()
    if not value:
        return {}
    if value.startswith('"'):
        quoted = re.fullmatch(r'("(?:\\.|[^"\\])*")(?:\s+#.*)?', value)
        if quoted is None:
            raise FrontmatterError("Invalid double-quoted value")
        try:
            return json.loads(quoted.group(1))
        except json.JSONDecodeError as error:
            raise FrontmatterError(
                f"Invalid double-quoted value: {error.msg}"
            ) from error
    if value.startswith("'"):
        quoted = re.fullmatch(r"('(?:''|[^'])*')(?:\s+#.*)?", value)
        if quoted is None:
            raise FrontmatterError("Invalid single-quoted value")
        return quoted.group(1)[1:-1].replace("''", "'")
    value = re.split(r"(?:^|\s+)#", value, maxsplit=1)[0].rstrip()
    if not value:
        return None
    if value[0] in "[]{}&*!|>%@`" or re.search(r":(?:\s|$)|^[?:-](?:\s|$)", value):
        raise FrontmatterError("Unsupported YAML value; quote scalar text")
    if value.lower() in {"true", "false", "yes", "no", "on", "off"}:
        return value.lower() in {"true", "yes", "on"}
    if value.lower() in {"null", "~"}:
        return None
    if re.fullmatch(r"[-+]?(?:0|[1-9]\d*)", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+)", value):
        return float(value)
    if re.fullmatch(
        r"[-+]?(?:0x[\da-f_]+|0o[0-7_]+|0b[01_]+"
        r"|(?:\d[\d_]*(?:\.[\d_]*)?|\.[\d_]+)(?:e[-+]?[\d_]+)?"
        r"|(?:\d+:)+[\d.]+|\.(?:inf|nan))"
        r"|\d{4}-\d{1,2}-\d{1,2}(?:[Tt ]\d.*)?",
        value,
        re.IGNORECASE,
    ):
        raise FrontmatterError("Unsupported numeric/date-like value; quote scalar text")
    return value


def parse_frontmatter(frontmatter_text):
    """Parse the top-level mapping and nested mappings used by this package."""
    frontmatter = {}
    current_mapping = None
    mapping_indent = None

    for line_number, line in enumerate(frontmatter_text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace():
            if current_mapping is None:
                raise FrontmatterError(
                    f"Unexpected indentation on frontmatter line {line_number}"
                )
            indent = len(line) - len(line.lstrip(" "))
            if "\t" in line[: len(line) - len(line.lstrip())] or (
                mapping_indent is not None and indent != mapping_indent
            ):
                raise FrontmatterError(
                    f"Unsupported indentation on frontmatter line {line_number}"
                )
            mapping_indent = indent
            nested = line.strip()
            key, separator, raw_value = nested.partition(":")
            if not separator or not key.strip():
                raise FrontmatterError(
                    f"Invalid nested mapping on frontmatter line {line_number}"
                )
            mapping = frontmatter[current_mapping]
            nested_key = key.strip()
            if (
                not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", nested_key)
                or not raw_value.strip()
            ):
                raise FrontmatterError(
                    f"Unsupported nested mapping on frontmatter line {line_number}"
                )
            if nested_key in mapping:
                raise FrontmatterError(
                    f"Duplicate nested key '{nested_key}' on frontmatter line {line_number}"
                )
            mapping[nested_key] = parse_scalar(raw_value)
            continue

        key, separator, raw_value = line.partition(":")
        key = key.strip()
        if not separator or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
            raise FrontmatterError(f"Invalid mapping on frontmatter line {line_number}")
        if key in frontmatter:
            raise FrontmatterError(
                f"Duplicate key '{key}' on frontmatter line {line_number}"
            )
        frontmatter[key] = parse_scalar(raw_value)
        current_mapping = key if frontmatter[key] == {} else None
        mapping_indent = None

    return frontmatter


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = parse_frontmatter(frontmatter_text)
    except FrontmatterError as error:
        return False, f"Invalid YAML frontmatter: {error}"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_PROPERTIES
    if unexpected_keys:
        allowed = ", ".join(sorted(ALLOWED_FRONTMATTER_PROPERTIES))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
        )

    expected_types = {
        "argument-hint": str,
        "disable-model-invocation": bool,
        "author": str,
        "version": str,
    }
    for key, expected_type in expected_types.items():
        value = frontmatter.get(key)
        if key in frontmatter and not isinstance(value, expected_type):
            return (
                False,
                f"'{key}' must be {expected_type.__name__}, got {type(value).__name__}",
            )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return False, "Name must not be empty"
    if not re.match(r"^[a-z0-9-]+$", name):
        return (
            False,
            f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
        )
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return (
            False,
            f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
        )
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return (
            False,
            f"Name is too long ({len(name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
        )
    if skill_path.name != name:
        return (
            False,
            f"Skill directory '{skill_path.name}' must match frontmatter name '{name}'",
        )

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return False, "Description must not be empty"
    if description.startswith("[TODO:"):
        return False, "Description contains an unfinished TODO placeholder"
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return (
            False,
            f"Description is too long ({len(description)} characters). Maximum is 1024 characters.",
        )

    body = content[match.end() :]
    fence_marker = None
    fence_length = 0
    for line in body.splitlines():
        fence = re.match(r"^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$", line)
        if fence:
            marker = fence.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
                fence_length = len(marker)
            elif (
                marker[0] == fence_marker
                and len(marker) >= fence_length
                and not fence.group(2).strip()
            ):
                fence_marker = None
                fence_length = 0
            continue

        if fence_marker is None and re.fullmatch(
            r"[ ]{0,3}\[TODO:[^\n]*\][ \t]*", line
        ):
            return False, "Skill instructions contain an unfinished TODO placeholder"

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
