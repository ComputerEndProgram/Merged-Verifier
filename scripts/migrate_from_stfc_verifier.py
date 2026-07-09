from pathlib import Path


def migrate(source_db_path: Path, target_db_path: Path) -> None:
    """
    Starter migration entrypoint for STFC-Verifier.
    Add source SELECT queries and target INSERT mappings here.
    """
    if not source_db_path.exists():
        raise FileNotFoundError(source_db_path)
    target_db_path.parent.mkdir(parents=True, exist_ok=True)

