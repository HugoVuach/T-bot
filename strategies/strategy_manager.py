# strategies/strategy_manager.py

class StrategyManager:
    """
    Point d'entrée pour toutes les stratégies de trading.
    """

    def __init__(self):
        # Tu pourrais instancier ici tes stratégies
        pass

    def on_new_data(self, data):
        """
        Méthode appelée à chaque nouveau tick reçu.
        Ici tu vas appeler tes stratégies (momentum, arbitrage, etc.)
        """
        print("Received new data:", data)
        # À terme, tu peux router ça vers tes stratégies.
