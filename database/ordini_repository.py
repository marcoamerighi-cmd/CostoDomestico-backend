import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_tabella_ordini():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY,
            email_cliente TEXT,
            nome_cliente TEXT,
            cognome_cliente TEXT,
            prodotto TEXT,
            importo REAL,
            stato TEXT,
            sessione_stripe TEXT,
            data_ordine TEXT,
            pdf_file TEXT,
            pdf_base64 TEXT
        )
    """)

    cursor.execute("""
        ALTER TABLE ordini
        ADD COLUMN IF NOT EXISTS sessione_stripe TEXT
    """)

    cursor.execute("""
        ALTER TABLE ordini
        ADD COLUMN IF NOT EXISTS pdf_file TEXT
    """)

    cursor.execute("""
        ALTER TABLE ordini
        ADD COLUMN IF NOT EXISTS pdf_base64 TEXT
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storico_calcoli (
        id SERIAL PRIMARY KEY,

        email_cliente TEXT,
        tipo TEXT,

        titolo TEXT,
        dettaglio TEXT,

        importo REAL,

        data_calcolo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.commit()
    cursor.close()
    conn.close()


def salva_ordine(
    email_cliente: str,
    nome_cliente: str,
    cognome_cliente: str,
    prodotto: str,
    importo: float,
    stato: str,
    sessione_stripe: str
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ordini (
            email_cliente,
            nome_cliente,
            cognome_cliente,
            prodotto,
            importo,
            stato,
            sessione_stripe,
            data_ordine
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        email_cliente,
        nome_cliente,
        cognome_cliente,
        prodotto,
        importo,
        stato,
        sessione_stripe,
        datetime.now().isoformat()
    ))

    conn.commit()
    cursor.close()
    conn.close()


def leggi_ordini():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email_cliente,
            nome_cliente,
            cognome_cliente,
            prodotto,
            importo,
            stato,
            sessione_stripe,
            data_ordine,
            pdf_file,
            pdf_base64
        FROM ordini
        ORDER BY id DESC
    """)

    ordini = cursor.fetchall()

    cursor.close()
    conn.close()

    return ordini


def salva_storico_calcolo(
    email_cliente: str,
    tipo: str,
    titolo: str,
    dettaglio: str,
    importo: float = 0
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO storico_calcoli (
            email_cliente,
            tipo,
            titolo,
            dettaglio,
            importo
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        email_cliente,
        tipo,
        titolo,
        dettaglio,
        importo
    ))

    conn.commit()
    cursor.close()
    conn.close()


def leggi_storico_calcoli(
    email_cliente: str
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            tipo,
            titolo,
            dettaglio,
            importo,
            data_calcolo
        FROM storico_calcoli
        WHERE email_cliente=%s
        ORDER BY id DESC
    """, (
        email_cliente,
    ))

    risultati = cursor.fetchall()

    cursor.close()
    conn.close()

    return risultati


def aggiorna_stato_ordine(
    sessione_stripe: str,
    stato: str
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ordini
        SET stato = %s
        WHERE sessione_stripe = %s
    """, (
        stato,
        sessione_stripe
    ))

    conn.commit()
    cursor.close()
    conn.close()


def aggiorna_pdf_ordine(
    sessione_stripe: str,
    pdf_file: str,
    pdf_base64: str = ""
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ordini
        SET pdf_file = %s,
            pdf_base64 = %s
        WHERE sessione_stripe = %s
    """, (
        pdf_file,
        pdf_base64,
        sessione_stripe
    ))

    conn.commit()
    cursor.close()
    conn.close()


def elimina_ordini_test():
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM ordini
        WHERE
            email_cliente ILIKE '%test%'
            OR email_cliente ILIKE '%postgres%'
    """)

    eliminati = cursor.rowcount

    conn.commit()
    cursor.close()
    conn.close()

    return eliminati


def crea_tabella_funnel():

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funnel_eventi (
            id SERIAL PRIMARY KEY,
            evento VARCHAR(100),
            data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def salva_evento_funnel(evento):

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO funnel_eventi (evento)
        VALUES (%s)
        """,
        (evento,)
    )

    conn.commit()
    cursor.close()
    conn.close()


def leggi_eventi_funnel():

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT evento, COUNT(*)
        FROM funnel_eventi
        GROUP BY evento
    """)

    risultati = cursor.fetchall()

    cursor.close()
    conn.close()

    eventi = {}

    for evento, totale in risultati:
        eventi[evento] = totale

    return eventi


def reset_dashboard_test():

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM funnel_eventi")
    cursor.execute("DELETE FROM ordini")
    cursor.execute("DELETE FROM clienti")

    conn.commit()

    cursor.close()
    conn.close()

    return True