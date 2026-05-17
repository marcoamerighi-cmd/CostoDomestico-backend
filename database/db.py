import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "costodomestico.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def crea_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lavoratori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            livello TEXT NOT NULL,
            convivente INTEGER NOT NULL,
            data_assunzione TEXT NOT NULL,
            data_cessazione TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lavoratore_id INTEGER NOT NULL,
            paga_lorda_annua REAL NOT NULL,
            ore_settimanali REAL NOT NULL,
            vitto_alloggio_annuo REAL DEFAULT 0,
            scatti_anzianita_annui REAL DEFAULT 0,
            superminimo_annuo REAL DEFAULT 0,
            FOREIGN KEY (lavoratore_id) REFERENCES lavoratori(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tfr_calcoli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lavoratore_id INTEGER NOT NULL,
            mesi_utili INTEGER NOT NULL,
            retribuzione_utile REAL NOT NULL,
            quota_tfr REAL NOT NULL,
            rivalutazione REAL DEFAULT 0,
            anticipi REAL DEFAULT 0,
            totale_da_liquidare REAL NOT NULL,
            data_calcolo TEXT NOT NULL,
            FOREIGN KEY (lavoratore_id) REFERENCES lavoratori(id)
        )
    """)

    conn.commit()
    conn.close()