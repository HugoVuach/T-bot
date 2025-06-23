import sys
import pandas as pd
import plotly.graph_objects as go
import threading
from collections import deque

import pyqtgraph as pg
from pyqtgraph.graphicsItems.DateAxisItem import DateAxisItem
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from data.market_data import data_buffer, start_finnhub_ws

# 1. Démarrage du WebSocket
ws_thread = threading.Thread(target=start_finnhub_ws, daemon=True)
ws_thread.start()

class LiveGraph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTC/USDT – Temps réel (PyQtGraph)")
        self.resize(1600, 800)

        # 2. Utiliser DateAxisItem pour l'axe X
        date_axis = DateAxisItem(orientation='bottom')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
        self.setCentralWidget(self.plot_widget)

        # 3. Stockage rolling window
        self.timestamps = deque(maxlen=400)  # stocker timestamps epoch
        self.prices     = deque(maxlen=400)
        

        # 4. Courbe
        self.curve = self.plot_widget.plot(pen=pg.mkPen('y', width=2))

        # 5. Timer d'update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(500)  # toutes les 500 ms

    def update_plot(self):
        # 6. Lire data_buffer
        while data_buffer:
            msg = data_buffer.pop(0)
            if msg["type"] == "trade":
                for d in msg["data"]:
                    # convertir ms -> s epoch
                    t = d["t"] / 1000.0
                    self.timestamps.append(t)
                    self.prices.append(d["p"])

        # 7. Mettre à jour la courbe  
        if self.prices:
            x = list(self.timestamps)
            y = list(self.prices)
            self.curve.setData(x=x, y=y)
            self.plot_widget.enableAutoRange('xy', True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LiveGraph()
    win.show()
    sys.exit(app.exec_())
