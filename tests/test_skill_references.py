from __future__ import annotations

from pathlib import Path
import re


REPO = Path(__file__).parents[1]
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def test_relative_skill_links_resolve() -> None:
    missing: list[str] = []
    for manifest in sorted((REPO / "skills").glob("*/SKILL.md")):
        for raw_target in LINK.findall(manifest.read_text()):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("/"):
                continue
            if not (manifest.parent / target).resolve().exists():
                missing.append(f"{manifest.relative_to(REPO)} -> {raw_target}")
    assert missing == []
