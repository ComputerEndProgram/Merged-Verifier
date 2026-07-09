from bot.config.settings import Settings
from bot.core.i18n.translator import Translator


def build_support_message(
    translator: Translator,
    language: str,
    settings: Settings,
) -> str:
    support_channel_mention = (
        f"<#{settings.support_channel_id}>" if settings.support_channel_id else None
    )

    if support_channel_mention:
        return translator.t(
            language,
            "verification.support_ticket",
            support_channel_mention=support_channel_mention,
        )
    return translator.t(language, "verification.support_ticket_fallback")

