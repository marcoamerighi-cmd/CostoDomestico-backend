COEFFICIENTI_TFR = {
    2022: {
        1: 1.184322,
        2: 2.086158,
        3: 2.987994,
        4: 2.971751,
        5: 3.732345,
        6: 4.775424,
        7: 5.182910,
        8: 5.943503,
        9: 6.280367,
        10: 9.018362,
        11: 9.637712,
        12: 9.974576
    },
    2023: {
        1: 0.188452,
        2: 0.440355,
        3: 0.375000,
        4: 0.626904,
        5: 0.878807,
        6: 1.003807,
        12: 1.944162
    },
    2024: {
        12: 2.320017
    },
    2025: {
        1: 0.561772,
        12: 2.311148
    },
    2026: {
        1: 0.363025,
        2: 0.862716,
        3: 1.437346,
        4: 2.311728
    }
}


def trova_coefficiente_tfr(
    anno: int,
    mese: int
) -> float:
    """
    Restituisce il coefficiente TFR disponibile per anno/mese.
    Se il mese richiesto non è presente, usa il mese precedente disponibile.
    Se l'anno non è presente, prova l'anno precedente.
    """

    anno_corrente = anno

    while anno_corrente >= 2022:

        coefficienti_anno = COEFFICIENTI_TFR.get(
            anno_corrente,
            {}
        )

        mese_partenza = mese if anno_corrente == anno else 12

        for mese_corrente in range(mese_partenza, 0, -1):
            if mese_corrente in coefficienti_anno:
                return coefficienti_anno[mese_corrente]

        anno_corrente -= 1

    return 0