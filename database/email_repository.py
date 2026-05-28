from database.ordini_repository import get_connessione


def crea_tabella_email():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_admin (
            id SERIAL PRIMARY KEY,
            destinatario TEXT,
            oggetto TEXT,
            testo TEXT,
            stato TEXT,
            errore TEXT,
            creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def salva_email_admin(
    destinatario: str,
    oggetto: str,
    testo: str,
    stato: str,
    errore: str = ""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO email_admin (
            destinatario,
            oggetto,
            testo,
            stato,
            errore
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        destinatario,
        oggetto,
        testo,
        stato,
        errore
    ))

    conn.commit()
    conn.close()


def leggi_email_admin():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            destinatario,
            oggetto,
            testo,
            stato,
            errore,
            creato_il
        FROM email_admin
        ORDER BY id DESC
    """)

    righe = cursor.fetchall()
    conn.close()

    return [
        {
            "id": riga[0],
            "destinatario": riga[1],
            "oggetto": riga[2],
            "testo": riga[3],
            "stato": riga[4],
            "errore": riga[5],
            "creato_il": riga[6],
        }
        for riga in righe
    ]