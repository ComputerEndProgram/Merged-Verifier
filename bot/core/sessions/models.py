from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class WizardSession:
    session_id: str
    user_id: int
    guild_id: int
    profile: str
    language: str
    current_step: str
    answers: dict[str, str] = field(default_factory=dict)
    status: str = "active"
    expires_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class PersistentViewRecord:
    message_id: int
    channel_id: int
    custom_id: str
    view_type: str
    payload: dict[str, str] = field(default_factory=dict)

