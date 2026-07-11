# DTB Verifier

A multi-profile Discord bot for verifying STFC (Star Trek Fleet Command) accounts via [stfc.pro](https://stfc.pro) / [stfc.wtf](https://stfc.wtf) player data.

One codebase, three verification profiles selected at runtime via `BOT_PROFILE`.

## Profiles

| Profile | Description |
|---|---|
| `stfc_verifier` | Rank-based verification with automatic alliance role management |
| `stfc_verifier_alliance` | Rank-based verification (alliance variant, no auto-created alliance roles) |
| `veil_security` | OPS level-based verification with server and OPS 71+ role gates |

## Quick Start

```bash
# Install (editable mode with dev dependencies)
python3 -m pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env — see below for required variables

# Run
python3 -m bot.main
# Or, if installed via pip install .
dtb-verifier
```

## Environment Variables

See [`.env.example`](.env.example) for the full annotated template.

### Required for all profiles

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from the [Discord Developer Portal](https://discord.com/developers/applications) |
| `BOT_PROFILE` | One of: `stfc_verifier`, `stfc_verifier_alliance`, `veil_security` |
| `GUILD_ID` | Your Discord server ID |
| `VERIFY_CHANNEL_ID` | Channel where `/verify` and the verification button are available |
| `ADMIN_ROLE_ID` | Role required for admin commands and rank confirmations |

### Channels

| Variable | Description |
|---|---|
| `LOG_CHANNEL_ID` | Channel for verification logs, rank confirmations, and recall audit trails. If unset, logging is silently skipped. |
| `SUPPORT_CHANNEL_ID` | Channel mentioned in support ticket prompts (`"Open a ticket in #support"`). Falls back to generic text if unset. |

### Roles

| Variable | Description |
|---|---|
| `VERIFIED_ROLE_ID` | Role given to every user after successful verification |
| `MEMBER_ROLE_ID` | **STFC** — base member role assigned on verification |
| `COMMODORE_ROLE_ID` | **STFC** — assigned after admin confirmation |
| `ADMIRAL_ROLE_ID` | **STFC** — assigned after admin confirmation |
| `OPS71_PLUS_ROLE_ID` | **Veil Security** — role for players meeting the OPS level threshold |

### Profile-specific criteria

| Variable | Required by | Description |
|---|---|---|
| `STFC_SERVER_NUMBER` | `stfc_verifier`, `stfc_verifier_alliance` | Players not on this server are rejected |
| `MINIMUM_OPS_LEVEL` | `veil_security` | Minimum OPS level to receive the OPS 71+ role |

### Behavior

| Variable | Default | Description |
|---|---|---|
| `UPDATE_CHECK_HOURS` | `24` | Hours between automatic player data refresh checks |
| `REQUIRE_SCREENSHOT` | `true` | Require a screenshot upload during the verification wizard |
| `DEFAULT_LANGUAGE` | `en` | Language for the verification wizard UI |
| `DEBUG` | `0` | Enable verbose debug logging |

### Database

By default, the bot creates a SQLite database at `data/{BOT_PROFILE}_{GUILD_ID}.sqlite3`. Override with:

| Variable | Description |
|---|---|
| `SQLITE_PATH` | Absolute path to a SQLite file |
| `DATABASE_URL` | `sqlite:///` URL to a SQLite file |

## Commands

### User commands

| Command | Description |
|---|---|
| `/verify` | Starts the verification wizard (sends a DM with step-by-step instructions) |

### Admin commands

All admin commands require the `ADMIN_ROLE_ID` role.

| Command | Description |
|---|---|
| `/admin verify <player_url> <user>` | Manually verify a user by their stfc.pro/stfc.wtf link (skips the wizard and screenshot) |
| `/admin recall <user> [reason]` | Recall a user's verification, remove all roles, and notify them via DM |
| `/admin send_button` | Post the verification button to the verify channel for users who struggle with slash commands |

## Verification Flow

1. User runs `/verify` or clicks the verification button
2. Bot sends a DM with the welcome embed and a **Start Verification** button
3. User sends their stfc.pro/stfc.wtf player link
4. Bot fetches fresh player data from stfc.pro (username, level, server, alliance, rank)
5. *(Optional)* User uploads a screenshot (skipped if `REQUIRE_SCREENSHOT=false`)
6. Bot shows a summary; user clicks **Complete**
7. Bot sets the nickname, assigns roles, stores player data, and logs to the log channel
8. For Commodore/Admiral ranks, a confirmation embed is posted to the log channel for admin approval

## Admin Manual Verification

When a user can't complete the wizard (DMs disabled, confusion, etc.), an admin can run:

```
/admin verify player_url: https://stfc.pro/players/1234567890 user: @username
```

This performs the same steps as the wizard (nickname, roles, logging) but skips the DM interaction and screenshot. Screenshot is always skipped.

## Tests

```bash
python3 -m pytest -q
```

## Architecture

```
bot/
├── main.py                    # Entry point
├── launcher.py                # Profile-based dynamic dispatch
├── config/
│   ├── settings.py            # Settings from .env
│   └── profiles.py            # Profile registry
├── core/
│   ├── bot_base.py            # BaseBot — shared verification logic
│   ├── store.py               # SQLite store (ProfileStore)
│   ├── views.py               # Discord UI views (wizards, confirmations)
│   ├── verification/          # Session flow and step constants
│   ├── sessions/              # New-style session store (WIP)
│   ├── roles/                 # Role assignment
│   ├── persistence/           # Database helpers
│   └── i18n/                  # Translation system
├── cogs/
│   ├── verification.py        # /verify command
│   └── admin.py               # /admin commands (verify, recall, send_button)
├── profiles/                  # New-style profile protocol (WIP)
├── legacy_profiles/           # Running bot implementations
│   ├── stfc_verifier/
│   ├── stfc_verifier_alliance/
│   └── veil_security/
└── i18n/                      # Translation JSON files (22 languages)
```
