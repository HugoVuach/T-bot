import websocket
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import threading
import requests
import pytz
import matplotlib.dates as mdates


# === Importer sous la forme suivante pour le 3 eme plot ===
# from indicators.momentum import X
# INDICATOR_CLASS = X
# INDICATOR_NAME = "X"
# INDICATOR_PARAMS = {"period": 10}
# INDICATOR_COLOR = "black"
# INDICATOR_LINE_LEVELS = [a, b]
# INDICATOR_YLIM = (-c, d)  



# === ATR ===
from indicators.volatility_indicator.atr import ATR
INDICATOR_CLASS = ATR
INDICATOR_NAME = "ATR_Value"
INDICATOR_PARAMS = {"period": 14}
INDICATOR_COLOR = "orange"
INDICATOR_LINE_LEVELS = []
INDICATOR_YLIM = (0, 60)  # axe automatique






# === Charger les 301 dernières bougies ===
def fetch_initial_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 301
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        '_', '_', '_', '_', '_', '_'
    ])
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp_local'] = df['timestamp'].dt.tz_convert('Europe/Paris')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

candles = fetch_initial_data()

# === WebSocket ===
def on_message(ws, message):
    global candles
    data = json.loads(message)
    k = data['k']
    ts = pd.to_datetime(k['t'], unit='ms', utc=True)
    ts_local = ts.tz_convert('Europe/Paris')

    new_candle = {
        'timestamp': ts,
        'timestamp_local': ts_local,
        'open': float(k['o']),
        'high': float(k['h']),
        'low': float(k['l']),
        'close': float(k['c']),
        'volume': float(k['v']),
    }

    if not candles.empty and candles.iloc[-1]['timestamp'] == ts:
        candles.iloc[-1] = new_candle
    elif ts > candles.iloc[-1]['timestamp']:
        candles = pd.concat([candles, pd.DataFrame([new_candle])], ignore_index=True)

    if len(candles) > 300:
        candles = candles.iloc[-300:]

def on_open(ws):
    print("✅ WebSocket connecté")
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@kline_1m"],
        "id": 1
    }))

# === Thread WebSocket ===
ws_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.daemon = True
ws_thread.start()

# === Matplotlib : 3 sous-graphiques (chandeliers + volumes + indicateurs) ===
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 7), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})

def animate(i):
    if candles.empty:
        return

    ax1.clear()
    ax2.clear()
    ax1.set_title("BTC/USDT – 300 dernières bougies 1m (Heure de Paris)", fontsize=14)
    ax1.set_ylabel("Prix (USDT)")
    ax2.set_ylabel("Volume")
    ax2.set_xlabel("Heure (Europe/Paris)")

    df = candles.copy()

    # === Appliquer l'indicateur dynamique ===
    indicator = INDICATOR_CLASS(df, **INDICATOR_PARAMS)
    df = indicator.compute()


    # === Graphique principal : chandeliers + prix moyen pondéré ===
    for idx in range(len(df)):
        row = df.iloc[idx]
        color = 'green' if row['close'] >= row['open'] else 'red'
        ax1.plot([row['timestamp_local'], row['timestamp_local']], [row['low'], row['high']], color=color)
        ax1.plot([row['timestamp_local'], row['timestamp_local']],
                 [min(row['open'], row['close']), max(row['open'], row['close'])],
                 color=color, linewidth=3)

    # === Prix moyen pondéré
    df['weighted_close'] = df['close'] * df['volume']
    wc_sum = df['weighted_close'].rolling(window=20).sum()
    vol_sum = df['volume'].rolling(window=20).sum()
    df['volume_avg_price'] = wc_sum / vol_sum
    ax1.plot(df['timestamp_local'], df['volume_avg_price'], label='Prix moyen pondéré (20 bougies)', color='blue', linewidth=2)
    
    # === Lignes horizontales : plus haut / plus bas ===
    highest = df['high'].max()
    lowest = df['low'].min()
    ax1.axhline(y=highest, color='green', linestyle='--', linewidth=1.5, label=f'Plus haut: {highest:.2f}')
    ax1.axhline(y=lowest, color='red', linestyle='--', linewidth=1.5, label=f'Plus bas: {lowest:.2f}')


    # === Afficher les valeurs à droite du graphique
    last_time = df['timestamp_local'].iloc[-1]
    ax1.text(last_time, highest, f'{highest:.2f}', color='green', va='bottom', ha='right', fontsize=10)
    ax1.text(last_time, lowest, f'{lowest:.2f}', color='red', va='top', ha='right', fontsize=10)
    ax1.legend()

    # === Graphique secondaire : volumes ===
    ax2.bar(df['timestamp_local'], df['volume'], width=0.0005, color='gray')

    # === Indicateur dynamique ===
    ax3.set_ylabel(INDICATOR_NAME)
    ax3.set_ylim(*INDICATOR_YLIM)
    for level in INDICATOR_LINE_LEVELS:
        color = 'red' if level > 50 else 'green'
        ax3.axhline(level, color=color, linestyle='--', linewidth=1)
    ax3.plot(df['timestamp_local'], df[INDICATOR_NAME], color=INDICATOR_COLOR)
    ax3.legend([f"{INDICATOR_NAME} ({', '.join(str(v) for v in INDICATOR_PARAMS.values())})"])

    # Format de l'heure sur l'axe X
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=pytz.timezone('Europe/Paris')))
    ax3.tick_params(axis='x', rotation=45)

    # Format de l'heure
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=pytz.timezone('Europe/Paris')))
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
