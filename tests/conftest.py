import json
from pathlib import Path

import pytest


@pytest.fixture()
def config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory mimicking ~/.config/google-workspace-cli/."""
    creds_dir = tmp_path / "credentials"
    creds_dir.mkdir()
    tokens_dir = tmp_path / "tokens"
    tokens_dir.mkdir()
    return tmp_path


@pytest.fixture()
def sample_config(config_dir: Path) -> Path:
    """Write a sample config.json and return the config dir path."""
    config = {
        "active_account": "test@gmail.com",
        "accounts": [
            {
                "email": "test@gmail.com",
                "credentials": "credentials/test@gmail.com.json",
                "added_at": "2026-04-16T10:00:00Z",
            }
        ],
        "defaults": {
            "calendar": {"days": 7, "timezone": "Asia/Tokyo"},
            "mail": {"limit": 20, "check_query": "is:unread"},
            "drive": {"default_folder": None},
        },
        "loop": {"mail_check_interval": "5m"},
    }
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps(config, indent=2))
    return config_dir


@pytest.fixture()
def mock_credentials(config_dir: Path) -> Path:
    """Write a mock credentials file and return its path."""
    creds = {
        "installed": {
            "client_id": "test-client-id.apps.googleusercontent.com",
            "client_secret": "test-secret",
            "redirect_uris": ["http://localhost"],
        }
    }
    creds_path = config_dir / "credentials" / "test@gmail.com.json"
    creds_path.write_text(json.dumps(creds))
    return creds_path
