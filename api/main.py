from datetime import date
from typing import List
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
import json

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension
)

from google.oauth2 import service_account

import stripe

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.stripe_config import STRIPE_SECRET_KEY
from api.email_service import (
    invia_report_tfr_email,
    invia_report_costo_domestico_email,
    invia_magic_link_email,
    invia_email_generica
)
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
    aggiorna_pdf_ordine,
    get_connessione,
    elimina_ordini_test,
    crea_tabella_funnel,
    salva_evento_funnel,
    leggi_eventi_funnel,
    reset_dashboard_test,
    salva_storico_calcolo,
    leggi_storico_calcoli,
    elimina_storico_calcoli,
    statistiche_conversione,
    statistiche_ordini,
    leggi_ordini_cliente,
)
from database.clienti_repository import (
    crea_tabella_clienti,
    salva_o_aggiorna_cliente,
    leggi_clienti,
    leggi_email_clienti,
    conta_clienti
)

from database.email_repository import (
    crea_tabella_email,
    salva_email_admin,
    leggi_email_admin,
    leggi_messaggi_clienti,
    segna_messaggio_letto
)

from pdf.report_tfr import genera_pdf_tfr


stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()

crea_tabella_funnel()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crea_database()
crea_tabella_ordini()
crea_tabella_clienti()
crea_tabella_email()

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount(
    "/js",
    StaticFiles(directory=str(FRONTEND_DIR / "js")),
    name="js"
)
PDF_DIR = BASE_DIR / "pdf_generati"
PDF_DIR.mkdir(exist_ok=True)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_TOKEN = "admin_sessione_ok"

STRIPE_PRICE_ID_TFR = os.getenv("STRIPE_PRICE_ID_TFR", "")


class AnnualitaTFR(BaseModel):
    anno: int
    retribuzione_netta: float
    mesi_utili: int


class RichiestaTFR(BaseModel):
    nome_datore: str = ""
    cognome_datore: str = ""
    email_cliente: str = ""
    session_id: str = ""

    nome: str
    cognome: str
    livello: str
    convivente: bool
    tempo_determinato: bool = False

    data_assunzione: date
    data_cessazione: date

    ore_settimanali: float
    annualita: List[AnnualitaTFR]

    anticipi: float = 0
    variazione_istat_foi: float = 2
    invia_email: bool = False


class RichiestaCheckoutTFR(BaseModel):
    email_cliente: str = ""
    nome_cliente: str = ""
    cognome_cliente: str = ""
    nome_completo_cliente: str = ""

    # Campi opzionali che possono arrivare dalla pagina TFR.
    # Non sono obbligatori per Stripe, ma evitano errori se il frontend li invia.
    nome_datore: str = ""
    cognome_datore: str = ""
    dati_calcolo: dict | None = None


class RichiestaOrdineCostoDomestico(BaseModel):
    email_cliente: str = ""
    nome_cliente: str = ""
    cognome_cliente: str = ""


class RichiestaLoginAdmin(BaseModel):
    password: str


class RichiestaLoginCliente(BaseModel):
    email_cliente: str


class RichiestaMagicLink(BaseModel):
    email: str

def elabora_tfr(richiesta: RichiestaTFR) -> dict:
    annualita_lorde = []

    for riga in richiesta.annualita:
        lordo = converti_netto_in_lordo(
            netto_annuo=riga.retribuzione_netta,
            anno=riga.anno,
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
        "tempo_determinato": richiesta.tempo_determinato,
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


def normalizza_email(email: str) -> str:
    return (email or "").strip().lower()


def aggiorna_pdf_ultimo_ordine_email(email_cliente: str, pdf_file: str):
    email_pulita = normalizza_email(email_cliente)

    if not email_pulita or not pdf_file:
        return False

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ordini
        SET pdf_file = %s
        WHERE id = (
            SELECT id
            FROM ordini
            WHERE LOWER(TRIM(email_cliente)) = %s
            AND prodotto = 'Costo Domestico'
            ORDER BY id DESC
            LIMIT 1
        )
    """, (
        pdf_file,
        email_pulita
    ))

    aggiornato = cursor.rowcount > 0

    conn.commit()
    cursor.close()
    conn.close()

    return aggiornato


@app.get("/")
def home():
    return FileResponse(
        path=str(FRONTEND_DIR / "index.html"),
        media_type="text/html"
    )


@app.get("/statistiche-conversione")
def get_statistiche_conversione():

    return statistiche_conversione()


@app.get("/{nome_file}.html")
def pagina_html(nome_file: str):

    percorso = FRONTEND_DIR / f"{nome_file}.html"

    if not percorso.exists():
        raise HTTPException(
            status_code=404,
            detail="Pagina non trovata"
        )

    return FileResponse(
        path=str(percorso),
        media_type="text/html"
    )


@app.get("/checkout-tfr")
def pagina_checkout_tfr():
    return FileResponse(
        path=str(FRONTEND_DIR / "checkout_tfr.html"),
        media_type="text/html"
    )

@app.get("/download_report.html")
def pagina_download_report_html(request: Request):
    session_id = request.query_params.get("session_id")

    if session_id:
        aggiorna_stato_ordine(
            sessione_stripe=session_id,
            stato="pagato"
        )

        app.state.ultima_sessione_tfr = session_id

    return FileResponse(
        path=str(FRONTEND_DIR / "download_report.html"),
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

        app.state.ultima_sessione_tfr = session_id

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
def pagina_dashboard_admin():
    return FileResponse(
        path=str(FRONTEND_DIR / "dashboard_admin.html"),
        media_type="text/html"
    )


@app.get("/login-admin")
def pagina_login_admin():
    return FileResponse(
        path=str(FRONTEND_DIR / "login_admin.html"),
        media_type="text/html"
    )


@app.get("/login-cliente")
def pagina_login_cliente():
    return FileResponse(
        path=str(FRONTEND_DIR / "login_cliente.html"),
        media_type="text/html"
    )


@app.get("/area-cliente")
def pagina_area_cliente():
    return FileResponse(
        path=str(FRONTEND_DIR / "area_cliente.html"),
        media_type="text/html"
    )


from fastapi.responses import RedirectResponse


@app.get("/webmail")
def apri_webmail():

    return RedirectResponse(
        url="https://webmail.siteground.com/webmail/log-in"
    )


@app.post("/login-admin")
def login_admin(richiesta: RichiestaLoginAdmin):
    if richiesta.password != ADMIN_PASSWORD:
        return {
            "success": False
        }

    return {
        "success": True,
        "token": ADMIN_TOKEN
    }


@app.post("/login-cliente")
def login_cliente(richiesta: RichiestaLoginCliente):
    email_pulita = normalizza_email(richiesta.email_cliente)

    if not email_pulita or "@" not in email_pulita:
        return {
            "success": False,
            "errore": "Email non valida"
        }

    ordini = leggi_ordini()
    ordini_cliente = [
        ordine
        for ordine in ordini
        if normalizza_email(ordine[1]) == email_pulita
        and ordine[6] == "pagato"
    ]

    if not ordini_cliente:
        return {
            "success": False,
            "errore": "Nessun report acquistato trovato per questa email"
        }

    return {
        "success": True,
        "email_cliente": email_pulita,
        "token": email_pulita
    }


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

    import base64

    with open(percorso_pdf, "rb") as file:
        pdf_base64 = base64.b64encode(
            file.read()
        ).decode()

    if richiesta.session_id:
        aggiorna_pdf_ordine(
            sessione_stripe=richiesta.session_id,
            pdf_file=nome_file,
            pdf_base64=pdf_base64
        )

    email_cliente = (
        richiesta.email_cliente or ""
    ).lower().strip()

    if email_cliente:
        salva_storico_calcolo(
            email_cliente=email_cliente,
            tipo="TFR",
            titolo=f"{richiesta.nome} {richiesta.cognome}",
            dettaglio=(
                f"{richiesta.data_assunzione} - "
                f"{richiesta.data_cessazione}"
            ),
            importo=risultato["liquidazione"]["totale_da_liquidare"]
        )

    chiave_email = (
        f"{email_cliente}_"
        f"{richiesta.nome}_"
        f"{richiesta.cognome}_"
        f"{richiesta.data_assunzione}_"
        f"{richiesta.data_cessazione}"
    )

    ultima_email = getattr(app.state, "ultima_email_tfr", None)

    forza_invio_email = richiesta.invia_email

    deve_inviare_email = (
        email_cliente
        and (
            forza_invio_email
            or ultima_email != chiave_email
        )
    )

    if deve_inviare_email:
        try:
            invia_report_tfr_email(
                destinatario=email_cliente,
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

    email_cliente = (richiesta.email_cliente or "").strip()
    nome_cliente = (richiesta.nome_cliente or richiesta.nome_datore or "").strip()
    cognome_cliente = (richiesta.cognome_cliente or richiesta.cognome_datore or "").strip()

    nome_completo = (
        richiesta.nome_completo_cliente
        or f"{nome_cliente} {cognome_cliente}"
    ).strip()

    line_item = {
        "quantity": 1
    }

    if STRIPE_PRICE_ID_TFR:
        line_item["price"] = STRIPE_PRICE_ID_TFR
    else:
        line_item["price_data"] = {
            "currency": "eur",
            "product_data": {
                "name": "Report TFR Colf e Badanti - CostoDomestico.it",
                "images": [
                    "https://costodomestico.it/favicon-512.png?v=2"
                ]
            },
            "unit_amount": 790
        }


    parametri_sessione = {
        "payment_method_types": ["card"],
        "mode": "payment",
        "billing_address_collection": "auto",
        "custom_fields": [
    {
        "key": "nome_completo",
        "label": {
            "type": "custom",
            "custom": "Nome completo"
        },
        "type": "text",
        "optional": False
    }
],
        "line_items": [
            line_item
        ],
        "metadata": {
            "prodotto": "Report Professionale TFR",
            "email_cliente": email_cliente,
            "nome_cliente": nome_cliente,
            "cognome_cliente": cognome_cliente,
            "nome_completo": nome_completo
        },
        "success_url": (
            "https://costodomestico.it/download_report.html"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        "cancel_url": "https://costodomestico.it/tfr-tool"
    }
    if email_cliente:
        parametri_sessione["customer_email"] = email_cliente

    parametri_sessione["customer_creation"] = "always"

    sessione = stripe.checkout.Session.create(
        **parametri_sessione
    )

    salva_ordine(
        email_cliente=email_cliente,
        nome_cliente=nome_cliente,
        cognome_cliente=cognome_cliente,
        prodotto="Report Professionale TFR",
        importo=7.90,
        stato="checkout_creato",
        sessione_stripe=sessione.id
    )

    salva_o_aggiorna_cliente(
        email=email_cliente,
        nome=nome_cliente,
        cognome=cognome_cliente
    )

    return {
        "checkout_url": sessione.url,
        "url": sessione.url,
        "session_url": sessione.url
    }

@app.get("/download-costo-domestico")
def pagina_download_costo_domestico(request: Request):

    session_id = request.query_params.get("session_id")

    if session_id:
        aggiorna_stato_ordine(
            sessione_stripe=session_id,
            stato="pagato"
        )

        app.state.ultima_sessione_costo_domestico = session_id

    return FileResponse(
        path=str(FRONTEND_DIR / "download_costo_domestico.html"),
        media_type="text/html"
    )


@app.post("/crea-checkout-costo-domestico")
def crea_checkout_costo_domestico(
    richiesta: RichiestaOrdineCostoDomestico
):

    email_cliente = (richiesta.email_cliente or "").strip().lower()
    nome_cliente = (richiesta.nome_cliente or "").strip()
    cognome_cliente = (richiesta.cognome_cliente or "").strip()

    nome_completo = (
        f"{nome_cliente} {cognome_cliente}"
        .strip()
    )

    parametri_sessione = {
        "payment_method_types": ["card"],
        "mode": "payment",
        "billing_address_collection": "auto",

        "line_items": [
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": "Report Costo Domestico - CostoDomestico.it",
                        "images": [
                            "https://costodomestico.it/favicon-512.png"
                        ]
                    },
                    "unit_amount": 990
                },
                "quantity": 1
            }
        ],

        "metadata": {
            "prodotto": "Costo Domestico",
            "email_cliente": email_cliente,
            "nome_cliente": nome_cliente,
            "cognome_cliente": cognome_cliente,
            "nome_completo": nome_completo
        },

        "success_url": (
            "https://costodomestico.it/download_costo_domestico.html"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),

        "cancel_url": "https://costodomestico.it/costo-domestico.html"
    }

    if email_cliente:
        parametri_sessione["customer_email"] = email_cliente

    parametri_sessione["customer_creation"] = "always"

    sessione = stripe.checkout.Session.create(
        **parametri_sessione
    )

    salva_ordine(
        email_cliente=email_cliente,
        nome_cliente=nome_cliente,
        cognome_cliente=cognome_cliente,
        prodotto="Costo Domestico",
        importo=9.90,
        stato="checkout_creato",
        sessione_stripe=sessione.id
    )

    salva_o_aggiorna_cliente(
        email=email_cliente,
        nome=nome_cliente,
        cognome=cognome_cliente
    )

    return {
        "checkout_url": sessione.url
    }
class RichiestaInvioEmailCostoDomestico(BaseModel):
    email_cliente: str
    nome_cliente: str = ""
    nome_file: str = "report_costo_lavoro_domestico.pdf"
    pdf_base64: str
    sessione_stripe: str = ""


@app.post("/invia-email-costo-domestico")
def invia_email_costo_domestico(
    richiesta: RichiestaInvioEmailCostoDomestico
):
    if not richiesta.email_cliente:
        return {"ok": False, "errore": "Email cliente mancante"}

    percorso_pdf = PDF_DIR / richiesta.nome_file

    import base64

    contenuto_pdf = base64.b64decode(richiesta.pdf_base64)

    with open(percorso_pdf, "wb") as file:
        file.write(contenuto_pdf)

        sessione_stripe = getattr(
    app.state,
    "ultima_sessione_costo_domestico",
    ""
)

    if sessione_stripe:
        import base64

    pdf_base64 = base64.b64encode(
        contenuto_pdf
    ).decode()

    aggiorna_pdf_ordine(
        sessione_stripe=sessione_stripe,
        pdf_file=richiesta.nome_file,
        pdf_base64=pdf_base64
    )

    invia_report_costo_domestico_email(
        destinatario=richiesta.email_cliente,
        percorso_pdf=str(percorso_pdf),
        nome_file=richiesta.nome_file
    )

    salva_storico_calcolo(
        email_cliente=richiesta.email_cliente.lower().strip(),
        tipo="Costo Domestico",
        titolo="Report Costo Domestico",
        dettaglio="Simulazione costo lavoro domestico",
        importo=0
    )

    if richiesta.sessione_stripe:
        aggiorna_pdf_ordine(
            sessione_stripe=richiesta.sessione_stripe,
            pdf_file=richiesta.nome_file
        )
    else:
        aggiorna_pdf_ultimo_ordine_email(
            email_cliente=richiesta.email_cliente,
            pdf_file=richiesta.nome_file
        )

    return {"ok": True}

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

    salva_o_aggiorna_cliente(
        email=richiesta.email_cliente,
        nome=richiesta.nome_cliente,
        cognome=richiesta.cognome_cliente
    )

    return {
        "success": True
    }


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

@app.get("/analytics-funnel")
def analytics_funnel():

    property_id = os.getenv("GA4_PROPERTY_ID")
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if not property_id:
        return {
            "success": False,
            "errore": "GA4_PROPERTY_ID mancante"
        }

    if not credentials_json:
        return {
            "success": False,
            "errore": "GOOGLE_CREDENTIALS_JSON mancante"
        }

    try:

        credentials_info = json.loads(
            credentials_json
        )

        credentials = (
            service_account.Credentials
            .from_service_account_info(
                credentials_info
            )
        )

        client = BetaAnalyticsDataClient(
            credentials=credentials
        )

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount")],
            date_ranges=[
                DateRange(
                    start_date="30daysAgo",
                    end_date="today"
                )
            ]
        )

        response = client.run_report(request)

        eventi = {}

        for row in response.rows:
            nome = row.dimension_values[0].value
            valore = int(row.metric_values[0].value)
            eventi[nome] = valore

        return {
            "success": True,
            "eventi": eventi
        }

    except Exception as errore:

        return {
            "success": False,
            "errore": str(errore)
        }
    
eventi_funnel = {
    "page_view": 0,
    "click_calcola": 0,
    "click_stripe": 0,
    "begin_checkout": 0,
    "purchase": 0,
    "pdf_download": 0,
    "click_calcola_tfr": 0,
    "click_stripe_tfr": 0,
    "begin_checkout_tfr": 0,
    "purchase_tfr": 0,
    "pdf_download_tfr": 0
}


@app.post("/track-event")
async def track_event(request: Request):

    dati = await request.json()

    evento = dati.get("evento")

    salva_evento_funnel(evento)

    return {
        "success": True
    }


@app.get("/storico-calcoli")
def storico_calcoli(email: str):

    risultati = leggi_storico_calcoli(
        email
    )

    storico = []

    for riga in risultati:

        storico.append({
            "id": riga[0],
            "tipo": riga[1],
            "titolo": riga[2],
            "dettaglio": riga[3],
            "importo": riga[4],
            "data": str(riga[5])
        })

    return storico

@app.get("/analytics-funnel-interno")
def analytics_funnel_interno():

    return {
        "success": True,
        "eventi": leggi_eventi_funnel()
    }

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
            "data_ordine": ordine[8],
            "pdf_file": ordine[9] if len(ordine) > 9 else None
        })

    return risultato


@app.get("/api/cliente/report")
def api_cliente_report(email: str):
    email_pulita = normalizza_email(email)

    if not email_pulita:
        return {
            "success": False,
            "errore": "Email mancante",
            "report": []
        }

    ordini = leggi_ordini()
    report = []

    for ordine in ordini:
        email_ordine = normalizza_email(ordine[1])
        stato = ordine[6]
        pdf_file = ordine[9] if len(ordine) > 9 else None

        if email_ordine == email_pulita and stato == "pagato":
            report.append({
                "id": ordine[0],
                "email_cliente": ordine[1],
                "nome_cliente": ordine[2],
                "cognome_cliente": ordine[3],
                "prodotto": ordine[4],
                "importo": ordine[5],
                "stato": stato,
                "sessione_stripe": ordine[7],
                "data_ordine": ordine[8],
                "pdf_file": pdf_file,
                "download_url": (
                    f"/download-report-cliente/{ordine[0]}"
                    if pdf_file
                    else None
                )
            })

    return {
        "success": True,
        "email_cliente": email_pulita,
        "report": report
    }


@app.get("/download-report-cliente/{ordine_id}")
def download_report_cliente(ordine_id: int):
    ordini = leggi_ordini()

    ordine_trovato = None

    for ordine in ordini:
        if ordine[0] == ordine_id:
            ordine_trovato = ordine
            break

    if not ordine_trovato:
        raise HTTPException(
            status_code=404,
            detail="Ordine non trovato"
        )

    stato = ordine_trovato[6]
    pdf_file = ordine_trovato[9] if len(ordine_trovato) > 9 else None

    if stato != "pagato":
        raise HTTPException(
            status_code=403,
            detail="Ordine non pagato"
        )

    if not pdf_file:
        raise HTTPException(
            status_code=404,
            detail="PDF non collegato all'ordine"
        )

    percorso_pdf = PDF_DIR / pdf_file

    if not percorso_pdf.exists():
        raise HTTPException(
            status_code=404,
            detail="File PDF non trovato"
        )

    return FileResponse(
        path=str(percorso_pdf),
        filename=pdf_file,
        media_type="application/pdf"
    )


@app.get("/clienti")
def clienti():
    elenco = leggi_clienti()

    risultato = []

    for cliente in elenco:
        risultato.append({
            "id": cliente[0],
            "email": cliente[1],
            "nome": cliente[2],
            "cognome": cliente[3],
            "data_creazione": cliente[4]
        })

    return risultato


async def gestisci_webhook_stripe(request: Request):
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

        metadata = sessione.get("metadata", {})
        prodotto = metadata.get("prodotto", "").lower()

        if "tfr" in prodotto:
            salva_evento_funnel("purchase_tfr")
        else:
            salva_evento_funnel("purchase")

    return {
        "success": True
    }


@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    return await gestisci_webhook_stripe(request)


@app.post("/webhook")
async def webhook(request: Request):
    return await gestisci_webhook_stripe(request)


@app.post("/richiedi-magic-link")
def richiedi_magic_link(richiesta: RichiestaMagicLink):

    import secrets
    from datetime import datetime, timedelta

    email = richiesta.email.lower().strip()

    if not email:
        return {
            "success": False,
            "errore": "Email mancante"
        }

    token = secrets.token_urlsafe(32)

    scadenza = (
        datetime.now() + timedelta(minutes=30)
    ).isoformat()

    salva_o_aggiorna_cliente(
        email=email,
        nome="",
        cognome=""
    )

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clienti
        SET magic_token = %s,
            magic_token_scadenza = %s
        WHERE LOWER(TRIM(email)) = %s
    """, (
        token,
        scadenza,
        email
    ))

    conn.commit()
    cursor.close()
    conn.close()

    magic_link = (
        "https://costodomestico.it/area-cliente"
        f"?token={token}"
    )

    try:
        invia_magic_link_email(
            destinatario=email,
            magic_link=magic_link
        )
        
    except Exception as errore:
        print("ERRORE INVIO MAGIC LINK:", errore)
    return {
        "success": True,
        "magic_link": magic_link
    }


@app.get("/verifica-magic-link")
def verifica_magic_link_endpoint(token: str):

    from datetime import datetime

    conn = get_connessione()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            nome,
            cognome,
            magic_token_scadenza
        FROM clienti
        WHERE magic_token = %s
    """, (
        token,
    ))

    cliente = cursor.fetchone()

    if not cliente:
        cursor.close()
        conn.close()
        return {
            "success": False,
            "errore": "Token non valido"
        }

    cursor.execute("""
        UPDATE clienti
        SET ultimo_accesso = %s,
            magic_token = NULL,
            magic_token_scadenza = NULL
        WHERE id = %s
    """, (
        datetime.now().isoformat(),
        cliente[0]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "cliente": {
            "id": cliente[0],
            "email": cliente[1],
            "nome": cliente[2],
            "cognome": cliente[3],
            "scadenza": cliente[4]
        }
    }

@app.delete("/elimina-ordini-email")
def elimina_ordini_email(email: str):
    import sqlite3

    email_pulita = email.strip().lower()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM ordini
        WHERE LOWER(TRIM(email_cliente)) = ?
        """,
        (email_pulita,)
    )

    ordini_eliminati = cursor.rowcount

    conn.commit()
    conn.close()

    return {
        "success": True,
        "ordini_eliminati": ordini_eliminati
    }

@app.delete("/elimina-ordini-senza-email")
def elimina_ordini_senza_email():

    return {
        "success": False,
        "messaggio": "Endpoint disabilitato in produzione"
    }

@app.delete("/reset-test-dashboard")
def reset_test_dashboard_endpoint():

    return {
        "success": False,
        "messaggio": "Endpoint disabilitato in produzione"
    }

@app.delete("/elimina-storico-calcoli")
def elimina_storico_calcoli_endpoint(
    email: str
):

    eliminati = elimina_storico_calcoli(email)

    return {
        "success": True,
        "eliminati": eliminati
    }

@app.get("/immagini/report-tfr-preview.png")
def immagine_report_tfr_preview():

    percorso = FRONTEND_DIR / "immagini" / "report-tfr-preview.png"

    if not percorso.exists():
        return {
            "errore": "Immagine non trovata",
            "percorso_cercato": str(percorso)
        }

    return FileResponse(
        path=str(percorso),
        media_type="image/png"
    )


@app.get("/ordini-cliente")
def ordini_cliente(email: str):

    ordini = leggi_ordini()

    risultato = []

    for ordine in ordini:

        email_ordine = (ordine[1] or "").lower()

        if email_ordine == email.lower():
            risultato.append({
                "id": ordine[0],
                "email_cliente": ordine[1],
                "nome_cliente": ordine[2],
                "cognome_cliente": ordine[3],
                "prodotto": ordine[4],
                "importo": ordine[5],
                "stato": ordine[6],
                "sessione_stripe": ordine[7],
                "data_ordine": ordine[8],
                "pdf_file": ordine[9] if len(ordine) > 9 else None
            })

    return risultato

@app.get("/download-pdf/{ordine_id}")
def download_pdf(ordine_id: int):

    import base64
    import tempfile

    ordini = leggi_ordini()

    for ordine in ordini:

        if ordine[0] == ordine_id:

            pdf_file = ordine[9] if len(ordine) > 9 else ""
            pdf_base64 = ordine[10] if len(ordine) > 10 else ""

            if not pdf_file:
                raise HTTPException(
                    status_code=404,
                    detail="PDF non disponibile"
                )

            if not pdf_base64:
                raise HTTPException(
                    status_code=404,
                    detail="PDF non presente in archivio"
                )

            contenuto_pdf = base64.b64decode(pdf_base64)

            file_temporaneo = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            )

            file_temporaneo.write(contenuto_pdf)
            file_temporaneo.close()

            return FileResponse(
                path=file_temporaneo.name,
                filename=pdf_file,
                media_type="application/pdf"
            )

    raise HTTPException(
        status_code=404,
        detail="Ordine non trovato"
    )

@app.get("/contributi-lavoro-domestico-2026.html")
def pagina_contributi_lavoro_domestico_2026():
    return FileResponse(
        path=str(FRONTEND_DIR / "contributi-lavoro-domestico-2026.html"),
        media_type="text/html"
    )


@app.get("/scadenza-contributi-colf.html")
def pagina_scadenza_contributi_colf():
    return FileResponse(
        path=str(FRONTEND_DIR / "scadenza-contributi-colf.html"),
        media_type="text/html"
    )


@app.get("/calcolo-contributi-colf.html")
def pagina_calcolo_contributi_colf():
    return FileResponse(
        path=str(FRONTEND_DIR / "calcolo-contributi-colf.html"),
        media_type="text/html"
    )


@app.get("/calcolo-contributi-badante.html")
def pagina_calcolo_contributi_badante():
    return FileResponse(
        path=str(FRONTEND_DIR / "calcolo-contributi-badante.html"),
        media_type="text/html"
    )


@app.get("/contributi-badante-54-ore.html")
def pagina_contributi_badante_54_ore():
    return FileResponse(
        path=str(FRONTEND_DIR / "contributi-badante-54-ore.html"),
        media_type="text/html"
    )


@app.get("/tfr-tool")
def pagina_tfr_tool():
    return FileResponse(
        path=str(FRONTEND_DIR / "calcolo-tfr-colf-badanti.html"),
        media_type="text/html"
    )

@app.get("/calcolo-tfr-colf-badanti.html")
def pagina_tfr_seo():
    return FileResponse(
        path=str(FRONTEND_DIR / "calcolo-tfr-colf-badanti.html"),
        media_type="text/html"
    )

@app.get("/calcolo-tfr-colf-badanti.html")
def pagina_calcolo_tfr_colf_badanti():
    return FileResponse(
        path=str(FRONTEND_DIR / "calcolo-tfr-colf-badanti.html")
    )

@app.get("/sitemap.xml")
def sitemap():
    return FileResponse(
        path=str(FRONTEND_DIR / "sitemap.xml"),
        media_type="application/xml"
    )

class RichiestaEmailAdmin(BaseModel):
    destinatario: str
    oggetto: str
    testo: str

class RichiestaEmailMassivaAdmin(BaseModel):
    oggetto: str
    testo: str

class RichiestaMessaggioCliente(BaseModel):
    email: str
    oggetto: str
    testo: str

@app.post("/admin/invia-email")
def admin_invia_email(richiesta: RichiestaEmailAdmin):

    try:
        invia_email_generica(
            destinatario=richiesta.destinatario,
            oggetto=richiesta.oggetto,
            testo=richiesta.testo
        )

        salva_email_admin(
            destinatario=richiesta.destinatario,
            oggetto=richiesta.oggetto,
            testo=richiesta.testo,
            stato="inviata"
        )

        return {
            "ok": True,
            "messaggio": "Email inviata e salvata correttamente"
        }

    except Exception as e:

        salva_email_admin(
            destinatario=richiesta.destinatario,
            oggetto=richiesta.oggetto,
            testo=richiesta.testo,
            stato="errore",
            errore=str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=f"Errore invio email: {str(e)}"
        )
    
@app.get("/admin/email-inviate")
def admin_email_inviate():
    return leggi_email_admin()

@app.get("/admin/clienti-email")
def admin_clienti_email():
    return {
        "totale": len(leggi_email_clienti()),
        "email": leggi_email_clienti()
    }

@app.get("/admin/statistiche-clienti")
def admin_statistiche_clienti():

    stats_ordini = statistiche_ordini()

    return {
        "clienti_registrati": conta_clienti(),
        "clienti_paganti": stats_ordini["clienti_paganti"],
        "ordini_pagati": stats_ordini["ordini_pagati"],
        "fatturato_totale": stats_ordini["fatturato_totale"]
    }

@app.post("/admin/invia-email-clienti")
def admin_invia_email_clienti(richiesta: RichiestaEmailMassivaAdmin):

    email_clienti = leggi_email_clienti()

    risultati = []

    for email in email_clienti:

        try:
            invia_email_generica(
                destinatario=email,
                oggetto=richiesta.oggetto,
                testo=richiesta.testo
            )

            salva_email_admin(
                destinatario=email,
                oggetto=richiesta.oggetto,
                testo=richiesta.testo,
                stato="inviata"
            )

            risultati.append({
                "email": email,
                "stato": "inviata"
            })

        except Exception as e:

            salva_email_admin(
                destinatario=email,
                oggetto=richiesta.oggetto,
                testo=richiesta.testo,
                stato="errore",
                errore=str(e)
            )

            risultati.append({
                "email": email,
                "stato": "errore",
                "errore": str(e)
            })

    return {
        "totale_clienti": len(email_clienti),
        "risultati": risultati
    }

@app.post("/cliente/invia-messaggio")
def cliente_invia_messaggio(
    richiesta: RichiestaMessaggioCliente
):

    salva_email_admin(
        destinatario="support@costodomestico.it",
        oggetto=richiesta.oggetto,
        testo=richiesta.testo,
        stato="ricevuta",
        tipo="ricevuta",
        mittente=richiesta.email
    )

    return {
        "ok": True,
        "messaggio": "Messaggio inviato correttamente"
    }

@app.post("/admin/messaggio-letto/{id_messaggio}")
def admin_messaggio_letto(id_messaggio: int):
    segna_messaggio_letto(id_messaggio)

    return {
        "ok": True,
        "messaggio": "Messaggio segnato come letto"
    }

@app.get("/api/miei-ordini")
def api_miei_ordini(email: str):

    ordini = leggi_ordini_cliente(email)

    return [
    {
        "id": ordine[0],
        "prodotto": ordine[1],
        "importo": ordine[2],
        "stato": ordine[3],
        "data_ordine": ordine[4],
        "pdf_file": ordine[5],
        "sessione_stripe": ordine[6],
    }
    for ordine in ordini
]

@app.get("/admin/messaggi-clienti")
def admin_messaggi_clienti():
    return leggi_messaggi_clienti()






