from indicators.base import Indicator

class ROC(Indicator):
    def compute(self):
        period = self.params.get("period", 12)

        # Calcul ROC : ((prix actuel - prix n périodes avant) / prix n périodes avant) * 100
        self.df["ROC"] = ((self.df["close"] - self.df["close"].shift(period)) / self.df["close"].shift(period)) * 100

        # Pour affichage dynamique
        self.df["ROC_Value"] = self.df["ROC"]
        return self.df
