from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import (
    crea_famiglia,
    leggi_famiglia,
    leggi_famiglia_per_email,
    aggiorna_famiglia,
    elimina_famiglia,
)


def test_paghe_famiglie_repository():
    email_test = "test.paghe.famiglia@costodomestico.it"

    famiglia_id = crea_famiglia(
        email=email_test,
        nome="Mario",
        cognome="Rossi",
        telefono="3331234567"
    )

    print("Famiglia creata:", famiglia_id)

    famiglia = leggi_famiglia(famiglia_id)
    print("Famiglia letta:", famiglia)

    famiglia_email = leggi_famiglia_per_email(email_test)
    print("Famiglia per email:", famiglia_email)

    aggiorna_famiglia(
        famiglia_id=famiglia_id,
        nome="Marco",
        cognome="Bianchi",
        telefono="3339999999"
    )

    famiglia_aggiornata = leggi_famiglia(famiglia_id)
    print("Famiglia aggiornata:", famiglia_aggiornata)

    elimina_famiglia(famiglia_id)

    famiglia_eliminata = leggi_famiglia(famiglia_id)
    print("Famiglia eliminata:", famiglia_eliminata)


if __name__ == "__main__":
    test_paghe_famiglie_repository()