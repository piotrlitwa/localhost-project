# ContentForge — Instrukcja generowania treści na miesiąc

## 1. Konfiguracja (jednorazowo)

### Klucze API

Uzupełnij plik `.env` w katalogu ContentForge:

```
POSTIZ_MCP_URL=https://twoja-instancja/api/mcp/twoj-klucz
POSTIZ_API_KEY=twoj-klucz
OPENAI_API_KEY=klucz-openai
```

### Uruchomienie

```bash
cd ContentForge
source venv/bin/activate
python main.py
```

---

## 2. Trzy mechaniki generowania

| # | Mechanika | Kiedy użyć | Co podajesz |
|---|-----------|------------|-------------|
| 1 | **Słowo kluczowe** | Masz konkretny temat SEO | np. "automatyzacja marketingu" |
| 2 | **Trendy** | Chcesz jechać na fali aktualnych tematów | Podajesz niszę, system sugeruje zapytania, wklejasz znaleziony trend |
| 3 | **Ogólny temat** | Masz luźny pomysł, chcesz kreatywności | np. "przyszłość pracy zdalnej" |

Każda mechanika generuje treść na **4 platformy naraz**:

- LinkedIn / Facebook (1300–2000 znaków, hook + CTA)
- X / Twitter (tweet 280 znaków + wątek 3–7 tweetów)
- WordPress blog (800–1500 słów, SEO, nagłówki H2/H3)
- Medium (1000–2000 słów, storytelling)

---

## 3. Flow jednej sesji (~10 min)

```
1. Uruchom: python main.py
2. Wybierz mechanikę (1 / 2 / 3)
3. Podaj input (słowo kluczowe / niszę / temat)
4. System generuje prompt briefu
5. Skopiuj prompt → wklej do Claude → skopiuj odpowiedź → wklej do ContentForge
6. System generuje prompt formatowania dla każdej z 4 platform
7. Dla każdej platformy: skopiuj prompt → Claude → wklej odpowiedź
8. Treści zapisane w bazie danych ze statusem "szkic"
```

---

## 4. Zatwierdzanie treści

Menu główne → **4 — Przeglądaj i zatwierdzaj treści**

### Statusy

| Status | Znaczenie |
|--------|-----------|
| Szkic | Nowo wygenerowana, czeka na przegląd |
| Zatwierdzony | Gotowa do publikacji |
| Odrzucony | Do poprawy lub pominięcia |
| Opublikowany | Opublikowana (Postiz lub ręcznie) |

### Opcje

- Przeglądaj szkice / zatwierdzone / odrzucone / z sesji
- Przejrzyj jedna po drugiej (a = zatwierdź, r = odrzuć, s = pomiń, q = zakończ)
- Zmień status konkretnej treści po ID
- Zatwierdź wszystkie szkice hurtowo

**Publikować można wyłącznie zatwierdzone treści.**

---

## 5. Publikacja przez Postiz (MCP)

Menu główne → **5 — Publikuj treść (Postiz)**

### Kroki:

1. System pokazuje tylko zatwierdzone treści
2. Wybierasz treść do publikacji
3. Wybierasz integrację (kanał w Postiz)
4. System pobiera wymagane ustawienia platformy
5. Wybierasz typ: teraz / zaplanuj / szkic
6. Potwierdzasz → post wysłany, treść oznaczona jako opublikowana

### Sugerowane optymalne godziny:

| Platforma | Godziny | Dni |
|-----------|---------|-----|
| LinkedIn | 8:00, 12:00, 17:30 | Pon–Czw |
| X/Twitter | 9:00, 12:00, 18:00, 21:00 | Pon–Pt |
| Blog | 7:00, 10:00, 14:00 | Pon–Śr |
| Medium | 8:00, 11:00, 20:00 | Wt–Czw |

### Formaty daty:

```
jutro 10:00
pojutrze 14:30
za 2 godziny
2026-03-15 09:00
```

---

## 6. Ręczna publikacja

Menu główne → **6 — Publikuj ręcznie (Quora, inne)**

Dla platform poza Postiz:

1. Wyświetla zatwierdzone treści
2. Pokazuje pełną treść do skopiowania
3. Kopiujesz i wklejasz na Quorę / newsletter / Reddit / gdziekolwiek
4. Podajesz nazwę platformy
5. Treść oznaczona jako opublikowana z logiem

---

## 7. Obrazy

Menu główne → **7 — Zarządzaj obrazami**

| Opcja | Opis |
|-------|------|
| **DALL-E** | System sugeruje prompt → potwierdzasz/edytujesz → obraz wygenerowany automatycznie |
| **Plik lokalny** | Wskazujesz plik z dysku (PNG, JPG, WEBP, GIF, BMP, max 20 MB) |
| **Postiz AI** | Generowanie obrazu podczas publikacji (menu 5) |

---

## 8. Historia i logi

| Menu | Co pokazuje |
|------|-------------|
| **8 — Historia sesji** | Lista sesji, podgląd treści ze statusami, pełna treść z formatowaniem |
| **9 — Log publikacji** | Wszystkie publikacje: status, integracja (Postiz/ręczna), data, typ |

---

## 9. Plan na miesiąc (20 dni roboczych)

> **20 sesji x 4 formaty = 80 treści**

### Strategia tygodniowa:

| Dzień | Mechanika | Cel |
|-------|-----------|-----|
| Poniedziałek | Trend (2) | Post na gorący temat — duży zasięg |
| Wtorek | Keyword (1) | Post SEO — evergreen content |
| Środa | Temat (3) | Kreatywny post — storytelling |
| Czwartek | Keyword (1) | Post ekspercki — budowanie autorytetu |
| Piątek | Trend (2) | Podsumowanie tygodnia w branży |

---

## 10. Szybki start

```bash
cd ContentForge
source venv/bin/activate
python main.py

# Menu: 1 (słowo kluczowe) → wpisz keyword → skopiuj prompt do Claude
# → wklej odpowiedź → powtórz dla 4 platform
# Menu: 4 (zatwierdź) → przejrzyj i zatwierdź treści
# Menu: 5 (Postiz) lub 6 (ręcznie) → opublikuj
```
