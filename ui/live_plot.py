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
        # self.plot_widget.setLabel('bottom', 'Temps (s)')
        self.plot_widget.showGrid(x=True, y=True)

        self.curve = self.plot_widget.plot(pen='b')

        layout = pg.QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

    @pyqtSlot(object)
    def update_plot(self, df):
        try:
        #### avec un horodatage 0 1 2 ect pas de heure en direct #########
            #x = list(range(len(df)))
            #y = df['mean_price'].values
            #self.curve.setData(x, y)
        ##############################################################
            times = df['second'].tolist()  # colonne 'second' = texte genre "10:39:25"
            prices = df['mean_price'].values

            x_values = list(range(len(times)))
            self.curve.setData(x=x_values, y=prices)

            # Création d'un dictionnaire de labels horaires
            ticks = [(i, times[i]) for i in range(len(times))]
            axis = self.plot_widget.getAxis('bottom')
            axis.setTicks([ticks])  # une seule ligne de ticks
                  
        except Exception as e:
            print(f"Erreur mise à jour graphique : {e}")
