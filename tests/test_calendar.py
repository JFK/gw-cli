import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from gw.cli import main


@patch("gw.calendar.build_service")
def test_cal_list(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().list().execute.return_value = {
        "items": [
            {
                "id": "evt1",
                "summary": "Team standup",
                "start": {"dateTime": "2026-04-17T10:00:00+09:00"},
                "end": {"dateTime": "2026-04-17T10:30:00+09:00"},
            }
        ]
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "cal", "list", "--days", "7",
    ])
    assert result.exit_code == 0, result.output
    assert "Team standup" in result.output


@patch("gw.calendar.build_service")
def test_cal_list_json(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().list().execute.return_value = {
        "items": [
            {
                "id": "evt1",
                "summary": "Meeting",
                "start": {"dateTime": "2026-04-17T10:00:00+09:00"},
                "end": {"dateTime": "2026-04-17T11:00:00+09:00"},
            }
        ]
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--json", "--config-dir", str(sample_config),
        "cal", "list",
    ])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert len(parsed) == 1
    assert parsed[0]["summary"] == "Meeting"


@patch("gw.calendar.build_service")
def test_cal_create(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().insert().execute.return_value = {
        "id": "new_evt",
        "summary": "New meeting",
        "htmlLink": "https://calendar.google.com/event?eid=xxx",
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "cal", "create",
        "--title", "New meeting",
        "--start", "2026-04-17 10:00",
        "--end", "2026-04-17 11:00",
    ])
    assert result.exit_code == 0, result.output
    assert "New meeting" in result.output


@patch("gw.calendar.build_service")
def test_cal_create_with_meet(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().insert().execute.return_value = {
        "id": "new_evt",
        "summary": "Meet meeting",
        "hangoutLink": "https://meet.google.com/abc-defg-hij",
        "htmlLink": "https://calendar.google.com/event?eid=xxx",
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "cal", "create",
        "--title", "Meet meeting",
        "--start", "2026-04-17 10:00",
        "--end", "2026-04-17 11:00",
        "--meet",
    ])
    assert result.exit_code == 0, result.output


@patch("gw.calendar.build_service")
def test_cal_delete(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.events().delete().execute.return_value = None
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "cal", "delete", "evt1",
    ])
    assert result.exit_code == 0, result.output
    assert "Deleted" in result.output


@patch("gw.calendar.build_service")
def test_cal_free(mock_build: MagicMock, sample_config: Path) -> None:
    mock_service = MagicMock()
    mock_service.freebusy().query().execute.return_value = {
        "calendars": {
            "test@gmail.com": {
                "busy": [
                    {"start": "2026-04-17T10:00:00+09:00", "end": "2026-04-17T11:00:00+09:00"}
                ]
            }
        }
    }
    mock_build.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "cal", "free",
        "--date", "2026-04-17",
        "--account", "test@gmail.com",
    ])
    assert result.exit_code == 0, result.output
    assert "10:00" in result.output
