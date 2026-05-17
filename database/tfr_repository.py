from datetime import date

from database.db import get_connection


def salva_calcolo_tfr(lavoratore_id: int, risultato_tfr: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tfr_calcoli (
            lavoratore_id,
            mesi_utili,
            retribuzione_utile,
            quota_tfr,
            rivalutazione,
            anticipi,
            totale_da_liquidare,
            data_calcolo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lavoratore_id,
        risultato_tfr["mesi_utili"],
        risultato_tfr["dettaglio_tfr"]["retribuzione_utile"],
        risultato_tfr["dettaglio_tfr"]["quota_tfr"],
        risultato_tfr["rivalutazione"],
        risultato_tfr["liquidazione"]["anticipi"],
        risultato_tfr["liquidazione"]["totale_da_liquidare"],
        date.today().isoformat()
    ))

    conn.commit()
    calcolo_id = cursor.lastrowid
    conn.close()

    return calcolo_id
def leggi_calcoli_tfr():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tfr_calcoli.id,
            lavoratori.nome,
            lavoratori.cognome,
            tfr_calcoli.mesi_utili,
            tfr_calcoli.retribuzione_utile,
            tfr_calcoli.quota_tfr,
            tfr_calcoli.rivalutazione,
            tfr_calcoli.anticipi,
            tfr_calcoli.totale_da_liquidare,
            tfr_calcoli.data_calcolo
        FROM tfr_calcoli
        JOIN lavoratori
            ON lavoratori.id = tfr_calcoli.lavoratore_id
    """)

    risultati = cursor.fetchall()
    conn.close()

    return risultati