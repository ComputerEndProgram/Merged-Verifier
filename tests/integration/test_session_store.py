from datetime import UTC, datetime, timedelta

from bot.core.sessions.models import PersistentViewRecord, WizardSession
from bot.core.sessions.store import SessionStore


def test_session_store_round_trip(tmp_path) -> None:
    database_path = tmp_path / "test.sqlite3"
    store = SessionStore(database_path)

    session = WizardSession(
        session_id="session-1",
        user_id=10,
        guild_id=20,
        profile="stfc_verifier",
        language="en",
        current_step="start",
        answers={"player_id": "abc"},
        expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
    store.save_session(session)

    loaded = store.get_session("session-1")
    assert loaded is not None
    assert loaded.language == "en"
    assert loaded.current_step == "start"
    assert loaded.answers["player_id"] == "abc"

    views = PersistentViewRecord(
        message_id=111,
        channel_id=222,
        custom_id="verify:next",
        view_type="verify_wizard",
        payload={"step": "start"},
    )
    store.save_persistent_view(views)
    loaded_views = store.load_persistent_views()
    assert len(loaded_views) == 1
    assert loaded_views[0].custom_id == "verify:next"

