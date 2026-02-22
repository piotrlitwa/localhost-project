"""Dołączanie lokalnych plików graficznych."""

import shutil
import uuid
from datetime import datetime
from pathlib import Path

from ..config import IMAGES_DIR
from ..models import ImageRecord, ImageSource

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


class LocalImageHandler:
    """Obsługa lokalnych plików graficznych."""

    def attach(self, source_path: str, session_id: int) -> ImageRecord:
        """Zwaliduj i skopiuj lokalny plik graficzny do data/images/."""
        src = Path(source_path).resolve()

        if not src.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {src}")

        if src.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Nieobsługiwany format: {src.suffix}. "
                f"Dozwolone: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        file_size = src.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"Plik za duży: {file_size / 1024 / 1024:.1f} MB. "
                f"Maksymalny rozmiar: {MAX_FILE_SIZE / 1024 / 1024:.0f} MB."
            )

        # Kopiuj do data/images/
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{src.suffix.lower()}"
        dest = IMAGES_DIR / filename
        shutil.copy2(src, dest)

        return ImageRecord(
            session_id=session_id,
            source=ImageSource.LOCAL,
            file_path=str(dest),
        )
