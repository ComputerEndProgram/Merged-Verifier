import pytest

from bot.config.profiles import get_profile
from bot.profiles.base import ProfileNotFoundError


def test_profile_registry_contains_expected_profiles() -> None:
    assert get_profile("stfc_verifier").name == "stfc_verifier"
    assert get_profile("stfc_verifier_alliance").name == "stfc_verifier_alliance"
    assert get_profile("veil_security").name == "veil_security"


def test_unknown_profile_raises() -> None:
    with pytest.raises(ProfileNotFoundError):
        get_profile("not_real")

