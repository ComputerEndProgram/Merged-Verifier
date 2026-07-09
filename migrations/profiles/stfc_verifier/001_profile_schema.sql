CREATE TABLE IF NOT EXISTS stfc_verifier_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    player_id TEXT NOT NULL,
    verified_at TEXT NOT NULL
);
