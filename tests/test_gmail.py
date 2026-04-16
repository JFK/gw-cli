import base64
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from gw.cli import main


def _make_message(msg_id: str, subject: str, sender: str, snippet: str = "") -> dict:
    return {
        "id": msg_id,
        "threadId": "thread1",
        "labelIds": ["INBOX", "UNREAD"],
        "snippet": snippet,
        "payload": {
            "headers": [
                {"name": "Subject", "value": subject},
                {"name": "From", "value": sender},
                {"name": "Date", "value": "Thu, 16 Apr 2026 10:00:00 +0900"},
            ],
            "mimeType": "text/plain",
            "body": {"data": base64.urlsafe_b64encode(b"Hello world").decode()},
        },
    }


@patch("gw.gmail.build_service")
def test_mail_list(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg1", "threadId": "t1"}],
        "resultSizeEstimate": 1,
    }
    mock_service.users().messages().get().execute.return_value = _make_message(
        "msg1", "Test Subject", "sender@example.com"
    )
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "mail", "list",
    ])
    assert result.exit_code == 0, result.output
    assert "Test Subject" in result.output


@patch("gw.gmail.build_service")
def test_mail_read(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().get().execute.return_value = _make_message(
        "msg1", "Read Test", "sender@example.com", "Hello"
    )
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "mail", "read", "msg1",
    ])
    assert result.exit_code == 0, result.output
    assert "Read Test" in result.output


@patch("gw.gmail.build_service")
def test_mail_send(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().send().execute.return_value = {"id": "sent1"}
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "mail", "send",
        "--to", "recipient@example.com",
        "--subject", "Test",
        "--body", "Hello",
    ])
    assert result.exit_code == 0, result.output
    assert "sent" in result.output.lower() or "Sent" in result.output


@patch("gw.gmail.build_service")
def test_mail_mark_read(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().messages().modify().execute.return_value = {"id": "msg1"}
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "mail", "mark", "msg1", "--read",
    ])
    assert result.exit_code == 0, result.output
    modify_call = mock_service.users().messages().modify
    call_kwargs = modify_call.call_args
    assert "UNREAD" in str(call_kwargs)


@patch("gw.gmail.build_service")
def test_mail_labels(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.users().labels().list().execute.return_value = {
        "labels": [
            {"id": "INBOX", "name": "INBOX"},
            {"id": "Label_1", "name": "Work"},
        ]
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config), "mail", "labels",
    ])
    assert result.exit_code == 0, result.output
    assert "INBOX" in result.output
    assert "Work" in result.output


@patch("gw.gmail.build_service")
def test_mail_attachments(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    msg = _make_message("msg1", "With attachment", "sender@example.com")
    msg["payload"]["parts"] = [
        {
            "filename": "report.pdf",
            "mimeType": "application/pdf",
            "body": {"attachmentId": "att1", "size": 12345},
        }
    ]
    mock_service.users().messages().get().execute.return_value = msg
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "mail", "attachments", "msg1",
    ])
    assert result.exit_code == 0, result.output
    assert "report.pdf" in result.output
