# Merged architecture

## Core modules

- `bot/core/`: shared runtime logic
- `bot/profiles/`: profile-specific verification criteria and behavior
- `bot/i18n/`: language JSON files (`en`, `de`, `fr`)
- `bot/config/`: env + settings + profile registry
- `migrations/`: shared and profile-specific SQL migrations
- `scripts/`: legacy import entrypoints from old repos
- `tests/`: unit/integration/migration tests

## Runtime profile selection

`BOT_PROFILE` selects behavior at startup via `bot/launcher.py`, which dispatches to:
- `bot/legacy_profiles/stfc_verifier/`
- `bot/legacy_profiles/stfc_verifier_alliance/`
- `bot/legacy_profiles/veil_security/`

## Config and dynamic mentions

All deployment-specific IDs are env-driven. Messages build channel mentions dynamically:
- configured: `<#{channel_id}>`
- not configured: fallback translation key

## i18n behavior

- Locale normalization to language only (`en-US -> en`, `es-419 -> es`, `nb -> no`)
- `Translator.t(lang, key, **kwargs)` with fallback to `en`
- Missing key in both language and `en` returns the key string

## Session persistence and restart restore

`wizard_sessions` stores `language`, `current_step`, `answers_json`, and TTL.
`persistent_views` stores message/channel/custom ID state for startup restoration.

## Data separation

By default, each deployment gets its own SQLite DB:

`data/{BOT_PROFILE}_{GUILD_ID}.sqlite3`

This keeps single-guild deployments isolated per profile and environment.
