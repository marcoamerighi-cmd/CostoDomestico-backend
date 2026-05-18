CONTRIBUTI_DOMESTICI = {
    2025: {
        "tempo_indeterminato": {
            "fino_24_ore": [
                {
                    "min": 0,
                    "max": 9.48,
                    "quota_lavoratore": 0.42,
                    "totale_con_cuaf": 1.79,
                    "totale_senza_cuaf": 1.80
                },
                {
                    "min": 9.49,
                    "max": 11.54,
                    "quota_lavoratore": 0.48,
                    "totale_con_cuaf": 2.03,
                    "totale_senza_cuaf": 2.04
                },
                {
                    "min": 11.55,
                    "max": 999,
                    "quota_lavoratore": 0.58,
                    "totale_con_cuaf": 2.47,
                    "totale_senza_cuaf": 2.48
                }
            ],
            "oltre_24_ore": {
                "quota_lavoratore": 0.31,
                "totale_con_cuaf": 1.31,
                "totale_senza_cuaf": 1.31
            }
        }
    },

    2026: {
        "tempo_indeterminato": {
            "fino_24_ore": [
                {
                    "min": 0,
                    "max": 9.61,
                    "quota_lavoratore": 0.43,
                    "totale_con_cuaf": 1.70,
                    "totale_senza_cuaf": 1.71
                },
                {
                    "min": 9.62,
                    "max": 11.70,
                    "quota_lavoratore": 0.48,
                    "totale_con_cuaf": 1.92,
                    "totale_senza_cuaf": 1.93
                },
                {
                    "min": 11.71,
                    "max": 999,
                    "quota_lavoratore": 0.59,
                    "totale_con_cuaf": 2.34,
                    "totale_senza_cuaf": 2.35
                }
            ],
            "oltre_24_ore": {
                "quota_lavoratore": 0.31,
                "totale_con_cuaf": 1.32,
                "totale_senza_cuaf": 1.33
            }
        }
    }
}


def trova_tabella_contributiva(
    anno: int
) -> dict:
    if anno in CONTRIBUTI_DOMESTICI:
        return CONTRIBUTI_DOMESTICI[anno]

    anni_disponibili = sorted(CONTRIBUTI_DOMESTICI.keys())

    for anno_disponibile in reversed(anni_disponibili):
        if anno_disponibile <= anno:
            return CONTRIBUTI_DOMESTICI[anno_disponibile]

    return CONTRIBUTI_DOMESTICI[anni_disponibili[0]]


def contributo_lavoratore_orario(
    anno: int,
    retribuzione_oraria_lorda: float,
    ore_settimanali: float,
    tempo_determinato: bool = False
) -> float:
    tabella = trova_tabella_contributiva(anno)

    dati = tabella["tempo_indeterminato"]

    if ore_settimanali > 24:
        return dati["oltre_24_ore"]["quota_lavoratore"]

    for fascia in dati["fino_24_ore"]:
        if (
            retribuzione_oraria_lorda >= fascia["min"]
            and retribuzione_oraria_lorda <= fascia["max"]
        ):
            return fascia["quota_lavoratore"]

    return dati["fino_24_ore"][-1]["quota_lavoratore"]


def contributo_totale_orario_datore(
    anno: int,
    retribuzione_oraria_lorda: float,
    ore_settimanali: float,
    con_cuaf: bool = True,
    tempo_determinato: bool = False
) -> float:
    tabella = trova_tabella_contributiva(anno)

    dati = tabella["tempo_indeterminato"]

    chiave = "totale_con_cuaf" if con_cuaf else "totale_senza_cuaf"

    if ore_settimanali > 24:
        return dati["oltre_24_ore"][chiave]

    for fascia in dati["fino_24_ore"]:
        if (
            retribuzione_oraria_lorda >= fascia["min"]
            and retribuzione_oraria_lorda <= fascia["max"]
        ):
            return fascia[chiave]

    return dati["fino_24_ore"][-1][chiave]