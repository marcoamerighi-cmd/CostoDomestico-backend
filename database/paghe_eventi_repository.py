import os

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_evento(
    mese_id,
    rapporto_id,
    tipo_evento,
    data_inizio,
    data_fine=None,
    ore=None,
    giorni=None,
    importo=None,
    note=""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_eventi (
            mese_id,
            rapporto_id,
            tipo_evento,
            data_inizio,
            data_fine,
            ore,
            giorni,
            importo,
            note
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        mese_id,
        rapporto_id,
        tipo_evento,
        data_inizio,
        data_fine,
        ore,
        giorni,
        importo,
        note
    ))

    evento_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return evento_id


def leggi_evento(evento_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_eventi
        WHERE id = %s
    """, (evento_id,))

    evento = cursor.fetchone()

    cursor.close()
    conn.close()

    return evento


def leggi_eventi_mese(mese_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_eventi
        WHERE mese_id = %s
        ORDER BY data_inizio ASC, created_at ASC
    """, (mese_id,))

    eventi = cursor.fetchall()

    cursor.close()
    conn.close()

    return eventi


def leggi_eventi_rapporto(rapporto_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_eventi
        WHERE rapporto_id = %s
        ORDER BY data_inizio DESC, created_at DESC
    """, (rapporto_id,))

    eventi = cursor.fetchall()

    cursor.close()
    conn.close()

    return eventi


def aggiorna_evento(
    evento_id,
    tipo_evento,
    data_inizio,
    data_fine,
    ore,
    giorni,
    importo,
    note
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_eventi
        SET
            tipo_evento = %s,
            data_inizio = %s,
            data_fine = %s,
            ore = %s,
            giorni = %s,
            importo = %s,
            note = %s
        WHERE id = %s
    """, (
        tipo_evento,
        data_inizio,
        data_fine,
        ore,
        giorni,
        importo,
        note,
        evento_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_evento(evento_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_eventi
        WHERE id = %s
    """, (evento_id,))

    conn.commit()

    cursor.close()
    conn.close()