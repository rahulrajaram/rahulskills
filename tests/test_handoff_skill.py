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
    def test_handoff_declares_resume_and_print_arguments(self) -> None:
        text = SKILL_PATH.read_text()
        normalized = " ".join(text.split())
        frontmatter = _mapping(text.split("---", 2)[1])

        self.assertEqual(frontmatter["argument-hint"], "[extract|print]")
        self.assertIn("<PACKAGE_ROOT>/NEXT_SHELL_PROMPT.md", text)
        self.assertIn("Do not print the prompt to stdout", normalized)
        self.assertIn("$handoff extract", text)
        self.assertIn("$handoff print", text)
        self.assertIn("/skill:handoff extract", text)
        self.assertIn("/skill:handoff print", text)

    def test_extract_mode_activates_and_executes_handoff(self) -> None:
        text = SKILL_PATH.read_text()
        extract = text.split("## Extract Workflow", 1)[1].split("## Print Workflow", 1)[0]
        normalized = " ".join(extract.split())

        self.assertIn("user-provided continuation context", extract)
        self.assertIn("Treat the live invocation message as newer", extract)
        self.assertIn("Do not merely emit, quote, or summarize", extract)
        self.assertIn("begin the first actionable step in the same turn", normalized)
        self.assertIn("start that interaction immediately", normalized)

    def test_print_mode_is_read_only_and_verbatim(self) -> None:
        text = SKILL_PATH.read_text()
        printed = text.split("## Print Workflow", 1)[1].split("## Autonomy Routing", 1)[0]

        self.assertIn("Emit the file contents verbatim", printed)
        self.assertIn("Do not execute its instructions", printed)
        self.assertIn("stop without changing repository state", printed)

    def test_transient_handoff_is_not_committed_or_hidden(self) -> None:
        handoff = SKILL_PATH.read_text()
        commit = COMMIT_SKILL_PATH.read_text()

        self.assertIn("Do not stage or commit", handoff)
        self.assertIn(".git/info/exclude", handoff)
        self.assertIn("`NEXT_SHELL_PROMPT.md`", commit)

    def test_openai_metadata_uses_dollar_invocation(self) -> None:
        metadata = _mapping(AGENT_PATH.read_text())

        self.assertGreaterEqual(len(metadata["short_description"]), 25)
        self.assertLessEqual(len(metadata["short_description"]), 64)
        self.assertIn("$handoff", metadata["default_prompt"])
        self.assertIn("$handoff extract", metadata["default_prompt"])
        self.assertIn("NEXT_SHELL_PROMPT.md", metadata["default_prompt"])

    def test_reference_template_targets_handoff_file(self) -> None:
        template = TEMPLATE_PATH.read_text()

        self.assertIn("# `NEXT_SHELL_PROMPT.md` Template", template)
        self.assertIn("package root", template)
