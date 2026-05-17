import os
from datetime import datetime

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_tabella_clienti():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clienti (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            nome TEXT,
            cognome TEXT,
            data_creazione TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def salva_o_aggiorna_cliente(
    email: str,
    nome: str = "",
    cognome: str = ""
):
    if not email:
        return

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clienti (
            email,
            nome,
            cognome,
            data_creazione
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email)
        DO UPDATE SET
            nome = EXCLUDED.nome,
            cognome = EXCLUDED.cognome
    """, (
        email,
        nome,
        cognome,
        datetime.now().isoformat()
    ))

    conn.commit()
    cursor.close()
    conn.close()


def leggi_clienti():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            nome,
            cognome,
            data_creazione
        FROM clienti
        ORDER BY id DESC
    """)

    clienti = cursor.fetchall()

    cursor.close()
    conn.close()

    return clienti