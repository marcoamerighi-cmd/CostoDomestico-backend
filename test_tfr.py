from database.tfr_repository import leggi_calcoli_tfr

calcoli = leggi_calcoli_tfr()

print("=== STORICO TFR ===")

for calcolo in calcoli:

    print("\n---------------------------")

    print(f"ID Calcolo: {calcolo[0]}")
    print(f"Lavoratore: {calcolo[1]} {calcolo[2]}")
    print(f"Mesi utili: {calcolo[3]}")
    print(f"Retribuzione utile: € {calcolo[4]}")
    print(f"Quota TFR: € {calcolo[5]}")
    print(f"Rivalutazione: € {calcolo[6]}")
    print(f"Anticipi: € {calcolo[7]}")
    print(f"Totale da liquidare: € {calcolo[8]}")
    print(f"Data calcolo: {calcolo[9]}")
    from database.tfr_repository import leggi_calcoli_tfr

calcoli = leggi_calcoli_tfr()

print("=== STORICO TFR ===")

for calcolo in calcoli:

    print("\n----------------")

    print(f"ID: {calcolo[0]}")
    print(f"Lavoratore: {calcolo[1]} {calcolo[2]}")
    print(f"Quota TFR: € {calcolo[5]}")
    print(f"Totale: € {calcolo[8]}")