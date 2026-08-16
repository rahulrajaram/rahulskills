from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


REPO = Path(__file__).parents[1]
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
SKILLS = {
    "invokellm": (
        "[cli[,cli...]] <prompt> [--model MODEL] [--session NAME] "
        "[--context-file FILE] [--timeout SECS] [--write]",
        "gptengage-invoke.md",
    ),
    "debate": (
        '<topic> [--rounds N] [--participants "cli:persona,..."] '
        "[--agent CLI] [--synthesize]",
        "gptengage-debate.md",
    ),
    "ideate": (
        "<seed> [--sigma 1.0] [--depth 2] [--cli claude] [--select]",
        "gptengage-ideate.md",
    ),
}


def metadata(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    assert match is not None
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            raw_value = value.strip()
            result[key] = (
                json.loads(raw_value)
                if raw_value.startswith('"') and raw_value.endswith('"')
                else raw_value
            )
    return result


class GptengageSkillTests(unittest.TestCase):
    def test_manifests_are_concise_compatible_routers(self) -> None:
        for name, (argument_hint, operation_reference) in SKILLS.items():
            with self.subTest(skill=name):
                text = (REPO / "skills" / name / "SKILL.md").read_text()
                frontmatter = metadata(text)
                self.assertEqual(frontmatter["name"], name)
                self.assertEqual(frontmatter["argument-hint"], argument_hint)
                self.assertIn(f"/{name}", frontmatter["description"])
                self.assertIn(f"${name}", frontmatter["description"])
                self.assertIn("gptengage-invocation.md", text)
                self.assertIn(operation_reference, text)
                self.assertNotIn("| Flag |", text)
                self.assertLessEqual(len(text.splitlines()), 60)

    def test_operation_contracts_preserve_required_boundaries(self) -> None:
        common = (REPO / "references" / "gptengage-invocation.md").read_text()
        invoke = (REPO / "references" / "gptengage-invoke.md").read_text()
        debate = (REPO / "references" / "gptengage-debate.md").read_text()
        ideate = (REPO / "references" / "gptengage-ideate.md").read_text()

        for phrase in ("outbound data", "--write", "sessions", "argument vector"):
            self.assertIn(phrase, common)
        self.assertIn("gemini`, `claude`, then\n  `codex", invoke)
        self.assertIn("defaults to 600 seconds", invoke)
        self.assertIn("synthesis adds another external call", debate)
        self.assertIn("per-invocation", debate)
        self.assertIn("depth is 1-5", ideate)
        self.assertIn("require `--force`", ideate)
