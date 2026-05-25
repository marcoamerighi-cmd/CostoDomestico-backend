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

def invia_magic_link_email(
    destinatario: str,
    magic_link: str
):
    resend.Emails.send({
        "from": EMAIL_MITTENTE,
        "to": destinatario,
        "subject": "Accedi alla tua Area Cliente - CostoDomestico.it",
        "html": f"""
        <div style="
            font-family:Arial,sans-serif;
            max-width:600px;
            margin:auto;
            padding:20px;
        ">

        <h2 style="color:#0b4dbb;">
            CostoDomestico.it
        </h2>

        <p>
            Hai richiesto un accesso alla tua Area Cliente.
        </p>

        <p>
            Premi il pulsante qui sotto:
        </p>

        <a
            href="{magic_link}"
            style="
                display:inline-block;
                padding:14px 24px;
                background:#16a34a;
                color:white;
                text-decoration:none;
                border-radius:10px;
                font-weight:bold;
            "
        >
            Accedi alla mia area
        </a>

        <p style="
            margin-top:25px;
            font-size:13px;
            color:#666;
        ">
            Il link scade dopo 30 minuti.
        </p>

        </div>
        """
    })