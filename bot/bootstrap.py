from bot.core.sessions.restore import restore_persistent_views, restore_sessions
from bot.core.sessions.store import SessionStore


def restore_runtime_state(session_store: SessionStore) -> None:
    restore_sessions(session_store)
    restore_persistent_views(session_store)

