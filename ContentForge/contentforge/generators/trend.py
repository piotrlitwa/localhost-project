"""Mechanika 2: Generowanie treści na podstawie trendów."""

from .base import BaseGenerator


class TrendGenerator(BaseGenerator):
    """Generator treści na podstawie znalezionego trendu."""

    def generate_brief(self, **kwargs) -> str:
        niche = kwargs.get("niche", "")
        trend = kwargs.get("trend", "")
        if not niche:
            raise ValueError("Wymagana nisza (niche)")
        if not trend:
            raise ValueError("Wymagany trend (trend)")

        user_prompt = self.build_prompt("trend.txt", niche=niche, trend=trend)
        return self.get_full_prompt(user_prompt)
