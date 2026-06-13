from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def genera_pdf_cedolino(dati_cedolino):
    numero = dati_cedolino["numero_cedolino"]

    pdf_path = OUTPUT_DIR / f"cedolino_{numero}.pdf"

    doc = SimpleDocTemplate(str(pdf_path))

    styles = getSampleStyleSheet()

    elementi = []

    elementi.append(
        Paragraph(
            f"Cedolino n. {numero}",
            styles["Title"]
        )
    )

    elementi.append(Spacer(1, 20))

    elementi.append(
        Paragraph(
            f"Lordo: € {dati_cedolino['lordo']}",
            styles["Normal"]
        )
    )

    elementi.append(
        Paragraph(
            f"Contributi lavoratore: € {dati_cedolino['contributi_lavoratore']}",
            styles["Normal"]
        )
    )

    elementi.append(
        Paragraph(
            f"Netto: € {dati_cedolino['netto']}",
            styles["Normal"]
        )
    )

    elementi.append(
        Paragraph(
            f"TFR maturato: € {dati_cedolino['tfr_maturato']}",
            styles["Normal"]
        )
    )

    elementi.append(
        Paragraph(
            f"Tredicesima maturata: € {dati_cedolino['tredicesima_maturata']}",
            styles["Normal"]
        )
    )

    elementi.append(Spacer(1, 20))

    elementi.append(
        Paragraph(
            "Dettaglio competenze",
            styles["Heading2"]
        )
    )

    for voce in dati_cedolino.get("competenze", []):
        elementi.append(
            Paragraph(
                f"{voce['descrizione']} - € {voce['importo']}",
                styles["Normal"]
            )
        )

    elementi.append(Spacer(1, 20))

    elementi.append(
        Paragraph(
            "Dettaglio trattenute",
            styles["Heading2"]
        )
    )

    for voce in dati_cedolino.get("trattenute", []):
        elementi.append(
            Paragraph(
                f"{voce['descrizione']} - € {voce['importo']}",
                styles["Normal"]
            )
        )

    doc.build(elementi)

    return str(pdf_path)