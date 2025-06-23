import sys
import pandas as pd
import plotly.graph_objects as go
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer
import threading
from data.market_data import data_buffer, start_finnhub_ws
import plotly.io as pio

# Démarre le WebSocket dans un thread
ws_thread = threading.Thread(target=start_finnhub_ws)
ws_thread.daemon = True
ws_thread.start()

class LiveGraph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTC/USDT - Visualisation en temps réel")
        self.setGeometry(50, 50, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)

        # Rafraîchir le graphique toutes les 3 secondes
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(3000)  # ms

        self.records = []

    def update_plot(self):
        while data_buffer:
            msg = data_buffer.pop(0)
            if msg["type"] == "trade":
                for d in msg["data"]:
                    self.records.append({
                        "timestamp": pd.to_datetime(d.get("t"), unit="ms"),
                        "price": d.get("p")
                    })

        if not self.records:
            print("Pas encore de données pour afficher le graphique.")
            return

        df = pd.DataFrame(self.records)
        df.set_index("timestamp", inplace=True)

        if df.shape[0] < 2:
            print("Pas encore assez de données pour générer une bougie.")
            return

        df = df['price'].resample("10S").ohlc().dropna()


        if df.empty:
            print("Pas encore assez de données pour générer des OHLC.")
            return

        print(f"Nombre de bougies : {len(df)}")
        print(df.tail())

        # Aplatir les colonnes
        #df.columns = df.columns.get_level_values(1)

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']
                )
            ]
        )

        fig.update_layout(title="BTC/USDT - Graphique interactif")

        # Générer le HTML et l'afficher dans le widget WebEngine
        html = pio.to_html(fig, full_html=False)
        self.browser.setHtml(html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveGraph()
    window.show()
    sys.exit(app.exec_())
