"""Regression tests for bugs found in the full-codebase debug review."""
import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gw.auth import build_service
from gw.cli import main
from gw.config import DEFAULT_DEFAULTS, GwConfig


def _write_config(config_dir: Path, defaults: dict) -> Path:
    config = {
        "active_account": "test@gmail.com",
        "accounts": [
            {
                "email": "test@gmail.com",
                "credentials": "credentials/test@gmail.com.json",
                "added_at": "2026-04-16T10:00:00Z",
            }
        ],
        "defaults": defaults,
        "loop": {"mail_check_interval": "5m"},
    }
    (config_dir / "config.json").write_text(json.dumps(config))
    return config_dir


# --- Finding 1: shallow copy mutates module-global DEFAULT_DEFAULTS ---


def test_set_default_does_not_mutate_module_defaults(config_dir: Path) -> None:
    original = DEFAULT_DEFAULTS["calendar"]["days"]
    cfg = GwConfig(config_dir)  # no config file -> defaults come from DEFAULT_DEFAULTS
    cfg.set_default("calendar", "days", 999)
    assert DEFAULT_DEFAULTS["calendar"]["days"] == original
    assert cfg.get_default("calendar", "days") == 999


# --- Finding 2: --since must convert ISO datetime to a Gmail-acceptable token ---


@patch("gw.gmail.build_service")
def test_mail_list_since_converts_iso_for_gmail(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().list().execute.return_value = {"messages": []}
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "mail", "list", "--query", "is:unread", "--since", "2026-06-15T10:00:00",
    ])
    assert result.exit_code == 0, result.output
    q = mock_service.users().messages().list.call_args.kwargs["q"]
    # Gmail's after: does not accept ISO datetime; must be epoch seconds.
    assert "after:2026-06-15T10:00:00" not in q
    assert re.search(r"after:\d+", q), q


# --- Finding 3: attachments / to-drive must walk nested multipart parts ---


def _msg_with_nested_attachment() -> dict:
    return {
        "id": "msg1",
        "payload": {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "multipart/alternative",
                    "parts": [
                        {
                            "filename": "nested.pdf",
                            "mimeType": "application/pdf",
                            "body": {"attachmentId": "att9", "size": 99},
                        }
                    ],
                }
            ],
        },
    }


@patch("gw.gmail.build_service")
def test_mail_attachments_finds_nested(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().get().execute.return_value = _msg_with_nested_attachment()
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "mail", "attachments", "msg1",
    ])
    assert result.exit_code == 0, result.output
    assert "nested.pdf" in result.output


# --- Finding 4: mark must require exactly one of --read / --unread ---


@patch("gw.gmail.build_service")
def test_mail_mark_requires_a_flag(mock_build: MagicMock, sample_config: Path) -> None:
    mock_build.return_value = MagicMock()
    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "mail", "mark", "msg1",
    ])
    assert result.exit_code != 0
    assert "read" in result.output.lower()


@patch("gw.gmail.build_service")
def test_mail_mark_rejects_both_flags(mock_build: MagicMock, sample_config: Path) -> None:
    mock_build.return_value = MagicMock()
    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "mail", "mark", "msg1", "--read", "--unread",
    ])
    assert result.exit_code != 0


# --- Finding 5: build_service must surface a friendly error on refresh failure ---


def test_build_service_reraises_on_refresh_failure(sample_config: Path) -> None:
    token_data = {
        "token": "access-token",
        "refresh_token": "refresh-token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test-client-id",
        "client_secret": "test-secret",
        "scopes": ["https://www.googleapis.com/auth/calendar"],
    }
    tokens_dir = sample_config / "tokens"
    tokens_dir.mkdir(exist_ok=True)
    (tokens_dir / "test@gmail.com.json").write_text(json.dumps(token_data))
    cfg = GwConfig(sample_config)

    mock_creds = MagicMock()
    mock_creds.expired = True
    mock_creds.refresh_token = "refresh-token"
    mock_creds.refresh.side_effect = Exception("token revoked")

    with patch(
        "google.oauth2.credentials.Credentials.from_authorized_user_file",
        return_value=mock_creds,
    ), patch("google.auth.transport.requests.Request"):
        with pytest.raises(RuntimeError, match="re-authenticate"):
            build_service(cfg, "test@gmail.com", "calendar", "v3")


# --- Finding 6: free's timeMax should cover the whole day (next-day 00:00) ---


@patch("gw.calendar.build_service")
def test_cal_free_covers_full_day(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.freebusy().query().execute.return_value = {"calendars": {}}
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "cal", "free", "--date", "2026-04-17",
    ])
    assert result.exit_code == 0, result.output
    body = mock_service.freebusy().query.call_args.kwargs["body"]
    # End of window must be the next day's start, not 23:59 (which drops the last minute).
    assert body["timeMax"].startswith("2026-04-18T00:00")


# --- Finding 7: a falsy (0) configured default must not silently fall back ---


@patch("gw.gmail.build_service")
def test_mail_list_zero_limit_is_respected(mock_build: MagicMock, config_dir: Path) -> None:
    _write_config(config_dir, {
        "calendar": {"days": 7, "timezone": "Asia/Tokyo"},
        "mail": {"limit": 0, "check_query": "is:unread"},
        "drive": {"default_folder": None},
    })
    mock_service = MagicMock()
    mock_service.users().messages().list().execute.return_value = {"messages": []}
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(config_dir), "mail", "list",
    ])
    assert result.exit_code == 0, result.output
    assert mock_service.users().messages().list.call_args.kwargs["maxResults"] == 0


# --- Finding 8: bad datetime input yields a friendly error, not a traceback ---


@patch("gw.calendar.build_service")
def test_cal_create_bad_datetime_is_friendly(mock_build: MagicMock, sample_config: Path) -> None:
    mock_build.return_value = MagicMock()
    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "cal", "create", "--title", "X",
        "--start", "4/17 10am", "--end", "2026-04-17 11:00",
    ])
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "YYYY-MM-DD" in result.output
