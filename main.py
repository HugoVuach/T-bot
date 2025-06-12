import threading
from data.market_data import start_finnhub_ws
from market_data_visualizer import run_visualizer

if __name__ == "__main__":
    # Démarrer la WebSocket Finnhub dans un thread
    threading.Thread(target=start_finnhub_ws, daemon=True).start()

    # Démarrer la visualisation dans le thread principal
    run_visualizer()
