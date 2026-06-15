from __future__ import annotations

import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "google-workspace-cli"

DEFAULT_DEFAULTS = {
    "calendar": {"days": 7, "timezone": "Asia/Tokyo"},
    "mail": {"limit": 20, "check_query": "is:unread"},
    "drive": {"default_folder": None},
}


class GwConfig:
    def __init__(self, config_dir: Path = DEFAULT_CONFIG_DIR) -> None:
        self.config_dir = config_dir
        self.config_path = config_dir / "config.json"
        self.credentials_dir = config_dir / "credentials"
        self.tokens_dir = config_dir / "tokens"
        self._load()

    def _load(self) -> None:
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text())
            self.active_account: str | None = data.get("active_account")
            self.accounts: list[dict] = data.get("accounts", [])
            self.defaults: dict = data["defaults"] if "defaults" in data else copy.deepcopy(DEFAULT_DEFAULTS)
            self.loop: dict = data.get("loop", {"mail_check_interval": "5m"})
        else:
            self.active_account = None
            self.accounts = []
            self.defaults = copy.deepcopy(DEFAULT_DEFAULTS)
            self.loop = {"mail_check_interval": "5m"}

    def save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        self.tokens_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "active_account": self.active_account,
            "accounts": self.accounts,
            "defaults": self.defaults,
            "loop": self.loop,
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        os.chmod(self.config_path, 0o600)

    def add_account(self, email: str, credentials_path: str) -> None:
        for acct in self.accounts:
            if acct["email"] == email:
                return
        self.accounts.append(
            {
                "email": email,
                "credentials": credentials_path,
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        if self.active_account is None:
            self.active_account = email
        self.save()

    def switch_account(self, email: str) -> None:
        if not any(a["email"] == email for a in self.accounts):
            raise ValueError(f"Account '{email}' not found. Use 'gw auth login' to add it.")
        self.active_account = email
        self.save()

    def remove_account(self, email: str) -> None:
        self.accounts = [a for a in self.accounts if a["email"] != email]
        if self.active_account == email:
            self.active_account = self.accounts[0]["email"] if self.accounts else None
        token_path = self.tokens_dir / f"{email}.json"
        if token_path.exists():
            token_path.unlink()
        creds_path = self.credentials_dir / f"{email}.json"
        if creds_path.exists():
            creds_path.unlink()
        self.save()

    def resolve_account(self, account: str | None) -> str:
        if account is not None:
            if not any(a["email"] == account for a in self.accounts):
                raise ValueError(f"Account '{account}' not found.")
            return account
        if self.active_account is None:
            raise RuntimeError("No active account. Run 'gw auth login' first.")
        return self.active_account

    def get_credentials_path(self, email: str) -> Path:
        for acct in self.accounts:
            if acct["email"] == email:
                return self.config_dir / acct["credentials"]
        raise ValueError(f"Account '{email}' not found.")

    def get_token_path(self, email: str) -> Path:
        return self.tokens_dir / f"{email}.json"

    def get_default(self, service: str, key: str) -> Any:
        return self.defaults.get(service, {}).get(key)

    def set_default(self, service: str, key: str, value: object) -> None:
        if service not in self.defaults:
            self.defaults[service] = {}
        self.defaults[service][key] = value
