"""Bazowy formatter treści."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..config import PROMPTS_DIR
from ..models import Platform


@dataclass
class FormattedContent:
    """Wynik formatowania treści."""
    platform: Platform
    title: str
    body: str
    hashtags: str


class BaseFormatter(ABC):
    """Bazowa klasa formattera."""

    platform: Platform = Platform.LINKEDIN
    template_file: str = ""

    def __init__(self):
        self.system_prompt = self._load_prompt("system.txt")

    def _load_prompt(self, filename: str) -> str:
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Nie znaleziono promptu: {path}")
        return path.read_text(encoding="utf-8")

    def build_format_prompt(self, brief: str) -> str:
        """Zbuduj prompt do formatowania."""
        template = self._load_prompt(self.template_file)
        user_prompt = template.format(brief=brief)
        return f"{self.system_prompt}\n\n---\n\n{user_prompt}"

    @abstractmethod
    def parse_response(self, response: str) -> FormattedContent:
        """Parsuj odpowiedź LLM na FormattedContent."""

    def _extract_field(self, response: str, field: str) -> str:
        """Wyciągnij wartość pola z odpowiedzi."""
        lines = response.split("\n")
        prefix = f"{field}:"
        for i, line in enumerate(lines):
            if line.strip().startswith(prefix):
                value = line.strip()[len(prefix):].strip()
                if value:
                    return value
                # Wartość może być w następnych liniach (dla CONTENT:)
                content_lines = []
                for next_line in lines[i + 1:]:
                    # Zatrzymaj się na następnym polu
                    if any(next_line.strip().startswith(f"{f}:") for f in ["TITLE", "HASHTAGS", "META_DESCRIPTION", "SUBTITLE", "CONTENT"]):
                        if next_line.strip().startswith(prefix):
                            continue
                        break
                    content_lines.append(next_line)
                return "\n".join(content_lines).strip()
        return ""

    def _extract_content(self, response: str) -> str:
        """Wyciągnij treść CONTENT z odpowiedzi."""
        marker = "CONTENT:"
        idx = response.find(marker)
        if idx == -1:
            return response
        return response[idx + len(marker):].strip()
