import threading
import time
from data import market_data
from data.market_data import start_finnhub_ws

from datetime import datetime



# 1) On démarre le WebSocket dans un thread
ws_thread = threading.Thread(target=start_finnhub_ws, daemon=True)
ws_thread.start()

# 2) Boucle pour surveiller les mises à jour de `grouped`
last_seen = None

while True:
    current = market_data.grouped

    if current is not None and not current.equals(last_seen if last_seen is not None else current.iloc[0:0]):
        print("🔁 Nouvelle mise à jour de grouped :")
        print(current)
        print("=" * 80)
        last_seen = current.copy()

    time.sleep(1)  # Réduit la charge CPU ; ajuste si nécessaire
