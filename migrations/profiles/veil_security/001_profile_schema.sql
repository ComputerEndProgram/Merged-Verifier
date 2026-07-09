CREATE TABLE IF NOT EXISTS veil_security_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    clearance_code TEXT NOT NULL,
    verified_at TEXT NOT NULL
);
