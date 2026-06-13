from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def euro(valore):
    return f"€ {float(valore or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def genera_pdf_cedolino_professionale(dati):
    numero = dati["numero_cedolino"]
    pdf_path = OUTPUT_DIR / f"cedolino_professionale_{numero}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elementi = []

    elementi.append(Paragraph("CostoDomestico.it", styles["Title"]))
    elementi.append(Paragraph("Cedolino paga lavoro domestico", styles["Heading2"]))
    elementi.append(Spacer(1, 14))

    tabella_intestazione = Table([
        ["Cedolino n.", numero, "Periodo", dati.get("periodo", "")],
        ["Livello", dati.get("livello", ""), "Mansione", dati.get("mansione", "")],
        ["Ore settimanali", dati.get("ore_settimanali", ""), "Tipo rapporto", dati.get("tipo_contratto", "")]
    ], colWidths=[90, 150, 90, 150])

    tabella_intestazione.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elementi.append(tabella_intestazione)
    elementi.append(Spacer(1, 18))

    elementi.append(Paragraph("Datore di lavoro", styles["Heading3"]))
    tabella_datore = Table([
        ["Nome", dati.get("datore_nome", "")],
        ["Codice fiscale", dati.get("datore_codice_fiscale", "")],
        ["Indirizzo", dati.get("datore_indirizzo", "")]
    ], colWidths=[110, 370])

    tabella_datore.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elementi.append(tabella_datore)
    elementi.append(Spacer(1, 12))

    elementi.append(Paragraph("Lavoratore", styles["Heading3"]))
    tabella_lavoratore = Table([
        ["Nome", dati.get("lavoratore_nome", "")],
        ["Codice fiscale", dati.get("lavoratore_codice_fiscale", "")],
        ["IBAN", dati.get("lavoratore_iban", "")]
    ], colWidths=[110, 370])

    tabella_lavoratore.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elementi.append(tabella_lavoratore)
    elementi.append(Spacer(1, 18))

    elementi.append(Paragraph("Competenze", styles["Heading3"]))

    righe_competenze = [["Descrizione", "Ore/Giorni", "Importo"]]

    for voce in dati.get("competenze", []):
        quantita = ""
        if voce.get("ore"):
            quantita = f"{voce.get('ore')} ore"
        elif voce.get("giorni"):
            quantita = f"{voce.get('giorni')} giorni"

        righe_competenze.append([
            voce.get("descrizione", ""),
            quantita,
            euro(voce.get("importo", 0))
        ])

    tabella_competenze = Table(righe_competenze, colWidths=[280, 100, 100])
    tabella_competenze.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elementi.append(tabella_competenze)
    elementi.append(Spacer(1, 14))

    elementi.append(Paragraph("Trattenute", styles["Heading3"]))

    righe_trattenute = [["Descrizione", "Ore/Giorni", "Importo"]]

    for voce in dati.get("trattenute", []):
        quantita = ""
        if voce.get("ore"):
            quantita = f"{voce.get('ore')} ore"
        elif voce.get("giorni"):
            quantita = f"{voce.get('giorni')} giorni"

        righe_trattenute.append([
            voce.get("descrizione", ""),
            quantita,
            euro(voce.get("importo", 0))
        ])

    tabella_trattenute = Table(righe_trattenute, colWidths=[280, 100, 100])
    tabella_trattenute.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elementi.append(tabella_trattenute)
    elementi.append(Spacer(1, 18))

    tabella_totali = Table([
        ["Lordo", euro(dati.get("lordo", 0))],
        ["Contributi lavoratore", euro(dati.get("contributi_lavoratore", 0))],
        ["Netto da pagare", euro(dati.get("netto", 0))],
        ["TFR maturato mese", euro(dati.get("tfr_maturato", 0))],
        ["Rateo tredicesima", euro(dati.get("tredicesima_maturata", 0))]
    ], colWidths=[300, 180])

    tabella_totali.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
        ("BACKGROUND", (0, 2), (-1, 2), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))

    elementi.append(tabella_totali)
    elementi.append(Spacer(1, 24))

    elementi.append(Paragraph(
        "Nota: il datore di lavoro domestico non è sostituto d'imposta. "
        "Il netto è calcolato sottraendo i soli contributi a carico lavoratore.",
        styles["Normal"]
    ))

    elementi.append(Spacer(1, 30))

    tabella_firme = Table([
        ["Firma datore", "Firma lavoratore"],
        ["________________________", "________________________"]
    ], colWidths=[240, 240])

    tabella_firme.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elementi.append(tabella_firme)

    doc.build(elementi)

    return str(pdf_path)