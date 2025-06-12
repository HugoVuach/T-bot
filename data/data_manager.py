# data_manager.py

import time
from data.market_data import data_buffer
from strategies.strategy_manager import StrategyManager  # On suppose que tu as ce module

def start_data_manager():
    """
    Cette fonction tourne en boucle et lit le buffer global de market_data.
    Elle récupère les nouvelles données et les transmet au StrategyManager.
    """

