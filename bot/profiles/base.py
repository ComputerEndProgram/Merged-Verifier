from dataclasses import dataclass
from typing import Protocol, Sequence

from bot.core.roles.assigner import RoleAssignment


class ProfileNotFoundError(ValueError):
    pass


@dataclass(slots=True)
class VerificationResult:
    passed: bool
    reason: str | None = None


class VerificationProfile(Protocol):
    name: str
    required_inputs: Sequence[str]

    def build_steps(self) -> list[str]:
        ...

    def verify(self, answers: dict[str, str]) -> VerificationResult:
        ...

    def assign_roles(self, answers: dict[str, str]) -> RoleAssignment:
        ...

    def finalize(self, answers: dict[str, str]) -> dict[str, str]:
        ...

