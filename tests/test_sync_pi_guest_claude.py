"""Claude runtime coverage for scripts/sync_pi_guest.py (guest side run locally)."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPTS = Path(__file__).parents[1] / "scripts"
SPEC = importlib.util.spec_from_file_location("sync_pi_guest_claude", SCRIPTS / "sync_pi_guest.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
sys.path.insert(0, str(SCRIPTS))
import activate_chasm_skills as activate  # noqa: E402


@pytest.fixture
def guest(tmp_path):
    root = tmp_path / "guest-store" / "claude"
    home = tmp_path / "guest-home"
    home.mkdir()
    code = sync.GUEST_APPLY.replace("/workspace/.agent-skills/claude", str(root)).replace("/home/agent", str(home))

    def run(manifest, config=None):
        payload = {**manifest, "runtime": "claude", "root": str(root), "link": str(root / "active"),
                   "claude_config": str(config or home / ".claude")}
        return subprocess.run([sys.executable, "-I", "-c", code], input=json.dumps(payload),
                              text=True, capture_output=True)
    return run, home / ".claude", root


def source_tree(tmp_path, skills, refs=None):
    source = tmp_path / "source"
    for name, body in skills.items():
        (source / name).mkdir(parents=True, exist_ok=True)
        (source / name / "SKILL.md").write_text(body)
    references = None
    if refs:
        references = tmp_path / "refs"
        references.mkdir(exist_ok=True)
        for name, body in refs.items():
            (references / name).write_text(body)
    return sync.build_manifest(source, (tmp_path,), references=references), source


def test_claude_projection_add_idempotent_update_and_stale_removal(tmp_path, guest):
    run, config, root = guest
    user = config / "skills" / "mine"
    user.mkdir(parents=True)
    (user / "SKILL.md").write_text("user")
    first, source = source_tree(tmp_path, {"demo": "v1", "old": "o"}, {"guide.md": "ref"})
    result = run(first)
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    assert out["projection"] == {"skills/demo": "add", "skills/old": "add", "references/guide.md": "add"}
    assert (config / "skills/demo/SKILL.md").read_text() == "v1"
    assert not (config / "skills/demo").is_symlink()
    assert (config / "skills/demo/../../references/guide.md").read_text() == "ref"
    assert (root / "active").resolve() == root / first["hash"] / "skills"
    again = run(first)
    assert again.returncode == 0 and json.loads(again.stdout)["projection"] == {}
    (source / "demo" / "SKILL.md").write_text("v2")
    import shutil
    shutil.rmtree(source / "old")
    second, _ = source_tree(tmp_path, {}, {"guide.md": "ref"})
    result = run(second)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["projection"] == {"skills/demo": "update", "skills/old": "remove"}
    assert (config / "skills/demo/SKILL.md").read_text() == "v2"
    assert not (config / "skills/old").exists()
    assert (user / "SKILL.md").read_text() == "user"
    ledger = json.loads((config / ".chasm-skills-ownership.json").read_text())
    assert set(ledger["entries"]) == {"skills/demo", "references/guide.md"}


def test_claude_refuses_unmanaged_or_edited_entries_before_switching(tmp_path, guest):
    run, config, root = guest
    clash = config / "skills" / "demo"
    clash.mkdir(parents=True)
    (clash / "SKILL.md").write_text("user demo")
    manifest, source = source_tree(tmp_path, {"demo": "v1"})
    result = run(manifest)
    assert result.returncode != 0 and "skills/demo" in result.stderr
    assert (clash / "SKILL.md").read_text() == "user demo"
    assert not (root / "active").exists()
    import shutil
    shutil.rmtree(clash)
    assert run(manifest).returncode == 0
    (clash / "SKILL.md").write_text("guest edit")
    (source / "demo" / "SKILL.md").write_text("v2")
    second, _ = source_tree(tmp_path, {})
    result = run(second)
    assert result.returncode != 0 and "locally edited" in result.stderr
    assert (clash / "SKILL.md").read_text() == "guest edit"
    assert (root / "active").resolve() == root / manifest["hash"] / "skills"


def test_claude_config_outside_guest_home_is_rejected(tmp_path, guest):
    run, _, _ = guest
    manifest, _ = source_tree(tmp_path, {"demo": "v1"})
    result = run(manifest, config=tmp_path / "elsewhere" / ".claude")
    assert result.returncode != 0 and "invalid claude config" in result.stderr


def test_host_validates_guest_claude_config_before_incus(monkeypatch):
    monkeypatch.setattr(sync, "_incus_prefix", lambda: (_ for _ in ()).throw(AssertionError("unexpected incus")))
    with pytest.raises(ValueError, match="/home/agent"):
        sync.apply_manifest({"hash": "a" * 64, "files": []}, runtime="claude", claude_config=Path("/root/.claude"))
    with pytest.raises(ValueError, match="/home/agent"):
        sync.apply_manifest({"hash": "a" * 64, "files": []}, runtime="claude",
                            claude_config=Path("/home/agent/../root/.claude"))


def test_claude_payload_carries_config_dir(monkeypatch):
    captured = {}
    monkeypatch.setattr(sync, "_incus_prefix", lambda: ["incus"])
    monkeypatch.setattr(sync, "guest_status", lambda *args: "running")

    def fake_run(cmd, input, **kwargs):
        captured["payload"] = json.loads(input.decode().splitlines()[1])
        return subprocess.CompletedProcess(cmd, 0, b'{"unchanged": true}', b"")
    monkeypatch.setattr(sync.subprocess, "run", fake_run)
    sync.apply_manifest({"hash": "a" * 64, "files": []}, runtime="claude")
    payload = captured["payload"]
    assert payload["claude_config"] == "/home/agent/.claude"
    assert (payload["root"], payload["link"]) == ("/workspace/.agent-skills/claude", "/workspace/.agent-skills/claude/active")


def test_default_claude_source_honors_claude_config_dir(tmp_path, monkeypatch, capsys):
    config = tmp_path / "host-claude"
    (config / "skills" / "demo").mkdir(parents=True)
    (config / "skills" / "demo" / "SKILL.md").write_text("host")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))
    assert sync.main(["--runtime", "claude", "--check"]) == 0
    out = json.loads(capsys.readouterr().out)
    expected = sync.build_manifest(config / "skills", (config / "skills",))
    assert out["runtime"] == "claude" and out["hash"] == expected["hash"]


def test_ledger_is_shared_with_local_activation(tmp_path, guest):
    """Timer sync and in-guest activation agree on fingerprints and ledger format."""
    run, config, _ = guest
    bundle = tmp_path / "bundle"
    (bundle / "skills" / "demo").mkdir(parents=True)
    (bundle / "skills" / "demo" / "SKILL.md").write_text("same")
    activate.apply(activate.prepare("claude", bundle, tmp_path / "unused-home", tmp_path / "local-snapshots",
                                    claude_config=config))
    manifest = sync.build_manifest(bundle / "skills", (tmp_path,))
    result = run(manifest)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["projection"] == {}
