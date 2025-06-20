import threading


from data.market_data import  start_finnhub_ws

# 1) On démarre Finnhub dans un thread séparé
ws_thread = threading.Thread(target=start_finnhub_ws, daemon=True)
ws_thread.start()
