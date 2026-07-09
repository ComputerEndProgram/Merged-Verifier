from bot.core.sessions.models import PersistentViewRecord, WizardSession
from bot.core.sessions.store import SessionStore


def restore_sessions(session_store: SessionStore) -> list[WizardSession]:
    return session_store.load_active_sessions()


def restore_persistent_views(session_store: SessionStore) -> list[PersistentViewRecord]:
    return session_store.load_persistent_views()

