from dataclasses import dataclass
from pathlib import Path

from bot.config import env


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    bot_profile: str
    guild_id: int
    verify_channel_id: int
    log_channel_id: int | None
    support_channel_id: int | None
    verified_role_id: int | None
    unverified_role_id: int | None
    member_role_id: int | None
    commodore_role_id: int | None
    admiral_role_id: int | None
    admin_role_id: int | None
    ops71_plus_role_id: int | None
    minimum_ops_level: int | None
    stfc_server_number: int | None
    update_check_hours: int
    debug: bool
    default_language: str
    session_ttl_hours: int
    database_url: str | None
    sqlite_path: str | None
    require_screenshot: bool

    @property
    def database_path(self) -> Path:
        if self.sqlite_path:
            return Path(self.sqlite_path)
        if self.database_url and self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.removeprefix("sqlite:///"))
        data_dir = Path("data")
        return data_dir / f"{self.bot_profile}_{self.guild_id}.sqlite3"

    @classmethod
    def from_env(cls) -> "Settings":
        settings = cls(
            discord_token=env.required("DISCORD_TOKEN"),
            bot_profile=env.required("BOT_PROFILE"),
            guild_id=int(env.required("GUILD_ID")),
            verify_channel_id=int(env.required("VERIFY_CHANNEL_ID")),
            log_channel_id=env.optional_int("LOG_CHANNEL_ID"),
            support_channel_id=env.optional_int("SUPPORT_CHANNEL_ID"),
            verified_role_id=env.optional_int("VERIFIED_ROLE_ID"),
            unverified_role_id=env.optional_int("UNVERIFIED_ROLE_ID"),
            member_role_id=env.optional_int("MEMBER_ROLE_ID"),
            commodore_role_id=env.optional_int("COMMODORE_ROLE_ID"),
            admiral_role_id=env.optional_int("ADMIRAL_ROLE_ID"),
            admin_role_id=env.optional_int("ADMIN_ROLE_ID"),
            ops71_plus_role_id=env.optional_int("OPS71_PLUS_ROLE_ID"),
            minimum_ops_level=env.optional_int("MINIMUM_OPS_LEVEL"),
            stfc_server_number=env.optional_int("STFC_SERVER_NUMBER"),
            update_check_hours=int(env.optional("UPDATE_CHECK_HOURS") or "24"),
            debug=bool(int(env.optional("DEBUG") or "0")),
            default_language=env.optional("DEFAULT_LANGUAGE") or "en",
            session_ttl_hours=int(env.optional("SESSION_TTL_HOURS") or "168"),
            database_url=env.optional("DATABASE_URL"),
            sqlite_path=env.optional("SQLITE_PATH"),
            require_screenshot=env.optional("REQUIRE_SCREENSHOT", default="true").lower() not in ("false", "0", "no"),
        )
        settings._validate_profile_requirements()
        return settings

    def _validate_profile_requirements(self) -> None:
        profile_requirements = {
            "stfc_verifier": ["STFC_SERVER_NUMBER"],
            "stfc_verifier_alliance": ["STFC_SERVER_NUMBER"],
            "veil_security": ["MINIMUM_OPS_LEVEL", "OPS71_PLUS_ROLE_ID"],
        }

        required = profile_requirements.get(self.bot_profile, [])
        missing: list[str] = []

        for req in required:
            var_name = req.split(" ")[0]
            if var_name.startswith("STFC_SERVER"):
                if self.stfc_server_number is None:
                    missing.append(req)
            elif var_name.startswith("MINIMUM_OPS"):
                if self.minimum_ops_level is None:
                    missing.append(req)
            elif var_name.startswith("OPS71"):
                if self.ops71_plus_role_id is None:
                    missing.append(req)

        if missing:
            names = ", ".join(missing)
            raise ValueError(
                f"{self.bot_profile} requires profile environment variables: {names}"
            )
