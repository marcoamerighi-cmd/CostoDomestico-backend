from dotenv import load_dotenv

load_dotenv(".env")

from database.paghe_famiglie_repository import crea_famiglia, elimina_famiglia
from database.paghe_datori_repository import crea_datore, elimina_datore
from database.paghe_lavoratori_repository import crea_lavoratore, elimina_lavoratore
from database.paghe_rapporti_repository import crea_rapporto, elimina_rapporto
from database.paghe_mesi_repository import crea_mese, elimina_mese
from database.paghe_eventi_repository import crea_evento, elimina_evento
from database.paghe_cedolini_repository import leggi_cedolino, elimina_cedolino

from services.calcolo_cedolino_service import calcola_cedolino_da_eventi
from services.cedolino_builder_service import genera_pdf_professionale_da_cedolino


def test_cedolino_builder_service():
    famiglia_id = crea_famiglia(
        email="test.builder.cedolino@costodomestico.it",
        nome="Famiglia",
        cognome="Builder"
    )

    datore_id = crea_datore(
        famiglia_id=famiglia_id,
        nome="Mario",
        cognome="Rossi",
        codice_fiscale="RSSMRA80A01H501U",
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
        note="Ore ordinarie giugno"
    )

    risultato = calcola_cedolino_da_eventi(
        mese_id=mese_id,
        rapporto_id=rapporto_id,
        anno=2026,
        mese=6
    )

    cedolino_id = risultato["cedolino_id"]

    print("Cedolino creato:", cedolino_id)

    pdf_path = genera_pdf_professionale_da_cedolino(cedolino_id)

    print("PDF professionale generato:", pdf_path)

    cedolino_finale = leggi_cedolino(cedolino_id)

    print("Cedolino finale:", cedolino_finale)

    elimina_cedolino(cedolino_id)
    elimina_evento(evento_id)
    elimina_mese(mese_id)
    elimina_rapporto(rapporto_id)
    elimina_lavoratore(lavoratore_id)
    elimina_datore(datore_id)
    elimina_famiglia(famiglia_id)


if __name__ == "__main__":
    test_cedolino_builder_service()