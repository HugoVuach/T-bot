from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot


class LivePlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Prix BTC moyen par seconde")
        self.plot_widget.setLabel('left', 'Prix moyen (USDT)')
        self.plot_widget.setLabel('bottom', 'Temps (s)')
        self.plot_widget.showGrid(x=True, y=True)

        self.curve = self.plot_widget.plot(pen='b')

        layout = pg.QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

    @pyqtSlot(object)
    def update_plot(self, df):
        try:
            x = list(range(len(df)))
            y = df['mean_price'].values
            self.curve.setData(x, y)
        except Exception as e:
            print(f"Erreur mise à jour graphique : {e}")
