import matplotlib.pyplot as plt
import matplotlib.animation as animation
from data.market_data import latest_grouped_df
import pandas as pd

def run_visualizer():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    def animate(i):
        df = latest_grouped_df.tail(4)
        if df.empty:
            return

        ax1.clear()
        ax2.clear()

        # Bougies simulées
        for idx, row in df.iterrows():
            price = row["mean_price"]
            low = price * 0.998
            high = price * 1.002
            open_ = price * 0.999
            close = price * 1.001
            color = 'green' if close >= open_ else 'red'
            ax1.plot([idx, idx], [low, high], color=color)
            ax1.plot([idx, idx], [open_, close], color=color, linewidth=5)

        seconds = df['second'].tolist()
        ax1.set_title("📈 BTC - Prix moyen (bougies simulées)")
        ax1.set_xticks(range(len(seconds)))
        ax1.set_xticklabels(seconds, rotation=45)
        ax1.set_ylabel("Prix")

        # Volume
        ax2.bar(range(len(df)), df["total_volume"], color="blue", alpha=0.6)
        ax2.set_title("📊 BTC - Volume échangé")
        ax2.set_xticks(range(len(seconds)))
        ax2.set_xticklabels(seconds, rotation=45)
        ax2.set_ylabel("Volume")

    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.tight_layout()
    plt.show()
