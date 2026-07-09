import importlib
import os

from dotenv import load_dotenv

from bot.config.profiles import get_profile

load_dotenv()

PROFILE_MODULES = {
    "stfc_verifier": "bot.legacy_profiles.stfc_verifier",
    "stfc_verifier_alliance": "bot.legacy_profiles.stfc_verifier_alliance",
    "veil_security": "bot.legacy_profiles.veil_security",
}


def run_selected_profile() -> None:
    profile_name = os.getenv("BOT_PROFILE")
    if not profile_name:
        raise SystemExit("Missing BOT_PROFILE in environment")

    module_name = PROFILE_MODULES.get(profile_name)
    if not module_name:
        valid = ", ".join(sorted(PROFILE_MODULES))
        raise SystemExit(f"Unknown BOT_PROFILE '{profile_name}'. Expected one of: {valid}")

    get_profile(profile_name)

    module = importlib.import_module(module_name)
    module.run()
