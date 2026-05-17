from dataclasses import dataclass
from datetime import date


@dataclass
class LavoratoreDomestico:
    nome: str
    cognome: str
    livello: str
    convivente: bool
    data_assunzione: date
    data_cessazione: date | None = None


@dataclass
class ContrattoDomestico:
    paga_lorda_annua: float
    ore_settimanali: float
    vitto_alloggio_annuo: float = 0
    scatti_anzianita_annui: float = 0
    superminimo_annuo: float = 0