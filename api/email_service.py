import base64
import resend

from api.resend_config import (
    RESEND_API_KEY,
    EMAIL_MITTENTE
)

resend.api_key = RESEND_API_KEY


def invia_report_tfr_email(
    destinatario: str,
    percorso_pdf: str,
    nome_file: str
):
    with open(percorso_pdf, "rb") as file:
        pdf_base64 = base64.b64encode(
            file.read()
        ).decode("utf-8")

    resend.Emails.send({
        "from": EMAIL_MITTENTE,
        "to": destinatario,
        "subject": "Il tuo report TFR - CostoDomestico.it",
        "html": """
            <h2>Report TFR CostoDomestico.it</h2>
            <p>In allegato trovi il report professionale TFR richiesto.</p>
            <p>Grazie per aver utilizzato CostoDomestico.it.</p>
        """,
        "attachments": [
            {
                "filename": nome_file,
                "content": pdf_base64
            }
        ]
    })


def invia_report_costo_domestico_email(
    destinatario: str,
    percorso_pdf: str,
    nome_file: str
):
    with open(percorso_pdf, "rb") as file:
        pdf_base64 = base64.b64encode(
            file.read()
        ).decode("utf-8")

    resend.Emails.send({
        "from": EMAIL_MITTENTE,
        "to": destinatario,
        "subject": "Il tuo report Costo Domestico - CostoDomestico.it",
        "html": """
            <h2>Report CostoDomestico.it</h2>
            <p>In allegato trovi il report professionale richiesto.</p>
            <p>Grazie per aver utilizzato CostoDomestico.it.</p>
        """,
        "attachments": [
            {
                "filename": nome_file,
                "content": pdf_base64
            }
        ]
    })