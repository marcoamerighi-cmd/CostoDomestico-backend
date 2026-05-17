import sqlite3
from datetime import datetime

DB_PATH = "database/costodomestico.db"


def crea_tabella_ordini():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordini (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_cliente TEXT,
            nome_cliente TEXT,
            cognome_cliente TEXT,
            prodotto TEXT,
            importo REAL,
            stato TEXT,
            sessione_stripe TEXT,
            data_ordine TEXT
        )
    """)

    conn.commit()
    conn.close()


def salva_ordine(
    email_cliente: str,
    nome_cliente: str,
    cognome_cliente: str,
    prodotto: str,
    importo: float,
    stato: str,
    sessione_stripe: str
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ordini (
            email_cliente,
            nome_cliente,
            cognome_cliente,
            prodotto,
            importo,
            stato,
            sessione_stripe,
            data_ordine
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email_cliente,
        nome_cliente,
        cognome_cliente,
        prodotto,
        importo,
        stato,
        sessione_stripe,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def leggi_ordini():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email_cliente,
            nome_cliente,
            cognome_cliente,
            prodotto,
            importo,
            stato,
            sessione_stripe,
            data_ordine
        FROM ordini
        ORDER BY id DESC
    """)

    ordini = cursor.fetchall()

    conn.close()

    return ordini

def aggiorna_stato_ordine(
    sessione_stripe: str,
    stato: str
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ordini
        SET stato = ?
        WHERE sessione_stripe = ?
    """, (
        stato,
        sessione_stripe
    ))

    conn.commit()
    conn.close()