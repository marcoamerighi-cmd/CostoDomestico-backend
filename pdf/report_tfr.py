from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

from reportlab.platypus.flowables import HRFlowable


def euro(valore) -> str:
    return f"€ {float(valore):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def genera_pdf_tfr(
    percorso_file: str,
    risultato: dict
):

    doc = SimpleDocTemplate(
        percorso_file,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elementi = []

    elementi.append(
        Paragraph("<b>Report Professionale TFR</b>", styles["Title"])
    )

    elementi.append(Spacer(1, 20))

    datore = risultato.get("datore", "")
    lavoratore = risultato.get("lavoratore", "")

    info = f"""
    <b>Datore di lavoro:</b> {datore}<br/>
    <b>Lavoratore:</b> {lavoratore}<br/>
    <b>Livello:</b> {risultato.get('livello')}<br/>
    <b>Tipo rapporto:</b>
    {"Convivente" if risultato.get("convivente") else "Non convivente"}
    """

    elementi.append(Paragraph(info, styles["BodyText"]))
    elementi.append(Spacer(1, 20))
    elementi.append(HRFlowable(width="100%"))
    elementi.append(Spacer(1, 20))

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
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3c88")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
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
            "Retribuzione utile T.F.R.",
            "Rivalutazione",
            "T.F.R. accantonato",
            "Anticipi",
            "T.F.R. totale"
        ]
    ]

    totale_progressivo = 0
    rivalutazione_totale = risultato.get("rivalutazione", 0)
    dettaglio_anni = risultato["dettaglio_anni"]

    for indice, riga in enumerate(dettaglio_anni):
        quota = float(riga["quota_tfr"])

        if indice == 0:
            rivalutazione_anno = 0
        else:
            rivalutazione_anno = float(
                riga.get("rivalutazione", 0)
            )

            totale_progressivo = float(
                riga.get(
                    "totale_progressivo",
                    totale_progressivo + quota + rivalutazione_anno
                )
            )

        riepilogo_dati.append([
            str(riga["anno"]),
            euro(riga["retribuzione_utile"]),
            euro(rivalutazione_anno),
            euro(quota),
            euro(0),
            euro(totale_progressivo)
        ])

    riepilogo_tabella = Table(riepilogo_dati)

    riepilogo_tabella.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3c88")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
        ])
    )

    elementi.append(riepilogo_tabella)
    elementi.append(Spacer(1, 25))

    riepilogo_finale = f"""
    <b>T.F.R. già erogato:</b> {euro(0)}<br/>
    <b>T.F.R. totale:</b> {euro(risultato['liquidazione']['totale_da_liquidare'])}
    """

    elementi.append(Paragraph(riepilogo_finale, styles["BodyText"]))
    elementi.append(Spacer(1, 30))

    disclaimer = """
    Calcolo elaborato sulla base dei dati inseriti dall'utente.
    Il presente documento ha valore informativo e non sostituisce
    il parere di un professionista abilitato.
    """

    elementi.append(Paragraph(disclaimer, styles["Italic"]))
    elementi.append(Spacer(1, 20))

    elementi.append(
        Paragraph("<b>CostoDomestico.it</b>", styles["BodyText"])
    )

    doc.build(elementi)