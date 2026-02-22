"""SQLite: schemat, migracje i operacje CRUD."""

import sqlite3
from datetime import datetime
from typing import Optional

from .config import DB_PATH, ensure_dirs
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
    ImageSource,
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS content_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mechanic TEXT NOT NULL,
    input_text TEXT NOT NULL,
    found_trend TEXT DEFAULT '',
    language TEXT DEFAULT 'pl',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    title TEXT DEFAULT '',
    body TEXT NOT NULL,
    hashtags TEXT DEFAULT '',
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES content_sessions(id)
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    file_path TEXT DEFAULT '',
    dalle_prompt TEXT DEFAULT '',
    postiz_id TEXT DEFAULT '',
    postiz_path TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES content_sessions(id)
);

CREATE TABLE IF NOT EXISTS publish_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    integration_id TEXT NOT NULL,
    integration_name TEXT DEFAULT '',
    publish_type TEXT NOT NULL,
    scheduled_at TIMESTAMP,
    status TEXT DEFAULT '',
    response_data TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES generated_content(id)
);

CREATE TABLE IF NOT EXISTS integrations_cache (
    id TEXT PRIMARY KEY,
    name TEXT DEFAULT '',
    provider TEXT DEFAULT '',
    picture TEXT DEFAULT '',
    disabled INTEGER DEFAULT 0,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Database:
    def __init__(self, db_path: Optional[str] = None):
        ensure_dirs()
        self.db_path = db_path or str(DB_PATH)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)
            self._migrate(conn)

    def _migrate(self, conn: sqlite3.Connection):
        """Migracje dla istniejących baz danych."""
        # Dodaj kolumnę status do generated_content jeśli nie istnieje
        columns = [row[1] for row in conn.execute("PRAGMA table_info(generated_content)").fetchall()]
        if "status" not in columns:
            conn.execute("ALTER TABLE generated_content ADD COLUMN status TEXT DEFAULT 'draft'")

    # --- Content Sessions ---

    def create_session(self, session: ContentSession) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO content_sessions (mechanic, input_text, found_trend, language) VALUES (?, ?, ?, ?)",
                (session.mechanic.value, session.input_text, session.found_trend, session.language),
            )
            return cursor.lastrowid

    def get_session(self, session_id: int) -> Optional[ContentSession]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM content_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return None
            return ContentSession(
                id=row["id"],
                mechanic=Mechanic(row["mechanic"]),
                input_text=row["input_text"],
                found_trend=row["found_trend"],
                language=row["language"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            )

    def list_sessions(self, limit: int = 20) -> list[ContentSession]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM content_sessions ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [
                ContentSession(
                    id=r["id"],
                    mechanic=Mechanic(r["mechanic"]),
                    input_text=r["input_text"],
                    found_trend=r["found_trend"],
                    language=r["language"],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
                )
                for r in rows
            ]

    # --- Generated Content ---

    def save_content(self, content: GeneratedContent) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO generated_content (session_id, platform, title, body, hashtags, status) VALUES (?, ?, ?, ?, ?, ?)",
                (content.session_id, content.platform.value, content.title, content.body, content.hashtags, content.status.value),
            )
            return cursor.lastrowid

    def _row_to_content(self, r) -> GeneratedContent:
        return GeneratedContent(
            id=r["id"],
            session_id=r["session_id"],
            platform=Platform(r["platform"]),
            title=r["title"],
            body=r["body"],
            hashtags=r["hashtags"],
            status=ContentStatus(r["status"]) if r["status"] else ContentStatus.DRAFT,
            created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
        )

    def get_contents_for_session(self, session_id: int) -> list[GeneratedContent]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM generated_content WHERE session_id = ? ORDER BY platform", (session_id,)
            ).fetchall()
            return [self._row_to_content(r) for r in rows]

    def get_content(self, content_id: int) -> Optional[GeneratedContent]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM generated_content WHERE id = ?", (content_id,)).fetchone()
            if not row:
                return None
            return self._row_to_content(row)

    def update_content_status(self, content_id: int, status: ContentStatus):
        with self._connect() as conn:
            conn.execute(
                "UPDATE generated_content SET status = ? WHERE id = ?",
                (status.value, content_id),
            )

    def get_contents_by_status(self, status: ContentStatus, limit: int = 50) -> list[GeneratedContent]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM generated_content WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status.value, limit),
            ).fetchall()
            return [self._row_to_content(r) for r in rows]

    def get_approved_contents(self, limit: int = 50) -> list[GeneratedContent]:
        return self.get_contents_by_status(ContentStatus.APPROVED, limit)

    # --- Images ---

    def save_image(self, image: ImageRecord) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO images (session_id, source, file_path, dalle_prompt, postiz_id, postiz_path) VALUES (?, ?, ?, ?, ?, ?)",
                (image.session_id, image.source.value, image.file_path, image.dalle_prompt, image.postiz_id, image.postiz_path),
            )
            return cursor.lastrowid

    def get_images_for_session(self, session_id: int) -> list[ImageRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM images WHERE session_id = ?", (session_id,)).fetchall()
            return [
                ImageRecord(
                    id=r["id"],
                    session_id=r["session_id"],
                    source=ImageSource(r["source"]),
                    file_path=r["file_path"],
                    dalle_prompt=r["dalle_prompt"],
                    postiz_id=r["postiz_id"],
                    postiz_path=r["postiz_path"],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
                )
                for r in rows
            ]

    def update_image_postiz(self, image_id: int, postiz_id: str, postiz_path: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE images SET postiz_id = ?, postiz_path = ? WHERE id = ?",
                (postiz_id, postiz_path, image_id),
            )

    # --- Publish Log ---

    def save_publish(self, record: PublishRecord) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO publish_log (content_id, integration_id, integration_name, publish_type, scheduled_at, status, response_data) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record.content_id,
                    record.integration_id,
                    record.integration_name,
                    record.publish_type.value,
                    record.scheduled_at.isoformat() if record.scheduled_at else None,
                    record.status,
                    record.response_data,
                ),
            )
            return cursor.lastrowid

    def get_publish_log(self, limit: int = 20) -> list[PublishRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM publish_log ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [
                PublishRecord(
                    id=r["id"],
                    content_id=r["content_id"],
                    integration_id=r["integration_id"],
                    integration_name=r["integration_name"],
                    publish_type=PublishType(r["publish_type"]),
                    scheduled_at=datetime.fromisoformat(r["scheduled_at"]) if r["scheduled_at"] else None,
                    status=r["status"],
                    response_data=r["response_data"],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
                )
                for r in rows
            ]

    # --- Integrations Cache ---

    def cache_integrations(self, integrations: list[Integration]):
        with self._connect() as conn:
            conn.execute("DELETE FROM integrations_cache")
            for integ in integrations:
                conn.execute(
                    "INSERT INTO integrations_cache (id, name, provider, picture, disabled, cached_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (integ.id, integ.name, integ.provider, integ.picture, int(integ.disabled), datetime.now().isoformat()),
                )

    def get_cached_integrations(self) -> tuple[list[Integration], Optional[datetime]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM integrations_cache").fetchall()
            if not rows:
                return [], None
            integrations = [
                Integration(
                    id=r["id"],
                    name=r["name"],
                    provider=r["provider"],
                    picture=r["picture"],
                    disabled=bool(r["disabled"]),
                    cached_at=datetime.fromisoformat(r["cached_at"]) if r["cached_at"] else None,
                )
                for r in rows
            ]
            cached_at = integrations[0].cached_at if integrations else None
            return integrations, cached_at
