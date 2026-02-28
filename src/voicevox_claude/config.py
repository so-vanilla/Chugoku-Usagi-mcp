"""TOML configuration management."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "voicevox-claude"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_VOICEVOX_HOST = "http://localhost"
DEFAULT_VOICEVOX_PORT = 50021
DEFAULT_SPEED = 1.0


@dataclass(frozen=True)
class VoicevoxConfig:
    host: str = DEFAULT_VOICEVOX_HOST
    port: int = DEFAULT_VOICEVOX_PORT

    @property
    def base_url(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass(frozen=True)
class Config:
    voicevox: VoicevoxConfig = field(default_factory=VoicevoxConfig)
    default_speed: float = DEFAULT_SPEED


def load_config() -> Config:
    """Load config from TOML file, falling back to defaults."""
    if not CONFIG_PATH.exists():
        return Config()

    with open(CONFIG_PATH, "rb") as f:
        data = tomllib.load(f)

    vv = data.get("voicevox", {})
    voicevox = VoicevoxConfig(
        host=vv.get("host", DEFAULT_VOICEVOX_HOST),
        port=vv.get("port", DEFAULT_VOICEVOX_PORT),
    )
    defaults = data.get("defaults", {})
    return Config(
        voicevox=voicevox,
        default_speed=defaults.get("speed", DEFAULT_SPEED),
    )
