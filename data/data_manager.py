# data_manager.py

import time
from data.market_data import data_buffer
from strategies.strategy_manager import StrategyManager  # On suppose que tu as ce module

def start_data_manager():
    """
    Cette fonction tourne en boucle et lit le buffer global de market_data.
    Elle récupère les nouvelles données et les transmet au StrategyManager.
    """
    strategy_manager = StrategyManager()
    
    while True:
        if data_buffer:
            data = data_buffer.pop(0)  # Récupère la première donnée du buffer
            strategy_manager.on_new_data(data)
        else:
            time.sleep(0.01)  # Petite pause pour ne pas saturer le CPU
