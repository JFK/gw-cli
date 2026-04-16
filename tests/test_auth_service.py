import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gw.auth import build_service
from gw.config import GwConfig


def test_build_service_loads_token(sample_config: Path) -> None:
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

    with patch("gw.auth.build") as mock_build:
        mock_build.return_value = MagicMock()
        service = build_service(cfg, "test@gmail.com", "calendar", "v3")
        mock_build.assert_called_once()
        assert service is not None


def test_build_service_missing_token_raises(sample_config: Path) -> None:
    cfg = GwConfig(sample_config)
    with pytest.raises(RuntimeError, match="No token found"):
        build_service(cfg, "test@gmail.com", "calendar", "v3")
