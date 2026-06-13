from decimal import Decimal, ROUND_HALF_UP


def euro(valore):
    return Decimal(str(valore or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def elabora_eventi_cedolino(eventi):
    competenze = []
    trattenute = []

    ore_retribuite = Decimal("0")
    giorni_retribuiti = Decimal("0")

    totale_competenze = Decimal("0")
    totale_trattenute = Decimal("0")

    riepilogo = {
        "ore_ordinarie": 0,
        "ferie_ore": 0,
        "permessi_ore": 0,
        "festivita_giorni": 0,
        "malattia_giorni": 0,
        "assenza_ore": 0,
        "anticipo_tfr": 0,
        "una_tantum": 0
    }

    for evento in eventi:
        tipo_evento = evento[3]
        data_inizio = evento[4]
        data_fine = evento[5]
        ore = Decimal(str(evento[6] or 0))
        giorni = Decimal(str(evento[7] or 0))
        importo = euro(evento[8])
        note = evento[9] or ""

        voce_base = {
            "tipo_evento": tipo_evento,
            "data_inizio": str(data_inizio),
            "data_fine": str(data_fine) if data_fine else None,
            "ore": float(ore),
            "giorni": float(giorni),
            "importo": float(importo),
            "note": note
        }

        if tipo_evento == "lavoro_ordinario":
            competenze.append({
                **voce_base,
                "descrizione": "Lavoro ordinario"
            })
            ore_retribuite += ore
            giorni_retribuiti += giorni
            totale_competenze += importo
            riepilogo["ore_ordinarie"] += float(ore)

        elif tipo_evento == "ferie":
            competenze.append({
                **voce_base,
                "descrizione": "Ferie retribuite"
            })
            ore_retribuite += ore
            giorni_retribuiti += giorni
            totale_competenze += importo
            riepilogo["ferie_ore"] += float(ore)

        elif tipo_evento == "permessi":
            competenze.append({
                **voce_base,
                "descrizione": "Permessi retribuiti"
            })
            ore_retribuite += ore
            giorni_retribuiti += giorni
            totale_competenze += importo
            riepilogo["permessi_ore"] += float(ore)

        elif tipo_evento == "festivita":
            competenze.append({
                **voce_base,
                "descrizione": "Festività retribuita"
            })
            giorni_retribuiti += giorni
            totale_competenze += importo
            riepilogo["festivita_giorni"] += float(giorni)

        elif tipo_evento == "malattia":
            competenze.append({
                **voce_base,
                "descrizione": "Malattia"
            })
            giorni_retribuiti += giorni
            totale_competenze += importo
            riepilogo["malattia_giorni"] += float(giorni)

        elif tipo_evento == "assenza_non_retribuita":
            trattenute.append({
                **voce_base,
                "descrizione": "Assenza non retribuita"
            })
            totale_trattenute += importo
            riepilogo["assenza_ore"] += float(ore)

        elif tipo_evento == "anticipo_tfr":
            trattenute.append({
                **voce_base,
                "descrizione": "Anticipo TFR"
            })
            totale_trattenute += importo
            riepilogo["anticipo_tfr"] += float(importo)

        elif tipo_evento == "una_tantum":
            competenze.append({
                **voce_base,
                "descrizione": "Una tantum"
            })
            totale_competenze += importo
            riepilogo["una_tantum"] += float(importo)

        else:
            competenze.append({
                **voce_base,
                "descrizione": tipo_evento
            })
            totale_competenze += importo

    netto_eventi = euro(totale_competenze - totale_trattenute)

    return {
        "competenze": competenze,
        "trattenute": trattenute,
        "ore_retribuite": float(ore_retribuite),
        "giorni_retribuiti": float(giorni_retribuiti),
        "totale_competenze": float(euro(totale_competenze)),
        "totale_trattenute": float(euro(totale_trattenute)),
        "netto_eventi": float(netto_eventi),
        "riepilogo": riepilogo
    }