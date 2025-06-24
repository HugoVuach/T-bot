from indicators.base import Indicator

class CCI(Indicator):
    def compute(self):
        period = self.params.get("period", 20)

        # Prix typique = (high + low + close) / 3
        tp = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        self.df['TP'] = tp

        # Moyenne mobile du TP
        tp_sma = tp.rolling(window=period).mean()

        # Écart absolu moyen
        mad = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean(), raw=True)

        self.df['CCI'] = (tp - tp_sma) / (0.015 * mad)

        # Pour intégration graphique
        self.df['CCI_Value'] = self.df['CCI']
        return self.df
