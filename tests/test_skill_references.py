from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO = Path(__file__).parents[1]
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


class SkillReferenceTests(unittest.TestCase):
    def test_relative_skill_links_resolve(self) -> None:
        missing: list[str] = []
        for manifest in sorted((REPO / "skills").glob("*/SKILL.md")):
            for raw_target in LINK.findall(manifest.read_text()):
                target = raw_target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("/"):
                    continue
                if not (manifest.parent / target).resolve().exists():
                    missing.append(f"{manifest.relative_to(REPO)} -> {raw_target}")
        self.assertEqual(missing, [])
