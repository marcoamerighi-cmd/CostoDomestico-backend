from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_datori_repository import crea_datore, elimina_datore
from database.paghe_lavoratori_repository import crea_lavoratore, elimina_lavoratore
from database.paghe_rapporti_repository import (
    crea_rapporto,
    leggi_rapporto,
    leggi_rapporti_famiglia,
    leggi_rapporti_lavoratore,
    aggiorna_rapporto,
    cessa_rapporto,
    elimina_rapporto,
)


def test_paghe_rapporti_repository():
    famiglia_id = crea_famiglia(
        email="test.rapporti.famiglia@costodomestico.it",
        nome="Famiglia",
        cognome="Rapporti",
        telefono="3330000000"
    )

    datore_id = crea_datore(
        famiglia_id=famiglia_id,
        nome="Mario",
        cognome="Rossi",
        codice_fiscale="RSSMRA80A01H501U",
        email="mario.rossi@test.it",
        telefono="3331111111",
        indirizzo="Via Roma 1",
        comune="Roma",
        provincia="RM",
        cap="00100"
    )

    lavoratore_id = crea_lavoratore(
        famiglia_id=famiglia_id,
        nome="Anna",
        cognome="Verdi",
        codice_fiscale="VRDNNA80A41H501U",
        data_nascita="1980-01-01",
        luogo_nascita="Roma",
        nazionalita="Italiana",
        email="anna.verdi@test.it",
        telefono="3332222222",
        indirizzo="Via Milano 20",
        iban="IT60X0542811101000000123456"
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
        paga_mensile=None,
        paga_pattuita_tipo="oraria",
        data_assunzione="2026-01-01",
        stato="attivo"
    )

    print("Rapporto creato:", rapporto_id)

    rapporto = leggi_rapporto(rapporto_id)
    print("Rapporto letto:", rapporto)

    rapporti_famiglia = leggi_rapporti_famiglia(famiglia_id)
    print("Rapporti famiglia:", rapporti_famiglia)

    rapporti_lavoratore = leggi_rapporti_lavoratore(lavoratore_id)
    print("Rapporti lavoratore:", rapporti_lavoratore)

    aggiorna_rapporto(
        rapporto_id=rapporto_id,
        tipo_contratto="tempo_determinato",
        data_fine_contratto="2026-12-31",
        motivo_termine="Sostituzione temporanea",
        proroghe='[{"numero": 1, "data_fine": "2027-03-31"}]',
        mansione="badante",
        livello="CS",
        convivente=True,
        ore_settimanali=30,
        tipo_orario="full_time",
        part_time_art14=False,
        paga_oraria=None,
        paga_mensile=1200.00,
        paga_pattuita_tipo="mensile",
        data_assunzione="2026-01-01",
        data_cessazione=None,
        stato="attivo"
    )

    rapporto_aggiornato = leggi_rapporto(rapporto_id)
    print("Rapporto aggiornato:", rapporto_aggiornato)

    cessa_rapporto(
        rapporto_id=rapporto_id,
        data_cessazione="2026-11-30"
    )

    rapporto_cessato = leggi_rapporto(rapporto_id)
    print("Rapporto cessato:", rapporto_cessato)

    elimina_rapporto(rapporto_id)
    rapporto_eliminato = leggi_rapporto(rapporto_id)
    print("Rapporto eliminato:", rapporto_eliminato)

    elimina_lavoratore(lavoratore_id)
    elimina_datore(datore_id)
    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_paghe_rapporti_repository()