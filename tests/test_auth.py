import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from gw.cli import main


def test_auth_login_copies_credentials_and_saves_token(
    config_dir: Path, mock_credentials: Path
) -> None:
    mock_flow = MagicMock()
    mock_flow.credentials = MagicMock()
    mock_flow.credentials.token = "access-token"
    mock_flow.credentials.refresh_token = "refresh-token"
    mock_flow.credentials.token_uri = "https://oauth2.googleapis.com/token"
    mock_flow.credentials.client_id = "test-client-id"
    mock_flow.credentials.client_secret = "test-secret"
    mock_flow.credentials.scopes = ["https://www.googleapis.com/auth/calendar"]
    mock_flow.credentials.to_json.return_value = json.dumps({
        "token": "access-token",
        "refresh_token": "refresh-token",
    })

    with (
        patch("gw.auth.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow),
        patch("gw.auth._get_user_email", return_value="user@gmail.com"),
    ):
        runner = CliRunner()
        result = runner.invoke(main, [
            "auth", "login",
            "--credentials", str(mock_credentials),
            "--config-dir", str(config_dir),
        ])

    assert result.exit_code == 0, result.output
    assert "user@gmail.com" in result.output
    token_path = config_dir / "tokens" / "user@gmail.com.json"
    assert token_path.exists()


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
    cfg["accounts"].append({
        "email": "other@gmail.com",
        "credentials": "credentials/other@gmail.com.json",
        "added_at": "2026-04-16T11:00:00Z",
    })
    cfg_path.write_text(json.dumps(cfg))

    runner = CliRunner()
    result = runner.invoke(main, [
        "auth", "switch", "other@gmail.com",
        "--config-dir", str(sample_config),
    ])
    assert result.exit_code == 0
    assert "other@gmail.com" in result.output


def test_auth_remove(sample_config: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [
        "auth", "remove", "test@gmail.com",
        "--config-dir", str(sample_config),
    ])
    assert result.exit_code == 0
    result2 = runner.invoke(main, ["auth", "list", "--config-dir", str(sample_config)])
    assert "test@gmail.com" not in result2.output
