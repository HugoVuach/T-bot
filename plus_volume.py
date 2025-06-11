import sys
import threading
from collections import deque

import pandas as pd
import pyqtgraph as pg
from pyqtgraph.graphicsItems.DateAxisItem import DateAxisItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

from data.market_data import data_buffer, start_finnhub_ws

# 1) Démarrer le WebSocket dans un thread
ws_thread = threading.Thread(target=start_finnhub_ws, daemon=True)
ws_thread.start()

class LiveGraph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTC/USDT – Prix et Volume (séparé)")
        self.resize(1000, 800)

        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # 2) Création de deux axes X DateAxisItem distincts
        date_axis_price  = DateAxisItem(orientation='bottom')
        date_axis_volume = DateAxisItem(orientation='bottom')

        # 3) PlotWidget pour le prix
        self.price_plot = pg.PlotWidget(axisItems={'bottom': date_axis_price})
        self.price_plot.setTitle("Prix BTC/USDT")
        self.price_curve = self.price_plot.plot(pen=pg.mkPen('y', width=2))
        layout.addWidget(self.price_plot)

        # 4) PlotWidget pour le volume, on le lie à l'axe X du prix
        self.volume_plot = pg.PlotWidget(axisItems={'bottom': date_axis_volume})
        self.volume_plot.setTitle("Volume")
        self.volume_curve = self.volume_plot.plot(pen=pg.mkPen('b', width=1))
        layout.addWidget(self.volume_plot)

        # Lier l’axe X de volume à celui de price
        self.volume_plot.plotItem.vb.setXLink(self.price_plot.plotItem.vb)

        # 5) Rolling windows pour stocker les derniers points
        self.timestamps = deque(maxlen=200)
        self.prices     = deque(maxlen=200)
        self.volumes    = deque(maxlen=200)

        # 6) Timer pour mettre à jour toutes les 500 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(500)

    def update_plots(self):
        # 7) Récupérer toutes les nouvelles données du buffer
        while data_buffer:
            msg = data_buffer.pop(0)
            if msg.get("type") == "trade":
                for d in msg["data"]:
                    ts = d["t"] / 1000.0  # convertir ms → s epoch
                    self.timestamps.append(ts)
                    self.prices.append(d["p"])
                    self.volumes.append(d["v"])

        # 8) Si on n’a pas de points, on sort
        if not self.timestamps:
            return

        # Préparer les données pour le tracé
        x = list(self.timestamps)
        y_price = list(self.prices)
        y_vol   = list(self.volumes)

        # 9) Mettre à jour les courbes
        self.price_curve.setData(x=x, y=y_price)
        self.volume_curve.setData(x=x, y=y_vol)

        # Ajuster automatiquement les axes
        self.price_plot.enableAutoRange('xy', True)
        self.volume_plot.enableAutoRange('xy', True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LiveGraph()
    win.show()
    sys.exit(app.exec_())
