def has_required_fields(answers: dict[str, str]) -> bool:
    return bool(answers.get("player_name")) and bool(answers.get("player_id"))

