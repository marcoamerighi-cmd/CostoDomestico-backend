COEFFICIENTI_TFR = {
    2016: {
        1: 0.125000,
        2: 0.250000,
        3: 0.375000,
        4: 0.500000,
        5: 0.625000,
        6: 0.750000,
        7: 0.945093,
        8: 1.220234,
        9: 1.195000,
        10: 1.320000,
        11: 1.445000,
        12: 1.795300
    },
    2017: {
        1: 0.349327,
        2: 0.773400,
        3: 0.898430,
        4: 1.247757,
        5: 1.223205
    },
    2018: {
        7: 1.913576,
        8: 2.335312,
        9: 2.089392,
        10: 2.214392,
        11: 2.191024,
        12: 2.241840
    },
    2019: {
        1: 0.198457,
        2: 0.396915,
        3: 0.668830,
        4: 0.867287,
        5: 1.065744,
        6: 1.190744,
        7: 1.315744,
        8: 1.808031,
        9: 1.418830,
        10: 1.470372,
        11: 1.521915,
        12: 1.793830
    },
    2020: {
        1: 0.271341,
        2: 0.250000,
        3: 0.448171,
        4: 0.500000,
        5: 0.625000,
        6: 0.750000,
        7: 0.875000,
        8: 1.000000,
        9: 1.125000,
        10: 1.250000,
        11: 1.375000,
        12: 1.500000
    },
    2021: {
        1: 0.564883,
        2: 0.763196,
        3: 1.108138,
        4: 1.526393,
        5: 1.578079,
        6: 1.849707,
        7: 2.267962,
        8: 2.759531,
        9: 2.737903,
        10: 3.302786,
        11: 3.867669,
        12: 4.359238
    },
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
        7: 1.873336,
        8: 1.998336,
        9: 2.060940,
        10: 1.998752,
        11: 2.061356,
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
    anno_corrente = anno

    while anno_corrente >= 2016:

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

def get_ultimo_coefficiente_disponibile() -> float:
    anni_disponibili = sorted(COEFFICIENTI_TFR.keys())

    ultimo_anno = anni_disponibili[-1]
    mesi_disponibili = sorted(COEFFICIENTI_TFR[ultimo_anno].keys())

    ultimo_mese = mesi_disponibili[-1]

    return COEFFICIENTI_TFR[ultimo_anno][ultimo_mese]


def get_coefficiente_tfr(anno: int, mese: int) -> float:
    if anno in COEFFICIENTI_TFR:
        mesi_anno = COEFFICIENTI_TFR[anno]

        if mese in mesi_anno:
            return mesi_anno[mese]

        mesi_precedenti = [
            mese_disponibile
            for mese_disponibile in mesi_anno.keys()
            if mese_disponibile <= mese
        ]

        if mesi_precedenti:
            ultimo_mese_disponibile = max(mesi_precedenti)
            return mesi_anno[ultimo_mese_disponibile]

    return get_ultimo_coefficiente_disponibile()