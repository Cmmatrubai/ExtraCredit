"""Seed a demo SQLite database (sample.db) using db_seed.sql."""

from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sample.db"
SQL_PATH = BASE_DIR / "db_seed.sql"


def seed() -> None:
    if not SQL_PATH.exists():
        raise FileNotFoundError(f"Seed SQL not found at {SQL_PATH}")

    script = SQL_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(script)
        conn.commit()
    print(f"Seeded {DB_PATH} with demo data.")


if __name__ == "__main__":
    seed()
