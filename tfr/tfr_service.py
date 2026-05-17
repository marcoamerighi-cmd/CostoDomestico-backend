from tfr.tfr_calculator import (
    calcola_mesi_utili,
    calcola_tfr_proporzionato,
    calcola_coefficiente_rivalutazione,
    calcola_rivalutazione_tfr,
    calcola_tfr_finale
)


def calcola_tfr_lavoratore(
    lavoratore,
    contratto,
    variazione_istat_foi: float = 0,
    anticipi: float = 0
) -> dict:

    data_fine = lavoratore.data_cessazione

    if data_fine is None:
        raise ValueError("Data cessazione mancante")

    mesi = calcola_mesi_utili(
        lavoratore.data_assunzione,
        data_fine
    )

    tfr = calcola_tfr_proporzionato(
        paga_lorda_annua=contratto.paga_lorda_annua,
        mesi_utili=mesi,
        vitto_alloggio=contratto.vitto_alloggio_annuo,
        scatti_anzianita=contratto.scatti_anzianita_annui,
        superminimo=contratto.superminimo_annuo
    )

    coefficiente = calcola_coefficiente_rivalutazione(
        variazione_istat_foi
    )

    rivalutazione = calcola_rivalutazione_tfr(
        tfr_pregresso=tfr["quota_tfr"],
        coefficiente=coefficiente
    )

    finale = calcola_tfr_finale(
        tfr_maturato=tfr["quota_tfr"],
        rivalutazione=rivalutazione,
        anticipi=anticipi
    )

    return {
        "lavoratore": f"{lavoratore.nome} {lavoratore.cognome}",
        "livello": lavoratore.livello,
        "convivente": lavoratore.convivente,
        "mesi_utili": mesi,
        "dettaglio_tfr": tfr,
        "coefficiente_rivalutazione": coefficiente,
        "rivalutazione": rivalutazione,
        "liquidazione": finale
    }