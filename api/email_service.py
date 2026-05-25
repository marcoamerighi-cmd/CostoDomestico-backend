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
            line-height:1.5;
        ">

            <h2 style="color:#0b4dbb;">
                CostoDomestico.it
            </h2>

            <p>Ciao,</p>

            <p>
                abbiamo ricevuto una richiesta di accesso alla tua area personale.
            </p>

            <p>
                Nell'area cliente puoi consultare i report acquistati,
                scaricare nuovamente i PDF e visualizzare lo storico dei calcoli.
            </p>

            <p>
                Puoi accedere usando il pulsante qui sotto:
            </p>

            <p style="text-align:center; margin:30px 0;">
                <a
                    href="{magic_link}"
                    style="
                        display:inline-block;
                        padding:14px 24px;
                        background:#16a34a;
                        color:white;
                        text-decoration:none;
                        border-radius:8px;
                        font-weight:bold;
                    "
                >
                    Accedi alla mia area cliente
                </a>
            </p>

            <p style="font-size:13px; color:#666;">
                Se il pulsante non funziona, copia e incolla questo link nel browser:
            </p>

            <p style="
                font-size:12px;
                word-break:break-all;
                color:#2563eb;
            ">
                {magic_link}
            </p>

            <p style="font-size:13px; color:#6b7280;">
                Il link resta valido per 30 minuti.
            </p>

            <p style="font-size:13px; color:#6b7280;">
                Se non hai richiesto tu questo accesso, puoi ignorare questa email.
            </p>

            <hr>

            <p style="font-size:12px; color:#9ca3af;">
                Email automatica inviata da CostoDomestico.it.
            </p>

        </div>
        """
    })