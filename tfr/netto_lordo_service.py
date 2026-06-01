from tfr.contributi_domestici import (
    contributo_lavoratore_orario
)


def converti_netto_in_lordo(
    netto_annuo: float,
    anno: int,
    livello: str,
    ore_settimanali: float,
    convivente: bool,
    mesi_utili: int = 12
) -> float:

    if netto_annuo <= 0:
        return 0

    settimane_periodo = 52 / 12 * mesi_utili
    ore_annue = ore_settimanali * settimane_periodo

    if ore_annue <= 0:
        return float(f"{netto_annuo:.2f}")

    lordo_annuo = netto_annuo

    for _ in range(10):
        paga_oraria_lorda = lordo_annuo / ore_annue

        contributo_orario = contributo_lavoratore_orario(
            anno=anno,
            retribuzione_oraria_lorda=paga_oraria_lorda,
            ore_settimanali=ore_settimanali
        )

        contributi_lavoratore = contributo_orario * ore_annue

        nuovo_lordo = netto_annuo + contributi_lavoratore

        if abs(nuovo_lordo - lordo_annuo) < 0.01:
            break

        lordo_annuo = nuovo_lordo

    return float(f"{lordo_annuo:.2f}")