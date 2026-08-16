from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills" / "handoff" / "SKILL.md"
AGENT_PATH = ROOT / "skills" / "handoff" / "agents" / "openai.yaml"
COMMIT_SKILL_PATH = ROOT / "skills" / "commit" / "SKILL.md"
TEMPLATE_PATH = (
    ROOT / "skills" / "handoff" / "references" / "next-shell-prompt-template.md"
)


def _mapping(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        key, separator, value = line.strip().partition(":")
        if not separator or not value.strip():
            continue
        raw = value.strip()
        result[key] = json.loads(raw) if raw.startswith('"') else raw
    return result


class HandoffSkillTests(unittest.TestCase):
    def test_handoff_declares_extract_argument_and_root_artifact(self) -> None:
        text = SKILL_PATH.read_text()
        normalized = " ".join(text.split())
        frontmatter = _mapping(text.split("---", 2)[1])

        self.assertEqual(frontmatter["argument-hint"], "[extract]")
        self.assertIn("<PACKAGE_ROOT>/HANDOFF.md", text)
        self.assertIn("Do not print the prompt to stdout", normalized)
        self.assertIn("$handoff extract", text)

    def test_extract_mode_is_read_only_and_verbatim(self) -> None:
        text = SKILL_PATH.read_text()
        extract = text.split("## Extract Workflow", 1)[1].split("## Autonomy Routing", 1)[0]

        self.assertIn("Do not reconcile docs, commit", text)
        self.assertIn("Emit the file contents verbatim", extract)
        self.assertIn("stop without changing repository state", extract)

    def test_transient_handoff_is_not_committed_or_hidden(self) -> None:
        handoff = SKILL_PATH.read_text()
        commit = COMMIT_SKILL_PATH.read_text()

        self.assertIn("Do not stage or commit", handoff)
        self.assertIn(".git/info/exclude", handoff)
        self.assertIn("`HANDOFF.md`", commit)

    def test_openai_metadata_uses_dollar_invocation(self) -> None:
        metadata = _mapping(AGENT_PATH.read_text())

        self.assertGreaterEqual(len(metadata["short_description"]), 25)
        self.assertLessEqual(len(metadata["short_description"]), 64)
        self.assertIn("$handoff", metadata["default_prompt"])
        self.assertIn("HANDOFF.md", metadata["default_prompt"])

    def test_reference_template_targets_handoff_file(self) -> None:
        template = TEMPLATE_PATH.read_text()

        self.assertIn("# `HANDOFF.md` Template", template)
        self.assertIn("package root", template)
