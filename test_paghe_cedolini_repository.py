from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_datori_repository import crea_datore, elimina_datore
from database.paghe_lavoratori_repository import crea_lavoratore, elimina_lavoratore
from database.paghe_rapporti_repository import crea_rapporto, elimina_rapporto
from database.paghe_mesi_repository import crea_mese, elimina_mese
from database.paghe_cedolini_repository import (
    crea_cedolino,
    leggi_cedolino,
    leggi_cedolini_mese,
    leggi_cedolini_rapporto,
    aggiorna_cedolino,
    marca_cedolino_definitivo,
    elimina_cedolino,
)


def test_paghe_cedolini_repository():
    famiglia_id = crea_famiglia(
        email="test.cedolini.famiglia@costodomestico.it",
        nome="Famiglia",
        cognome="Cedolini"
    )

    datore_id = crea_datore(
        famiglia_id=famiglia_id,
        nome="Mario",
        cognome="Rossi"
    )

    lavoratore_id = crea_lavoratore(
        famiglia_id=famiglia_id,
        nome="Anna",
        cognome="Verdi"
    )

    rapporto_id = crea_rapporto(
        famiglia_id=famiglia_id,
        datore_id=datore_id,
        lavoratore_id=lavoratore_id,
        mansione="colf",
        livello="B",
        convivente=False,
        ore_settimanali=20,
        tipo_orario="part_time",
        paga_oraria=8.50,
        paga_pattuita_tipo="oraria",
        data_assunzione="2026-01-01"
    )

    mese_id = crea_mese(
        rapporto_id=rapporto_id,
        anno=2026,
        mese=6
    )

    cedolino_id = crea_cedolino(
        mese_id=mese_id,
        rapporto_id=rapporto_id,
        numero_cedolino="2026-06-001",
        lordo=680.00,
        contributi_lavoratore=20.00,
        netto=660.00,
        tfr_maturato=50.37,
        tredicesima_maturata=56.67,
        dati_calcolo={
            "ore_ordinarie": 80,
            "paga_oraria": 8.50,
            "note": "Cedolino test giugno 2026"
        },
        stato="bozza"
    )

    print("Cedolino creato:", cedolino_id)

    cedolino = leggi_cedolino(cedolino_id)
    print("Cedolino letto:", cedolino)

    cedolini_mese = leggi_cedolini_mese(mese_id)
    print("Cedolini mese:", cedolini_mese)

    cedolini_rapporto = leggi_cedolini_rapporto(rapporto_id)
    print("Cedolini rapporto:", cedolini_rapporto)

    aggiorna_cedolino(
        cedolino_id=cedolino_id,
        numero_cedolino="2026-06-001",
        lordo=700.00,
        contributi_lavoratore=21.00,
        netto=679.00,
        tfr_maturato=51.85,
        tredicesima_maturata=58.33,
        dati_calcolo={
            "ore_ordinarie": 82,
            "paga_oraria": 8.50,
            "note": "Cedolino aggiornato"
        },
        pdf_url="",
        stato="bozza"
    )

    cedolino_aggiornato = leggi_cedolino(cedolino_id)
    print("Cedolino aggiornato:", cedolino_aggiornato)

    marca_cedolino_definitivo(
        cedolino_id=cedolino_id,
        pdf_url="/documenti/cedolini/test-cedolino.pdf"
    )

    cedolino_definitivo = leggi_cedolino(cedolino_id)
    print("Cedolino definitivo:", cedolino_definitivo)

    elimina_cedolino(cedolino_id)
    cedolino_eliminato = leggi_cedolino(cedolino_id)
    print("Cedolino eliminato:", cedolino_eliminato)

    elimina_mese(mese_id)
    elimina_rapporto(rapporto_id)
    elimina_lavoratore(lavoratore_id)
    elimina_datore(datore_id)
    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_paghe_cedolini_repository()