import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gw.auth import _can_auto_open_browser
from gw.cli import main


def _make_mock_flow() -> MagicMock:
    mock_flow = MagicMock()
    mock_flow.credentials = MagicMock()
    mock_flow.credentials.token = "access-token"
    mock_flow.credentials.refresh_token = "refresh-token"
    mock_flow.credentials.token_uri = "https://oauth2.googleapis.com/token"
    mock_flow.credentials.client_id = "test-client-id"
    mock_flow.credentials.client_secret = "test-secret"
    mock_flow.credentials.scopes = ["https://www.googleapis.com/auth/calendar"]
    mock_flow.credentials.to_json.return_value = json.dumps(
        {
            "token": "access-token",
            "refresh_token": "refresh-token",
        }
    )
    return mock_flow


def _run_login(config_dir: Path, mock_credentials: Path, mock_flow: MagicMock):
    with (
        patch("gw.auth.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow),
        patch("gw.auth._get_user_email", return_value="user@gmail.com"),
    ):
        runner = CliRunner()
        return runner.invoke(
            main,
            [
                "auth",
                "login",
                "--credentials",
                str(mock_credentials),
                "--config-dir",
                str(config_dir),
            ],
        )


def test_auth_login_copies_credentials_and_saves_token(config_dir: Path, mock_credentials: Path) -> None:
    mock_flow = _make_mock_flow()
    result = _run_login(config_dir, mock_credentials, mock_flow)

    assert result.exit_code == 0, result.output
    assert "user@gmail.com" in result.output
    token_path = config_dir / "tokens" / "user@gmail.com.json"
    assert token_path.exists()


def test_auth_login_prints_url_explicitly(config_dir: Path, mock_credentials: Path) -> None:
    """The consent URL must be printed via an explicit prompt message, not the
    library's mutable default, so the operator always sees a URL to open."""
    mock_flow = _make_mock_flow()
    result = _run_login(config_dir, mock_credentials, mock_flow)

    assert result.exit_code == 0, result.output
    mock_flow.run_local_server.assert_called_once()
    kwargs = mock_flow.run_local_server.call_args.kwargs
    assert "{url}" in kwargs["authorization_prompt_message"]
    assert isinstance(kwargs["open_browser"], bool)


def test_auth_login_skips_browser_on_wsl(
    config_dir: Path, mock_credentials: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """On WSL2 the OS default URL handler is unreliable, so the auto-open is
    skipped and the operator opens the printed URL manually."""
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    mock_flow = _make_mock_flow()
    result = _run_login(config_dir, mock_credentials, mock_flow)

    assert result.exit_code == 0, result.output
    assert mock_flow.run_local_server.call_args.kwargs["open_browser"] is False


def test_can_auto_open_browser_false_on_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    assert _can_auto_open_browser() is False


def test_auth_list_shows_accounts(sample_config: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["auth", "list", "--config-dir", str(sample_config)])
    assert result.exit_code == 0
    assert "test@gmail.com" in result.output


def test_auth_status_shows_active(sample_config: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["auth", "status", "--config-dir", str(sample_config)])
    assert result.exit_code == 0
    assert "test@gmail.com" in result.output


def test_auth_switch(sample_config: Path) -> None:
    cfg_path = sample_config / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["accounts"].append(
        {
            "email": "other@gmail.com",
            "credentials": "credentials/other@gmail.com.json",
            "added_at": "2026-04-16T11:00:00Z",
        }
    )
    cfg_path.write_text(json.dumps(cfg))

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "auth",
            "switch",
            "other@gmail.com",
            "--config-dir",
            str(sample_config),
        ],
    )
    assert result.exit_code == 0
    assert "other@gmail.com" in result.output


def test_auth_remove(sample_config: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "auth",
            "remove",
            "test@gmail.com",
            "--config-dir",
            str(sample_config),
        ],
    )
    assert result.exit_code == 0
    result2 = runner.invoke(main, ["auth", "list", "--config-dir", str(sample_config)])
    assert "test@gmail.com" not in result2.output
