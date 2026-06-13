from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_datori_repository import (
    crea_datore,
    leggi_datore,
    leggi_datori_famiglia,
    aggiorna_datore,
    elimina_datore,
)


def test_paghe_datori_repository():
    famiglia_id = crea_famiglia(
        email="test.datore.famiglia@costodomestico.it",
        nome="Famiglia",
        cognome="Test",
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

    print("Datore creato:", datore_id)

    datore = leggi_datore(datore_id)
    print("Datore letto:", datore)

    datori_famiglia = leggi_datori_famiglia(famiglia_id)
    print("Datori famiglia:", datori_famiglia)

    aggiorna_datore(
        datore_id=datore_id,
        nome="Giuseppe",
        cognome="Bianchi",
        codice_fiscale="BNCGPP80A01H501U",
        email="giuseppe.bianchi@test.it",
        telefono="3332222222",
        indirizzo="Via Milano 2",
        comune="Milano",
        provincia="MI",
        cap="20100"
    )

    datore_aggiornato = leggi_datore(datore_id)
    print("Datore aggiornato:", datore_aggiornato)

    elimina_datore(datore_id)

    datore_eliminato = leggi_datore(datore_id)
    print("Datore eliminato:", datore_eliminato)

    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_paghe_datori_repository()