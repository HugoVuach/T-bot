# data/market_data.py

import websocket
import json
import threading
import yaml
import time


# Lecture de la clé API depuis config.yaml
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    FINNHUB_API_KEY = config['finnhub']['api_key']


    data_buffer = []

def on_message(ws, message):
    """
    Fonction appelée à chaque fois qu'un message est reçu du WebSocket Finnhub.Cette fonction est appelée 
    automatiquement à chaque fois qu’un message arrive via le WebSocket

        ws : l'objet WebSocket actif
        message : le message reçu du WebSocket

    À améliorer plus tard : remplacer print(...) par une fonction qui alimente un buffer ou qui envoie la donnée dans ton moteur de stratégie.
    """
    data = json.loads(message)
    data_buffer.append(data)
    print("Nouveau message reçu :", data)  # Ajoute ce print pour debug

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
