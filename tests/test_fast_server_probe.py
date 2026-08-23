import asyncio

import pytest

from hermes_gate.app import HermesGateApp
from hermes_gate.session import SessionManager


@pytest.mark.asyncio
async def test_server_capabilities_use_one_lightweight_ssh_call(monkeypatch):
    captured = {}

    class FakeProcess:
        returncode = 0

        async def communicate(self):
            return b"tmux\nhermes\n", b""

    async def fake_create_subprocess_exec(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeProcess()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    app = HermesGateApp()
    assert await app._server_capabilities(
        "hermes", "203.0.113.10", "22", "example-host"
    ) == (True, True, True)

    remote_command = captured["args"][-1]
    assert "command -v tmux" in remote_command
    assert '$HOME/.local/bin/hermes' in remote_command
    assert "hermes --version" not in remote_command


def test_ssh_options_reuse_a_persistent_control_connection(tmp_path, monkeypatch):
    monkeypatch.setattr("hermes_gate.session._config_dir", lambda: tmp_path)

    options = SessionManager("hermes", "example.com")._ssh_options()
    rendered = " ".join(options)

    assert "ControlMaster=auto" in rendered
    assert "ControlPersist=300" in rendered
    assert f"ControlPath={tmp_path}/ssh/%C" in rendered
    assert (tmp_path / "ssh").stat().st_mode & 0o777 == 0o700
