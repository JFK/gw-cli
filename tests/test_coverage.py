"""Additional tests targeting previously-uncovered command paths.

Focus areas: Gmail reply/label/mark/download/to-drive and helper edge cases,
Calendar get/update/delete/free, and the CLI config setter + entry-point error
handling.
"""

from __future__ import annotations

import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from gw import cli as cli_module
from gw.cli import main


def _msg_with_headers(headers: list[dict], **extra: object) -> dict:
    payload = {"headers": headers, "mimeType": "text/plain", "body": {}}
    msg = {"id": "m1", "threadId": "thread1", "labelIds": [], "payload": payload}
    msg.update(extra)
    return msg


# --------------------------------------------------------------------------- #
# Gmail commands
# --------------------------------------------------------------------------- #


@patch("gw.gmail.build_service")
def test_mail_reply(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().get().execute.return_value = _msg_with_headers(
        [
            {"name": "Subject", "value": "Hello"},
            {"name": "From", "value": "sender@example.com"},
            {"name": "Message-ID", "value": "<abc@mail>"},
        ]
    )
    mock_service.users().messages().send().execute.return_value = {"id": "reply1"}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        ["--config-dir", str(sample_config), "mail", "reply", "m1", "--body", "Thanks"],
    )
    assert result.exit_code == 0, result.output
    assert "reply1" in result.output


@patch("gw.gmail.build_service")
def test_mail_reply_keeps_existing_re_prefix(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().get().execute.return_value = _msg_with_headers(
        [
            {"name": "Subject", "value": "Re: Hello"},
            {"name": "From", "value": "sender@example.com"},
            {"name": "Message-ID", "value": "<abc@mail>"},
        ]
    )
    mock_service.users().messages().send().execute.return_value = {"id": "reply2"}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        ["--config-dir", str(sample_config), "mail", "reply", "m1", "--body", "Thanks"],
    )
    assert result.exit_code == 0, result.output


@patch("gw.gmail.build_service")
def test_mail_label_add_remove(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().modify().execute.return_value = {"id": "m1"}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        [
            "--config-dir",
            str(sample_config),
            "mail",
            "label",
            "m1",
            "--add",
            "Label_1",
            "--remove",
            "UNREAD",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Labels updated" in result.output
    body = mock_service.users().messages().modify.call_args.kwargs["body"]
    assert body["addLabelIds"] == ["Label_1"]
    assert body["removeLabelIds"] == ["UNREAD"]


@patch("gw.gmail.build_service")
def test_mail_mark_unread(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().modify().execute.return_value = {"id": "m1"}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        ["--config-dir", str(sample_config), "mail", "mark", "m1", "--unread"],
    )
    assert result.exit_code == 0, result.output
    assert "unread" in result.output.lower()


def test_mail_mark_requires_exactly_one_flag(sample_config: Path) -> None:
    # Neither flag → UsageError (exit code 2)
    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "mail", "mark", "m1"])
    assert result.exit_code != 0
    assert "exactly one" in result.output.lower()


@patch("gw.gmail.build_service")
def test_mail_download(mock_build: MagicMock, sample_config: Path, tmp_path: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().attachments().get().execute.return_value = {
        "data": base64.urlsafe_b64encode(b"file-bytes").decode()
    }
    mock_build.return_value = mock_service

    out = tmp_path / "out.bin"
    result = CliRunner().invoke(
        main,
        [
            "--config-dir",
            str(sample_config),
            "mail",
            "download",
            "m1",
            "--attachment-id",
            "att1",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.read_bytes() == b"file-bytes"


@patch("gw.gmail.build_service")
def test_mail_to_drive(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().get().execute.return_value = {
        "id": "m1",
        "payload": {
            "parts": [
                {
                    "filename": "report.pdf",
                    "mimeType": "application/pdf",
                    "body": {"attachmentId": "att1", "size": 10},
                }
            ]
        },
    }
    mock_service.users().messages().attachments().get().execute.return_value = {
        "data": base64.urlsafe_b64encode(b"pdf-bytes").decode()
    }
    mock_service.files().create().execute.return_value = {
        "id": "f1",
        "name": "report.pdf",
        "webViewLink": "https://drive.example/f1",
    }
    # build_service is called for both gmail and drive — same mock serves both.
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        [
            "--config-dir",
            str(sample_config),
            "mail",
            "to-drive",
            "m1",
            "--attachment-id",
            "att1",
            "--folder",
            "folder1",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "report.pdf" in result.output


@patch("gw.gmail.build_service")
def test_mail_list_since_iso_and_query(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().list().execute.return_value = {"messages": []}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        [
            "--config-dir",
            str(sample_config),
            "mail",
            "list",
            "--query",
            "from:boss",
            "--limit",
            "5",
            "--since",
            "2026-01-01T00:00:00",
        ],
    )
    assert result.exit_code == 0, result.output
    q = mock_service.users().messages().list.call_args.kwargs["q"]
    assert "from:boss" in q
    assert "after:" in q


@patch("gw.gmail.build_service")
def test_mail_list_since_non_iso_passthrough(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().list().execute.return_value = {"messages": []}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        ["--config-dir", str(sample_config), "mail", "list", "--since", "2026/01/01"],
    )
    assert result.exit_code == 0, result.output
    q = mock_service.users().messages().list.call_args.kwargs["q"]
    assert "after:2026/01/01" in q


@patch("gw.gmail.build_service")
def test_mail_read_nested_body_and_missing_header(mock_build: MagicMock, sample_config: Path) -> None:
    # Nested multipart: text lives in a child part; no Subject header present.
    nested = {
        "id": "m1",
        "payload": {
            "mimeType": "multipart/alternative",
            "headers": [{"name": "From", "value": "x@example.com"}],
            "parts": [
                {"mimeType": "text/html", "body": {}},
                {
                    "mimeType": "text/plain",
                    "body": {"data": base64.urlsafe_b64encode(b"deep body").decode()},
                },
            ],
        },
    }
    mock_service = MagicMock()
    mock_service.users().messages().get().execute.return_value = nested
    mock_build.return_value = mock_service

    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "mail", "read", "m1"])
    assert result.exit_code == 0, result.output
    assert "deep body" in result.output


# --------------------------------------------------------------------------- #
# Calendar commands
# --------------------------------------------------------------------------- #


@patch("gw.calendar.build_service")
def test_cal_get(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().get().execute.return_value = {
        "id": "e1",
        "summary": "Standup",
        "start": {"dateTime": "2026-01-01T10:00:00+09:00"},
        "end": {"dateTime": "2026-01-01T10:30:00+09:00"},
        "attendees": [{"email": "a@example.com"}],
    }
    mock_build.return_value = mock_service

    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "cal", "get", "e1"])
    assert result.exit_code == 0, result.output
    assert "Standup" in result.output


@patch("gw.calendar.build_service")
def test_cal_update(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().get().execute.return_value = {"id": "e1", "summary": "Old"}
    mock_service.events().update().execute.return_value = {"summary": "New title"}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(
        main,
        [
            "--config-dir",
            str(sample_config),
            "cal",
            "update",
            "e1",
            "--title",
            "New title",
            "--start",
            "2026-01-01 10:00",
            "--end",
            "2026-01-01 11:00",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "New title" in result.output


@patch("gw.calendar.build_service")
def test_cal_delete(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().delete().execute.return_value = {}
    mock_build.return_value = mock_service

    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "cal", "delete", "e1"])
    assert result.exit_code == 0, result.output
    assert "Deleted" in result.output


@patch("gw.calendar.build_service")
def test_cal_free_busy(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.freebusy().query().execute.return_value = {
        "calendars": {"test@gmail.com": {"busy": [{"start": "2026-01-01T10:00:00Z", "end": "2026-01-01T11:00:00Z"}]}}
    }
    mock_build.return_value = mock_service

    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "cal", "free", "--date", "2026-01-01"])
    assert result.exit_code == 0, result.output


def test_cal_free_invalid_date(sample_config: Path) -> None:
    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "cal", "free", "--date", "not-a-date"])
    assert result.exit_code != 0
    assert "Invalid date" in result.output


# --------------------------------------------------------------------------- #
# CLI config setter + entry-point error handling
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "value,expected",
    [("3.5", "3.5"), ("true", "True"), ("false", "False"), ("null", "None")],
)
def test_config_set_type_coercion(sample_config: Path, value: str, expected: str) -> None:
    result = CliRunner().invoke(
        main,
        ["--config-dir", str(sample_config), "config", "set", "defaults.mail.flag", value],
    )
    assert result.exit_code == 0, result.output
    assert f"= {expected}" in result.output


def test_config_set_unknown_key(sample_config: Path) -> None:
    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "config", "set", "bogus", "1"])
    assert result.exit_code != 0
    assert "Unknown config key" in result.output


def test_config_show(sample_config: Path) -> None:
    result = CliRunner().invoke(main, ["--config-dir", str(sample_config), "config", "show"])
    assert result.exit_code == 0, result.output
    assert "active_account" in result.output


def test_cli_entrypoint_click_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_module, "main", MagicMock(side_effect=click.ClickException("bad")))
    with pytest.raises(SystemExit) as exc:
        cli_module.cli()
    assert exc.value.code == 1


def test_cli_entrypoint_abort(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_module, "main", MagicMock(side_effect=click.exceptions.Abort()))
    with pytest.raises(SystemExit) as exc:
        cli_module.cli()
    assert exc.value.code == 1


def test_cli_entrypoint_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_module, "main", MagicMock(side_effect=RuntimeError("boom")))
    with pytest.raises(SystemExit) as exc:
        cli_module.cli()
    assert exc.value.code == 1
