from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_RIGHT

from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import ParagraphStyle


def euro(valore) -> str:
    return (
        f"€ {float(valore):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def genera_pdf_tfr(
    percorso_file: str,
    risultato: dict
):

    doc = SimpleDocTemplate(
        percorso_file,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    style_left = ParagraphStyle(
        "left",
        parent=styles["BodyText"],
        alignment=TA_LEFT
    )

    style_right = ParagraphStyle(
        "right",
        parent=styles["BodyText"],
        alignment=TA_RIGHT
    )

    elementi = []

    data_generazione = datetime.now().strftime("%d/%m/%Y")

    header_table = Table(
        [[
            Paragraph(
                "<font color='white'><b>CostoDomestico.it</b></font>",
                styles["Title"]
            ),
            Paragraph(
                f"<font color='white'>Generato il {data_generazione}</font>",
                style_right
            )
        ]],
        colWidths=[350, 150]
    )

    header_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2962ff")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 18),
            ("RIGHTPADDING", (0, 0), (-1, -1), 18),
            ("TOPPADDING", (0, 0), (-1, -1), 18),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 18)
        ])
    )

    elementi.append(header_table)
    elementi.append(Spacer(1, 25))

    titolo = Paragraph(
        "<font size='22'><b>Calcolo T.F.R. lavoro domestico</b></font>",
        styles["Heading1"]
    )

    elementi.append(titolo)

    sottotitolo = Paragraph(
        "Simulazione indicativa elaborata sulla base dei dati inseriti.",
        styles["BodyText"]
    )

    elementi.append(sottotitolo)
    elementi.append(Spacer(1, 25))

    datore = risultato.get("datore", "")
    lavoratore = risultato.get("lavoratore", "")

    box_info = Table([
        [
            Paragraph(
                f"""
                <b>Datore di lavoro:</b> {datore}<br/>
                <b>Lavoratore:</b> {lavoratore}
                """,
                style_left
            ),

            Paragraph(
                f"""
                <b>Livello:</b> {risultato.get('livello')}<br/>
                <b>Rapporto:</b>
                {"Convivente" if risultato.get("convivente") else "Non convivente"}
                """,
                style_left
            )
        ]
    ], colWidths=[250, 250])

    box_info.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
            ("ROUNDEDCORNERS", [10, 10, 10, 10]),
            ("LEFTPADDING", (0, 0), (-1, -1), 15),
            ("RIGHTPADDING", (0, 0), (-1, -1), 15),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12)
        ])
    )

    elementi.append(box_info)
    elementi.append(Spacer(1, 25))

    elementi.append(
        Paragraph("<b>Dettaglio annualità</b>", styles["Heading2"])
    )

    tabella_dati = [
        [
            "Anno",
            "Mesi utili",
            "Lordo",
            "Retribuzione utile",
            "Quota TFR"
        ]
    ]

    for riga in risultato["dettaglio_anni"]:
        tabella_dati.append([
            str(riga["anno"]),
            str(riga["mesi_utili"]),
            euro(riga["retribuzione_lorda"]),
            euro(riga["retribuzione_utile"]),
            euro(riga["quota_tfr"])
        ])

    tabella = Table(tabella_dati)

    tabella.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2962ff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#d1d5db")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
        ])
    )

    elementi.append(tabella)
    elementi.append(Spacer(1, 30))

    elementi.append(
        Paragraph("<b>Riepilogo del T.F.R.</b>", styles["Heading2"])
    )

    riepilogo_dati = [
        [
            "Anno",
            "Retribuzione utile",
            "Rivalutazione",
            "Quota TFR",
            "Totale progressivo"
        ]
    ]

    for riga in risultato["dettaglio_anni"]:

        riepilogo_dati.append([
            str(riga["anno"]),
            euro(riga["retribuzione_utile"]),
            euro(riga.get("rivalutazione", 0)),
            euro(riga["quota_tfr"]),
            euro(riga.get("totale_progressivo", 0))
        ])

    riepilogo_tabella = Table(riepilogo_dati)

    riepilogo_tabella.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2962ff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#d1d5db")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
        ])
    )

    elementi.append(riepilogo_tabella)
    elementi.append(Spacer(1, 30))

    totale_box = Table([
        [
            Paragraph(
                f"""
                <font size='13'>
                <b>T.F.R. totale da liquidare:</b><br/><br/>
                <font size='18'>
                <b>{euro(risultato['liquidazione']['totale_da_liquidare'])}</b>
                </font>
                </font>
                """,
                styles["BodyText"]
            )
        ]
    ], colWidths=[500])

    totale_box.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#c7d2fe")),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ("TOPPADDING", (0, 0), (-1, -1), 18),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 18)
        ])
    )

    elementi.append(totale_box)
    elementi.append(Spacer(1, 30))

    disclaimer = Paragraph(
        """
        Il presente calcolo ha finalità informativa e deve essere
        verificato sul caso specifico da un professionista abilitato.
        """,
        styles["Italic"]
    )

    elementi.append(disclaimer)
    elementi.append(Spacer(1, 50))

    footer = Table([
        [
            Paragraph(
                "Report generato da CostoDomestico.it",
                style_left
            ),

            Paragraph(
                "Simulatore informativo per lavoro domestico",
                style_right
            )
        ]
    ], colWidths=[250, 250])

    footer.setStyle(
        TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 1, colors.HexColor("#d1d5db")),
            ("TOPPADDING", (0, 0), (-1, -1), 12)
        ])
    )

    elementi.append(footer)

    doc.build(elementi)