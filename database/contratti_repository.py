from database.db import get_connection


def salva_contratto(lavoratore_id: int, contratto) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contratti (
            lavoratore_id,
            paga_lorda_annua,
            ore_settimanali,
            vitto_alloggio_annuo,
            scatti_anzianita_annui,
            superminimo_annuo
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        lavoratore_id,
        contratto.paga_lorda_annua,
        contratto.ore_settimanali,
        contratto.vitto_alloggio_annuo,
        contratto.scatti_anzianita_annui,
        contratto.superminimo_annuo
    ))

    conn.commit()
    contratto_id = cursor.lastrowid
    conn.close()

    return contratto_id