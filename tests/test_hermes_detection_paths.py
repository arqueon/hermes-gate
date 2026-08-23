import pytest

from hermes_gate.app import HermesGateApp


@pytest.mark.asyncio
async def test_hermes_check_falls_back_to_standard_install_paths(monkeypatch):
    app = HermesGateApp()
    captured = {}

    async def fake_remote_command_ok(user, host, port, command, ssh_alias=None):
        captured["command"] = command
        captured["ssh_alias"] = ssh_alias
        return True

    monkeypatch.setattr(app, "_remote_command_ok", fake_remote_command_ok)

    assert await app._hermes_ok(
        "hermes", "203.0.113.10", "22", "example-host"
    )
    assert 'command -v hermes' in captured["command"]
    assert '$HOME/.local/bin/hermes' in captured["command"]
    assert '$HOME/.hermes/hermes-agent/venv/bin/hermes' in captured["command"]
    assert captured["ssh_alias"] == "example-host"
