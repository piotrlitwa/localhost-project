"""Ładowanie konfiguracji z config.yaml + nadpisywanie przez zmienne środowiskowe."""

import os
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "contentforge.db"
PROMPTS_DIR = PROJECT_ROOT / "prompts"


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
    """Załaduj konfigurację z pliku YAML i nadpisz zmiennymi środowiskowymi."""
    config = {
        "postiz": {"base_url": "", "api_key": ""},
        "openai": {"api_key": ""},
        "dalle": {"model": "dall-e-3", "size": "1024x1024"},
    }

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            file_config = yaml.safe_load(f) or {}
        config = _deep_merge(config, file_config)

    # Env vars nadpisują YAML
    env_overrides = {
        "POSTIZ_BASE_URL": ("postiz", "base_url"),
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
