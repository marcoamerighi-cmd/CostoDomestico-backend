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

    cursor.execute("""
        ALTER TABLE email_admin
        ADD COLUMN IF NOT EXISTS tipo TEXT DEFAULT 'inviata'
    """)

    cursor.execute("""
        ALTER TABLE email_admin
        ADD COLUMN IF NOT EXISTS mittente TEXT
    """)

    conn.commit()
    cursor.close()
    conn.close()


def salva_email_admin(
    destinatario: str,
    oggetto: str,
    testo: str,
    stato: str,
    errore: str = "",
    tipo: str = "inviata",
    mittente: str = ""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO email_admin (
            destinatario,
            oggetto,
            testo,
            stato,
            errore,
            tipo,
            mittente
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        destinatario,
        oggetto,
        testo,
        stato,
        errore,
        tipo,
        mittente
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

def leggi_messaggi_clienti():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            mittente,
            oggetto,
            testo,
            stato,
            creato_il
        FROM email_admin
        WHERE tipo = 'ricevuta'
        ORDER BY id DESC
    """)

    righe = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": riga[0],
            "mittente": riga[1],
            "oggetto": riga[2],
            "testo": riga[3],
            "stato": riga[4],
            "creato_il": riga[5],
        }
        for riga in righe
    ]