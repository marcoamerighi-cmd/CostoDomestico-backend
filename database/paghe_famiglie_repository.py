import os
from datetime import datetime

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_famiglia(
    email: str,
    nome: str = "",
    cognome: str = "",
    telefono: str = ""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_famiglie (
            email,
            nome,
            cognome,
            telefono
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        email,
        nome,
        cognome,
        telefono
    ))

    famiglia_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return famiglia_id


def leggi_famiglia(famiglia_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            nome,
            cognome,
            telefono,
            stato,
            created_at
        FROM paghe_famiglie
        WHERE id = %s
    """, (famiglia_id,))

    famiglia = cursor.fetchone()

    cursor.close()
    conn.close()

    return famiglia


def leggi_famiglia_per_email(email):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            nome,
            cognome,
            telefono,
            stato
        FROM paghe_famiglie
        WHERE LOWER(email) = LOWER(%s)
    """, (email,))

    famiglia = cursor.fetchone()

    cursor.close()
    conn.close()

    return famiglia


def aggiorna_famiglia(
    famiglia_id,
    nome,
    cognome,
    telefono
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_famiglie
        SET
            nome = %s,
            cognome = %s,
            telefono = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        nome,
        cognome,
        telefono,
        famiglia_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_famiglia(famiglia_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_famiglie
        WHERE id = %s
    """, (
        famiglia_id,
    ))

    conn.commit()

    cursor.close()
    conn.close()