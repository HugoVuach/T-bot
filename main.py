# main.py

from data.market_data import start_finnhub_ws
from data.data_manager import start_data_manager
import threading

if __name__ == "__main__":
    # Démarrer le WebSocket
    start_finnhub_ws()

    # Démarrer le DataManager dans un thread séparé
    data_manager_thread = threading.Thread(target=start_data_manager)
    data_manager_thread.start()

    # Tu peux rajouter d'autres threads ici (ex. dashboard)
