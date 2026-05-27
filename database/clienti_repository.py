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

    cursor.execute("""
    ALTER TABLE clienti
    ADD COLUMN IF NOT EXISTS magic_token TEXT
""")

    cursor.execute("""
    ALTER TABLE clienti
    ADD COLUMN IF NOT EXISTS magic_token_scadenza TEXT
""")

    cursor.execute("""
    ALTER TABLE clienti
    ADD COLUMN IF NOT EXISTS ultimo_accesso TEXT
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

    email = email.strip().lower()

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

def salva_magic_token(
    email: str,
    token: str,
    scadenza: str
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clienti
        SET magic_token = %s,
            magic_token_scadenza = %s
        WHERE LOWER(TRIM(email)) = %s
    """, (
        token,
        scadenza,
        email.lower().strip()
    ))

    conn.commit()
    cursor.close()
    conn.close()


def verifica_magic_token(
    token: str
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            nome,
            cognome,
            magic_token_scadenza
        FROM clienti
        WHERE magic_token = %s
    """, (
        token,
    ))

    cliente = cursor.fetchone()

    if not cliente:
        cursor.close()
        conn.close()
        return None

    cursor.execute("""
        UPDATE clienti
        SET ultimo_accesso = %s,
            magic_token = NULL,
            magic_token_scadenza = NULL
        WHERE id = %s
    """, (
        datetime.now().isoformat(),
        cliente[0]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "id": cliente[0],
        "email": cliente[1],
        "nome": cliente[2],
        "cognome": cliente[3],
        "scadenza": cliente[4]
    }