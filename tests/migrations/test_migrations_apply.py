import sqlite3
from pathlib import Path


def _sql_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.sql"))


def test_all_migrations_apply_cleanly(tmp_path) -> None:
    database_path = tmp_path / "migration-test.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        migration_root = Path(__file__).resolve().parents[2] / "migrations"
        for sql_file in _sql_files(migration_root):
            sql = sql_file.read_text(encoding="utf-8")
            connection.executescript(sql)
    finally:
        connection.close()

