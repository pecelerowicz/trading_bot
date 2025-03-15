import asyncio
import logging

# Importowanie komponentów
from bot.data.stream.multiple_tickers_data_source import MultipleTickersDataSource
from bot.data.stream.binance_stream_manager import BinanceStreamManager
# from data.binance_data_fetcher import BinanceDataFetcher
# from core.candle_store import CandleStore
from bot.core.strategy05 import Strategy05
from bot.core.executor import Executor
from bot.core.engine import Engine

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Konfiguracja parametrów
#tickers = [
#    "ETHUSDC", "SOLUSDC", "XRPUSDC", "BTCUSDC", "ADAUSDC", "PEPEUSDC", "DOGEUSDC", "AVAXUSDC", "POLUSDC", "DOTUSDC", "LTCUSDC"]
tickers = ["ETHUSDT", "XRPUSDT", "SOLUSDT"]
source_interval = "1m"
intervals = ['1m', '5m', '15m', '1h', '4h']
number_candles = 50

# Tworzenie komponentów
# binance_data_fetcher = BinanceDataFetcher()
data_source = MultipleTickersDataSource(tickers=tickers, interval=source_interval, only_closed=False)

# Strategia z domyślnymi kolumnami: 'time_utc', 'open', 'close', 'is_closed'
strategy = Strategy05(tickers, intervals, number_candles, display_columns=['time_utc', 'open', 'close', 'volume', 'is_closed'])
executor = Executor(
    bot_token="7807553871:AAHAKc62nu51cnuCouOEwTnX4WlJ7BjTZc4",  # Twój token
    chat_id=5939592276  # Twoje chat_id
)
engine = Engine(data_source, strategy, executor)

# Główna funkcja asynchroniczna
async def main():
    logger.info("Setting up the engine...")
    engine.setup()
    logger.info("Starting the engine...")
    await engine.start()

# Uruchomienie skryptu
if __name__ == "__main__":
    asyncio.run(main())
