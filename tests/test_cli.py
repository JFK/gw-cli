from click.testing import CliRunner

from gw.cli import main


def test_main_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "gw" in result.output
    assert "auth" in result.output
    assert "cal" in result.output
    assert "mail" in result.output
    assert "drive" in result.output
    assert "config" in result.output


def test_auth_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["auth", "--help"])
    assert result.exit_code == 0
    assert "login" in result.output
    assert "list" in result.output
    assert "switch" in result.output
    assert "status" in result.output
    assert "remove" in result.output


def test_cal_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["cal", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "create" in result.output
    assert "delete" in result.output
    assert "free" in result.output


def test_mail_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["mail", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "read" in result.output
    assert "send" in result.output
    assert "mark" in result.output
    assert "attachments" in result.output


def test_drive_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["drive", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "upload" in result.output
    assert "create" in result.output
    assert "share" in result.output


def test_config_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["config", "--help"])
    assert result.exit_code == 0
    assert "show" in result.output
    assert "set" in result.output
