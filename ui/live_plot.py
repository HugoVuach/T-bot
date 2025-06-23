from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot
import datetime


class LivePlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        ### zone de tr&cé du prix ###
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Prix BTC moyen par seconde")
        self.plot_widget.setLabel('left', 'Prix moyen (USDT)')
        self.plot_widget.showGrid(x=True, y=True)
        self.curve = self.plot_widget.plot(pen='b')

        ### Zone de tracé du volume ###
        self.volume_plot = pg.PlotWidget()
        self.volume_plot.setBackground('w')
        self.volume_plot.setLabel('left', 'Volume')
        self.volume_plot.setLabel('bottom', 'Temps')
        self.volume_plot.showGrid(x=True, y=True)

        # Barre initiale vide
        self.volume_bar = pg.BarGraphItem(x=[], height=[], width=0.8, brush='gray')
        self.volume_plot.addItem(self.volume_bar)

        ### synchronisation des axes ###
        self.volume_plot.setXLink(self.plot_widget)

        ###########################""
        ### Ligne jaune verticale (début du live) ###
        self.live_start_line = pg.InfiniteLine(angle=90, pen=pg.mkPen('y', width=2, style=pg.QtCore.Qt.DashLine))
        self.plot_widget.addItem(self.live_start_line)
        self.live_start_line.hide()

        self.websocket_start_second = None
        self.websocket_start_marked = False
        ##############################""

        ### lignes de niveau du dernier plus haut et plus bas ###
        self.high_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('g', width=1.5, style=pg.QtCore.Qt.DashLine))
        self.low_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('r', width=1.5, style=pg.QtCore.Qt.DashLine))
        self.plot_widget.addItem(self.high_line)
        self.plot_widget.addItem(self.low_line)
        self.high_label = pg.TextItem(color='g', anchor=(0, 1))
        self.low_label = pg.TextItem(color='r', anchor=(0, 0))
        self.plot_widget.addItem(self.high_label)
        self.plot_widget.addItem(self.low_label)


        ### Layout  ###
        layout = pg.QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget, stretch=3)
        layout.addWidget(self.volume_plot, stretch=1)
        self.setLayout(layout)

        ###############
    def set_websocket_start_time(self, second_str):
        self.websocket_start_second = second_str
        print(f"🟡 Ligne WebSocket prévue à : {second_str}")

    def mark_websocket_start(self, x_position):
        self.live_start_line.setPos(x_position)
        self.live_start_line.show()
        print(f"✅ Ligne jaune affichée à x = {x_position}")
        ############

    @pyqtSlot(object)


    def update_plot(self, df):
        try:
   
            times = df['second'].tolist()  # colonne 'second' = texte genre "10:39:25"
            prices = df['mean_price'].values
            volumes = df['total_volume'].values
            x_values = list(range(len(times)))
            
            ### Prix ###
            self.curve.setData(x=x_values, y=prices)

            ### Volume ###
            self.volume_plot.removeItem(self.volume_bar)  # reinit barres
            self.volume_bar = pg.BarGraphItem(x=x_values, height=volumes, width=0.8, brush='gray')
            self.volume_plot.addItem(self.volume_bar)
            
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
            if x_values:
                last_x = x_values[-1]
                self.high_label.setText(f"↑ {high:.2f}")
                self.low_label.setText(f"↓ {low:.2f}")
                self.high_label.setPos(last_x, high)
                self.low_label.setPos(last_x, low)

            ##################
            ### ✅ Affichage ligne jaune WebSocket ###
            if not self.websocket_start_marked and self.websocket_start_second:
                for i, t in enumerate(times):
                    if t >= self.websocket_start_second:
                        self.mark_websocket_start(i)
                        self.websocket_start_marked = True
                        break
            ###################
        

        except Exception as e:
            print(f"Erreur mise à jour graphique : {e}")
