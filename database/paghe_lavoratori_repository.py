import os

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_lavoratore(
    famiglia_id,
    nome,
    cognome,
    codice_fiscale="",
    data_nascita=None,
    luogo_nascita="",
    nazionalita="",
    email="",
    telefono="",
    indirizzo="",
    iban=""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_lavoratori (
            famiglia_id,
            nome,
            cognome,
            codice_fiscale,
            data_nascita,
            luogo_nascita,
            nazionalita,
            email,
            telefono,
            indirizzo,
            iban
        )
        VALUES (
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s
        )
        RETURNING id
    """, (
        famiglia_id,
        nome,
        cognome,
        codice_fiscale,
        data_nascita,
        luogo_nascita,
        nazionalita,
        email,
        telefono,
        indirizzo,
        iban
    ))

    lavoratore_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return lavoratore_id


def leggi_lavoratore(lavoratore_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_lavoratori
        WHERE id = %s
    """, (lavoratore_id,))

    lavoratore = cursor.fetchone()

    cursor.close()
    conn.close()

    return lavoratore


def leggi_lavoratori_famiglia(famiglia_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_lavoratori
        WHERE famiglia_id = %s
        ORDER BY cognome, nome
    """, (famiglia_id,))

    lavoratori = cursor.fetchall()

    cursor.close()
    conn.close()

    return lavoratori


def aggiorna_lavoratore(
    lavoratore_id,
    nome,
    cognome,
    codice_fiscale,
    data_nascita,
    luogo_nascita,
    nazionalita,
    email,
    telefono,
    indirizzo,
    iban
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_lavoratori
        SET
            nome = %s,
            cognome = %s,
            codice_fiscale = %s,
            data_nascita = %s,
            luogo_nascita = %s,
            nazionalita = %s,
            email = %s,
            telefono = %s,
            indirizzo = %s,
            iban = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        nome,
        cognome,
        codice_fiscale,
        data_nascita,
        luogo_nascita,
        nazionalita,
        email,
        telefono,
        indirizzo,
        iban,
        lavoratore_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_lavoratore(lavoratore_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_lavoratori
        WHERE id = %s
    """, (lavoratore_id,))

    conn.commit()

    cursor.close()
    conn.close()