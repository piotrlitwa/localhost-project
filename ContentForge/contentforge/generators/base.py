"""Bazowy generator treści — ładowanie promptów i wspólna logika."""

from abc import ABC, abstractmethod
from pathlib import Path

from ..config import PROMPTS_DIR


class BaseGenerator(ABC):
    """Bazowa klasa generatora treści."""

    def __init__(self):
        self.system_prompt = self._load_prompt("system.txt")

    def _load_prompt(self, filename: str) -> str:
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Nie znaleziono promptu: {path}")
        return path.read_text(encoding="utf-8")

    @abstractmethod
    def generate_brief(self, **kwargs) -> str:
        """Wygeneruj brief na podstawie inputu. Zwraca tekst briefu."""

    def build_prompt(self, template_file: str, **kwargs) -> str:
        """Załaduj szablon i wypełnij zmiennymi."""
        template = self._load_prompt(template_file)
        return template.format(**kwargs)

    def get_full_prompt(self, user_prompt: str) -> str:
        """Połącz prompt systemowy z promptem użytkownika."""
        return f"{self.system_prompt}\n\n---\n\n{user_prompt}"
