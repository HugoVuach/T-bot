from indicators.base import Indicator

class WilliamsR(Indicator):
    def compute(self):
        period = self.params.get("period", 14)

        high_max = self.df['high'].rolling(window=period).max()
        low_min = self.df['low'].rolling(window=period).min()

        self.df['Williams_%R'] = -100 * (high_max - self.df['close']) / (high_max - low_min)

        # Pour affichage automatique
        self.df['WilliamsR'] = self.df['Williams_%R']
        return self.df
