from decimal import Decimal

from services.calcolo_eventi_cedolino import elabora_eventi_cedolino


def test_calcolo_eventi_cedolino():
    eventi = [
        (
            "id1",
            "mese1",
            "rapporto1",
            "lavoro_ordinario",
            "2026-06-01",
            "2026-06-30",
            Decimal("80"),
            Decimal("20"),
            Decimal("680.00"),
            "Ore ordinarie"
        ),
        (
            "id2",
            "mese1",
            "rapporto1",
            "ferie",
            "2026-06-10",
            "2026-06-11",
            Decimal("8"),
            Decimal("2"),
            Decimal("68.00"),
            "Ferie retribuite"
        ),
        (
            "id3",
            "mese1",
            "rapporto1",
            "assenza_non_retribuita",
            "2026-06-20",
            "2026-06-20",
            Decimal("4"),
            Decimal("1"),
            Decimal("34.00"),
            "Assenza"
        ),
        (
            "id4",
            "mese1",
            "rapporto1",
            "una_tantum",
            "2026-06-30",
            None,
            Decimal("0"),
            Decimal("0"),
            Decimal("50.00"),
            "Premio"
        )
    ]

    risultato = elabora_eventi_cedolino(eventi)

    print("Risultato eventi:", risultato)


if __name__ == "__main__":
    test_calcolo_eventi_cedolino()