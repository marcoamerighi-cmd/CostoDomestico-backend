from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_datori_repository import crea_datore, elimina_datore
from database.paghe_lavoratori_repository import crea_lavoratore, elimina_lavoratore
from database.paghe_rapporti_repository import crea_rapporto, elimina_rapporto
from database.paghe_mesi_repository import crea_mese, elimina_mese
from database.paghe_eventi_repository import (
    crea_evento,
    leggi_evento,
    leggi_eventi_mese,
    leggi_eventi_rapporto,
    aggiorna_evento,
    elimina_evento,
)


def test_paghe_eventi_repository():
    famiglia_id = crea_famiglia(
        email="test.eventi.famiglia@costodomestico.it",
        nome="Famiglia",
        cognome="Eventi",
        telefono="3330000000"
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

    evento_id = crea_evento(
        mese_id=mese_id,
        rapporto_id=rapporto_id,
        tipo_evento="lavoro_ordinario",
        data_inizio="2026-06-01",
        data_fine="2026-06-30",
        ore=80,
        giorni=20,
        importo=680.00,
        note="Ore ordinarie mese giugno"
    )

    print("Evento creato:", evento_id)

    evento = leggi_evento(evento_id)
    print("Evento letto:", evento)

    evento_ferie_id = crea_evento(
        mese_id=mese_id,
        rapporto_id=rapporto_id,
        tipo_evento="ferie",
        data_inizio="2026-06-10",
        data_fine="2026-06-11",
        ore=8,
        giorni=2,
        importo=68.00,
        note="Ferie retribuite"
    )

    evento_malattia_id = crea_evento(
        mese_id=mese_id,
        rapporto_id=rapporto_id,
        tipo_evento="malattia",
        data_inizio="2026-06-20",
        data_fine="2026-06-21",
        ore=8,
        giorni=2,
        importo=0,
        note="Malattia da gestire nel cedolino"
    )

    eventi_mese = leggi_eventi_mese(mese_id)
    print("Eventi mese:", eventi_mese)

    eventi_rapporto = leggi_eventi_rapporto(rapporto_id)
    print("Eventi rapporto:", eventi_rapporto)

    aggiorna_evento(
        evento_id=evento_id,
        tipo_evento="lavoro_ordinario",
        data_inizio="2026-06-01",
        data_fine="2026-06-30",
        ore=82,
        giorni=21,
        importo=697.00,
        note="Ore ordinarie aggiornate"
    )

    evento_aggiornato = leggi_evento(evento_id)
    print("Evento aggiornato:", evento_aggiornato)

    elimina_evento(evento_id)
    elimina_evento(evento_ferie_id)
    elimina_evento(evento_malattia_id)

    evento_eliminato = leggi_evento(evento_id)
    print("Evento eliminato:", evento_eliminato)

    elimina_mese(mese_id)
    elimina_rapporto(rapporto_id)
    elimina_lavoratore(lavoratore_id)
    elimina_datore(datore_id)
    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_paghe_eventi_repository()