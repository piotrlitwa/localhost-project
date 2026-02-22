# ContentForge — Instrukcja generowania treści na miesiąc

## 1. Konfiguracja (jednorazowo)

### Klucze API

```bash
cd ContentForge
cp config.yaml.example config.yaml
```

Uzupełnij `config.yaml`:

```yaml
postiz:
  base_url: "https://twoja-instancja/public/v1"
  api_key: "twoj-klucz-postiz"

openai:
  api_key: "twoj-klucz-openai"    # opcjonalnie, do obrazów DALL-E

dalle:
  model: "dall-e-3"
  size: "1024x1024"
```

Alternatywnie ustaw zmienne środowiskowe:

```bash
export POSTIZ_BASE_URL="https://twoja-instancja/public/v1"
export POSTIZ_API_KEY="twoj-klucz"
export OPENAI_API_KEY="twoj-klucz-openai"
```

### Uruchomienie

```bash
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
8. Treści zapisane w bazie danych
9. (Opcjonalnie) Dodaj obraz — menu 5
10. (Opcjonalnie) Opublikuj / zaplanuj — menu 4
```

---

## 4. Obrazy (opcjonalnie)

Menu główne → **5 — Zarządzaj obrazami**

| Opcja | Opis |
|-------|------|
| **DALL-E** | System sugeruje prompt na podstawie treści → potwierdzasz/edytujesz → obraz generowany automatycznie |
| **Plik lokalny** | Wskazujesz plik z dysku (PNG, JPG, WEBP, GIF, BMP, max 20 MB) → kopiowany do `data/images/` |

Obrazy są automatycznie uploadowane do Postiz przy publikacji.

---

## 5. Publikacja przez Postiz

Menu główne → **4 — Publikuj treść**

### Kroki:

1. Wybierz sesję (lista ostatnich 10)
2. Wybierz treść (LinkedIn / Twitter / Blog / Medium)
3. Wybierz integrację (kanał w Postiz)
4. Wybierz typ publikacji:
   - **Teraz** — natychmiastowa publikacja
   - **Zaplanuj** — system sugeruje optymalne godziny per platforma
   - **Szkic** — zapisz w Postiz jako draft
5. Potwierdź → post wysłany

### Sugerowane optymalne godziny (per platforma):

| Platforma | Najlepsze godziny | Najlepsze dni |
|-----------|-------------------|---------------|
| LinkedIn  | 8:00, 12:00, 17:30 | Pon–Czw |
| X/Twitter | 9:00, 12:00, 18:00, 21:00 | Pon–Pt |
| Blog      | 7:00, 10:00, 14:00 | Pon–Śr |
| Medium    | 8:00, 11:00, 20:00 | Wt–Czw |

### Formaty daty przy planowaniu:

```
jutro 10:00
pojutrze 14:30
za 2 godziny
2025-03-15 09:00
15 marca 10:00
```

### Rate limit: 30 żądań/godzinę (~5 pełnych sesji publikacji/h)

---

## 6. Plan na miesiąc (20 dni roboczych)

### Matematyka:

> **20 sesji × 4 formaty = 80 treści**
>
> 20× LinkedIn, 20× Twitter, 20× Blog, 20× Medium

### Sugerowana strategia tygodniowa:

| Dzień | Mechanika | Cel |
|-------|-----------|-----|
| Poniedziałek | Trend (2) | Post na gorący temat — duży zasięg |
| Wtorek | Keyword (1) | Post SEO — evergreen content |
| Środa | Temat (3) | Kreatywny post — storytelling |
| Czwartek | Keyword (1) | Post ekspercki — budowanie autorytetu |
| Piątek | Trend (2) | Podsumowanie tygodnia w branży |

### Przykładowy harmonogram marca:

| Tydzień | Pon 🔥 | Wt 🔑 | Śr 💡 | Czw 🔑 | Pt 🔥 |
|---------|--------|--------|--------|---------|--------|
| 1 (3–7) | Trend w AI | SEO: automatyzacja | Temat: praca zdalna | SEO: produktywność | Trend: social media |
| 2 (10–14) | Trend w branży | SEO: content marketing | Temat: personal branding | SEO: copywriting | Trend: technologie |
| 3 (17–21) | Trend w ecommerce | SEO: email marketing | Temat: storytelling | SEO: analytics | Trend: startup |
| 4 (24–28) | Trend w SaaS | SEO: lead generation | Temat: kreatywność | SEO: social selling | Trend: podsumowanie |

---

## 7. Historia i przegląd

| Menu | Co pokazuje |
|------|-------------|
| **6 — Historia sesji** | Lista wszystkich sesji, podgląd treści, pełna treść z formatowaniem |
| **7 — Log publikacji** | Wszystkie publikacje: status, integracja, data, typ |

---

## 8. Struktura plików

```
ContentForge/
├── main.py              ← uruchamiasz to
├── config.yaml          ← twoje klucze API (gitignored)
├── data/
│   ├── contentforge.db  ← baza SQLite (gitignored)
│   └── images/          ← obrazy (gitignored)
└── venv/                ← środowisko Python
```

---

## 9. Szybki start — pierwsza sesja

```bash
# 1. Wejdź do projektu
cd ContentForge
source venv/bin/activate

# 2. Skonfiguruj (jednorazowo)
cp config.yaml.example config.yaml
# edytuj config.yaml — dodaj klucze API

# 3. Uruchom
python main.py

# 4. Wybierz: 1 (słowo kluczowe)
# 5. Wpisz: "content marketing"
# 6. Skopiuj wygenerowany prompt do Claude
# 7. Wklej odpowiedź Claude do ContentForge
# 8. Powtórz dla 4 platform
# 9. Gotowe — treści w bazie!
```
