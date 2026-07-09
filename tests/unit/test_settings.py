import os

from bot.config.settings import Settings


def _clear_env() -> None:
    keys = [
        "DISCORD_TOKEN",
        "BOT_PROFILE",
        "GUILD_ID",
        "VERIFY_CHANNEL_ID",
        "MINIMUM_OPS_LEVEL",
        "STFC_SERVER_NUMBER",
        "DATABASE_URL",
        "SQLITE_PATH",
        "ADMIN_ROLE_ID",
        "OPS71_PLUS_ROLE_ID",
        "MEMBER_ROLE_ID",
        "COMMODORE_ROLE_ID",
        "ADMIRAL_ROLE_ID",
        "UPDATE_CHECK_HOURS",
        "DEBUG",
        "VERIFIED_ROLE_ID",
        "LOG_CHANNEL_ID",
        "SUPPORT_CHANNEL_ID",
    ]
    for key in keys:
        os.environ.pop(key, None)


def test_settings_build_default_database_path() -> None:
    _clear_env()
    os.environ["DISCORD_TOKEN"] = "token"
    os.environ["BOT_PROFILE"] = "stfc_verifier"
    os.environ["GUILD_ID"] = "42"
    os.environ["VERIFY_CHANNEL_ID"] = "100"
    os.environ["MINIMUM_OPS_LEVEL"] = "71"
    os.environ["STFC_SERVER_NUMBER"] = "106"

    settings = Settings.from_env()

    assert settings.database_path.as_posix().endswith("data/stfc_verifier_42.sqlite3")


def test_settings_reads_profile_specific_values() -> None:
    _clear_env()
    os.environ["DISCORD_TOKEN"] = "token"
    os.environ["BOT_PROFILE"] = "stfc_verifier"
    os.environ["GUILD_ID"] = "42"
    os.environ["VERIFY_CHANNEL_ID"] = "100"
    os.environ["ADMIN_ROLE_ID"] = "200"
    os.environ["OPS71_PLUS_ROLE_ID"] = "201"
    os.environ["MINIMUM_OPS_LEVEL"] = "71"
    os.environ["STFC_SERVER_NUMBER"] = "106"
    os.environ["EXTRA_ROLE_IDS"] = "300,301"
    os.environ["MEMBER_ROLE_ID"] = "210"
    os.environ["COMMODORE_ROLE_ID"] = "211"
    os.environ["ADMIRAL_ROLE_ID"] = "212"
    os.environ["UPDATE_CHECK_HOURS"] = "12"
    os.environ["DEBUG"] = "1"

    settings = Settings.from_env()

    assert settings.member_role_id == 210
    assert settings.commodore_role_id == 211
    assert settings.admiral_role_id == 212
    assert settings.admin_role_id == 200
    assert settings.ops71_plus_role_id == 201
    assert settings.minimum_ops_level == 71
    assert settings.update_check_hours == 12
    assert settings.debug is True


def test_settings_uses_canonical_env_names() -> None:
    _clear_env()
    os.environ["DISCORD_TOKEN"] = "token"
    os.environ["BOT_PROFILE"] = "stfc_verifier"
    os.environ["GUILD_ID"] = "42"
    os.environ["VERIFY_CHANNEL_ID"] = "100"
    os.environ["VERIFIED_ROLE_ID"] = "555"
    os.environ["OPS71_PLUS_ROLE_ID"] = "201"
    os.environ["MINIMUM_OPS_LEVEL"] = "71"
    os.environ["STFC_SERVER_NUMBER"] = "106"
    os.environ["SQLITE_PATH"] = "stfc_players.db"

    settings = Settings.from_env()

    assert settings.verified_role_id == 555
    assert settings.ops71_plus_role_id == 201
    assert settings.minimum_ops_level == 71
    assert settings.stfc_server_number == 106
    assert settings.database_path.as_posix().endswith("stfc_players.db")
