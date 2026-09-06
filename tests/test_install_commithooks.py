"""Exercise the installer published in SKILL.md using isolated Git fixtures."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1] / "skills/install-commithooks/SKILL.md"


class InstallerPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.source = self.root / "source"
        (self.source / "lib").mkdir(parents=True)
        (self.source / "lib/common.sh").write_text("# harmless fixture library\n")
        (self.source / "pre-commit").write_text(
            '#!/bin/sh\nexec "$(git rev-parse --show-toplevel)/.githooks/pre-commit" "$@"\n'
        )
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(
            HOME=str(self.root), XDG_CONFIG_HOME=str(self.root / "xdg"),
            GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.root / "global.gitconfig"),
            COMMITHOOKS_DIR=str(self.source),
        )
        self.git("init", "--template=", ".")
        self.installer = self.root / "setup_hooks.py"
        self.installer.write_text(SKILL.read_text().split("```python\n", 1)[1].split("```", 1)[0])

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              text=True, capture_output=True, check=True).stdout.strip()

    def install(self):
        import sys
        return subprocess.run([sys.executable, str(self.installer)], cwd=self.repo,
                              env=self.env, text=True, capture_output=True, check=True).stdout

    def test_initial_and_repeated_install_dispatch_marker(self):
        local = self.repo / ".githooks"
        local.mkdir()
        hook = local / "pre-commit"
        hook.write_text('#!/bin/sh\nprintf "marker\\n" >> dispatch-marker\n')
        hook.chmod(0o755)
        for _ in range(3):
            self.assertIn("installed from", self.install())
            self.git("hook", "run", "pre-commit")
        self.assertEqual((self.repo / "dispatch-marker").read_text(), "marker\n" * 3)
        self.assertEqual(hook.read_text(), '#!/bin/sh\nprintf "marker\\n" >> dispatch-marker\n')

    def test_custom_dispatcher_preserved_before_library_mutation(self):
        self.install()
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("# custom dispatcher; never executed\n")
        library = self.repo / ".git/lib/common.sh"
        library.write_text("# custom library\n")
        for _ in range(2):
            self.assertIn("Preserving custom dispatcher", self.install())
            self.assertEqual(hook.read_text(), "# custom dispatcher; never executed\n")
            self.assertEqual(library.read_text(), "# custom library\n")

    def test_initial_custom_dispatcher_preserved(self):
        hook = self.repo / ".git/hooks/pre-commit"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("# existing hook\n")
        for _ in range(2):
            self.assertIn("Preserving custom dispatcher", self.install())
            self.assertEqual(hook.read_text(), "# existing hook\n")
            self.assertFalse((self.repo / ".git/lib").exists())

    def test_local_and_inherited_routing_preserved(self):
        for scope in ("--local", "--global"):
            with self.subTest(scope=scope):
                self.git("config", scope, "core.hooksPath", "custom-hooks")
                before = self.git("config", "--show-origin", "--get", "core.hooksPath")
                for _ in range(2):
                    self.assertIn("Preserving core.hooksPath", self.install())
                    self.assertEqual(self.git("config", "--show-origin", "--get", "core.hooksPath"), before)
                    self.assertFalse((self.repo / ".git/lib").exists())
                    self.assertFalse((self.repo / ".git/hooks/pre-commit").exists())
                self.git("config", scope, "--unset", "core.hooksPath")

    def test_broken_hook_symlink_preserved(self):
        hook = self.repo / ".git/hooks/pre-commit"
        hook.parent.mkdir(exist_ok=True)
        hook.symlink_to(self.root / "missing-custom-hook")
        for _ in range(2):
            self.assertIn("Preserving custom dispatcher", self.install())
            self.assertTrue(hook.is_symlink())
            self.assertFalse((self.repo / ".git/lib").exists())

    def test_sample_hook_can_be_replaced(self):
        hook = self.repo / ".git/hooks/pre-commit"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("# fixture sample\n")
        hook.with_name("pre-commit.sample").write_bytes(hook.read_bytes())
        self.install()
        self.assertEqual(hook.read_bytes(), (self.source / "pre-commit").read_bytes())

    def test_symlinked_hooks_directory_preserved(self):
        hooks = self.repo / ".git/hooks"
        if hooks.exists():
            hooks.rmdir()  # Empty because git init used --template=.
        external = self.root / "custom-hooks"
        external.mkdir()
        marker = external / "pre-commit"
        marker.write_text("# custom hook; never executed\n")
        hooks.symlink_to(external, target_is_directory=True)
        for _ in range(2):
            self.assertIn("Preserving custom hooks directory", self.install())
            self.assertTrue(hooks.is_symlink())
            self.assertEqual(marker.read_text(), "# custom hook; never executed\n")
            self.assertFalse((self.repo / ".git/lib").exists())


if __name__ == "__main__":
    unittest.main()
