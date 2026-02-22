"""Klient Postiz oparty na MCP protocol — integracje, obrazy, tworzenie postów."""

import json
import re
from datetime import datetime, timezone
from typing import Optional

import requests

from ..config import load_config
from ..database import Database
from ..models import Integration, PublishType
from ..utils.rate_limiter import RateLimiter

_rate_limiter = RateLimiter(max_requests=30, window_seconds=3600)


def _markdown_to_html(text: str) -> str:
    """Konwertuj markdown/plain text na HTML wymagany przez Postiz.

    Postiz wymaga HTML z tagami: p, h1, h2, h3, strong, u, li, ul.
    """
    lines = text.split("\n")
    html_parts = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Pusta linia
        if not stripped:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        # Nagłówki
        if stripped.startswith("### "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h3>{_inline_format(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h2>{_inline_format(stripped[3:])}</h2>")
            continue
        if stripped.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h1>{_inline_format(stripped[2:])}</h1>")
            continue

        # Lista
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{_inline_format(stripped[2:])}</li>")
            continue

        # Zwykły akapit
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        html_parts.append(f"<p>{_inline_format(stripped)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "".join(html_parts)


def _inline_format(text: str) -> str:
    """Zamień **bold** na <strong> i __underline__ na <u>."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<u>\1</u>", text)
    return text


class PostizMCPClient:
    """Klient Postiz przez MCP (Model Context Protocol)."""

    def __init__(self, config: dict | None = None, db: Database | None = None):
        cfg = config or load_config()
        self.mcp_url = cfg["postiz"]["mcp_url"]
        self.api_key = cfg["postiz"]["api_key"]
        self.db = db or Database()
        self.rate_limiter = _rate_limiter
        self._session_id: Optional[str] = None

    def _ensure_session(self):
        """Zainicjalizuj sesję MCP jeśli nie istnieje."""
        if self._session_id:
            return

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        # Initialize
        r = requests.post(
            self.mcp_url,
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": 1,
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "ContentForge", "version": "1.0.0"},
                },
            },
            headers=headers,
            timeout=15,
        )
        r.raise_for_status()
        self._session_id = r.headers.get("mcp-session-id", "")

        # Notifications/initialized
        requests.post(
            self.mcp_url,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers={**headers, "Mcp-Session-Id": self._session_id},
            timeout=15,
        )

    def _call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Wywołaj narzędzie MCP i zwróć wynik."""
        self._ensure_session()
        self.rate_limiter.wait_if_needed()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self._session_id,
        }

        r = requests.post(
            self.mcp_url,
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 2,
                "params": {"name": tool_name, "arguments": arguments},
            },
            headers=headers,
            timeout=60,
        )
        self.rate_limiter.record_request()
        r.raise_for_status()

        # Parsuj SSE response
        for line in r.text.split("\n"):
            if line.startswith("data: "):
                data = json.loads(line[6:])
                result = data.get("result", {})

                if result.get("isError"):
                    error_text = ""
                    for content in result.get("content", []):
                        if content.get("type") == "text":
                            error_text += content["text"]
                    raise RuntimeError(f"Postiz MCP error: {error_text}")

                # Zwróć structured content lub text
                if "structuredContent" in result:
                    return result["structuredContent"]

                for content in result.get("content", []):
                    if content.get("type") == "text":
                        try:
                            return json.loads(content["text"])
                        except (json.JSONDecodeError, TypeError):
                            return {"text": content["text"]}

                return result

        raise RuntimeError("Brak odpowiedzi z Postiz MCP")

    # --- Integracje ---

    def get_integrations(self, force_refresh: bool = False) -> list[Integration]:
        """Pobierz integracje z cache lub MCP."""
        if not force_refresh:
            cached, cached_at = self.db.get_cached_integrations()
            if cached and cached_at:
                age = (datetime.now() - cached_at).total_seconds()
                if age < 3600:
                    return cached

        result = self._call_tool("integrationList", {})

        integrations = []
        items = result.get("output", result) if isinstance(result, dict) else result
        if isinstance(items, list):
            for item in items:
                integ = Integration(
                    id=str(item.get("id", "")),
                    name=item.get("name", ""),
                    provider=item.get("providerIdentifier", item.get("provider", "")),
                    picture=item.get("picture", ""),
                    disabled=item.get("disabled", False),
                )
                integrations.append(integ)

        self.db.cache_integrations(integrations)
        return integrations

    def get_integration_schema(self, platform: str, is_premium: bool = False) -> dict:
        """Pobierz schemat integracji (wymagane settings) dla platformy."""
        return self._call_tool("integrationSchema", {
            "isPremium": is_premium,
            "platform": platform,
        })

    def trigger_tool(self, integration_id: str, method_name: str, data: list[dict] | None = None) -> dict:
        """Wywołaj trigger tool dla integracji (np. pobranie dodatkowych danych)."""
        return self._call_tool("triggerTool", {
            "integrationId": integration_id,
            "methodName": method_name,
            "dataSchema": data or [],
        })

    # --- Tworzenie postów ---

    def create_post(
        self,
        content: str,
        integration_id: str,
        publish_type: PublishType = PublishType.NOW,
        scheduled_at: Optional[datetime] = None,
        image_urls: Optional[list[str]] = None,
        settings: Optional[list[dict]] = None,
        is_premium: bool = False,
    ) -> dict:
        """Utwórz post przez MCP integrationSchedulePostTool."""
        # Konwertuj treść na HTML
        html_content = _markdown_to_html(content)

        # Data w UTC
        if publish_type == PublishType.SCHEDULE and scheduled_at:
            post_date = scheduled_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            post_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        post_payload = {
            "integrationId": integration_id,
            "isPremium": is_premium,
            "date": post_date,
            "shortLink": False,
            "type": publish_type.value,
            "postsAndComments": [
                {
                    "content": html_content,
                    "attachments": image_urls or [],
                }
            ],
            "settings": settings or [],
        }

        return self._call_tool("integrationSchedulePostTool", {
            "socialPost": [post_payload],
        })

    # --- Obrazy ---

    def generate_image(self, prompt: str) -> dict:
        """Wygeneruj obraz przez Postiz (wbudowane AI)."""
        return self._call_tool("generateImageTool", {"prompt": prompt})

    @property
    def remaining_requests(self) -> int:
        return self.rate_limiter.remaining

    def is_configured(self) -> bool:
        return bool(self.mcp_url and self.api_key)
