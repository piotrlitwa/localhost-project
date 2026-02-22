"""Budowanie zapytań do wyszukiwania trendów."""

from datetime import datetime


def build_trend_queries(niche: str, language: str = "pl") -> list[str]:
    """Zbuduj listę zapytań do wyszukiwania trendów w danej niszy.

    Zwraca listę zapytań, które mogą być użyte z WebSearch.
    """
    year = datetime.now().year
    month_names_pl = {
        1: "styczeń", 2: "luty", 3: "marzec", 4: "kwiecień",
        5: "maj", 6: "czerwiec", 7: "lipiec", 8: "sierpień",
        9: "wrzesień", 10: "październik", 11: "listopad", 12: "grudzień",
    }
    current_month = month_names_pl.get(datetime.now().month, "")

    queries = [
        f"{niche} trendy {year}",
        f"{niche} nowości {current_month} {year}",
        f"{niche} trending topics {year}",
        f"najnowsze trendy {niche} Polska",
        f"{niche} what's new {year}",
    ]

    return queries


def format_trend_results(results: list[dict]) -> list[str]:
    """Sformatuj wyniki wyszukiwania jako listę trendów.

    Args:
        results: Lista słowników z kluczami 'title' i 'snippet'.

    Returns:
        Lista sformatowanych trendów.
    """
    trends = []
    for r in results:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        if title:
            trend = title
            if snippet:
                trend += f" — {snippet[:150]}"
            trends.append(trend)
    return trends
