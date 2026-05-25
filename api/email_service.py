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
        "subject": "Il tuo accesso personale a CostoDomestico.it",
        "html": f"""
        <div style="
            font-family:Arial,sans-serif;
            max-width:650px;
            margin:auto;
            padding:20px;
            color:#374151;
        ">

            <div style="
                text-align:center;
                margin-bottom:25px;
            ">
                <h1 style="
                    color:#0b4dbb;
                    margin:0;
                ">
                    CostoDomestico.it
                </h1>
            </div>

            <p>Ciao,</p>

            <p>
                hai richiesto l'accesso alla tua area personale su
                <strong>CostoDomestico.it</strong>.
            </p>

            <p>
                Da qui potrai consultare:
            </p>

            <ul>
                <li>Report acquistati</li>
                <li>Storico calcoli</li>
                <li>PDF generati</li>
            </ul>

            <div style="
                text-align:center;
                margin:35px 0;
            ">

                <a
                    href="{magic_link}"
                    style="
                        display:inline-block;
                        padding:16px 28px;
                        background:#16a34a;
                        color:white;
                        text-decoration:none;
                        border-radius:10px;
                        font-weight:bold;
                    "
                >
                    Accedi alla mia area personale
                </a>

            </div>

            <p style="
                font-size:13px;
                color:#6b7280;
            ">
                Per motivi di sicurezza il link sarà valido per 30 minuti.
            </p>

            <hr>

            <p style="
                font-size:12px;
                color:#9ca3af;
            ">
                Se non hai richiesto questo accesso puoi ignorare questa email.
            </p>

        </div>
        """
    })