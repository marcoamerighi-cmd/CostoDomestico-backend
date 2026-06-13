import os
import json

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_cedolino(
    mese_id,
    rapporto_id,
    numero_cedolino="",
    lordo=0,
    contributi_lavoratore=0,
    netto=0,
    tfr_maturato=0,
    tredicesima_maturata=0,
    dati_calcolo=None,
    pdf_url="",
    stato="bozza"
):
    if dati_calcolo is None:
        dati_calcolo = {}

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_cedolini (
            mese_id,
            rapporto_id,
            numero_cedolino,
            lordo,
            contributi_lavoratore,
            netto,
            tfr_maturato,
            tredicesima_maturata,
            dati_calcolo,
            pdf_url,
            stato
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        mese_id,
        rapporto_id,
        numero_cedolino,
        lordo,
        contributi_lavoratore,
        netto,
        tfr_maturato,
        tredicesima_maturata,
        json.dumps(dati_calcolo),
        pdf_url,
        stato
    ))

    cedolino_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return cedolino_id


def leggi_cedolino(cedolino_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_cedolini
        WHERE id = %s
    """, (cedolino_id,))

    cedolino = cursor.fetchone()

    cursor.close()
    conn.close()

    return cedolino


def leggi_cedolini_mese(mese_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_cedolini
        WHERE mese_id = %s
        ORDER BY created_at DESC
    """, (mese_id,))

    cedolini = cursor.fetchall()

    cursor.close()
    conn.close()

    return cedolini


def leggi_cedolini_rapporto(rapporto_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_cedolini
        WHERE rapporto_id = %s
        ORDER BY created_at DESC
    """, (rapporto_id,))

    cedolini = cursor.fetchall()

    cursor.close()
    conn.close()

    return cedolini


def aggiorna_cedolino(
    cedolino_id,
    numero_cedolino,
    lordo,
    contributi_lavoratore,
    netto,
    tfr_maturato,
    tredicesima_maturata,
    dati_calcolo,
    pdf_url,
    stato
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_cedolini
        SET
            numero_cedolino = %s,
            lordo = %s,
            contributi_lavoratore = %s,
            netto = %s,
            tfr_maturato = %s,
            tredicesima_maturata = %s,
            dati_calcolo = %s,
            pdf_url = %s,
            stato = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        numero_cedolino,
        lordo,
        contributi_lavoratore,
        netto,
        tfr_maturato,
        tredicesima_maturata,
        json.dumps(dati_calcolo),
        pdf_url,
        stato,
        cedolino_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def marca_cedolino_definitivo(
    cedolino_id,
    pdf_url=""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_cedolini
        SET
            stato = 'definitivo',
            pdf_url = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        pdf_url,
        cedolino_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_cedolino(cedolino_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_cedolini
        WHERE id = %s
    """, (cedolino_id,))

    conn.commit()

    cursor.close()
    conn.close()