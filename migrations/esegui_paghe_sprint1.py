from pathlib import Path
import os
import sys

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "2026_06_13_paghe_sprint1.sql"


def carica_env():
    app_dir = BASE_DIR.parent
    env_path = app_dir / ".env"

    if env_path.exists():
        load_dotenv(env_path)


def get_connessione():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL non trovata nel file .env")

    return psycopg2.connect(database_url)


def esegui_migration():
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"File SQL non trovato: {SQL_FILE}")

    sql = SQL_FILE.read_text(encoding="utf-8")

    conn = get_connessione()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        conn.commit()
        print("Migration Sprint 1 paghe eseguita correttamente.")
    except Exception as errore:
        conn.rollback()
        print("Errore durante la migration Sprint 1 paghe:")
        print(errore)
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    carica_env()
    esegui_migration()