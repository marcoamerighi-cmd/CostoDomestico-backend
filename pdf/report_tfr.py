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

    titolo = Paragraph(
        "<b>Report Professionale TFR</b>",
        styles["Title"]
    )

    elementi.append(titolo)

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

    elementi.append(
        Paragraph(info, styles["BodyText"])
    )

    elementi.append(Spacer(1, 20))

    elementi.append(
        HRFlowable(width="100%")
    )

    elementi.append(Spacer(1, 20))

    tabella_dati = [
        [
            "Anno",
            "Mesi utili",
            "Lordo stimato",
            "Retribuzione utile",
            "Quota TFR"
        ]
    ]

    for riga in risultato["dettaglio_anni"]:

        tabella_dati.append([
            str(riga["anno"]),
            str(riga["mesi_utili"]),
            f"€ {riga['retribuzione_lorda']}",
            f"€ {riga['retribuzione_utile']}",
            f"€ {riga['quota_tfr']}"
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

    riepilogo = f"""
    <b>Totale TFR maturato:</b>
    € {risultato['dettaglio_tfr']['quota_tfr']}<br/><br/>

    <b>Rivalutazione:</b>
    € {risultato['rivalutazione']}<br/><br/>

    <b>Anticipi:</b>
    € {risultato['liquidazione']['anticipi']}<br/><br/>

    <b>Totale da liquidare:</b>
    € {risultato['liquidazione']['totale_da_liquidare']}
    """

    elementi.append(
        Paragraph(riepilogo, styles["BodyText"])
    )

    elementi.append(Spacer(1, 30))

    disclaimer = """
    Calcolo elaborato sulla base dei dati inseriti
    dall'utente. Il presente documento ha valore
    informativo e non sostituisce il parere di un
    professionista abilitato.
    """

    elementi.append(
        Paragraph(disclaimer, styles["Italic"])
    )

    elementi.append(Spacer(1, 20))

    footer = Paragraph(
        "<b>CostoDomestico.it</b>",
        styles["BodyText"]
    )

    elementi.append(footer)

    doc.build(elementi)