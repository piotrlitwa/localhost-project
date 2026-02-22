"""Mechanika 1: Generowanie treści ze słowa kluczowego."""

from .base import BaseGenerator


class KeywordGenerator(BaseGenerator):
    """Generator treści na podstawie słowa kluczowego."""

    def generate_brief(self, **kwargs) -> str:
        keyword = kwargs.get("keyword", "")
        if not keyword:
            raise ValueError("Wymagane słowo kluczowe (keyword)")

        user_prompt = self.build_prompt("keyword.txt", keyword=keyword)
        return self.get_full_prompt(user_prompt)
