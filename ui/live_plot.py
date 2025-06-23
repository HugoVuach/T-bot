from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot
import datetime


class LivePlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Prix BTC moyen par seconde")
        self.plot_widget.setLabel('left', 'Prix moyen (USDT)')
        self.plot_widget.showGrid(x=True, y=True)

        ### dernier plus haut et plus bas ###
        self.high_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('g', width=1.5, style=pg.QtCore.Qt.DashLine))
        self.low_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('r', width=1.5, style=pg.QtCore.Qt.DashLine))
        self.plot_widget.addItem(self.high_line)
        self.plot_widget.addItem(self.low_line)

        self.high_label = pg.TextItem(color='g', anchor=(0, 1))
        self.low_label = pg.TextItem(color='r', anchor=(0, 0))
        self.plot_widget.addItem(self.high_label)
        self.plot_widget.addItem(self.low_label)
        ########################################


        self.curve = self.plot_widget.plot(pen='b')

        layout = pg.QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

    @pyqtSlot(object)
    def update_plot(self, df):
        try:
   
            times = df['second'].tolist()  # colonne 'second' = texte genre "10:39:25"
            prices = df['mean_price'].values

            x_values = list(range(len(times)))
            self.curve.setData(x=x_values, y=prices)
            
            ### On affiche un label toutes les 5 secondes ###
            tick_interval = 5
            ticks = [(i, times[i]) for i in range(len(times)) if i % tick_interval == 0]

            axis = self.plot_widget.getAxis('bottom')
            axis.setTicks([ticks])  # une seule ligne de ticks

            ### Affichage du plus haut / plus bas ###
            high = max(prices)
            low = min(prices)
            self.high_line.setPos(high)
            self.low_line.setPos(low)
            # Positionner les labels à droite du dernier point visible
            if x_values:
                last_x = x_values[-1]
                self.high_label.setText(f"↑ {high:.2f}")
                self.low_label.setText(f"↓ {low:.2f}")
                self.high_label.setPos(last_x, high)
                self.low_label.setPos(last_x, low)

            ###########################""

        except Exception as e:
            print(f"Erreur mise à jour graphique : {e}")
