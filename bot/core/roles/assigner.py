from dataclasses import dataclass


@dataclass(slots=True)
class RoleAssignment:
    add_role_ids: list[int]
    remove_role_ids: list[int]

