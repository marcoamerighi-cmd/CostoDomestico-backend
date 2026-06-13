from database.paghe_cedolini_repository import (
    leggi_cedolino,
    marca_cedolino_definitivo
)
from database.paghe_rapporti_repository import leggi_rapporto
from database.paghe_datori_repository import leggi_datore
from database.paghe_lavoratori_repository import leggi_lavoratore

from services.genera_pdf_cedolino_professionale import (
    genera_pdf_cedolino_professionale
)


def costruisci_dati_pdf_da_cedolino(cedolino_id):
    cedolino = leggi_cedolino(cedolino_id)

    if not cedolino:
        raise ValueError("Cedolino non trovato")

    rapporto_id = cedolino[2]
    rapporto = leggi_rapporto(rapporto_id)

    if not rapporto:
        raise ValueError("Rapporto non trovato")

    datore_id = rapporto[2]
    lavoratore_id = rapporto[3]

    datore = leggi_datore(datore_id)
    lavoratore = leggi_lavoratore(lavoratore_id)

    if not datore:
        raise ValueError("Datore non trovato")

    if not lavoratore:
        raise ValueError("Lavoratore non trovato")

    dati_calcolo = cedolino[9] or {}

    dati_pdf = {
        "numero_cedolino": cedolino[3],
        "periodo": cedolino[3],

        "livello": rapporto[9],
        "mansione": rapporto[8],
        "ore_settimanali": rapporto[11],
        "tipo_contratto": rapporto[4],

        "datore_nome": f"{datore[2]} {datore[3]}",
        "datore_codice_fiscale": datore[4] or "",
        "datore_indirizzo": f"{datore[7] or ''}, {datore[10] or ''} {datore[8] or ''} {datore[9] or ''}".strip(),

        "lavoratore_nome": f"{lavoratore[2]} {lavoratore[3]}",
        "lavoratore_codice_fiscale": lavoratore[4] or "",
        "lavoratore_iban": lavoratore[11] or "",

        "lordo": cedolino[4],
        "contributi_lavoratore": cedolino[5],
        "netto": cedolino[6],
        "tfr_maturato": cedolino[7],
        "tredicesima_maturata": cedolino[8],

        "competenze": dati_calcolo.get("competenze", []),
        "trattenute": dati_calcolo.get("trattenute", [])
    }

    return dati_pdf


def genera_pdf_professionale_da_cedolino(cedolino_id):
    dati_pdf = costruisci_dati_pdf_da_cedolino(cedolino_id)

    pdf_path = genera_pdf_cedolino_professionale(dati_pdf)

    marca_cedolino_definitivo(
        cedolino_id=cedolino_id,
        pdf_url=pdf_path
    )

    return pdf_path