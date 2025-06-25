from indicators.base import Indicator

class Momentum(Indicator):
    def compute(self):
        period = self.params.get("period", 10)

        # Momentum = close(t) - close(t - n)
        self.df["Momentum"] = self.df["close"] - self.df["close"].shift(period)

        # Pour intégration dans le graphe dynamique
        self.df["Momentum_Value"] = self.df["Momentum"]
        return self.df
