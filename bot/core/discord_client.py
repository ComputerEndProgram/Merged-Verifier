from dataclasses import dataclass


@dataclass(slots=True)
class DiscordRuntimeContext:
    guild_id: int
    verify_channel_id: int
    log_channel_id: int | None
    support_channel_id: int | None

