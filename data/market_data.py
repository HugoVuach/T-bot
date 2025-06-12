# market_data.py

import websocket
import json
import threading
import yaml
import time

from esthetic.upgrade_form import pretty_print_data, convert_to_dataframe


# Lecture de la clé API depuis config.yaml
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    FINNHUB_API_KEY = config['finnhub']['api_key']


data_buffer = []
message_count = 1  # Compteur global pour arrêter après 5 messages



def on_message(ws, message):
    global message_count, data_buffer

    # Décoder le JSON reçu
    data = json.loads(message)

    # Convertir en DataFrame
    df = convert_to_dataframe([data])

    # Ajouter le DataFrame au buffer
    data_buffer.append(df)

    print(f"\nMessage numéro {message_count} reçu :")
    print(df)
    print("#" * 80)

    # Calculer et afficher la moyenne par seconde
    calculate_and_print_average_per_second()

    message_count += 1
    if message_count >= 6:
        print("5 messages reçus. Arrêt du WebSocket.")
        ws.close()


    message_count += 1
    if message_count >= 6:
        print("5 messages reçus. Arrêt du WebSocket.")
        ws.close()


def calculate_and_print_average_per_second():
    """
    Concatène tous les trades reçus et calcule la moyenne du prix par seconde.
    """
    if not data_buffer:
        return

    # Concaténer tous les DataFrames du buffer
    full_df = pd.concat(data_buffer, ignore_index=True)

    # Extraire la seconde à partir de 'time'
    # On tronque au format "HH:MM:SS"
    full_df['second'] = full_df['time'].str.slice(0, 8)

    # Calculer la moyenne du prix par seconde
    avg_per_second = full_df.groupby('second')['price'].mean()

    # Afficher la dernière seconde seulement (ou tout si tu veux)
    last_second = avg_per_second.index[-1]
    last_avg = avg_per_second.iloc[-1]
    print(f"\n🟢 Moyenne BTC seconde {last_second} : {last_avg:.2f}")
    print("#" * 80

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

if __name__ == "__main__":
    start_finnhub_ws()
