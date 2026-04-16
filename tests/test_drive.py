import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from gw.cli import main


@patch("gw.drive.build_service")
def test_drive_list(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.files().list().execute.return_value = {
        "files": [
            {"id": "f1", "name": "report.pdf", "mimeType": "application/pdf", "modifiedTime": "2026-04-16T10:00:00Z"},
        ]
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, ["--config-dir", str(sample_config), "drive", "list"])
    assert result.exit_code == 0, result.output
    assert "report.pdf" in result.output


@patch("gw.drive.build_service")
def test_drive_upload(mock_build: MagicMock, sample_config: Path, tmp_path: Path) -> None:
    mock_service = MagicMock()
    mock_service.files().create().execute.return_value = {
        "id": "new_f1", "name": "upload.txt",
        "webViewLink": "https://drive.google.com/file/d/new_f1/view",
    }
    mock_build.return_value = mock_service

    upload_file = tmp_path / "upload.txt"
    upload_file.write_text("test content")

    runner = CliRunner()
    result = runner.invoke(main, ["--config-dir", str(sample_config), "drive", "upload", str(upload_file)])
    assert result.exit_code == 0, result.output
    assert "upload.txt" in result.output


@patch("gw.drive.build_service")
def test_drive_create(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.files().create().execute.return_value = {
        "id": "doc1", "name": "New Doc",
        "webViewLink": "https://docs.google.com/document/d/doc1/edit",
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "drive", "create", "--type", "doc", "--title", "New Doc",
    ])
    assert result.exit_code == 0, result.output
    assert "New Doc" in result.output


@patch("gw.drive.build_service")
def test_drive_share(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.permissions().create().execute.return_value = {"id": "perm1"}
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "drive", "share", "f1", "--email", "user@example.com", "--role", "writer",
    ])
    assert result.exit_code == 0, result.output
    assert "Shared" in result.output


@patch("gw.drive.build_service")
def test_drive_unshare(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.permissions().list().execute.return_value = {
        "permissions": [
            {"id": "perm1", "emailAddress": "user@example.com", "role": "writer"},
        ]
    }
    mock_service.permissions().delete().execute.return_value = None
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "drive", "unshare", "f1", "--email", "user@example.com",
    ])
    assert result.exit_code == 0, result.output
