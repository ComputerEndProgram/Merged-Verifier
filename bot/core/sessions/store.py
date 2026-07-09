import json
from datetime import UTC, datetime
from pathlib import Path

from bot.core.persistence.db import connect_sqlite
from bot.core.sessions.models import PersistentViewRecord, WizardSession


class SessionStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._init_schema()

    def _init_schema(self) -> None:
        with connect_sqlite(self.database_path) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS wizard_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    profile TEXT NOT NULL,
                    language TEXT NOT NULL,
                    current_step TEXT NOT NULL,
                    answers_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    expires_at TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS persistent_views (
                    message_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    custom_id TEXT NOT NULL,
                    view_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (message_id, custom_id)
                );
                """
            )

    def save_session(self, session: WizardSession) -> None:
        now = datetime.now(UTC).isoformat()
        expires_at = session.expires_at.isoformat() if session.expires_at else None
        answers_json = json.dumps(session.answers, sort_keys=True)
        with connect_sqlite(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO wizard_sessions (
                    session_id, user_id, guild_id, profile, language, current_step,
                    answers_json, status, expires_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    language=excluded.language,
                    current_step=excluded.current_step,
                    answers_json=excluded.answers_json,
                    status=excluded.status,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at
                """,
                (
                    session.session_id,
                    session.user_id,
                    session.guild_id,
                    session.profile,
                    session.language,
                    session.current_step,
                    answers_json,
                    session.status,
                    expires_at,
                    now,
                ),
            )

    def get_session(self, session_id: str) -> WizardSession | None:
        with connect_sqlite(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT session_id, user_id, guild_id, profile, language, current_step,
                       answers_json, status, expires_at, updated_at
                FROM wizard_sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        return self._row_to_session(row) if row else None

    def load_active_sessions(self) -> list[WizardSession]:
        now = datetime.now(UTC).isoformat()
        with connect_sqlite(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT session_id, user_id, guild_id, profile, language, current_step,
                       answers_json, status, expires_at, updated_at
                FROM wizard_sessions
                WHERE status = 'active'
                  AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY updated_at DESC
                """,
                (now,),
            ).fetchall()
        return [self._row_to_session(row) for row in rows]

    def save_persistent_view(self, view: PersistentViewRecord) -> None:
        now = datetime.now(UTC).isoformat()
        payload_json = json.dumps(view.payload, sort_keys=True)
        with connect_sqlite(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO persistent_views (
                    message_id, channel_id, custom_id, view_type, payload_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id, custom_id) DO UPDATE SET
                    channel_id=excluded.channel_id,
                    view_type=excluded.view_type,
                    payload_json=excluded.payload_json,
                    updated_at=excluded.updated_at
                """,
                (
                    view.message_id,
                    view.channel_id,
                    view.custom_id,
                    view.view_type,
                    payload_json,
                    now,
                ),
            )

    def load_persistent_views(self) -> list[PersistentViewRecord]:
        with connect_sqlite(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT message_id, channel_id, custom_id, view_type, payload_json
                FROM persistent_views
                ORDER BY updated_at DESC
                """
            ).fetchall()
        return [
            PersistentViewRecord(
                message_id=int(row["message_id"]),
                channel_id=int(row["channel_id"]),
                custom_id=str(row["custom_id"]),
                view_type=str(row["view_type"]),
                payload=json.loads(str(row["payload_json"])),
            )
            for row in rows
        ]

    def _row_to_session(self, row: object) -> WizardSession:
        answers = json.loads(str(row["answers_json"]))
        expires_at = datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
        updated_at = datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None
        return WizardSession(
            session_id=str(row["session_id"]),
            user_id=int(row["user_id"]),
            guild_id=int(row["guild_id"]),
            profile=str(row["profile"]),
            language=str(row["language"]),
            current_step=str(row["current_step"]),
            answers=answers,
            status=str(row["status"]),
            expires_at=expires_at,
            updated_at=updated_at,
        )

