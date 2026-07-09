from os import getenv


def required(name: str) -> str:
    value = getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def optional(name: str, default: str | None = None) -> str | None:
    value = getenv(name)
    return value if value else default


def optional_first(*names: str) -> str | None:
    for name in names:
        value = optional(name)
        if value is not None:
            return value
    return None


def optional_int(name: str) -> int | None:
    value = optional(name)
    return int(value) if value is not None else None


def optional_int_first(*names: str) -> int | None:
    value = optional_first(*names)
    return int(value) if value is not None else None
