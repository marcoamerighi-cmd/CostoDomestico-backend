import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_tabella_ordini():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY,
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
    cursor.close()
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
    conn = get_connessione()
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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
    cursor.close()
    conn.close()


def leggi_ordini():
    conn = get_connessione()
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

    cursor.close()
    conn.close()

    return ordini


def aggiorna_stato_ordine(
    sessione_stripe: str,
    stato: str
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ordini
        SET stato = %s
        WHERE sessione_stripe = %s
    """, (
        stato,
        sessione_stripe
    ))

    conn.commit()
    cursor.close()
    conn.close()