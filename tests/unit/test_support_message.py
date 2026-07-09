from bot.config.settings import Settings
from bot.core.i18n.translator import Translator
from bot.core.verification.finalizer import build_support_message


def _settings(support_channel_id: int | None) -> Settings:
    return Settings(
        discord_token="token",
        bot_profile="stfc_verifier",
        guild_id=1,
        verify_channel_id=2,
        log_channel_id=3,
        support_channel_id=support_channel_id,
        verified_role_id=None,
        unverified_role_id=None,
        member_role_id=None,
        commodore_role_id=None,
        admiral_role_id=None,
        admin_role_id=None,
        ops71_plus_role_id=None,
        minimum_ops_level=71,
        stfc_server_number=106,
        update_check_hours=24,
        debug=False,
        default_language="en",
        session_ttl_hours=1,
        database_url=None,
        sqlite_path=None,
        require_screenshot=True,
    )


def test_support_message_uses_channel_mention_when_configured() -> None:
    translator = Translator(default_language="en")
    message = build_support_message(translator, "en", _settings(150))
    assert message == "Open a support ticket in <#150>."


def test_support_message_falls_back_when_channel_not_configured() -> None:
    translator = Translator(default_language="en")
    message = build_support_message(translator, "en", _settings(None))
    assert "support process configured by your admins" in message
