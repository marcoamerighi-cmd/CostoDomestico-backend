import os

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_datore(
    famiglia_id,
    nome,
    cognome,
    codice_fiscale="",
    email="",
    telefono="",
    indirizzo="",
    comune="",
    provincia="",
    cap=""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_datori (
            famiglia_id,
            nome,
            cognome,
            codice_fiscale,
            email,
            telefono,
            indirizzo,
            comune,
            provincia,
            cap
        )
        VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s
        )
        RETURNING id
    """, (
        famiglia_id,
        nome,
        cognome,
        codice_fiscale,
        email,
        telefono,
        indirizzo,
        comune,
        provincia,
        cap
    ))

    datore_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return datore_id


def leggi_datore(datore_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_datori
        WHERE id = %s
    """, (datore_id,))

    dato = cursor.fetchone()

    cursor.close()
    conn.close()

    return dato


def leggi_datori_famiglia(famiglia_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_datori
        WHERE famiglia_id = %s
        ORDER BY cognome, nome
    """, (famiglia_id,))

    dati = cursor.fetchall()

    cursor.close()
    conn.close()

    return dati


def aggiorna_datore(
    datore_id,
    nome,
    cognome,
    codice_fiscale,
    email,
    telefono,
    indirizzo,
    comune,
    provincia,
    cap
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_datori
        SET
            nome=%s,
            cognome=%s,
            codice_fiscale=%s,
            email=%s,
            telefono=%s,
            indirizzo=%s,
            comune=%s,
            provincia=%s,
            cap=%s,
            updated_at=NOW()
        WHERE id=%s
    """, (
        nome,
        cognome,
        codice_fiscale,
        email,
        telefono,
        indirizzo,
        comune,
        provincia,
        cap,
        datore_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_datore(datore_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_datori
        WHERE id = %s
    """, (datore_id,))

    conn.commit()

    cursor.close()
    conn.close()