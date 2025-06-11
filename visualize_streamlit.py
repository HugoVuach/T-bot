# visualize_streamlit.py

import streamlit as st
import pandas as pd
import time
import threading
from data.market_data import data_buffer, start_finnhub_ws

# Fonction de collecte des données en arrière-plan
def run_websocket():
    start_finnhub_ws()

# Démarrer le WebSocket dans un thread parallèle
ws_thread = threading.Thread(target=run_websocket)
ws_thread.daemon = True
ws_thread.start()

st.title("📈 Visualisation des prix en temps réel (BTCUSDT)")

# Initialiser un DataFrame vide
df = pd.DataFrame(columns=["symbol", "price", "timestamp", "volume"])

# Boucle principale Streamlit
while True:
    # Traiter les nouvelles données du buffer
    while data_buffer:
        msg = data_buffer.pop(0)
        if msg["type"] == "trade":
            for d in msg["data"]:
                new_row = {
                    "symbol": d.get("s"),
                    "price": d.get("p"),
                    "timestamp": pd.to_datetime(d.get("t"), unit="ms"),
                    "volume": d.get("v")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    # Afficher les dernières données
    if not df.empty:
        st.line_chart(df[["timestamp", "price"]].set_index("timestamp"))

    time.sleep(1)
