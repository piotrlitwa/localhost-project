"""Klient API Postiz — integracje, upload obrazów, tworzenie postów."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from ..config import load_config
from ..database import Database
from ..models import Integration, PublishType
from ..utils.rate_limiter import RateLimiter

# Globalny rate limiter współdzielony przez wszystkie operacje Postiz
_rate_limiter = RateLimiter(max_requests=30, window_seconds=3600)


class PostizClient:
    """Klient REST API Postiz (self-hosted)."""

    def __init__(self, config: dict | None = None, db: Database | None = None):
        cfg = config or load_config()
        self.base_url = cfg["postiz"]["base_url"].rstrip("/")
        self.api_key = cfg["postiz"]["api_key"]
        self.db = db or Database()
        self.rate_limiter = _rate_limiter

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Wykonaj żądanie z rate limitingiem."""
        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", self._headers())

        response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        self.rate_limiter.record_request()
        response.raise_for_status()
        return response

    # --- Integracje ---

    def get_integrations(self, force_refresh: bool = False) -> list[Integration]:
        """Pobierz integracje z cache lub API.

        Cache jest ważny przez 1 godzinę.
        """
        if not force_refresh:
            cached, cached_at = self.db.get_cached_integrations()
            if cached and cached_at:
                age = (datetime.now() - cached_at).total_seconds()
                if age < 3600:  # 1 godzina
                    return cached

        response = self._request("GET", "/integrations")
        data = response.json()

        integrations = []
        for item in data:
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

    # --- Upload obrazów ---

    def upload_image(self, file_path: str) -> dict:
        """Upload obrazu do Postiz. Zwraca dict z id i path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}/upload"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        with open(path, "rb") as f:
            files = {"file": (path.name, f, "image/png")}
            response = requests.post(url, headers=headers, files=files, timeout=60)

        self.rate_limiter.record_request()
        response.raise_for_status()

        result = response.json()
        return {
            "id": result.get("id", ""),
            "path": result.get("path", result.get("url", "")),
        }

    # --- Tworzenie postów ---

    def create_post(
        self,
        content: str,
        integration_ids: list[str],
        publish_type: PublishType = PublishType.NOW,
        scheduled_at: Optional[datetime] = None,
        image_ids: Optional[list[str]] = None,
        title: str = "",
    ) -> dict:
        """Utwórz post w Postiz."""
        payload = {
            "content": content,
            "integration": integration_ids,
            "type": publish_type.value,
        }

        if title:
            payload["title"] = title

        if image_ids:
            payload["image"] = image_ids

        if publish_type == PublishType.SCHEDULE and scheduled_at:
            payload["publishDate"] = scheduled_at.isoformat()

        response = self._request("POST", "/posts", json=payload)
        return response.json()

    @property
    def remaining_requests(self) -> int:
        return self.rate_limiter.remaining

    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)
