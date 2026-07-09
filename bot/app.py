from dataclasses import dataclass

from bot.bootstrap import restore_runtime_state
from bot.config.profiles import get_profile
from bot.config.settings import Settings
from bot.core.i18n.translator import Translator
from bot.core.sessions.store import SessionStore


@dataclass(slots=True)
class Application:
    settings: Settings
    translator: Translator
    session_store: SessionStore
    profile_name: str

    def run(self) -> None:
        restore_runtime_state(self.session_store)


def build_app() -> Application:
    settings = Settings.from_env()
    translator = Translator(default_language="en")
    session_store = SessionStore(settings.database_path)
    get_profile(settings.bot_profile)  # Validate profile value on boot.
    return Application(
        settings=settings,
        translator=translator,
        session_store=session_store,
        profile_name=settings.bot_profile,
    )

