from datetime import date
import calendar

from tfr.coefficienti_tfr import trova_coefficiente_tfr


def calcola_quota_tfr(retribuzione_utile_annua: float) -> float:
    return round(retribuzione_utile_annua / 13.5, 2)


def calcola_retribuzione_utile(
    paga_lorda_annua: float,
    tredicesima: float = 0,
    vitto_alloggio: float = 0,
    scatti_anzianita: float = 0,
    superminimo: float = 0
) -> float:
    return round(
        paga_lorda_annua
        + tredicesima
        + vitto_alloggio
        + scatti_anzianita
        + superminimo,
        2
    )


def calcola_tfr_annuo(
    paga_lorda_annua: float,
    tredicesima: float = 0,
    vitto_alloggio: float = 0,
    scatti_anzianita: float = 0,
    superminimo: float = 0
) -> dict:
    retribuzione_utile = calcola_retribuzione_utile(
        paga_lorda_annua,
        tredicesima,
        vitto_alloggio,
        scatti_anzianita,
        superminimo
    )

    quota_tfr = calcola_quota_tfr(retribuzione_utile)

    return {
        "retribuzione_utile": retribuzione_utile,
        "quota_tfr": quota_tfr
    }


def calcola_mesi_utili(data_inizio: date, data_fine: date) -> int:
    mesi_utili = 0

    anno = data_inizio.year
    mese = data_inizio.month

    while (anno < data_fine.year) or (
        anno == data_fine.year and mese <= data_fine.month
    ):
        primo_giorno = date(anno, mese, 1)
        ultimo_giorno = date(
            anno,
            mese,
            calendar.monthrange(anno, mese)[1]
        )

        inizio_effettivo = max(data_inizio, primo_giorno)
        fine_effettiva = min(data_fine, ultimo_giorno)

        giorni = (fine_effettiva - inizio_effettivo).days + 1

        if giorni >= 15:
            mesi_utili += 1

        if mese == 12:
            mese = 1
            anno += 1
        else:
            mese += 1

    return mesi_utili


def calcola_tfr_proporzionato(
    paga_lorda_annua: float,
    mesi_utili: int,
    vitto_alloggio: float = 0,
    scatti_anzianita: float = 0,
    superminimo: float = 0
) -> dict:
    retribuzione_mensile = paga_lorda_annua / 12
    retribuzione_periodo = retribuzione_mensile * mesi_utili

    tredicesima = (retribuzione_mensile / 12) * mesi_utili
    vitto_alloggio_proporzionato = (vitto_alloggio / 12) * mesi_utili
    scatti_proporzionati = (scatti_anzianita / 12) * mesi_utili
    superminimo_proporzionato = (superminimo / 12) * mesi_utili

    retribuzione_utile = calcola_retribuzione_utile(
        retribuzione_periodo,
        tredicesima,
        vitto_alloggio_proporzionato,
        scatti_proporzionati,
        superminimo_proporzionato
    )

    quota_tfr = calcola_quota_tfr(retribuzione_utile)

    return {
        "mesi_utili": mesi_utili,
        "retribuzione_periodo": round(retribuzione_periodo, 2),
        "tredicesima": round(tredicesima, 2),
        "vitto_alloggio_proporzionato": round(vitto_alloggio_proporzionato, 2),
        "scatti_proporzionati": round(scatti_proporzionati, 2),
        "superminimo_proporzionato": round(superminimo_proporzionato, 2),
        "retribuzione_utile": round(retribuzione_utile, 2),
        "quota_tfr": round(quota_tfr, 2)
    }


def calcola_coefficiente_rivalutazione(
    variazione_istat_foi: float
) -> float:
    quota_fissa = 1.5
    quota_istat = variazione_istat_foi * 0.75

    coefficiente = quota_fissa + quota_istat

    return round(coefficiente, 4)


def calcola_rivalutazione_tfr(
    dettaglio_anni: list | None = None,
    variazione_istat_foi: float = 2,
    tfr_pregresso: float | None = None,
    coefficiente: float | None = None
) -> float:
    if tfr_pregresso is not None and coefficiente is not None:
        return round(tfr_pregresso * coefficiente / 100, 2)

    if not dettaglio_anni or len(dettaglio_anni) <= 1:
        return 0

    tfr_accantonato = 0
    rivalutazione_totale = 0

    for riga in dettaglio_anni:
        anno = riga["anno"]
        quota_tfr = riga["quota_tfr"]

        coefficiente_anno = trova_coefficiente_tfr(
            anno=anno,
            mese=12
        )

        rivalutazione_anno = round(
            tfr_accantonato * coefficiente_anno / 100,
            2
        )

        riga["coefficiente_rivalutazione"] = coefficiente_anno
        riga["rivalutazione"] = rivalutazione_anno

        rivalutazione_totale += rivalutazione_anno

        tfr_accantonato += quota_tfr + rivalutazione_anno

        riga["totale_progressivo"] = round(
            tfr_accantonato,
            2
        )

    return round(rivalutazione_totale, 2)


def calcola_tfr_finale(
    tfr_maturato: float,
    rivalutazione: float = 0,
    anticipi: float = 0
) -> dict:
    totale_lordo = tfr_maturato + rivalutazione
    differenza = totale_lordo - anticipi

    if differenza < 0:
        totale_da_liquidare = 0
        anticipo_eccedente = abs(differenza)
    else:
        totale_da_liquidare = differenza
        anticipo_eccedente = 0

    return {
        "tfr_maturato": round(tfr_maturato, 2),
        "rivalutazione": round(rivalutazione, 2),
        "anticipi": round(anticipi, 2),
        "totale_lordo": round(totale_lordo, 2),
        "totale_da_liquidare": round(totale_da_liquidare, 2),
        "anticipo_eccedente": round(anticipo_eccedente, 2)
    }


def calcola_tfr_annualita_lorde(
    annualita: list,
    anticipi: float = 0,
    variazione_istat_foi: float = 2
) -> dict:
    dettaglio_anni = []
    totale_tfr = 0

    for riga in annualita:
        anno = riga["anno"]
        retribuzione_lorda = riga["retribuzione_lorda"]
        mesi_utili = riga["mesi_utili"]

        retribuzione_utile = (
            retribuzione_lorda / 12
        ) * mesi_utili

        quota_tfr = retribuzione_utile / 13.5

        totale_tfr += quota_tfr

        dettaglio_anni.append({
            "anno": anno,
            "mesi_utili": mesi_utili,
            "retribuzione_lorda": round(retribuzione_lorda, 2),
            "retribuzione_utile": round(retribuzione_utile, 2),
            "quota_tfr": round(quota_tfr, 2)
        })

    coefficiente = calcola_coefficiente_rivalutazione(
        variazione_istat_foi
    )

    rivalutazione = calcola_rivalutazione_tfr(
        dettaglio_anni=dettaglio_anni,
        variazione_istat_foi=variazione_istat_foi
    )

    liquidazione = calcola_tfr_finale(
        tfr_maturato=totale_tfr,
        rivalutazione=rivalutazione,
        anticipi=anticipi
    )

    return {
        "dettaglio_anni": dettaglio_anni,
        "totale_tfr": round(totale_tfr, 2),
        "coefficiente_rivalutazione": coefficiente,
        "rivalutazione": rivalutazione,
        "liquidazione": liquidazione
    }