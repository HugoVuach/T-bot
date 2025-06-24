import pandas as pd

def generate_candles(df, timeframe='5min'):
    """
    Regroupe les données par chandeliers OHLCV selon l'intervalle spécifié.

    Args:
        df (pd.DataFrame): Doit contenir les colonnes ['second', 'mean_price', 'total_volume'].
                           'second' doit être au format HH:MM:SS (str).
        timeframe (str): ex. '1min', '5min', etc.

    Returns:
        pd.DataFrame: colonnes ['datetime', 'open', 'high', 'low', 'close', 'volume']
    """
    required_cols = {'second', 'mean_price', 'total_volume'}
    
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Le DataFrame doit contenir les colonnes {required_cols}")

    # Construction d'un datetime complet basé sur aujourd'hui + l'heure fournie
    today = pd.Timestamp.today().normalize()  # = aujourd'hui à 00:00:00
    df['datetime'] = pd.to_datetime(df['second'], format="%H:%M:%S", errors='coerce')
    df['datetime'] = df['datetime'].apply(
        lambda t: today + pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second) if pd.notnull(t) else pd.NaT
    )
    df = df.dropna(subset=['datetime'])

    # Renommage des colonnes pour compatibilité
    df = df.rename(columns={'mean_price': 'price', 'total_volume': 'volume'})
    df.set_index('datetime', inplace=True)

    # Agrégation
    ohlc = df['price'].resample(timeframe).ohlc()
    volume = df['volume'].resample(timeframe).sum()

    # Fusion
    ohlcv = pd.concat([ohlc, volume], axis=1).dropna()
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    ohlcv.reset_index(inplace=True)

    return ohlcv
