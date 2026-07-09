def has_required_fields(answers: dict[str, str]) -> bool:
    return (
        bool(answers.get("agent_name"))
        and bool(answers.get("security_phrase"))
        and bool(answers.get("clearance_code"))
    )

