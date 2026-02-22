"""Ładowanie konfiguracji z config.yaml + nadpisywanie przez zmienne środowiskowe."""

import os
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
ENV_PATH = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "contentforge.db"
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def _load_dotenv():
    """Załaduj zmienne z .env do os.environ (bez nadpisywania istniejących)."""
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def _deep_merge(base: dict, override: dict) -> dict:
    """Rekursywne łączenie dwóch słowników."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> dict:
    """Załaduj konfigurację z .env + config.yaml + zmiennych środowiskowych."""
    _load_dotenv()

    config = {
        "postiz": {"mcp_url": "", "api_key": ""},
        "openai": {"api_key": ""},
        "dalle": {"model": "dall-e-3", "size": "1024x1024"},
    }

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            file_config = yaml.safe_load(f) or {}
        config = _deep_merge(config, file_config)

    # Env vars nadpisują YAML
    env_overrides = {
        "POSTIZ_MCP_URL": ("postiz", "mcp_url"),
        "POSTIZ_API_KEY": ("postiz", "api_key"),
        "OPENAI_API_KEY": ("openai", "api_key"),
    }
    for env_var, (section, key) in env_overrides.items():
        value = os.environ.get(env_var)
        if value:
            config[section][key] = value

    return config


def ensure_dirs():
    """Upewnij się, że katalogi danych istnieją."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
