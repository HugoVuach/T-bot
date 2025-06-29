from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from ui.live_plot import LivePlotWidget
import time
import pandas as pd
from data import market_data
from data.market_data import start_finnhub_ws
from datetime import datetime
from data.esthetic.ohlc_tools import generate_candles


class DataWorker(QObject):
    data_updated = pyqtSignal(pd.DataFrame)
    started_at = pyqtSignal(datetime)
    running = True

    def run(self):
        # Démarrage du WebSocket
        start_finnhub_ws()
        self.start_time = datetime.now()
        self.started_at.emit(self.start_time) 

        last_seen = None
        while self.running:
            current = market_data.grouped
            if current is not None and not current.equals(last_seen if last_seen is not None else current.iloc[0:0]):
                self.data_updated.emit(current.copy())
                last_seen = current.copy()
            time.sleep(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTC Live Dashboard")
        self.resize(1600, 800)

        self.plot_widget = LivePlotWidget()
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.thread = QThread()
        self.worker = DataWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.data_updated.connect(self.plot_widget.update_plot)

        self.worker.started_at.connect(self.mark_websocket_start)  #  Connexion au slot

        ###########
        # Candlestick View
        self.worker.data_updated.connect(lambda df: self.plot_widget.update_candlestick(generate_candles(df)))
        #############


        self.thread.start()


    def mark_websocket_start(self, dt):
   
        second_str = dt.strftime("%H:%M:%S")
        self.plot_widget.set_websocket_start_time(second_str)


    def closeEvent(self, event):
        self.worker.running = False
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)
