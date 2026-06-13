from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_lavoratori_repository import (
    crea_lavoratore,
    leggi_lavoratore,
    leggi_lavoratori_famiglia,
    aggiorna_lavoratore,
    elimina_lavoratore,
)


def test_paghe_lavoratori_repository():
    famiglia_id = crea_famiglia(
        email="test.lavoratore.famiglia@costodomestico.it",
        nome="Famiglia",
        cognome="Lavoratore",
        telefono="3330000000"
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
        telefono="3331111111",
        indirizzo="Via Roma 10",
        iban="IT60X0542811101000000123456"
    )

    print("Lavoratore creato:", lavoratore_id)

    lavoratore = leggi_lavoratore(lavoratore_id)
    print("Lavoratore letto:", lavoratore)

    lavoratori_famiglia = leggi_lavoratori_famiglia(famiglia_id)
    print("Lavoratori famiglia:", lavoratori_famiglia)

    aggiorna_lavoratore(
        lavoratore_id=lavoratore_id,
        nome="Maria",
        cognome="Bianchi",
        codice_fiscale="BNCMRA80A41H501U",
        data_nascita="1980-02-02",
        luogo_nascita="Milano",
        nazionalita="Italiana",
        email="maria.bianchi@test.it",
        telefono="3332222222",
        indirizzo="Via Milano 20",
        iban="IT60X0542811101000000654321"
    )

    lavoratore_aggiornato = leggi_lavoratore(lavoratore_id)
    print("Lavoratore aggiornato:", lavoratore_aggiornato)

    elimina_lavoratore(lavoratore_id)

    lavoratore_eliminato = leggi_lavoratore(lavoratore_id)
    print("Lavoratore eliminato:", lavoratore_eliminato)

    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_paghe_lavoratori_repository()