from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_datori_repository import crea_datore, elimina_datore
from database.paghe_lavoratori_repository import crea_lavoratore, elimina_lavoratore
from database.paghe_rapporti_repository import crea_rapporto, elimina_rapporto
from database.paghe_mesi_repository import (
    crea_mese,
    leggi_mese,
    leggi_mese_rapporto,
    leggi_mesi_rapporto,
    chiudi_mese,
    riapri_mese,
    elimina_mese,
)


def test_paghe_mesi_repository():
    famiglia_id = crea_famiglia(
        email="test.mesi.famiglia@costodomestico.it",
        nome="Famiglia",
        cognome="Mesi",
        telefono="3330000000"
    )

    datore_id = crea_datore(
        famiglia_id=famiglia_id,
        nome="Mario",
        cognome="Rossi",
        codice_fiscale="RSSMRA80A01H501U"
    )

    lavoratore_id = crea_lavoratore(
        famiglia_id=famiglia_id,
        nome="Anna",
        cognome="Verdi",
        codice_fiscale="VRDNNA80A41H501U"
    )

    rapporto_id = crea_rapporto(
        famiglia_id=famiglia_id,
        datore_id=datore_id,
        lavoratore_id=lavoratore_id,
        tipo_contratto="tempo_indeterminato",
        mansione="colf",
        livello="B",
        convivente=False,
        ore_settimanali=20,
        tipo_orario="part_time",
        part_time_art14=True,
        paga_oraria=8.50,
        paga_pattuita_tipo="oraria",
        data_assunzione="2026-01-01"
    )

    mese_id = crea_mese(
        rapporto_id=rapporto_id,
        anno=2026,
        mese=6
    )

    print("Mese creato:", mese_id)

    mese = leggi_mese(mese_id)
    print("Mese letto:", mese)

    mese_rapporto = leggi_mese_rapporto(
        rapporto_id=rapporto_id,
        anno=2026,
        mese=6
    )
    print("Mese rapporto:", mese_rapporto)

    mesi_rapporto = leggi_mesi_rapporto(rapporto_id)
    print("Mesi rapporto:", mesi_rapporto)

    chiudi_mese(mese_id)
    mese_chiuso = leggi_mese(mese_id)
    print("Mese chiuso:", mese_chiuso)

    riapri_mese(mese_id)
    mese_riaperto = leggi_mese(mese_id)
    print("Mese riaperto:", mese_riaperto)

    elimina_mese(mese_id)
    mese_eliminato = leggi_mese(mese_id)
    print("Mese eliminato:", mese_eliminato)

    elimina_rapporto(rapporto_id)
    elimina_lavoratore(lavoratore_id)
    elimina_datore(datore_id)
    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_paghe_mesi_repository()