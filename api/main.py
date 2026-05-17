from datetime import date
from typing import List
from pathlib import Path
import os

import stripe

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.stripe_config import STRIPE_SECRET_KEY
from api.email_service import invia_report_tfr_email
from api.stripe_webhook_config import STRIPE_WEBHOOK_SECRET

from tfr.tfr_models import LavoratoreDomestico, ContrattoDomestico
from tfr.tfr_calculator import calcola_tfr_annualita_lorde
from tfr.netto_lordo_service import converti_netto_in_lordo

from database.db import crea_database
from database.lavoratori_repository import salva_lavoratore
from database.contratti_repository import salva_contratto
from database.tfr_repository import salva_calcolo_tfr, leggi_calcoli_tfr
from database.ordini_repository import (
    crea_tabella_ordini,
    salva_ordine,
    leggi_ordini,
    aggiorna_stato_ordine,
    elimina_ordini_test
)

from pdf.report_tfr import genera_pdf_tfr


stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crea_database()
crea_tabella_ordini()

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"
PDF_DIR = BASE_DIR / "pdf_generati"
PDF_DIR.mkdir(exist_ok=True)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

class AnnualitaTFR(BaseModel):
    anno: int
    retribuzione_netta: float
    mesi_utili: int


class RichiestaTFR(BaseModel):
    nome_datore: str = ""
    cognome_datore: str = ""
    email_cliente: str = ""

    nome: str
    cognome: str
    livello: str
    convivente: bool

    data_assunzione: date
    data_cessazione: date

    ore_settimanali: float
    annualita: List[AnnualitaTFR]

    anticipi: float = 0
    variazione_istat_foi: float = 2


class RichiestaCheckoutTFR(BaseModel):
    email_cliente: str = ""
    nome_cliente: str = ""
    cognome_cliente: str = ""


class RichiestaOrdineCostoDomestico(BaseModel):
    email_cliente: str = ""
    nome_cliente: str = ""
    cognome_cliente: str = ""


def elabora_tfr(richiesta: RichiestaTFR) -> dict:
    annualita_lorde = []

    for riga in richiesta.annualita:
        lordo = converti_netto_in_lordo(
            netto_annuo=riga.retribuzione_netta,
            livello=richiesta.livello,
            ore_settimanali=richiesta.ore_settimanali,
            convivente=richiesta.convivente
        )

        annualita_lorde.append({
            "anno": riga.anno,
            "retribuzione_netta": riga.retribuzione_netta,
            "retribuzione_lorda": lordo,
            "mesi_utili": riga.mesi_utili
        })

    risultato_annuale = calcola_tfr_annualita_lorde(
        annualita=annualita_lorde,
        anticipi=richiesta.anticipi,
        variazione_istat_foi=richiesta.variazione_istat_foi
    )

    mesi_totali = sum(riga["mesi_utili"] for riga in annualita_lorde)

    retribuzione_utile_totale = sum(
        riga["retribuzione_utile"]
        for riga in risultato_annuale["dettaglio_anni"]
    )

    return {
        "datore": f"{richiesta.nome_datore} {richiesta.cognome_datore}",
        "email_cliente": richiesta.email_cliente,
        "lavoratore": f"{richiesta.nome} {richiesta.cognome}",
        "livello": richiesta.livello,
        "convivente": richiesta.convivente,
        "mesi_utili": mesi_totali,
        "dettaglio_anni": risultato_annuale["dettaglio_anni"],
        "annualita_elaborate": annualita_lorde,
        "dettaglio_tfr": {
            "mesi_utili": mesi_totali,
            "retribuzione_utile": round(retribuzione_utile_totale, 2),
            "quota_tfr": risultato_annuale["totale_tfr"]
        },
        "coefficiente_rivalutazione": risultato_annuale["coefficiente_rivalutazione"],
        "rivalutazione": risultato_annuale["rivalutazione"],
        "liquidazione": risultato_annuale["liquidazione"]
    }


@app.get("/")
def home():
    return {"messaggio": "API CostoDomestico attiva"}


@app.get("/tfr-tool")
def pagina_tfr_tool():
    return FileResponse(
        path=str(FRONTEND_DIR / "test_tfr.html"),
        media_type="text/html"
    )


@app.get("/checkout-tfr")
def pagina_checkout_tfr():
    return FileResponse(
        path=str(FRONTEND_DIR / "checkout_tfr.html"),
        media_type="text/html"
    )


@app.get("/download-report")
def pagina_download_report(request: Request):
    session_id = request.query_params.get("session_id")

    if session_id:
        aggiorna_stato_ordine(
            sessione_stripe=session_id,
            stato="pagato"
        )

    return FileResponse(
        path=str(FRONTEND_DIR / "download_report.html"),
        media_type="text/html"
    )


@app.get("/storico-ordini-page")
def pagina_storico_ordini():
    return FileResponse(
        path=str(FRONTEND_DIR / "storico_ordini.html"),
        media_type="text/html"
    )


@app.get("/dashboard-tfr")
def pagina_dashboard_tfr():
    return FileResponse(
        path=str(FRONTEND_DIR / "dashboard_tfr.html"),
        media_type="text/html"
    )


@app.get("/dashboard-admin")
def pagina_dashboard_admin(request: Request):

    password = request.query_params.get("password")

    if password != ADMIN_PASSWORD:
        return {
            "errore": "Accesso non autorizzato"
        }

    return FileResponse(
        path=str(FRONTEND_DIR / "dashboard_admin.html"),
        media_type="text/html"
    )


@app.post("/calcola-tfr")
def calcola_tfr(richiesta: RichiestaTFR):
    risultato = elabora_tfr(richiesta)

    lavoratore = LavoratoreDomestico(
        nome=richiesta.nome,
        cognome=richiesta.cognome,
        livello=richiesta.livello,
        convivente=richiesta.convivente,
        data_assunzione=richiesta.data_assunzione,
        data_cessazione=richiesta.data_cessazione
    )

    lordo_medio = sum(
        riga["retribuzione_lorda"]
        for riga in risultato["annualita_elaborate"]
    ) / len(risultato["annualita_elaborate"])

    contratto = ContrattoDomestico(
        paga_lorda_annua=lordo_medio,
        ore_settimanali=richiesta.ore_settimanali
    )

    lavoratore_id = salva_lavoratore(lavoratore)
    salva_contratto(lavoratore_id, contratto)
    salva_calcolo_tfr(lavoratore_id, risultato)

    return risultato


@app.post("/genera-pdf-tfr")
def genera_pdf(richiesta: RichiestaTFR):
    risultato = elabora_tfr(richiesta)

    nome_file = (
        f"report_tfr_{richiesta.nome}_{richiesta.cognome}.pdf"
        .replace(" ", "_")
        .lower()
    )

    percorso_pdf = PDF_DIR / nome_file

    genera_pdf_tfr(
        percorso_file=str(percorso_pdf),
        risultato=risultato
    )

    chiave_email = (
        f"{richiesta.email_cliente}_"
        f"{richiesta.nome}_"
        f"{richiesta.cognome}_"
        f"{richiesta.data_assunzione}_"
        f"{richiesta.data_cessazione}"
    )

    ultima_email = getattr(app.state, "ultima_email_tfr", None)

    if richiesta.email_cliente and ultima_email != chiave_email:
        try:
            invia_report_tfr_email(
                destinatario=richiesta.email_cliente,
                percorso_pdf=str(percorso_pdf),
                nome_file=nome_file
            )

            app.state.ultima_email_tfr = chiave_email

        except Exception as errore:
            print("Errore invio email:", errore)

    return FileResponse(
        path=str(percorso_pdf),
        filename=nome_file,
        media_type="application/pdf"
    )


@app.post("/crea-checkout-tfr")
def crea_checkout_tfr(richiesta: RichiestaCheckoutTFR):
    sessione = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": "Report Professionale TFR - CostoDomestico.it"
                    },
                    "unit_amount": 790
                },
                "quantity": 1
            }
        ],
        success_url=(
            "https://costodomestico-backend.onrender.com/download-report"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url="https://costodomestico-backend.onrender.com/checkout-tfr"
    )

    salva_ordine(
        email_cliente=richiesta.email_cliente,
        nome_cliente=richiesta.nome_cliente,
        cognome_cliente=richiesta.cognome_cliente,
        prodotto="Report Professionale TFR",
        importo=7.90,
        stato="checkout_creato",
        sessione_stripe=sessione.id
    )

    return {"checkout_url": sessione.url}


@app.get("/pagamento-successo")
def pagamento_successo():
    return {"messaggio": "Pagamento completato."}


@app.get("/pagamento-annullato")
def pagamento_annullato():
    return {"messaggio": "Pagamento annullato."}


@app.get("/storico-tfr")
def storico_tfr():
    calcoli = leggi_calcoli_tfr()

    storico = []

    for calcolo in calcoli:
        storico.append({
            "id": calcolo[0],
            "nome": calcolo[1],
            "cognome": calcolo[2],
            "mesi_utili": calcolo[3],
            "retribuzione_utile": calcolo[4],
            "quota_tfr": calcolo[5],
            "rivalutazione": calcolo[6],
            "anticipi": calcolo[7],
            "totale_da_liquidare": calcolo[8],
            "data_calcolo": calcolo[9]
        })

    return storico


@app.get("/storico-ordini")
def storico_ordini():
    ordini = leggi_ordini()

    risultato = []

    for ordine in ordini:
        risultato.append({
            "id": ordine[0],
            "email_cliente": ordine[1],
            "nome_cliente": ordine[2],
            "cognome_cliente": ordine[3],
            "prodotto": ordine[4],
            "importo": ordine[5],
            "stato": ordine[6],
            "sessione_stripe": ordine[7],
            "data_ordine": ordine[8]
        })

    return risultato


@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    try:
        evento = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=STRIPE_WEBHOOK_SECRET
        )

    except Exception as errore:
        return {
            "errore": str(errore)
        }

    if evento["type"] == "checkout.session.completed":
        sessione = evento["data"]["object"]

        aggiorna_stato_ordine(
            sessione_stripe=sessione["id"],
            stato="pagato"
        )

    return {
        "success": True
    }


@app.post("/salva-ordine-costo-domestico")
def salva_ordine_costo_domestico(
    richiesta: RichiestaOrdineCostoDomestico
):
    salva_ordine(
        email_cliente=richiesta.email_cliente,
        nome_cliente=richiesta.nome_cliente,
        cognome_cliente=richiesta.cognome_cliente,
        prodotto="Costo Domestico",
        importo=9.90,
        stato="pagato",
        sessione_stripe="checkout_statico_costo_domestico"
    )

    return {
        "success": True
    }


@app.delete("/elimina-ordini-test")
def elimina_ordini_test_endpoint():
    eliminati = elimina_ordini_test()

    return {
        "success": True,
        "ordini_eliminati": eliminati
    }