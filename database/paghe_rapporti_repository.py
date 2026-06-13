import os

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connessione():
    return psycopg2.connect(DATABASE_URL)


def crea_rapporto(
    famiglia_id,
    datore_id,
    lavoratore_id,
    tipo_contratto="tempo_indeterminato",
    data_fine_contratto=None,
    motivo_termine="",
    proroghe=None,
    mansione="colf",
    livello="A",
    convivente=False,
    ore_settimanali=0,
    tipo_orario="part_time",
    part_time_art14=False,
    paga_oraria=None,
    paga_mensile=None,
    paga_pattuita_tipo="mensile",
    data_assunzione=None,
    data_cessazione=None,
    stato="attivo"
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paghe_rapporti (
            famiglia_id,
            datore_id,
            lavoratore_id,
            tipo_contratto,
            data_fine_contratto,
            motivo_termine,
            proroghe,
            mansione,
            livello,
            convivente,
            ore_settimanali,
            tipo_orario,
            part_time_art14,
            paga_oraria,
            paga_mensile,
            paga_pattuita_tipo,
            data_assunzione,
            data_cessazione,
            stato
        )
        VALUES (
            %s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s
        )
        RETURNING id
    """, (
        famiglia_id,
        datore_id,
        lavoratore_id,
        tipo_contratto,
        data_fine_contratto,
        motivo_termine,
        proroghe,
        mansione,
        livello,
        convivente,
        ore_settimanali,
        tipo_orario,
        part_time_art14,
        paga_oraria,
        paga_mensile,
        paga_pattuita_tipo,
        data_assunzione,
        data_cessazione,
        stato
    ))

    rapporto_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return rapporto_id


def leggi_rapporto(rapporto_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_rapporti
        WHERE id = %s
    """, (rapporto_id,))

    rapporto = cursor.fetchone()

    cursor.close()
    conn.close()

    return rapporto


def leggi_rapporti_famiglia(famiglia_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_rapporti
        WHERE famiglia_id = %s
        ORDER BY created_at DESC
    """, (famiglia_id,))

    rapporti = cursor.fetchall()

    cursor.close()
    conn.close()

    return rapporti


def leggi_rapporti_lavoratore(lavoratore_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM paghe_rapporti
        WHERE lavoratore_id = %s
        ORDER BY data_assunzione DESC
    """, (lavoratore_id,))

    rapporti = cursor.fetchall()

    cursor.close()
    conn.close()

    return rapporti


def aggiorna_rapporto(
    rapporto_id,
    tipo_contratto,
    data_fine_contratto,
    motivo_termine,
    proroghe,
    mansione,
    livello,
    convivente,
    ore_settimanali,
    tipo_orario,
    part_time_art14,
    paga_oraria,
    paga_mensile,
    paga_pattuita_tipo,
    data_assunzione,
    data_cessazione,
    stato
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_rapporti
        SET
            tipo_contratto = %s,
            data_fine_contratto = %s,
            motivo_termine = %s,
            proroghe = %s,
            mansione = %s,
            livello = %s,
            convivente = %s,
            ore_settimanali = %s,
            tipo_orario = %s,
            part_time_art14 = %s,
            paga_oraria = %s,
            paga_mensile = %s,
            paga_pattuita_tipo = %s,
            data_assunzione = %s,
            data_cessazione = %s,
            stato = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        tipo_contratto,
        data_fine_contratto,
        motivo_termine,
        proroghe,
        mansione,
        livello,
        convivente,
        ore_settimanali,
        tipo_orario,
        part_time_art14,
        paga_oraria,
        paga_mensile,
        paga_pattuita_tipo,
        data_assunzione,
        data_cessazione,
        stato,
        rapporto_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def cessa_rapporto(
    rapporto_id,
    data_cessazione,
    stato="cessato"
):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE paghe_rapporti
        SET
            data_cessazione = %s,
            stato = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        data_cessazione,
        stato,
        rapporto_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def elimina_rapporto(rapporto_id):
    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM paghe_rapporti
        WHERE id = %s
    """, (rapporto_id,))

    conn.commit()

    cursor.close()
    conn.close()