# visualize_data.py

import pandas as pd
import time
from data.market_data import data_buffer, start_finnhub_ws

def visualize_data():
    """
    Démarre le WebSocket, collecte les données, puis affiche un résumé.
    s : Symbole de l'actif
    p : Le prix de l'actif
    t : Horodatage en millisecondes (Epoch time)
    v : Le volume échangé
    """
    # Démarre la connexion WebSocket
    start_finnhub_ws()

    # Attend quelques secondes pour remplir le buffer
    print("Collecte des données en cours...")
    time.sleep(25)  # Ajuste si tu veux plus ou moins de données

    # Transforme le buffer en DataFrame
    records = []
    for msg in data_buffer:
        if msg["type"] == "trade":
            for d in msg["data"]:
                records.append({
                    "symbol": d.get("symbol"),
                    "price": d.get("price"),
                    "timestamp": pd.to_datetime(d.get("timestamp"), unit="ms"),
                    "volume": d.get("volume")
                })

    # Crée un DataFrame
    if records:
        df = pd.DataFrame(records)
        print("\nDonnées collectées :")
        print(df)
    else:
        print("Aucune donnée collectée.")

if __name__ == "__main__":
    visualize_data()
