"""Parsowanie dat i sugestie optymalnych godzin publikacji."""

from datetime import datetime, timedelta
from typing import Optional

from dateutil import parser as date_parser

from ..models import Platform

# Optymalne godziny publikacji wg platformy (czas lokalny)
OPTIMAL_HOURS = {
    Platform.LINKEDIN: [
        (8, 0, "Rano — przed rozpoczęciem pracy"),
        (12, 0, "Lunch — przerwa w pracy"),
        (17, 30, "Po pracy — sprawdzanie LinkedIn"),
    ],
    Platform.TWITTER: [
        (9, 0, "Rano — przeglądanie X"),
        (12, 0, "Lunch"),
        (18, 0, "Wieczór — peak engagement"),
        (21, 0, "Późny wieczór — scrollowanie"),
    ],
    Platform.BLOG: [
        (7, 0, "Rano — czytanie przy kawie"),
        (10, 0, "Przedpołudnie — szukanie informacji"),
        (14, 0, "Popołudnie — przerwa na lekturę"),
    ],
    Platform.MEDIUM: [
        (8, 0, "Rano — czytanie artykułów"),
        (11, 0, "Przedpołudnie"),
        (20, 0, "Wieczór — dłuższe czytanie"),
    ],
}

# Najlepsze dni wg platformy
OPTIMAL_DAYS = {
    Platform.LINKEDIN: [0, 1, 2, 3],  # Pon-Czw
    Platform.TWITTER: [0, 1, 2, 3, 4],  # Pon-Pt
    Platform.BLOG: [0, 1, 2],  # Pon-Śr
    Platform.MEDIUM: [1, 2, 3],  # Wt-Czw
}


def parse_schedule_date(text: str) -> Optional[datetime]:
    """Parsuj elastycznie podaną datę/godzinę.

    Obsługuje formaty:
    - "2025-01-15 14:00"
    - "15 stycznia 14:00"
    - "jutro 10:00"
    - "za 2 godziny"
    - "pojutrze 9:00"
    """
    text = text.strip().lower()

    now = datetime.now()

    # Relatywne: "za X godzin/minut"
    if text.startswith("za "):
        parts = text[3:].split()
        if len(parts) >= 2:
            try:
                amount = int(parts[0])
            except ValueError:
                return None
            unit = parts[1]
            if unit.startswith("godzin"):
                return now + timedelta(hours=amount)
            elif unit.startswith("minut"):
                return now + timedelta(minutes=amount)
            elif unit.startswith("dni") or unit.startswith("dzień"):
                return now + timedelta(days=amount)

    # "jutro HH:MM"
    if text.startswith("jutro"):
        time_str = text.replace("jutro", "").strip()
        tomorrow = now + timedelta(days=1)
        if time_str:
            try:
                t = date_parser.parse(time_str)
                return tomorrow.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            except (ValueError, date_parser.ParserError):
                pass
        return tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

    # "pojutrze HH:MM"
    if text.startswith("pojutrze"):
        time_str = text.replace("pojutrze", "").strip()
        day_after = now + timedelta(days=2)
        if time_str:
            try:
                t = date_parser.parse(time_str)
                return day_after.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            except (ValueError, date_parser.ParserError):
                pass
        return day_after.replace(hour=10, minute=0, second=0, microsecond=0)

    # Standardowe parsowanie
    try:
        return date_parser.parse(text, dayfirst=True)
    except (ValueError, date_parser.ParserError):
        return None


def suggest_times(platform: Platform, count: int = 3) -> list[tuple[datetime, str]]:
    """Zasugeruj optymalne czasy publikacji."""
    now = datetime.now()
    suggestions = []
    hours = OPTIMAL_HOURS.get(platform, OPTIMAL_HOURS[Platform.LINKEDIN])
    best_days = OPTIMAL_DAYS.get(platform, [0, 1, 2, 3, 4])

    # Szukaj w najbliższych 7 dniach
    for day_offset in range(7):
        candidate_day = now + timedelta(days=day_offset)
        if candidate_day.weekday() not in best_days:
            continue

        for hour, minute, desc in hours:
            candidate = candidate_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if candidate > now + timedelta(minutes=30):  # Min 30 min w przód
                day_name = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"][candidate.weekday()]
                label = f"{day_name} {candidate.strftime('%d.%m %H:%M')} — {desc}"
                suggestions.append((candidate, label))

            if len(suggestions) >= count:
                return suggestions

    return suggestions
