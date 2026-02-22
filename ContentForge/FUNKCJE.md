# ContentForge — Pełna lista funkcji

## Menu główne

| # | Opcja | Opis |
|---|-------|------|
| 1 | Generuj ze słowa kluczowego | Podajesz keyword, system buduje brief i formatuje na 4 platformy |
| 2 | Generuj z trendów | Podajesz niszę, system sugeruje zapytania, wybierasz trend, formatowanie na 4 platformy |
| 3 | Generuj z ogólnego tematu | Podajesz temat, generator z większą swobodą kreatywną, formatowanie na 4 platformy |
| 4 | Przeglądaj i zatwierdzaj | Przeglądanie treści, zatwierdzanie/odrzucanie, zmiana statusów |
| 5 | Publikuj przez Postiz | Automatyczna publikacja na podłączone kanały social media (MCP) |
| 6 | Publikuj ręcznie | Kopiowanie treści na platformy poza Postiz (Quora, newsletter, Reddit itd.) |
| 7 | Zarządzaj obrazami | Generowanie DALL-E lub dołączanie plików lokalnych |
| 8 | Historia sesji | Przeglądanie wszystkich sesji, podgląd i pełna treść |
| 9 | Log publikacji | Historia wszystkich publikacji ze statusami |

---

## 3 mechaniki generowania treści

### Mechanika 1 — Słowo kluczowe
- Podajesz keyword (np. "automatyzacja marketingu")
- System generuje brief z: tematem, grupą docelową, kątem podejścia, kluczowymi punktami, CTA
- Brief formatowany na 4 platformy

### Mechanika 2 — Trendy
- Podajesz niszę/branżę
- System generuje 5 zapytań do wyszukiwania trendów (po polsku i angielsku, z aktualnym miesiącem i rokiem)
- Wklejasz znaleziony trend
- Brief łączący trend z niszą, formatowany na 4 platformy

### Mechanika 3 — Ogólny temat
- Podajesz temat (np. "przyszłość pracy zdalnej")
- Generator z większą swobodą kreatywną — szuka nietypowego kąta, dodaje storytelling
- Brief z elementem narracyjnym, formatowany na 4 platformy

---

## 4 formaty wyjściowe

| Platforma | Format | Specyfikacja |
|-----------|--------|--------------|
| **LinkedIn / Facebook** | Post socialowy | 1300–2000 znaków, hook w pierwszych 2 liniach, krótkie akapity, emoji, CTA, 3–5 hashtagów |
| **X / Twitter** | Tweet + wątek | Wariant A: pojedynczy tweet (280 znaków). Wariant B: wątek 3–7 tweetów z numeracją |
| **WordPress Blog** | Artykuł SEO | 800–1500 słów, tytuł SEO (max 60 znaków), meta opis, nagłówki H2/H3, Markdown |
| **Medium** | Artykuł storytelling | 1000–2000 słów, tytuł + podtytuł, styl konwersacyjny, cytaty/statystyki, Markdown |

---

## Workflow zatwierdzania treści

### Statusy

| Status | Kolor | Znaczenie |
|--------|-------|-----------|
| `draft` (szkic) | zółty | Nowo wygenerowana, czeka na przegląd |
| `approved` (zatwierdzony) | zielony | Przejrzana i zatwierdzona — gotowa do publikacji |
| `rejected` (odrzucony) | czerwony | Odrzucona — do poprawy lub pominięcia |
| `published` (opublikowany) | niebieski | Opublikowana (automatycznie lub ręcznie) |

### Przepływ

```
Generowanie → draft → [przegląd] → approved → [publikacja] → published
                                  → rejected
```

### Opcje przeglądu (menu 4)

- **Przeglądaj szkice** — lista treści do zatwierdzenia
- **Przeglądaj zatwierdzone** — co jest gotowe do publikacji
- **Przeglądaj odrzucone** — co zostało odrzucone
- **Przeglądaj z sesji** — wszystkie treści z konkretnej sesji
- **Przegląd jedna po drugiej** — pełna treść + decyzja (zatwierdź / odrzuć / pomiń / zakończ)
- **Zmień status** — ręczna zmiana statusu po ID
- **Zatwierdź wszystkie** — hurtowe zatwierdzanie szkiców

### Blokada publikacji

Publikować można **wyłącznie zatwierdzone** treści. System blokuje publikację szkiców i odrzuconych.

---

## Publikacja przez Postiz (MCP)

### Protokół

Komunikacja z Postiz przez **Model Context Protocol (MCP)** — nie REST API. Sesja MCP inicjalizowana automatycznie.

### Dostępne narzędzia MCP

| Narzędzie | Cel |
|-----------|-----|
| `integrationList` | Lista podłączonych kanałów (LinkedIn, X, Facebook itd.) |
| `integrationSchema` | Schemat wymaganych ustawień per platforma |
| `triggerTool` | Pobieranie dodatkowych danych (np. ID grup) |
| `integrationSchedulePostTool` | Tworzenie/planowanie postów |
| `generateImageTool` | Generowanie obrazów AI przez Postiz |

### Obsługiwane platformy Postiz

x, linkedin, linkedin-page, reddit, instagram, instagram-standalone, facebook, threads, youtube, gmb, tiktok, pinterest, dribbble, discord, slack, mastodon, bluesky, lemmy, wrapcast, telegram, nostr, vk, medium, devto, hashnode, wordpress, listmonk

### Typy publikacji

| Typ | Opis |
|-----|------|
| **Teraz** | Natychmiastowa publikacja |
| **Zaplanuj** | Publikacja w wybranym terminie (system sugeruje optymalne godziny) |
| **Szkic** | Zapisanie jako draft w Postiz do późniejszej edycji |

### Sugerowane optymalne godziny

| Platforma | Godziny | Najlepsze dni |
|-----------|---------|---------------|
| LinkedIn | 8:00, 12:00, 17:30 | Pon–Czw |
| X/Twitter | 9:00, 12:00, 18:00, 21:00 | Pon–Pt |
| Blog | 7:00, 10:00, 14:00 | Pon–Śr |
| Medium | 8:00, 11:00, 20:00 | Wt–Czw |

### Parsowanie dat

```
jutro 10:00              → następny dzień, 10:00
pojutrze 14:30           → za 2 dni, 14:30
za 2 godziny             → teraz + 2h
za 3 dni                 → teraz + 3 dni
2026-03-15 09:00         → konkretna data
15 marca 10:00           → naturalny format
```

### Konwersja treści

Markdown automatycznie konwertowany na HTML wymagany przez Postiz:
- `## Nagłówek` → `<h2>Nagłówek</h2>`
- `**pogrubienie**` → `<strong>pogrubienie</strong>`
- `- punkt` → `<ul><li>punkt</li></ul>`
- Akapity → `<p>tekst</p>`

### Rate limiting

30 żądań na godzinę (sliding window). System automatycznie czeka gdy limit wyczerpany. Wyświetla ile żądań pozostało.

---

## Ręczna publikacja

Dla platform **poza Postiz** (Quora, newsletter, Reddit, forum itd.):

1. Wyświetla listę zatwierdzonych treści
2. Pokazuje pełną treść sformatowaną do skopiowania
3. Kopiujesz i wklejasz na docelową platformę
4. Podajesz nazwę platformy (np. "Quora")
5. System oznacza treść jako opublikowaną z logiem `Ręcznie: Quora`

---

## Obrazy

### DALL-E 3 (OpenAI API)

- Automatycznie sugeruje prompt na podstawie treści sesji
- Możesz edytować prompt przed generowaniem
- Obraz zapisywany lokalnie w `data/images/` jako PNG
- Model: dall-e-3, rozmiar: 1024x1024 (konfigurowalne)

### Plik lokalny

- Dozwolone formaty: PNG, JPG, JPEG, GIF, WebP, BMP
- Maksymalny rozmiar: 20 MB
- Plik kopiowany do `data/images/` (oryginał nietknięty)

### Postiz AI

- Generowanie obrazu bezpośrednio przez Postiz podczas publikacji
- Prompt na podstawie tytułu treści
- Obraz automatycznie dołączany do posta

### Powiązanie z treścią

- Obrazy przypisane do **sesji** (nie pojedynczej treści)
- Jedna sesja może mieć wiele obrazów
- Automatycznie dołączane przy publikacji przez Postiz

---

## Baza danych SQLite

### 5 tabel

| Tabela | Cel | Kluczowe pola |
|--------|-----|---------------|
| `content_sessions` | Sesje generowania | mechanika, input, trend, język, data |
| `generated_content` | Wygenerowane treści | sesja, platforma, tytuł, body, hashtagi, **status** |
| `images` | Obrazy | sesja, źródło (DALL-E/lokalny), ścieżka, prompt, Postiz ID |
| `publish_log` | Log publikacji | treść, integracja, typ, status, odpowiedź API, data |
| `integrations_cache` | Cache integracji Postiz | ID, nazwa, provider, odświeżany co 1h |

### Automatyczne migracje

Schemat tworzony automatycznie przy pierwszym uruchomieniu. Migracje dodają nowe kolumny (np. `status`) bez utraty danych.

---

## Konfiguracja

### Plik `.env` (zalecany)

```
POSTIZ_MCP_URL=https://twoja-instancja/api/mcp/twoj-klucz
POSTIZ_API_KEY=twoj-klucz
OPENAI_API_KEY=klucz-openai
```

### Plik `config.yaml` (alternatywnie)

```yaml
postiz:
  mcp_url: "https://twoja-instancja/api/mcp/twoj-klucz"
  api_key: "twoj-klucz"
openai:
  api_key: "klucz-openai"
dalle:
  model: "dall-e-3"
  size: "1024x1024"
```

### Priorytet

`.env` → `config.yaml` → zmienne systemowe (nadpisują poprzednie)

---

## Język i adaptacja kulturowa

Wszystkie prompty zawierają zasady:

- Naturalny polski (nie kalki z angielskiego)
- Polska interpunkcja i konwencje
- Uniwersalne przykłady i odniesienia
- Elementy kulturowo specyficzne oznaczone tagiem `[KULTUROWO]`
- Profesjonalny, ale przystępny ton
- Aktywna strona zdań
- Poprawna odmiana i składnia

---

## Wymagania techniczne

### Zależności

```
requests>=2.31.0        # HTTP: Postiz MCP + OpenAI API
rich>=13.7.0            # Formatowanie CLI (tabele, panele, markdown)
pyyaml>=6.0.1           # Parsowanie config.yaml
python-dateutil>=2.8.2  # Elastyczne parsowanie dat
```

### Stdlib

sqlite3, json, pathlib, dataclasses, base64, shutil, enum, abc, re, uuid, time, collections

### Uruchomienie

```bash
cd ContentForge
source venv/bin/activate
python main.py
```
