CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS wizard_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    profile TEXT NOT NULL,
    language TEXT NOT NULL,
    current_step TEXT NOT NULL,
    answers_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    expires_at TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS persistent_views (
    message_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    custom_id TEXT NOT NULL,
    view_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (message_id, custom_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    profile TEXT NOT NULL,
    user_id INTEGER,
    guild_id INTEGER,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
