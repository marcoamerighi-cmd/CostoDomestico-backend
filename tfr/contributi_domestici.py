import json
from pathlib import Path
CONTRIBUTI_DOMESTICI = {
    2016: {
        "fino_24_ore": [
            {"min": 0, "max": 7.88, "quota_lavoratore": 0.35},
            {"min": 7.89, "max": 9.59, "quota_lavoratore": 0.40},
            {"min": 9.60, "max": 999, "quota_lavoratore": 0.48},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.25}
    },
    2017: {
        "fino_24_ore": [
            {"min": 0, "max": 7.88, "quota_lavoratore": 0.35},
            {"min": 7.89, "max": 9.59, "quota_lavoratore": 0.40},
            {"min": 9.60, "max": 999, "quota_lavoratore": 0.48},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.25}
    },
    2018: {
        "fino_24_ore": [
            {"min": 0, "max": 7.97, "quota_lavoratore": 0.35},
            {"min": 7.98, "max": 9.70, "quota_lavoratore": 0.40},
            {"min": 9.71, "max": 999, "quota_lavoratore": 0.49},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.26}
    },
    2019: {
        "fino_24_ore": [
            {"min": 0, "max": 8.06, "quota_lavoratore": 0.36},
            {"min": 8.07, "max": 9.81, "quota_lavoratore": 0.40},
            {"min": 9.82, "max": 999, "quota_lavoratore": 0.49},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.26}
    },
    2020: {
        "fino_24_ore": [
            {"min": 0, "max": 8.10, "quota_lavoratore": 0.36},
            {"min": 8.11, "max": 9.86, "quota_lavoratore": 0.41},
            {"min": 9.87, "max": 999, "quota_lavoratore": 0.49},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.26}
    },
    2021: {
        "fino_24_ore": [
            {"min": 0, "max": 8.10, "quota_lavoratore": 0.36},
            {"min": 8.11, "max": 9.86, "quota_lavoratore": 0.41},
            {"min": 9.87, "max": 999, "quota_lavoratore": 0.49},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.26}
    },
    2022: {
        "fino_24_ore": [
            {"min": 0, "max": 8.25, "quota_lavoratore": 0.37},
            {"min": 8.26, "max": 10.05, "quota_lavoratore": 0.41},
            {"min": 10.06, "max": 999, "quota_lavoratore": 0.50},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.27}
    },
    2023: {
        "fino_24_ore": [
            {"min": 0, "max": 8.92, "quota_lavoratore": 0.40},
            {"min": 8.93, "max": 10.86, "quota_lavoratore": 0.45},
            {"min": 10.87, "max": 999, "quota_lavoratore": 0.55},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.29}
    },
    2024: {
        "fino_24_ore": [
            {"min": 0, "max": 9.40, "quota_lavoratore": 0.42},
            {"min": 9.41, "max": 11.45, "quota_lavoratore": 0.47},
            {"min": 11.46, "max": 999, "quota_lavoratore": 0.57},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.30}
    },
    2025: {
        "fino_24_ore": [
            {"min": 0, "max": 9.48, "quota_lavoratore": 0.42},
            {"min": 9.49, "max": 11.54, "quota_lavoratore": 0.48},
            {"min": 11.55, "max": 999, "quota_lavoratore": 0.58},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.31}
    },
    2026: {
        "fino_24_ore": [
            {"min": 0, "max": 9.61, "quota_lavoratore": 0.43},
            {"min": 9.62, "max": 11.70, "quota_lavoratore": 0.48},
            {"min": 11.71, "max": 999, "quota_lavoratore": 0.59},
        ],
        "oltre_24_ore": {"quota_lavoratore": 0.31}
    }
}


def trova_tabella_contributiva(anno: int) -> dict:
    if anno in CONTRIBUTI_DOMESTICI:
        return CONTRIBUTI_DOMESTICI[anno]

    anni = sorted(CONTRIBUTI_DOMESTICI.keys())

    for anno_disponibile in reversed(anni):
        if anno_disponibile <= anno:
            return CONTRIBUTI_DOMESTICI[anno_disponibile]

    return CONTRIBUTI_DOMESTICI[anni[0]]


def contributo_lavoratore_orario(
    anno: int,
    retribuzione_oraria_lorda: float,
    ore_settimanali: float,
    tempo_determinato: bool = False
) -> float:
    tabella = get_contributi_domestici(anno)

    if ore_settimanali > 24:
        return tabella["oltre_24_ore"]["quota_lavoratore"]

    for fascia in tabella["fino_24_ore"]:
        if (
            retribuzione_oraria_lorda >= fascia["min"]
            and retribuzione_oraria_lorda <= fascia["max"]
        ):
            return fascia["quota_lavoratore"]

    return tabella["fino_24_ore"][-1]["quota_lavoratore"]

def get_anno_contributi_disponibile(anno: int) -> int:
    anni_disponibili = sorted(CONTRIBUTI_DOMESTICI.keys())

    if anno in CONTRIBUTI_DOMESTICI:
        return anno

    anni_precedenti = [
        anno_disponibile
        for anno_disponibile in anni_disponibili
        if anno_disponibile <= anno
    ]

    if anni_precedenti:
        return anni_precedenti[-1]

    return anni_disponibili[0]


def carica_contributi_json() -> dict:
    percorso = (
        Path(__file__).parent
        / "contributi_inps_lavoro_domestico.json"
    )

    if not percorso.exists():
        return {}

    try:
        with open(percorso, "r", encoding="utf-8") as file:
            dati = json.load(file)

        return {
            int(anno): valore
            for anno, valore in dati.items()
        }

    except Exception:
        return {}
    

def get_contributi_domestici(anno: int) -> dict:
    contributi_json = carica_contributi_json()

    if contributi_json:
        contributi_uniti = {
            **CONTRIBUTI_DOMESTICI,
            **contributi_json
        }

        anni_disponibili = sorted(contributi_uniti.keys())

        if anno in contributi_uniti:
            return contributi_uniti[anno]

        anni_precedenti = [
            anno_disponibile
            for anno_disponibile in anni_disponibili
            if anno_disponibile <= anno
        ]

        if anni_precedenti:
            return contributi_uniti[anni_precedenti[-1]]

        return contributi_uniti[anni_disponibili[0]]

    anno_disponibile = get_anno_contributi_disponibile(anno)
    return CONTRIBUTI_DOMESTICI[anno_disponibile]