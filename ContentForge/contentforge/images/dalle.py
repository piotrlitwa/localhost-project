"""Generowanie obrazów przez DALL-E (OpenAI API via requests)."""

import base64
import json
import uuid
from datetime import datetime
from pathlib import Path

import requests

from ..config import IMAGES_DIR, load_config
from ..models import ImageRecord, ImageSource


class DalleGenerator:
    """Klient DALL-E do generowania obrazów."""

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        self.api_key = cfg["openai"]["api_key"]
        self.model = cfg["dalle"]["model"]
        self.size = cfg["dalle"]["size"]
        self.api_url = "https://api.openai.com/v1/images/generations"

    def generate(self, prompt: str, session_id: int) -> ImageRecord:
        """Wygeneruj obraz z DALL-E i zapisz lokalnie."""
        if not self.api_key:
            raise ValueError("Brak klucza API OpenAI. Ustaw OPENAI_API_KEY lub skonfiguruj config.yaml.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": self.size,
            "response_format": "b64_json",
        }

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        image_b64 = data["data"][0]["b64_json"]
        image_bytes = base64.b64decode(image_b64)

        # Zapisz do pliku
        filename = f"dalle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
        file_path = IMAGES_DIR / filename
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(image_bytes)

        return ImageRecord(
            session_id=session_id,
            source=ImageSource.DALLE,
            file_path=str(file_path),
            dalle_prompt=prompt,
        )

    def suggest_prompt(self, brief: str) -> str:
        """Zasugeruj prompt DALL-E na podstawie briefu treści."""
        return (
            f"Professional, modern illustration for a social media post about: {brief[:200]}. "
            f"Clean design, vibrant colors, no text in image."
        )
