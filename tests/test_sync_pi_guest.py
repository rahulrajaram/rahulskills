import importlib.util
from pathlib import Path
import pytest

SPEC = importlib.util.spec_from_file_location("sync_pi_guest", Path(__file__).parents[1] / "scripts/sync_pi_guest.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def test_manifest_is_deterministic_and_preserves_modes(tmp_path):
    source = tmp_path / "skills"
    (source / "demo").mkdir(parents=True)
    (source / "demo" / "SKILL.md").write_text("hello")
    (source / "standalone.md").write_text("standalone")
    references = tmp_path / "references"
    references.mkdir()
    (references / "support.md").write_text("support")
    first = sync.build_manifest(source, (tmp_path,), references=references)
    second = sync.build_manifest(source, (tmp_path,), references=references)
    assert first["hash"] == second["hash"]
    assert {row["path"] for row in first["files"]} == {"skills/demo/SKILL.md", "skills/standalone.md", "references/support.md"}


def test_symlink_escape_and_secret_names_are_rejected(tmp_path):
    source = tmp_path / "skills"
    source.mkdir()
    (source / ".env").write_text("secret")
    try:
        sync.build_manifest(source, (tmp_path,))
    except ValueError as error:
        assert "forbidden" in str(error)
    else:
        raise AssertionError("credential filename was accepted")

    (source / ".env").unlink()
    outside = tmp_path / "outside.md"
    outside.write_text("outside")
    (source / "escape.md").symlink_to(outside)
    try:
        sync.build_manifest(source, (source,))
    except ValueError as error:
        assert "escapes" in str(error)
    else:
        raise AssertionError("escaping symlink was accepted")


def test_stopped_guest_is_skipped_without_apply(monkeypatch):
    monkeypatch.setattr(sync, "_incus_prefix", lambda: ["incus"])
    monkeypatch.setattr(sync, "guest_status", lambda *args: "stopped")
    monkeypatch.setattr(sync.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("unexpected mutation")))
    assert sync.apply_manifest({"hash": "x", "files": []})["status"] == "skipped"


@pytest.mark.parametrize("runtime", ["pi", "codex"])
def test_guest_publish_idempotence_and_edit_conflict(tmp_path, runtime):
    import json
    import subprocess
    import sys
    source = tmp_path / "source"
    (source / "demo").mkdir(parents=True)
    (source / "demo" / "SKILL.md").write_text("version one")
    references = tmp_path / "references"
    references.mkdir()
    (references / "support.md").write_text("support")
    root = tmp_path / "guest-store"
    link = tmp_path / "guest-home" / "skills" / "host-synced"
    root_path, link_path = sync.RUNTIME_PATHS[runtime]
    code = sync.GUEST_APPLY.replace(str(root_path), str(root)).replace(str(link_path), str(link))
    def apply(manifest):
        return subprocess.run([sys.executable, "-I", "-c", code], input=json.dumps({**manifest, "runtime": runtime, "root": str(root), "link": str(link)}), text=True, capture_output=True)
    first = sync.build_manifest(source, (tmp_path,), references=references)
    result = apply(first)
    assert result.returncode == 0, result.stderr
    assert (link / "demo" / "SKILL.md").read_text() == "version one"
    assert (link.resolve().parent / "references" / "support.md").read_text() == "support"
    result = apply(first)
    assert result.returncode == 0 and json.loads(result.stdout)["unchanged"]
    (link / "demo" / "SKILL.md").write_text("guest edit")
    (source / "demo" / "SKILL.md").write_text("version two")
    second = sync.build_manifest(source, (tmp_path,), references=references)
    result = apply(second)
    assert result.returncode != 0 and "edited" in result.stderr
    assert (link / "demo" / "SKILL.md").read_text() == "guest edit"
    assert not (root / second["hash"]).exists()


def test_mutation_timeout_is_not_retried(monkeypatch):
    import subprocess
    calls = []
    monkeypatch.setattr(sync, "_incus_prefix", lambda: ["incus"])
    monkeypatch.setattr(sync, "guest_status", lambda *args: "running")
    def timeout(*args, **kwargs):
        calls.append(args)
        raise subprocess.TimeoutExpired(args[0], 90)
    monkeypatch.setattr(sync.subprocess, "run", timeout)
    import pytest
    with pytest.raises(subprocess.TimeoutExpired):
        sync.apply_manifest({"hash": "a" * 64, "files": []})
    assert len(calls) == 1
