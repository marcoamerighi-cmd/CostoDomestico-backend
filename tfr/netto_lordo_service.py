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
        return round(netto_annuo, 2)

    lordo_annuo = netto_annuo

    for _ in range(10):
        paga_oraria_lorda = lordo_annuo / ore_annue

        contributo_orario = contributo_lavoratore_orario_2026(
            paga_oraria_lorda,
            ore_settimanali
        )

        contributi_lavoratore = contributo_orario * ore_annue

        nuovo_lordo = netto_annuo + contributi_lavoratore

        if abs(nuovo_lordo - lordo_annuo) < 0.01:
            break

        lordo_annuo = nuovo_lordo

    return float(f"{lordo_annuo:.2f}")