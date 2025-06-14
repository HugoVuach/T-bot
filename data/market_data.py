# market_data.py

import websocket
import json
import threading
import yaml
import time
import pandas as pd

from data.esthetic.upgrade_form import  convert_to_dataframe


# Lecture de la clé API depuis config.yaml
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    FINNHUB_API_KEY = config['finnhub']['api_key']


data_buffer = []
last_stats = {}
latest_grouped_df = pd.DataFrame()
message_count = 1  # Compteur global pour arrêter après 5 messages



def on_message(ws, message):
    global message_count, data_buffer, latest_grouped_df

    # Décoder le JSON reçu
    data = json.loads(message)

    # Convertir en DataFrame
    df = convert_to_dataframe([data])

    # Ajouter le DataFrame au buffer
    data_buffer.append(df)

    print(f"\nMessage numéro {message_count} reçu :")
    print(df)
    print("-" * 80)
    grouped = calculate_btc_stats_per_second()
    print("#" * 80)


    message_count += 1
    if message_count >= 11:
        print("10 messages reçus. Arrêt du WebSocket.")
        ws.close()


def calculate_btc_stats_per_second():
    """
    Calcule les stats BTC par seconde et détecte si une seconde déjà vue est mise à jour.
    Affiche uniquement les secondes dont les valeurs changent.
    """
    global last_stats

    if not data_buffer:
        return

    full_df = pd.concat(data_buffer, ignore_index=True)

    # Extraire la seconde (HH:MM:SS)
    full_df['second'] = full_df['time'].str.slice(0, 8)

    # Groupby avec moyenne pondérée du prix
    grouped = full_df.groupby('second').apply(
        lambda g: pd.Series({
            'mean_price': (g['price'] * g['volume']).sum() / g['volume'].sum(),
            'total_volume': g['volume'].sum()
        })
    ).reset_index()

    for _, row in grouped.iterrows():
        sec = row['second']
        mean_price = round(row['mean_price'], 2)
        total_volume = round(row['total_volume'], 5)

        previous = last_stats.get(sec)

        if previous is None or previous['mean_price'] != mean_price or previous['total_volume'] != total_volume:
            print(f"📊 Prix moyen BTC ACTUALISÉ — {sec} : {mean_price} USDT | Volume échangé : {total_volume}")
            last_stats[sec] = {
                'mean_price': mean_price,
                'total_volume': total_volume
            }
    print(grouped)
    return grouped


def on_error(ws, error):
    """
    Appelée automatiquement par la librairie quand une erreur survient (exemple : perte de connexion, problème d’authentification).
    À améliorer plus tard : ajouter une logique de reconnexion automatique ou une alerte
    """
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    """
    Appelée quand la connexion WebSocket est fermée (volontairement ou non).
    À améliorer plus tard : planifier une reconnexion automatique pour continuer à recevoir les prix.
    """
    print("WebSocket closed. Trying to reconnect...")
    time.sleep(5)
    start_finnhub_ws()

def on_open(ws):
    """
    Appelée automatiquement quand la connexion WebSocket s’ouvre et que tu es prêt à envoyer des messages.
    """
    # Exemple : souscrire au ticker Apple & Tesla
    #symbols = ["AAPL", "TSLA"]
    symbols = ["BINANCE:BTCUSDT"]

    for symbol in symbols:
        subscribe_message = json.dumps({
            "type": "subscribe",
            "symbol": symbol
            })
        ws.send(subscribe_message)

def start_finnhub_ws():
    """
    Crée l'URL de connexion WebSocket en ajoutant ta clé API
    Crée l'objet WebSocketApp avec les callbacks (on_open, on_message, on_error, on_close).
    Lance la connexion dans un thread parallèle pour ne pas bloquer ton programme principal.
    Ce thread va tourner indéfiniment tant que la connexion est active
    """
    ws_url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    wst = threading.Thread(target=ws.run_forever)
    wst.start()

#if __name__ == "__main__":
  #  start_finnhub_ws()
