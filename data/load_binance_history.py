import requests
import pandas as pd
from datetime import datetime, timedelta


def load_historical_btc_stats_from_binance(hours=10):
    """
    Récupère les dernières `hours` heures de BTC/USDT depuis l'API Binance
    et retourne un DataFrame au format :
    ['second', 'mean_price', 'total_volume']
    """

    # Binance accepte max 1000 points par requête → 10h * 60min = 600 OK
    limit = hours * 60
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",  # 1 minute candles
        "limit": limit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Colonnes Binance : [open_time, open, high, low, close, volume, ...]
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])

    # Conversion types
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    # Formater la colonne 'second' (HH:MM:SS)
    #df["datetime"] = pd.to_datetime(df["open_time"], unit="ms")
    df["datetime"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["datetime"] = df["datetime"].dt.tz_convert("Europe/Paris")
    df["second"] = df["datetime"].dt.strftime("%H:%M:%S")

    # Calcul des colonnes attendues
    df["mean_price"] = df["close"]
    df["total_volume"] = df["volume"]

    # Retourner seulement les colonnes utiles
    return df[["second", "mean_price", "total_volume"]]


if __name__ == "__main__":
    df = load_historical_btc_stats_from_binance(hours=10)
    print(df.tail())
