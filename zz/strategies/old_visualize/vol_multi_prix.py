# vol_multi_prix.py

import sys
import threading
from collections import deque
import datetime

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

from data.market_data import data_buffer, start_finnhub_ws

# Démarre le WebSocket dans un thread séparé
ws_thread = threading.Thread(target=start_finnhub_ws, daemon=True)
ws_thread.start()

# Axe X personnalisé en HH:MM:SS
class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(v).strftime("%H:%M:%S") for v in values]

class LiveGraph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTC/USDT – Prix, Volume & Moyennes")
        self.resize(1000, 800)

        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # --- Instancier deux axes X distincts ---
        time_axis_price  = TimeAxisItem(orientation='bottom')
        time_axis_volume = TimeAxisItem(orientation='bottom')

        # Graphique prix
        self.price_plot = pg.PlotWidget(axisItems={'bottom': time_axis_price})
        self.price_plot.setTitle("Prix BTC/USDT")
        self.price_curve  = self.price_plot.plot(pen=pg.mkPen('y', width=2), name="Last")
        self.mid_curve    = self.price_plot.plot(pen=pg.mkPen('r', width=2), name="Mid")
        self.vwap_curve   = self.price_plot.plot(pen=pg.mkPen('g', width=2), name="VWAP")
        self.ohlc_curve   = self.price_plot.plot(pen=pg.mkPen('w', width=2), name="Close OHLC")
        layout.addWidget(self.price_plot)

        # Graphique volume
        self.volume_plot = pg.PlotWidget(axisItems={'bottom': time_axis_volume})
        self.volume_plot.setTitle("Volume")
        self.volume_curve = self.volume_plot.plot(pen=pg.mkPen('b', width=1))
        layout.addWidget(self.volume_plot)

        # Lier l'axe X du volume à celui du prix
        self.volume_plot.plotItem.vb.setXLink(self.price_plot.plotItem.vb)

        # Rolling buffers
        self.timestamps = deque(maxlen=300)
        self.prices     = deque(maxlen=300)
        self.volumes    = deque(maxlen=300)

        # Timer de mise à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(500)

    def update_plots(self):
        # Récupération des nouveaux trades
        while data_buffer:
            msg = data_buffer.pop(0)
            if msg.get("type") == "trade":
                # Collecte par message
                batch_prices  = []
                batch_volumes = []
                for d in msg["data"]:
                    t = d["t"] / 1000.0
                    p = d["p"]
                    v = d["v"]
                    self.timestamps.append(t)
                    self.prices.append(p)
                    self.volumes.append(v)
                    batch_prices.append(p)
                    batch_volumes.append(v)

                # Calcul du mid price sur ce batch
                if batch_prices:
                    mid = (max(batch_prices) + min(batch_prices)) / 2
                    self.mid_curve.setData(
                        x=[t],
                        y=[mid],
                        symbol='o',
                        symbolBrush='r'
                    )
                # Calcul du VWAP cumulatif
                pv = sum(p*v for p,v in zip(self.prices, self.volumes))
                vsum = sum(self.volumes)
                vwap = pv / vsum if vsum else None
                if vwap:
                    self.vwap_curve.setData(
                        x=[t],
                        y=[vwap],
                        symbol='t',
                        symbolBrush='g'
                    )

                # OHLC close toutes les 10s
                df = pg.pd.DataFrame({
                    'price': list(self.prices)
                }, index=pd.to_datetime(list(self.timestamps), unit='s'))
                ohlc = df['price'].resample('10S').ohlc().dropna()
                if not ohlc.empty:
                    last_close = ohlc['close'].iloc[-1]
                    last_time  = ohlc.index[-1].timestamp()
                    self.ohlc_curve.setData(
                        x=[last_time],
                        y=[last_close],
                        symbol='s',
                        symbolBrush='w'
                    )

        if not self.timestamps:
            return

        # Mise à jour du prix et volume complets
        x = list(self.timestamps)
        self.price_curve.setData(x=x, y=list(self.prices))
        self.volume_curve.setData(x=x, y=list(self.volumes))

        # Verrouillage de l'axe X sur 60 dernières secondes
        now = x[-1]
        self.price_plot.setXRange(now-60, now, padding=0)

        # Autorange Y uniquement
        self.price_plot.enableAutoRange('y', True)
        self.volume_plot.enableAutoRange('y', True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LiveGraph()
    win.show()
    sys.exit(app.exec_())
