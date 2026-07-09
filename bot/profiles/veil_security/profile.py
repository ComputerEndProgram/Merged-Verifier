from bot.core.roles.assigner import RoleAssignment
from bot.core.verification.steps import FINALIZE_STEP, START_STEP, SUBMIT_STEP
from bot.profiles.base import VerificationProfile, VerificationResult


class VeilSecurityProfile(VerificationProfile):
    name = "veil_security"
    required_inputs = ("stfc_link", "screenshot")
    required_roles = ("ops71_plus_role_id",)
    optional_roles = ("verified_role_id", "admin_role_id")
    features = ("ops_level_check", "server_role_match")

    def build_steps(self) -> list[str]:
        return [START_STEP, SUBMIT_STEP, FINALIZE_STEP]

    def verify(self, answers: dict[str, str]) -> VerificationResult:
        if not answers.get("stfc_link"):
            return VerificationResult(False, "missing_stfc_link")
        return VerificationResult(True)

    def assign_roles(self, answers: dict[str, str]) -> RoleAssignment:
        return RoleAssignment(add_role_ids=[], remove_role_ids=[])

    def finalize(self, answers: dict[str, str]) -> dict[str, str]:
        return {"event": "verified", "profile": self.name}
