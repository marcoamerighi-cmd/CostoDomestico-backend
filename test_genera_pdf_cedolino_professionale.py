from services.genera_pdf_cedolino_professionale import (
    genera_pdf_cedolino_professionale
)


def test_genera_pdf_cedolino_professionale():
    dati = {
        "numero_cedolino": "2026-06",
        "periodo": "Giugno 2026",
        "livello": "B",
        "mansione": "Colf",
        "ore_settimanali": 20,
        "tipo_contratto": "Tempo indeterminato",

        "datore_nome": "Mario Rossi",
        "datore_codice_fiscale": "RSSMRA80A01H501U",
        "datore_indirizzo": "Via Roma 1, 00100 Roma RM",

        "lavoratore_nome": "Anna Verdi",
        "lavoratore_codice_fiscale": "VRDNNA80A41H501U",
        "lavoratore_iban": "IT60X0542811101000000123456",

        "lordo": 798.00,
        "contributi_lavoratore": 37.84,
        "netto": 760.16,
        "tfr_maturato": 59.11,
        "tredicesima_maturata": 66.50,

        "competenze": [
            {
                "descrizione": "Lavoro ordinario",
                "ore": 80,
                "giorni": 20,
                "importo": 680.00
            },
            {
                "descrizione": "Ferie retribuite",
                "ore": 8,
                "giorni": 2,
                "importo": 68.00
            },
            {
                "descrizione": "Una tantum",
                "ore": 0,
                "giorni": 0,
                "importo": 50.00
            }
        ],

        "trattenute": [
            {
                "descrizione": "Assenza non retribuita",
                "ore": 4,
                "giorni": 1,
                "importo": 34.00
            }
        ]
    }

    pdf = genera_pdf_cedolino_professionale(dati)

    print("PDF professionale generato:", pdf)


if __name__ == "__main__":
    test_genera_pdf_cedolino_professionale()