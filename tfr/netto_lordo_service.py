# Tabelle contributive semplificate lavoro domestico 2026
# Quota contributiva a carico lavoratore


def contributo_lavoratore_orario_2026(
    retribuzione_oraria_lorda: float,
    ore_settimanali: float
) -> float:

    if ore_settimanali > 24:
        return 0.31

    if retribuzione_oraria_lorda <= 9.61:
        return 0.43

    if retribuzione_oraria_lorda <= 11.70:
        return 0.48

    return 0.59


def converti_netto_in_lordo(
    netto_annuo: float,
    livello: str,
    ore_settimanali: float,
    convivente: bool
) -> float:

    if netto_annuo <= 0:
        return 0

    settimane_annue = 52
    ore_annue = ore_settimanali * settimane_annue

    if ore_annue <= 0:
        return netto_annuo

    paga_oraria_netta = netto_annuo / ore_annue

    lordo_orario_stimato = paga_oraria_netta + 0.50

    contributo_orario = contributo_lavoratore_orario_2026(
        lordo_orario_stimato,
        ore_settimanali
    )

    paga_oraria_lorda = paga_oraria_netta + contributo_orario

    lordo_annuo = paga_oraria_lorda * ore_annue

    if convivente:
        lordo_annuo += 2200

    if livello in ["D", "DS"]:
        lordo_annuo *= 1.02

    return round(lordo_annuo, 2)