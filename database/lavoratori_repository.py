from database.db import get_connection


def salva_lavoratore(lavoratore) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lavoratori (
            nome,
            cognome,
            livello,
            convivente,
            data_assunzione,
            data_cessazione
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        lavoratore.nome,
        lavoratore.cognome,
        lavoratore.livello,
        1 if lavoratore.convivente else 0,
        lavoratore.data_assunzione.isoformat(),
        lavoratore.data_cessazione.isoformat() if lavoratore.data_cessazione else None
    ))

    conn.commit()
    lavoratore_id = cursor.lastrowid
    conn.close()

    return lavoratore_id
def leggi_lavoratori():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cognome,
            livello,
            convivente,
            data_assunzione,
            data_cessazione
        FROM lavoratori
    """)

    risultati = cursor.fetchall()

    conn.close()

    return risultati