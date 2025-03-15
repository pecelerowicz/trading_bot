import os
import sys
import yaml
import asyncio

# Pobranie katalogu bazowego na podstawie lokalizacji tego skryptu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

# Sprawdzenie, czy plik istnieje
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Nie znaleziono pliku konfiguracyjnego: {CONFIG_PATH}")

# Wczytanie pliku YAML
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

bot_token = config["telegram"]["bot_token"]
chat_id = config["telegram"]["chat_id"]

sys.path.append(BASE_DIR)

from bot.data.stream.multiple_tickers_data_source import MultipleTickersDataSource
from bot.core.strategy05 import Strategy05
from bot.core.executor import Executor
from bot.core.engine import Engine

tickers = ["BTCUSDT", "ETHUSDT"]
source_interval = "1m"
intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
number_candles = 50

data_source = MultipleTickersDataSource(tickers=tickers, interval=source_interval, only_closed=False)
strategy = Strategy05(tickers, intervals, number_candles, display_columns=['time_utc', 'open', 'close', 'volume', 'is_closed'])
executor = Executor(bot_token=bot_token, chat_id=chat_id)

engine = Engine(data_source, executor)
engine.add_strategy(strategy)

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

async def main():
    engine.setup()
    await engine.start()

if __name__ == "__main__":
    asyncio.run(main())

