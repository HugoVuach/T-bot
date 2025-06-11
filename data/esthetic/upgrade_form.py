from datetime import datetime
import pandas as pd


def pretty_print_data(data):
    trades = data.get('data', [])
    print("\n" + "="*80)
    print(f"{'Time':<20} {'Price':<15} {'Volume':<10}")
    print("-"*80)
    for trade in trades:
        timestamp_ms = trade['t']
        # Conversion timestamp (ms) en datetime
        dt_object = datetime.fromtimestamp(timestamp_ms / 1000.0)
        formatted_time = dt_object.strftime('%H:%M:%S.%f')[:-3]  # On enlève les 3 derniers digits pour ms
        price = trade['p']
        volume = trade['v']
        print(f"{formatted_time:<20} {price:<15} {volume:<10}")
    print("="*80 + "\n")


def convert_to_dataframe(messages):
    """
    Transforme une liste de messages JSON Finnhub en un DataFrame pandas
    ne gardant que : time (hh:mm:ss.mmm), price et volume.
    """
    all_trades = []
    
    for message in messages:
        trades = message.get('data', [])
        for trade in trades:
            timestamp_ms = trade.get('t')
            dt_object = datetime.fromtimestamp(timestamp_ms / 1000.0)
            formatted_time = dt_object.strftime('%H:%M:%S.%f')[:-3]  # Heure, minutes, secondes et millisecondes
            
            all_trades.append({
                'time': formatted_time,
                'price': trade.get('p'),
                'volume': trade.get('v')
            })
    
    df = pd.DataFrame(all_trades)
    return df
