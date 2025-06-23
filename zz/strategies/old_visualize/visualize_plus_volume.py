# visualize_pyqtgraph_timeaxis.py

import sys
import threading
from collections import deque
import datetime

import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

from data.market_data import data_buffer, start_finnhub_ws

# 1) On démarre Finnhub dans un thread séparé
ws_thread = threading.Thread(target=start_finnhub_ws, daemon=True)
ws_thread.start()

# 2) Subclass pour formater les ticks en heure
class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(v).strftime("%H:%M:%S") for v in values]

class LiveGraph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTC/USDT – Prix et Volume avec heures")
        self.resize(1000, 800)

        # Container et layout
        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # 3) Deux axes X distincts mais formatés en heures
        time_axis_price  = TimeAxisItem(orientation='bottom')
        time_axis_volume = TimeAxisItem(orientation='bottom')

        # 4) Graphique prix
        self.price_plot = pg.PlotWidget(axisItems={'bottom': time_axis_price})
        self.price_plot.setTitle("Prix BTC/USDT")
        self.price_curve = self.price_plot.plot(pen=pg.mkPen('y', width=2))
        layout.addWidget(self.price_plot)

        # 5) Graphique volume (lié en X)
        self.volume_plot = pg.PlotWidget(axisItems={'bottom': time_axis_volume})
        self.volume_plot.setTitle("Volume")
        self.volume_curve = self.volume_plot.plot(pen=pg.mkPen('b', width=1))
        layout.addWidget(self.volume_plot)
        # Lien X commun
        self.volume_plot.plotItem.vb.setXLink(self.price_plot.plotItem.vb)

        # Buffers pour rolling data
        self.timestamps = deque(maxlen=200)
        self.prices     = deque(maxlen=200)
        self.volumes    = deque(maxlen=200)

        # 6) Timer pour update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(500)

    def update_plots(self):
        # Récupération des nouveaux trades
        while data_buffer:
            msg = data_buffer.pop(0)
            if msg.get("type") == "trade":
                for d in msg["data"]:
                    t = d["t"] / 1000.0
                    self.timestamps.append(t)
                    self.prices.append(d["p"])
                    self.volumes.append(d["v"])

        if not self.timestamps:
            return

        x = list(self.timestamps)
        self.price_curve.setData(x=x, y=list(self.prices))
        self.volume_curve.setData(x=x, y=list(self.volumes))

        # Rafraîchir les axes
        self.price_plot.enableAutoRange('xy', True)
        self.volume_plot.enableAutoRange('xy', True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LiveGraph()
    win.show()
    sys.exit(app.exec_())
