from pathlib import Path

from click.testing import CliRunner

from gw.cli import main


def test_config_show(sample_config: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--config-dir", str(sample_config), "config", "show"])
    assert result.exit_code == 0, result.output
    assert "calendar" in result.output
    assert "days" in result.output


def test_config_set(sample_config: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [
        "--config-dir", str(sample_config),
        "config", "set", "defaults.calendar.days", "14",
    ])
    assert result.exit_code == 0, result.output

    result2 = runner.invoke(main, ["--config-dir", str(sample_config), "config", "show"])
    assert "14" in result2.output
