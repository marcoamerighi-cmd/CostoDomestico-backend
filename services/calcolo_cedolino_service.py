from decimal import Decimal, ROUND_HALF_UP

from database.paghe_rapporti_repository import leggi_rapporto
from database.paghe_eventi_repository import leggi_eventi_mese
from database.paghe_cedolini_repository import crea_cedolino

from services.calcolo_eventi_cedolino import elabora_eventi_cedolino


def euro(valore):
    return Decimal(str(valore or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def contributo_lavoratore_orario(paga_oraria, ore_settimanali):
    paga_oraria = Decimal(str(paga_oraria or 0))
    ore_settimanali = Decimal(str(ore_settimanali or 0))

    if ore_settimanali > 24:
        return Decimal("0.25")

    if paga_oraria <= Decimal("9.61"):
        return Decimal("0.43")

    if paga_oraria <= Decimal("11.70"):
        return Decimal("0.48")

    return Decimal("0.59")


def calcola_cedolino_da_eventi(
    mese_id,
    rapporto_id,
    anno,
    mese,
    numero_cedolino=None
):
    rapporto = leggi_rapporto(rapporto_id)

    if not rapporto:
        raise ValueError("Rapporto non trovato")

    livello = rapporto[9]
    ore_settimanali = Decimal(str(rapporto[11] or 0))
    paga_oraria = rapporto[14]
    paga_mensile = rapporto[15]
    paga_pattuita_tipo = rapporto[16]

    eventi = leggi_eventi_mese(mese_id)
    risultato_eventi = elabora_eventi_cedolino(eventi)

    ore_retribuite = Decimal(str(risultato_eventi["ore_retribuite"] or 0))
    totale_competenze = euro(risultato_eventi["totale_competenze"])
    totale_trattenute = euro(risultato_eventi["totale_trattenute"])

    if paga_pattuita_tipo == "mensile" and paga_mensile:
        lordo_base = euro(paga_mensile)

        if ore_retribuite == 0:
            ore_retribuite = euro(
                ore_settimanali * Decimal("52") / Decimal("12")
            )

        paga_oraria_calcolo = (
            euro(lordo_base / ore_retribuite)
            if ore_retribuite
            else Decimal("0")
        )

        lordo = euro(lordo_base + totale_competenze - totale_trattenute)

    else:
        paga_oraria_calcolo = euro(paga_oraria or 0)

        if totale_competenze == 0 and ore_retribuite:
            totale_competenze = euro(
                ore_retribuite * paga_oraria_calcolo
            )

        lordo = euro(totale_competenze - totale_trattenute)

    quota_contributo_lavoratore = contributo_lavoratore_orario(
        paga_oraria=paga_oraria_calcolo,
        ore_settimanali=ore_settimanali
    )

    contributi_lavoratore = euro(
        ore_retribuite * quota_contributo_lavoratore
    )

    netto = euro(lordo - contributi_lavoratore)

    tfr_maturato = euro(lordo / Decimal("13.5"))
    tredicesima_maturata = euro(lordo / Decimal("12"))

    if not numero_cedolino:
        numero_cedolino = f"{anno}-{str(mese).zfill(2)}"

    dati_calcolo = {
        "livello": livello,
        "ore_settimanali": float(ore_settimanali),
        "ore_retribuite": float(ore_retribuite),
        "paga_oraria_calcolo": float(paga_oraria_calcolo),
        "quota_contributo_lavoratore": float(quota_contributo_lavoratore),
        "totale_competenze": float(totale_competenze),
        "totale_trattenute": float(totale_trattenute),
        "competenze": risultato_eventi["competenze"],
        "trattenute": risultato_eventi["trattenute"],
        "riepilogo": risultato_eventi["riepilogo"],
        "nota_fiscale": (
            "Il datore domestico non è sostituto d'imposta: "
            "il netto è calcolato sottraendo solo i contributi "
            "a carico lavoratore."
        )
    }

    cedolino_id = crea_cedolino(
        mese_id=mese_id,
        rapporto_id=rapporto_id,
        numero_cedolino=numero_cedolino,
        lordo=lordo,
        contributi_lavoratore=contributi_lavoratore,
        netto=netto,
        tfr_maturato=tfr_maturato,
        tredicesima_maturata=tredicesima_maturata,
        dati_calcolo=dati_calcolo,
        stato="bozza"
    )

    return {
        "cedolino_id": cedolino_id,
        "lordo": float(lordo),
        "contributi_lavoratore": float(contributi_lavoratore),
        "netto": float(netto),
        "tfr_maturato": float(tfr_maturato),
        "tredicesima_maturata": float(tredicesima_maturata),
        "dati_calcolo": dati_calcolo
    }