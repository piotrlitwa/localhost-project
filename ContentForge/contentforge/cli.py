"""Menu CLI (rich) — orkiestracja całego flow ContentForge."""

import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from .config import load_config, ensure_dirs
from .database import Database
from .formatters.base import FormattedContent
from .formatters.blog import BlogFormatter
from .formatters.linkedin import LinkedInFormatter
from .formatters.medium import MediumFormatter
from .formatters.twitter import TwitterFormatter
from .generators.keyword import KeywordGenerator
from .generators.topic import TopicGenerator
from .generators.trend import TrendGenerator
from .images.dalle import DalleGenerator
from .images.local import LocalImageHandler
from .models import (
    ContentSession,
    ContentStatus,
    GeneratedContent,
    ImageRecord,
    Integration,
    Mechanic,
    Platform,
    PublishRecord,
    PublishType,
)
from .publishing.postiz import PostizClient
from .publishing.scheduler import parse_schedule_date, suggest_times
from .utils.web_search import build_trend_queries

console = Console()

ALL_FORMATTERS = [
    LinkedInFormatter(),
    TwitterFormatter(),
    BlogFormatter(),
    MediumFormatter(),
]

PLATFORM_LABELS = {
    Platform.LINKEDIN: "LinkedIn/Facebook",
    Platform.TWITTER: "X/Twitter",
    Platform.BLOG: "WordPress Blog",
    Platform.MEDIUM: "Medium",
}

STATUS_STYLES = {
    ContentStatus.DRAFT: ("[yellow]szkic[/yellow]", "yellow"),
    ContentStatus.APPROVED: ("[green]zatwierdzony[/green]", "green"),
    ContentStatus.REJECTED: ("[red]odrzucony[/red]", "red"),
    ContentStatus.PUBLISHED: ("[blue]opublikowany[/blue]", "blue"),
}


class ContentForgeCLI:
    """Główna klasa CLI ContentForge."""

    def __init__(self):
        self.config = load_config()
        ensure_dirs()
        self.db = Database()

    def run(self):
        """Uruchom główną pętlę menu."""
        console.print(
            Panel.fit(
                "[bold cyan]ContentForge[/bold cyan]\n"
                "System tworzenia treści w języku polskim",
                border_style="cyan",
            )
        )

        while True:
            console.print()
            console.print("[bold]Menu główne:[/bold]")
            console.print("  [cyan]1[/cyan] — Generuj treść ze słowa kluczowego")
            console.print("  [cyan]2[/cyan] — Generuj treść z trendów")
            console.print("  [cyan]3[/cyan] — Generuj treść z ogólnego tematu")
            console.print("  [cyan]4[/cyan] — Przeglądaj i zatwierdzaj treści")
            console.print("  [cyan]5[/cyan] — Publikuj treść (Postiz)")
            console.print("  [cyan]6[/cyan] — Zarządzaj obrazami")
            console.print("  [cyan]7[/cyan] — Historia sesji")
            console.print("  [cyan]8[/cyan] — Log publikacji")
            console.print("  [cyan]0[/cyan] — Wyjście")
            console.print()

            choice = Prompt.ask("Wybierz opcję", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"], default="0")

            try:
                if choice == "1":
                    self._mechanic_keyword()
                elif choice == "2":
                    self._mechanic_trend()
                elif choice == "3":
                    self._mechanic_topic()
                elif choice == "4":
                    self._review_flow()
                elif choice == "5":
                    self._publish_flow()
                elif choice == "6":
                    self._images_menu()
                elif choice == "7":
                    self._show_history()
                elif choice == "8":
                    self._show_publish_log()
                elif choice == "0":
                    console.print("[dim]Do zobaczenia![/dim]")
                    break
            except KeyboardInterrupt:
                console.print("\n[dim]Przerwano.[/dim]")
            except Exception as e:
                console.print(f"[red]Błąd: {e}[/red]")

    # === MECHANIKA 1: Słowo kluczowe ===

    def _mechanic_keyword(self):
        console.print(Panel("[bold]Mechanika 1: Generowanie ze słowa kluczowego[/bold]", border_style="green"))
        keyword = Prompt.ask("Podaj słowo kluczowe")
        if not keyword.strip():
            console.print("[yellow]Nie podano słowa kluczowego.[/yellow]")
            return

        generator = KeywordGenerator()
        prompt = generator.generate_brief(keyword=keyword)

        session = ContentSession(mechanic=Mechanic.KEYWORD, input_text=keyword)
        session_id = self.db.create_session(session)

        console.print(f"\n[dim]Sesja #{session_id} utworzona.[/dim]")
        self._display_prompt_and_format(prompt, session_id)

    # === MECHANIKA 2: Trendy ===

    def _mechanic_trend(self):
        console.print(Panel("[bold]Mechanika 2: Generowanie z trendów[/bold]", border_style="green"))
        niche = Prompt.ask("Podaj niszę / branżę")
        if not niche.strip():
            console.print("[yellow]Nie podano niszy.[/yellow]")
            return

        # Buduj zapytania do wyszukiwania
        queries = build_trend_queries(niche)
        console.print("\n[bold]Sugerowane zapytania do wyszukiwania trendów:[/bold]")
        for i, q in enumerate(queries, 1):
            console.print(f"  {i}. {q}")

        console.print(
            "\n[dim]Użyj tych zapytań z WebSearch lub podaj znaleziony trend ręcznie.[/dim]"
        )

        trend = Prompt.ask("\nPodaj znaleziony trend")
        if not trend.strip():
            console.print("[yellow]Nie podano trendu.[/yellow]")
            return

        generator = TrendGenerator()
        prompt = generator.generate_brief(niche=niche, trend=trend)

        session = ContentSession(mechanic=Mechanic.TREND, input_text=niche, found_trend=trend)
        session_id = self.db.create_session(session)

        console.print(f"\n[dim]Sesja #{session_id} utworzona.[/dim]")
        self._display_prompt_and_format(prompt, session_id)

    # === MECHANIKA 3: Ogólny temat ===

    def _mechanic_topic(self):
        console.print(Panel("[bold]Mechanika 3: Generowanie z ogólnego tematu[/bold]", border_style="green"))
        topic = Prompt.ask("Podaj temat")
        if not topic.strip():
            console.print("[yellow]Nie podano tematu.[/yellow]")
            return

        generator = TopicGenerator()
        prompt = generator.generate_brief(topic=topic)

        session = ContentSession(mechanic=Mechanic.TOPIC, input_text=topic)
        session_id = self.db.create_session(session)

        console.print(f"\n[dim]Sesja #{session_id} utworzona.[/dim]")
        self._display_prompt_and_format(prompt, session_id)

    # === Wyświetlanie promptu i formatowanie ===

    def _display_prompt_and_format(self, brief_prompt: str, session_id: int):
        """Wyświetl prompt generatora i uruchom formatowanie."""
        console.print(Panel("[bold]Wygenerowany prompt briefu:[/bold]", border_style="blue"))
        console.print(brief_prompt)

        console.print(
            "\n[dim]Powyższy prompt jest gotowy do przekazania do LLM. "
            "Wklej odpowiedź LLM poniżej (zakończ pustą linią + Enter):[/dim]"
        )

        brief_response = self._read_multiline("Brief od LLM")
        if not brief_response:
            console.print("[yellow]Nie podano briefu. Sesja zapisana bez treści.[/yellow]")
            return

        # Formatowanie na 4 platformy
        console.print("\n[bold]Generowanie promptów formatowania dla 4 platform...[/bold]")

        for formatter in ALL_FORMATTERS:
            label = PLATFORM_LABELS[formatter.platform]
            console.print(f"\n{'='*60}")
            console.print(Panel(f"[bold]{label}[/bold]", border_style="magenta"))

            format_prompt = formatter.build_format_prompt(brief_response)
            console.print(format_prompt)

            console.print(
                f"\n[dim]Wklej odpowiedź LLM dla {label} (zakończ pustą linią + Enter):[/dim]"
            )
            format_response = self._read_multiline(f"Odpowiedź {label}")

            if format_response:
                parsed = formatter.parse_response(format_response)
                content = GeneratedContent(
                    session_id=session_id,
                    platform=parsed.platform,
                    title=parsed.title,
                    body=parsed.body,
                    hashtags=parsed.hashtags,
                )
                content_id = self.db.save_content(content)
                console.print(f"[green]Zapisano treść #{content_id} ({label})[/green]")
            else:
                console.print(f"[yellow]Pominięto {label}.[/yellow]")

        console.print(f"\n[bold green]Sesja #{session_id} zakończona.[/bold green]")

    # === Przegląd i zatwierdzanie ===

    def _review_flow(self):
        console.print(Panel("[bold]Przeglądaj i zatwierdzaj treści[/bold]", border_style="yellow"))

        console.print("  [cyan]1[/cyan] — Przeglądaj szkice (do zatwierdzenia)")
        console.print("  [cyan]2[/cyan] — Przeglądaj zatwierdzone")
        console.print("  [cyan]3[/cyan] — Przeglądaj odrzucone")
        console.print("  [cyan]4[/cyan] — Przeglądaj wszystkie z sesji")
        console.print("  [cyan]0[/cyan] — Powrót")

        choice = Prompt.ask("Wybierz", choices=["0", "1", "2", "3", "4"], default="1")

        if choice == "0":
            return

        if choice == "4":
            sessions = self.db.list_sessions(limit=10)
            if not sessions:
                console.print("[dim]Brak sesji.[/dim]")
                return
            self._display_sessions_table(sessions)
            session_id = IntPrompt.ask("Podaj ID sesji")
            contents = self.db.get_contents_for_session(session_id)
        else:
            status_map = {"1": ContentStatus.DRAFT, "2": ContentStatus.APPROVED, "3": ContentStatus.REJECTED}
            contents = self.db.get_contents_by_status(status_map[choice])

        if not contents:
            console.print("[dim]Brak treści o tym statusie.[/dim]")
            return

        self._display_contents_table(contents)

        console.print("\n[bold]Akcje:[/bold]")
        console.print("  [cyan]1[/cyan] — Przejrzyj treści jedna po drugiej")
        console.print("  [cyan]2[/cyan] — Zmień status konkretnej treści")
        console.print("  [cyan]3[/cyan] — Zatwierdź wszystkie szkice z listy")
        console.print("  [cyan]0[/cyan] — Powrót")

        action = Prompt.ask("Wybierz", choices=["0", "1", "2", "3"], default="1")

        if action == "1":
            self._review_one_by_one(contents)
        elif action == "2":
            self._change_single_status()
        elif action == "3":
            self._approve_all(contents)

    def _review_one_by_one(self, contents: list[GeneratedContent]):
        """Przeglądaj treści jedna po drugiej z opcją zatwierdzenia."""
        for i, content in enumerate(contents, 1):
            label = PLATFORM_LABELS.get(content.platform, content.platform.value)
            status_label, _ = STATUS_STYLES.get(content.status, ("[dim]?[/dim]", "dim"))

            console.print(f"\n{'='*60}")
            console.print(f"[bold]Treść {i}/{len(contents)}[/bold] — #{content.id} | {label} | {status_label}")
            console.print(Panel(
                Markdown(content.body),
                title=content.title,
                subtitle=content.hashtags,
                border_style="cyan",
            ))
            console.print(f"[dim]Długość: {len(content.body)} znaków[/dim]")

            console.print("\n  [green]a[/green] — Zatwierdź")
            console.print("  [red]r[/red] — Odrzuć")
            console.print("  [yellow]s[/yellow] — Pomiń (zostaw obecny status)")
            console.print("  [dim]q[/dim] — Zakończ przeglądanie")

            decision = Prompt.ask("Decyzja", choices=["a", "r", "s", "q"], default="s")

            if decision == "a":
                self.db.update_content_status(content.id, ContentStatus.APPROVED)
                console.print(f"[green]#{content.id} zatwierdzony[/green]")
            elif decision == "r":
                self.db.update_content_status(content.id, ContentStatus.REJECTED)
                console.print(f"[red]#{content.id} odrzucony[/red]")
            elif decision == "q":
                console.print("[dim]Zakończono przeglądanie.[/dim]")
                break

    def _change_single_status(self):
        """Zmień status konkretnej treści po ID."""
        content_id = IntPrompt.ask("Podaj ID treści")
        content = self.db.get_content(content_id)
        if not content:
            console.print("[red]Nie znaleziono treści.[/red]")
            return

        label = PLATFORM_LABELS.get(content.platform, content.platform.value)
        status_label, _ = STATUS_STYLES.get(content.status, ("[dim]?[/dim]", "dim"))
        console.print(f"\n[bold]{content.title}[/bold] ({label}) — obecny status: {status_label}")

        console.print("\n  [cyan]1[/cyan] — Szkic")
        console.print("  [cyan]2[/cyan] — Zatwierdzony")
        console.print("  [cyan]3[/cyan] — Odrzucony")

        new = Prompt.ask("Nowy status", choices=["1", "2", "3"])
        new_status = {"1": ContentStatus.DRAFT, "2": ContentStatus.APPROVED, "3": ContentStatus.REJECTED}[new]
        self.db.update_content_status(content_id, new_status)
        new_label, _ = STATUS_STYLES[new_status]
        console.print(f"[green]Status zmieniony na: {new_label}[/green]")

    def _approve_all(self, contents: list[GeneratedContent]):
        """Zatwierdź wszystkie szkice z listy."""
        drafts = [c for c in contents if c.status == ContentStatus.DRAFT]
        if not drafts:
            console.print("[dim]Brak szkiców do zatwierdzenia.[/dim]")
            return

        console.print(f"\n[bold]Zatwierdzam {len(drafts)} szkic(ów)...[/bold]")
        if not Confirm.ask("Na pewno zatwierdzić wszystkie?", default=False):
            return

        for c in drafts:
            self.db.update_content_status(c.id, ContentStatus.APPROVED)
            console.print(f"  [green]#{c.id} — {c.title[:40]} — zatwierdzony[/green]")

        console.print(f"\n[bold green]Zatwierdzono {len(drafts)} treści.[/bold green]")

    # === Publikacja ===

    def _publish_flow(self):
        console.print(Panel("[bold]Publikacja treści przez Postiz[/bold]", border_style="yellow"))

        postiz = PostizClient(config=self.config, db=self.db)
        if not postiz.is_configured():
            console.print("[red]Postiz nie jest skonfigurowany. Sprawdź config.yaml lub zmienne środowiskowe.[/red]")
            return

        # Pokaż zatwierdzone treści gotowe do publikacji
        approved = self.db.get_approved_contents()
        if not approved:
            console.print("[yellow]Brak zatwierdzonych treści. Najpierw zatwierdź treści w menu 4.[/yellow]")
            return

        console.print("\n[bold green]Zatwierdzone treści gotowe do publikacji:[/bold green]")
        self._display_contents_table(approved)

        content_id = IntPrompt.ask("Podaj ID treści do publikacji")

        content = self.db.get_content(content_id)
        if not content:
            console.print("[red]Nie znaleziono treści.[/red]")
            return

        if content.status != ContentStatus.APPROVED:
            status_label, _ = STATUS_STYLES.get(content.status, ("[dim]?[/dim]", "dim"))
            console.print(f"[red]Treść #{content_id} ma status: {status_label} — można publikować tylko zatwierdzone treści.[/red]")
            return

        # Pokaż treść
        console.print(Panel(content.body[:500] + ("..." if len(content.body) > 500 else ""), title=content.title))

        # Pobierz integracje
        try:
            integrations = postiz.get_integrations()
        except Exception as e:
            console.print(f"[red]Nie można pobrać integracji: {e}[/red]")
            return

        if not integrations:
            console.print("[yellow]Brak integracji w Postiz.[/yellow]")
            return

        # Wybierz integrację
        console.print("\n[bold]Dostępne integracje:[/bold]")
        for i, integ in enumerate(integrations, 1):
            status = "[red]wyłączona[/red]" if integ.disabled else "[green]aktywna[/green]"
            console.print(f"  {i}. {integ.name} ({integ.provider}) — {status}")

        integ_idx = IntPrompt.ask("Wybierz integrację (numer)", default=1)
        if integ_idx < 1 or integ_idx > len(integrations):
            console.print("[red]Nieprawidłowy wybór.[/red]")
            return
        selected_integ = integrations[integ_idx - 1]

        # Typ publikacji
        console.print("\n[bold]Typ publikacji:[/bold]")
        console.print("  1 — Opublikuj teraz")
        console.print("  2 — Zaplanuj")
        console.print("  3 — Zapisz jako szkic")
        pub_choice = Prompt.ask("Wybierz", choices=["1", "2", "3"], default="1")

        publish_type = {
            "1": PublishType.NOW,
            "2": PublishType.SCHEDULE,
            "3": PublishType.DRAFT,
        }[pub_choice]

        scheduled_at = None
        if publish_type == PublishType.SCHEDULE:
            # Sugestie optymalnych godzin
            suggestions = suggest_times(content.platform)
            if suggestions:
                console.print("\n[bold]Sugerowane terminy:[/bold]")
                for i, (dt, label) in enumerate(suggestions, 1):
                    console.print(f"  {i}. {label}")

            date_str = Prompt.ask("\nPodaj datę i godzinę (np. 'jutro 10:00', '2025-01-15 14:00')")
            scheduled_at = parse_schedule_date(date_str)
            if not scheduled_at:
                console.print("[red]Nie udało się sparsować daty.[/red]")
                return
            console.print(f"[dim]Zaplanowano na: {scheduled_at.strftime('%Y-%m-%d %H:%M')}[/dim]")

        # Upload obrazu jeśli jest
        images = self.db.get_images_for_session(content.session_id)
        image_ids = []
        if images:
            console.print(f"\n[bold]Znaleziono {len(images)} obraz(y/ów) dla tej sesji.[/bold]")
            if Confirm.ask("Dołączyć obraz do posta?", default=True):
                for img in images:
                    if img.postiz_id:
                        image_ids.append(img.postiz_id)
                        console.print(f"[dim]Obraz #{img.id} już uploadowany (ID: {img.postiz_id})[/dim]")
                    else:
                        try:
                            result = postiz.upload_image(img.file_path)
                            self.db.update_image_postiz(img.id, result["id"], result["path"])
                            image_ids.append(result["id"])
                            console.print(f"[green]Uploadowano obraz #{img.id}[/green]")
                        except Exception as e:
                            console.print(f"[red]Błąd uploadu: {e}[/red]")

        # Potwierdzenie
        console.print(f"\n[bold]Podsumowanie:[/bold]")
        console.print(f"  Treść: {content.title} ({PLATFORM_LABELS.get(content.platform, content.platform.value)})")
        console.print(f"  Integracja: {selected_integ.name} ({selected_integ.provider})")
        console.print(f"  Typ: {publish_type.value}")
        if scheduled_at:
            console.print(f"  Zaplanowano: {scheduled_at.strftime('%Y-%m-%d %H:%M')}")
        if image_ids:
            console.print(f"  Obrazy: {len(image_ids)}")
        console.print(f"  Pozostałe żądania: {postiz.remaining_requests}/30")

        if not Confirm.ask("\nOpublikować?", default=True):
            console.print("[dim]Anulowano.[/dim]")
            return

        # Publikacja
        try:
            result = postiz.create_post(
                content=content.body,
                integration_ids=[selected_integ.id],
                publish_type=publish_type,
                scheduled_at=scheduled_at,
                image_ids=image_ids if image_ids else None,
                title=content.title,
            )

            record = PublishRecord(
                content_id=content.id,
                integration_id=selected_integ.id,
                integration_name=selected_integ.name,
                publish_type=publish_type,
                scheduled_at=scheduled_at,
                status="success",
                response_data=json.dumps(result, ensure_ascii=False),
            )
            self.db.save_publish(record)
            self.db.update_content_status(content.id, ContentStatus.PUBLISHED)
            console.print(f"[bold green]Opublikowano![/bold green]")
        except Exception as e:
            record = PublishRecord(
                content_id=content.id,
                integration_id=selected_integ.id,
                integration_name=selected_integ.name,
                publish_type=publish_type,
                scheduled_at=scheduled_at,
                status="error",
                response_data=str(e),
            )
            self.db.save_publish(record)
            console.print(f"[red]Błąd publikacji: {e}[/red]")

    # === Obrazy ===

    def _images_menu(self):
        console.print(Panel("[bold]Zarządzanie obrazami[/bold]", border_style="blue"))
        console.print("  [cyan]1[/cyan] — Generuj obraz DALL-E")
        console.print("  [cyan]2[/cyan] — Dołącz plik lokalny")
        console.print("  [cyan]0[/cyan] — Powrót")

        choice = Prompt.ask("Wybierz", choices=["0", "1", "2"], default="0")

        if choice == "1":
            self._dalle_generate()
        elif choice == "2":
            self._attach_local()

    def _dalle_generate(self):
        sessions = self.db.list_sessions(limit=5)
        if not sessions:
            console.print("[yellow]Brak sesji. Najpierw wygeneruj treść.[/yellow]")
            return

        self._display_sessions_table(sessions)
        session_id = IntPrompt.ask("Podaj ID sesji dla obrazu")

        session = self.db.get_session(session_id)
        if not session:
            console.print("[red]Nie znaleziono sesji.[/red]")
            return

        dalle = DalleGenerator(self.config)
        suggested = dalle.suggest_prompt(session.input_text)
        console.print(f"\n[bold]Sugerowany prompt:[/bold] {suggested}")

        prompt = Prompt.ask("Prompt DALL-E (Enter = sugerowany)", default=suggested)

        try:
            image = dalle.generate(prompt, session_id)
            image.id = self.db.save_image(image)
            console.print(f"[bold green]Obraz wygenerowany: {image.file_path}[/bold green]")
        except Exception as e:
            console.print(f"[red]Błąd generowania: {e}[/red]")

    def _attach_local(self):
        sessions = self.db.list_sessions(limit=5)
        if not sessions:
            console.print("[yellow]Brak sesji. Najpierw wygeneruj treść.[/yellow]")
            return

        self._display_sessions_table(sessions)
        session_id = IntPrompt.ask("Podaj ID sesji dla obrazu")

        file_path = Prompt.ask("Ścieżka do pliku graficznego")

        handler = LocalImageHandler()
        try:
            image = handler.attach(file_path, session_id)
            image.id = self.db.save_image(image)
            console.print(f"[bold green]Obraz dołączony: {image.file_path}[/bold green]")
        except Exception as e:
            console.print(f"[red]Błąd: {e}[/red]")

    # === Historia ===

    def _show_history(self):
        console.print(Panel("[bold]Historia sesji[/bold]", border_style="blue"))
        sessions = self.db.list_sessions(limit=20)
        if not sessions:
            console.print("[dim]Brak sesji.[/dim]")
            return

        self._display_sessions_table(sessions)

        if Confirm.ask("Wyświetlić szczegóły sesji?", default=False):
            session_id = IntPrompt.ask("Podaj ID sesji")
            contents = self.db.get_contents_for_session(session_id)
            if not contents:
                console.print("[dim]Brak treści w tej sesji.[/dim]")
                return

            self._display_contents_table(contents)

            if Confirm.ask("Wyświetlić pełną treść?", default=False):
                content_id = IntPrompt.ask("Podaj ID treści")
                content = self.db.get_content(content_id)
                if content:
                    console.print(Panel(
                        Markdown(content.body),
                        title=f"{content.title} ({PLATFORM_LABELS.get(content.platform, content.platform.value)})",
                        subtitle=content.hashtags,
                    ))

    def _show_publish_log(self):
        console.print(Panel("[bold]Log publikacji[/bold]", border_style="blue"))
        records = self.db.get_publish_log(limit=20)
        if not records:
            console.print("[dim]Brak wpisów.[/dim]")
            return

        table = Table(title="Publish Log")
        table.add_column("ID", style="dim")
        table.add_column("Content ID")
        table.add_column("Integracja")
        table.add_column("Typ")
        table.add_column("Status")
        table.add_column("Data")

        for r in records:
            status_style = "green" if r.status == "success" else "red"
            table.add_row(
                str(r.id),
                str(r.content_id),
                r.integration_name,
                r.publish_type.value,
                f"[{status_style}]{r.status}[/{status_style}]",
                r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            )
        console.print(table)

    # === Helpers ===

    def _display_sessions_table(self, sessions: list[ContentSession]):
        table = Table(title="Sesje")
        table.add_column("ID", style="dim")
        table.add_column("Mechanika")
        table.add_column("Input")
        table.add_column("Trend")
        table.add_column("Data")

        for s in sessions:
            table.add_row(
                str(s.id),
                s.mechanic.value,
                s.input_text[:40],
                s.found_trend[:30] if s.found_trend else "",
                s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
            )
        console.print(table)

    def _display_contents_table(self, contents: list[GeneratedContent]):
        table = Table(title="Wygenerowane treści")
        table.add_column("ID", style="dim")
        table.add_column("Platforma")
        table.add_column("Tytuł")
        table.add_column("Status")
        table.add_column("Długość")
        table.add_column("Hashtagi")

        for c in contents:
            status_label, _ = STATUS_STYLES.get(c.status, ("[dim]?[/dim]", "dim"))
            table.add_row(
                str(c.id),
                PLATFORM_LABELS.get(c.platform, c.platform.value),
                c.title[:40],
                status_label,
                str(len(c.body)),
                c.hashtags[:30],
            )
        console.print(table)

    def _read_multiline(self, label: str) -> str:
        """Czytaj wieloliniowy input (pusta linia kończy)."""
        console.print(f"[dim]({label} — pusta linia kończy wprowadzanie)[/dim]")
        lines = []
        empty_count = 0
        while True:
            try:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                    lines.append("")
                else:
                    empty_count = 0
                    lines.append(line)
            except EOFError:
                break
        return "\n".join(lines).strip()
