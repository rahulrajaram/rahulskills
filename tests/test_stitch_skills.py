import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI may not ship PyYAML
    yaml = None


ROOT = Path(__file__).parents[1]
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def isolated_env(home: Path) -> dict[str, str]:
    """Environment whose default runtime roots all live under a temp HOME."""
    env = {key: value for key, value in os.environ.items()
           if key not in ("CLAUDE_CONFIG_DIR", "CLAUDE_SKILLS_DIR", "PI_SKILLS_DIR",
                          "OPENCODE_SKILLS_DIR", "CODEX_SKILLS_DIR")}
    env["HOME"] = str(home)
    return env


def run(*args: str, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([str(arg) for arg in args], cwd=ROOT, check=check, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def json_reports(stdout: str) -> list[dict]:
    """Decode every JSON migration report printed between progress lines."""
    decoder, reports, index = json.JSONDecoder(), [], 0
    while (index := stdout.find("{", index)) != -1:
        report, end = decoder.raw_decode(stdout, index)
        reports.append(report)
        index = end
    return reports


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    assert match, f"no frontmatter: {path}"
    if yaml is not None:
        data = yaml.safe_load(match.group(1))
        assert isinstance(data, dict), path
        return data
    keys = [line.split(":", 1)[0] for line in match.group(1).splitlines()
            if line and not line.startswith((" ", "\t", "-"))]
    assert len(keys) == len(set(keys)), f"duplicate frontmatter key: {path}"
    return {line.split(":", 1)[0]: line.split(":", 1)[1].strip()
            for line in match.group(1).splitlines() if ":" in line and not line.startswith((" ", "\t"))}


class StitchFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls._tmp.name) / "assembled"
        run(ROOT / "stitch-skills.sh", "assemble", "--output", cls.output)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_isolated_assembly_is_fresh_and_default_omits_design_pair(self):
        output = self.output
        self.assertTrue((output / "codex" / "references").is_dir())
        self.assertFalse((output / "codex" / "skills" / "figma").exists())
        self.assertFalse((output / "codex" / "skills" / "tui-web-design-orchestrator").exists())

    def test_claude_assembly_applies_overlay_and_codex_strips_cli_keys(self):
        claude = frontmatter(self.output / "claude/skills/postmortem/SKILL.md")
        codex = frontmatter(self.output / "codex/skills/postmortem/SKILL.md")
        self.assertIn("Agent", claude["allowed-tools"])
        self.assertNotIn("Task", claude["allowed-tools"].split(", "))
        self.assertNotIn("allowed-tools", codex)
        self.assertTrue((self.output / "claude/references").is_dir())

    def test_every_assembled_manifest_has_parseable_matching_frontmatter(self):
        for runtime in ("claude", "codex"):
            for manifest in sorted((self.output / runtime / "skills").glob("*/SKILL.md")):
                with self.subTest(runtime=runtime, skill=manifest.parent.name):
                    data = frontmatter(manifest)
                    self.assertEqual(data["name"], manifest.parent.name)
                    self.assertTrue(data["description"])
                    if runtime == "codex":
                        self.assertNotIn("allowed-tools", data)

    def test_runtime_gated_skill_is_not_assembled_for_claude_or_codex(self):
        for runtime in ("claude", "codex"):
            self.assertFalse((self.output / runtime / "skills/pi-defects-harvester").exists())

    def test_overlays_use_current_claude_tool_names(self):
        for overlay in (ROOT / "overlays/claude").glob("*.yml"):
            with self.subTest(overlay=overlay.name):
                self.assertIsNone(re.search(r"\bTask\b", overlay.read_text()),
                                  "Claude Code renamed the Task tool to Agent")


class RuntimeSelectionTests(unittest.TestCase):
    def test_runtime_option_assembles_only_the_selected_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "claude-only"
            run(ROOT / "stitch-skills.sh", "assemble", "--runtime", "claude",
                "--skill", "postmortem", "--output", output)
            self.assertEqual(sorted(p.name for p in output.iterdir()), ["claude"])
            self.assertTrue((output / "claude/skills/postmortem/SKILL.md").is_file())

    def test_unknown_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(ROOT / "stitch-skills.sh", "assemble", "--runtime", "pi",
                         "--output", Path(tmp) / "x", check=False)
            self.assertEqual(result.returncode, 2)
            self.assertIn("--runtime must be one of", result.stderr)
            self.assertFalse((Path(tmp) / "x").exists())

    def test_codex_ownership_conflict_does_not_block_claude_only_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            codex = home / ".codex"
            codex.mkdir()
            (codex / ".rahulskills-ownership.json").write_text(
                json.dumps({"version": 1, "source": "/elsewhere", "entries": {}}))
            env = isolated_env(home)
            both = run(ROOT / "stitch-skills.sh", "preview", "--skill", "postmortem",
                       "--output", home / "both", env=env, check=False)
            self.assertNotEqual(both.returncode, 0)
            claude = run(ROOT / "stitch-skills.sh", "preview", "--runtime", "claude",
                         "--skill", "postmortem", "--output", home / "claude", env=env)
            self.assertIn('"runtime": "claude"', claude.stdout)
            self.assertNotIn('"runtime": "codex"', claude.stdout)


class InstallClaudeSkillsTests(unittest.TestCase):
    script = ROOT / "install-claude-skills.sh"

    def test_preview_is_read_only_against_temp_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "claude"
            result = run(self.script, "--preview", "--claude-root", root, "--skill", "postmortem",
                         env=isolated_env(Path(tmp)))
            report = json_reports(result.stdout)[-1]
            self.assertEqual(report["runtime"], "claude")
            self.assertEqual(report["selection"], ["postmortem"])
            self.assertIn({"path": "skills/postmortem", "action": "add", "reason": "absent"}, report["changes"])
            self.assertFalse(root.exists())
            self.assertFalse((Path(tmp) / ".claude").exists())

    def test_install_is_idempotent_and_honors_claude_config_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            env = isolated_env(home)
            env["CLAUDE_CONFIG_DIR"] = str(home / "config")
            run(self.script, "--skill", "postmortem", env=env)
            installed = home / "config/skills/postmortem/SKILL.md"
            self.assertIn("Agent", frontmatter(installed)["allowed-tools"])
            self.assertFalse((home / ".claude").exists())
            rerun = run(self.script, "--skill", "postmortem", env=env)
            actions = {change["action"] for change in json_reports(rerun.stdout)[-1]["changes"]}
            self.assertEqual(actions, {"unchanged"})

    def test_foreign_ledger_requires_adopt_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            root = home / "claude"
            root.mkdir()
            (root / ".rahulskills-ownership.json").write_text(
                json.dumps({"version": 1, "source": "/other/checkout", "entries": {}}))
            env = isolated_env(home)
            refused = run(self.script, "--claude-root", root, "--skill", "postmortem", env=env, check=False)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("--adopt-source", refused.stderr)
            self.assertFalse((root / "skills/postmortem").exists())
            run(self.script, "--claude-root", root, "--skill", "postmortem", "--adopt-source", env=env)
            ledger = json.loads((root / ".rahulskills-ownership.json").read_text())
            self.assertEqual(ledger["source"], str(ROOT.resolve()))
            self.assertIn("skills/postmortem", ledger["entries"])

    def test_pi_only_skill_is_not_installed_for_claude(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "claude"
            result = run(self.script, "--preview", "--claude-root", root,
                         "--skill", "pi-defects-harvester", env=isolated_env(Path(tmp)))
            report = json_reports(result.stdout)[-1]
            self.assertEqual(report["selection"], [])


class SyncPushTests(unittest.TestCase):
    def test_push_installs_every_runtime_under_an_isolated_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            run(ROOT / "sync-skills.sh", "push", "--skill", "postmortem", env=isolated_env(home))
            self.assertIn("Agent", frontmatter(home / ".claude/skills/postmortem/SKILL.md")["allowed-tools"])
            self.assertNotIn("allowed-tools", frontmatter(home / ".codex/skills/postmortem/SKILL.md"))
            for link in (home / ".pi/agent/skills/postmortem", home / ".config/opencode/skills/postmortem"):
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), (ROOT / "skills/postmortem").resolve())

    def test_push_runtime_filter_limits_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            run(ROOT / "sync-skills.sh", "push", "--runtime", "claude", "--skill", "postmortem",
                env=isolated_env(home))
            self.assertTrue((home / ".claude/skills/postmortem").is_dir())
            for other in (".codex", ".pi", ".config"):
                self.assertFalse((home / other).exists(), other)


if __name__ == "__main__":
    unittest.main()
