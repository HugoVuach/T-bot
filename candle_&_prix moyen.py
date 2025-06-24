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

# === Matplotlib : 2 sous-graphiques (chandeliers + volumes) ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

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

    # === Graphique principal : chandeliers + prix moyen pondéré ===
    for idx in range(len(df)):
        row = df.iloc[idx]
        color = 'green' if row['close'] >= row['open'] else 'red'
        ax1.plot([row['timestamp_local'], row['timestamp_local']], [row['low'], row['high']], color=color)
        ax1.plot([row['timestamp_local'], row['timestamp_local']],
                 [min(row['open'], row['close']), max(row['open'], row['close'])],
                 color=color, linewidth=3)

    # Prix moyen pondéré
    df['weighted_close'] = df['close'] * df['volume']
    wc_sum = df['weighted_close'].rolling(window=20).sum()
    vol_sum = df['volume'].rolling(window=20).sum()
    df['volume_avg_price'] = wc_sum / vol_sum

    ax1.plot(df['timestamp_local'], df['volume_avg_price'], label='Prix moyen pondéré (20 bougies)', color='blue', linewidth=2)
    ax1.legend()

    # === Graphique secondaire : volumes ===
    ax2.bar(df['timestamp_local'], df['volume'], width=0.0005, color='gray')

    # Format de l'heure
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=pytz.timezone('Europe/Paris')))
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
