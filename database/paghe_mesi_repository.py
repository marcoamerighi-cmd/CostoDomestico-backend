import os

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_mese(
    rapporto_id,
    anno,
    mese,
    stato="aperto"
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_mesi (
            rapporto_id,
            anno,
            mese,
            stato
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        rapporto_id,
        anno,
        mese,
        stato
    ))

    mese_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return mese_id


def leggi_mese(mese_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_mesi
        WHERE id = %s
    """, (mese_id,))

    mese = cursor.fetchone()

    cursor.close()
    conn.close()

    return mese


def leggi_mese_rapporto(
    rapporto_id,
    anno,
    mese
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_mesi
        WHERE rapporto_id = %s
        AND anno = %s
        AND mese = %s
    """, (
        rapporto_id,
        anno,
        mese
    ))

    risultato = cursor.fetchone()

    cursor.close()
    conn.close()

    return risultato


def leggi_mesi_rapporto(rapporto_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_mesi
        WHERE rapporto_id = %s
        ORDER BY anno DESC, mese DESC
    """, (rapporto_id,))

    mesi = cursor.fetchall()

    cursor.close()
    conn.close()

    return mesi


def chiudi_mese(mese_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_mesi
        SET
            stato = 'chiuso',
            updated_at = NOW()
        WHERE id = %s
    """, (mese_id,))

    conn.commit()

    cursor.close()
    conn.close()


def riapri_mese(mese_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_mesi
        SET
            stato = 'aperto',
            updated_at = NOW()
        WHERE id = %s
    """, (mese_id,))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_mese(mese_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_mesi
        WHERE id = %s
    """, (mese_id,))

    conn.commit()

    cursor.close()
    conn.close()