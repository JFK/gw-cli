from pathlib import Path

import pytest

from gw.config import GwConfig


def test_load_creates_default_config_when_missing(config_dir: Path) -> None:
    cfg = GwConfig(config_dir)
    assert cfg.active_account is None
    assert cfg.accounts == []


def test_load_reads_existing_config(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    assert cfg.active_account == "test@gmail.com"
    assert len(cfg.accounts) == 1
    assert cfg.accounts[0]["email"] == "test@gmail.com"


def test_add_account(config_dir: Path) -> None:
    cfg = GwConfig(config_dir)
    cfg.add_account("new@gmail.com", "credentials/new@gmail.com.json")
    assert len(cfg.accounts) == 1
    assert cfg.active_account == "new@gmail.com"


def test_add_account_sets_first_as_active(config_dir: Path) -> None:
    cfg = GwConfig(config_dir)
    cfg.add_account("first@gmail.com", "credentials/first@gmail.com.json")
    cfg.add_account("second@gmail.com", "credentials/second@gmail.com.json")
    assert cfg.active_account == "first@gmail.com"
    assert len(cfg.accounts) == 2


def test_switch_account(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    cfg.add_account("other@gmail.com", "credentials/other@gmail.com.json")
    cfg.switch_account("other@gmail.com")
    assert cfg.active_account == "other@gmail.com"


def test_switch_account_unknown_raises(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    with pytest.raises(ValueError, match="not found"):
        cfg.switch_account("unknown@gmail.com")


def test_remove_account(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    cfg.remove_account("test@gmail.com")
    assert cfg.accounts == []
    assert cfg.active_account is None


def test_save_and_reload(config_dir: Path) -> None:
    cfg = GwConfig(config_dir)
    cfg.add_account("a@gmail.com", "credentials/a@gmail.com.json")
    cfg.save()

    cfg2 = GwConfig(config_dir)
    assert cfg2.active_account == "a@gmail.com"
    assert len(cfg2.accounts) == 1


def test_get_default(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    assert cfg.get_default("calendar", "days") == 7
    assert cfg.get_default("mail", "limit") == 20


def test_set_default(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    cfg.set_default("calendar", "days", 14)
    cfg.save()
    cfg2 = GwConfig(sample_config)
    assert cfg2.get_default("calendar", "days") == 14


def test_resolve_account_uses_active(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    assert cfg.resolve_account(None) == "test@gmail.com"


def test_resolve_account_uses_override(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    cfg.add_account("other@gmail.com", "credentials/other@gmail.com.json")
    assert cfg.resolve_account("other@gmail.com") == "other@gmail.com"


def test_resolve_account_no_active_raises(config_dir: Path) -> None:
    cfg = GwConfig(config_dir)
    with pytest.raises(RuntimeError, match="No active account"):
        cfg.resolve_account(None)
