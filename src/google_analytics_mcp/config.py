"""Configuration for Google Analytics MCP Server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/analytics.readonly",
]

DEFAULT_CREDENTIALS_PATH = Path.home() / ".google-analytics-mcp" / "credentials.json"


@dataclass(frozen=True)
class Config:
    credentials_json: str | None  # raw JSON string from env var
    credentials_path: Path  # file path fallback

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            credentials_json=os.environ.get("GA_CREDENTIALS"),
            credentials_path=Path(
                os.environ.get("GA_CREDENTIALS_PATH", str(DEFAULT_CREDENTIALS_PATH))
            ).expanduser(),
        )


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
