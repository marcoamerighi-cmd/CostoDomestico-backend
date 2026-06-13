from services.genera_pdf_cedolino_service import genera_pdf_cedolino


def test_genera_pdf_cedolino():

    dati_cedolino = {
        "numero_cedolino": "2026-06",

        "lordo": 798.00,
        "contributi_lavoratore": 37.84,
        "netto": 760.16,
        "tfr_maturato": 59.11,
        "tredicesima_maturata": 66.50,

        "competenze": [
            {
                "descrizione": "Lavoro ordinario",
                "importo": 680.00
            },
            {
                "descrizione": "Ferie retribuite",
                "importo": 68.00
            },
            {
                "descrizione": "Una tantum",
                "importo": 50.00
            }
        ],

        "trattenute": [
            {
                "descrizione": "Assenza non retribuita",
                "importo": 34.00
            }
        ]
    }

    pdf_generato = genera_pdf_cedolino(
        dati_cedolino
    )

    print("PDF generato:", pdf_generato)


if __name__ == "__main__":
    test_genera_pdf_cedolino()