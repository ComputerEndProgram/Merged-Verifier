# Merged-Verifier

Merged single-repo Discord bot for:
- STFC-Verifier
- STFC-Verifier-Alliance
- Veil-Security

The runtime is profile-selected with `BOT_PROFILE` and executes the corresponding
merged implementation from `bot/legacy_profiles/`.

## Run

```bash
python3 -m pip install -e ".[dev]"
cp .env.example .env
python3 -m bot.main
```

## Profile selection

Set one value:
- `BOT_PROFILE=stfc_verifier`
- `BOT_PROFILE=stfc_verifier_alliance`
- `BOT_PROFILE=veil_security`

## Environment variables

Core:
- `DISCORD_TOKEN`, `BOT_PROFILE`, `GUILD_ID`, `VERIFY_CHANNEL_ID`
- `LOG_CHANNEL_ID`, `SUPPORT_CHANNEL_ID`, `UPDATE_CHECK_HOURS`, `DEBUG`

STFC rank profiles (`stfc_verifier`, `stfc_verifier_alliance`):
- `STFC_SERVER_NUMBER` or `STFC_SERVER_ID`
- `MEMBER_ROLE_ID`, `COMMODORE_ROLE_ID`, `ADMIRAL_ROLE_ID`
- `VERIFY_ROLE_ID` (or `VERIFIED_ROLE_ID`)
- `ADMIN_ROLE_ID`

Veil security profile:
- `OPS71_PLUS_ROLE_ID` or `OPS71_ROLE_ID`
- `MINIMUM_OPS_LEVEL` or `MIN_OPS_LEVEL`
- `VERIFY_ROLE_ID` (or `VERIFIED_ROLE_ID`)
- `ADMIN_ROLE_ID`

Database:
- `DB_PATH` (optional explicit path)
- default when unset: `data/{BOT_PROFILE}_{GUILD_ID}.sqlite3`

## Support channel mentions

Hardcoded channel mentions were removed from profile implementations.
Set `SUPPORT_CHANNEL_ID` to render `<#id>` dynamically. If unset, fallback text is used.

## Tests

```bash
python3 -m pytest -q
```
