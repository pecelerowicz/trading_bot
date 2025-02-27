from binance.client import Client
from bot.data.historic.binance_client_wrapper import BinanceClientWrapper
from bot.models.kline_message import KlineMessage
from datetime import datetime, timezone
import pandas as pd

INTERVALS_TO_MS = {
    '1m': 60 * 1000,
    '3m': 3 * 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '30m': 30 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '2h': 2 * 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '6h': 6 * 60 * 60 * 1000,
    '8h': 8 * 60 * 60 * 1000,
    '12h': 12 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
    '3d': 3 * 24 * 60 * 60 * 1000,
    '1w': 7 * 24 * 60 * 60 * 1000,
    '1M': 30 * 24 * 60 * 60 * 1000,  # Approximation
}

class BinanceDataFetcher:
    def __init__(self):
        self.client = Client()
        self.client_wrapper = BinanceClientWrapper()

    def fetch_klines_dates(self, ticker, interval, start_date: str, end_date: str, offset: int = None):
        date_format = "%Y-%m-%d %H:%M:%S"
        # Obliczanie przedziału czasowego w milisekundach
        interval_mapping = {
            "1m": 60 * 1000,          # 1 minuta
            "5m": 5 * 60 * 1000,      # 5 minut
            "15m": 15 * 60 * 1000,    # 15 minut
            "1h": 60 * 60 * 1000,     # 1 godzina
            "4h": 4 * 60 * 60 * 1000, # 4 godziny
            "1d": 24 * 60 * 60 * 1000 # 1 dzień
        }
        # Parsowanie dat do znaczników czasu (ms)
        start_timestamp_ms = int(datetime.strptime(start_date, date_format).replace(tzinfo=timezone.utc).timestamp() * 1000)
        end_timestamp_ms = int(datetime.strptime(end_date, date_format).replace(tzinfo=timezone.utc).timestamp() * 1000)
        # Użycie offsetu, aby zmniejszyć start_timestamp_ms
        if interval in interval_mapping and offset > 0:
            start_timestamp_ms -= offset * interval_mapping[interval]
            
        klines = self.fetch_klines(ticker, interval, start_timestamp_ms, end_timestamp_ms)
        data = [k.__dict__ for k in klines] # Convert simulated output to list of dicts
        return pd.DataFrame(data)    
        
    def fetch_klines(self, ticker: str, interval: str, startTime: int, endTime: int = None) -> list[KlineMessage]:
        """
        Fetch candlestick (kline) data from Binance for a given time range.

        :param ticker: Symbol of the trading pair (e.g., 'BTCUSDT').
        :param interval: Candle interval (e.g., '1m', '1h').
        :param start_time: Start time in milliseconds (timestamp).
        :param end_time: End time in milliseconds (timestamp) (optional).
        :return: List of KlineMessage objects.
        """
        if interval not in INTERVALS_TO_MS:
            raise ValueError(f"Unsupported interval: {interval}")

        # Get Binance server time
        server_time = int(self.client.get_server_time()['serverTime'])

        params = {
            'symbol': ticker,
            'interval': interval,
            'startTime': startTime,
            'endTime': endTime,
        }
        klines = self.client_wrapper.get_klines(**params)

        # Prepare list of KlineMessage objects
        kline_messages = [
            KlineMessage(
                timestamp=kline[0],
                open=float(kline[1]),
                high=float(kline[2]),
                low=float(kline[3]),
                close=float(kline[4]),
                volume=float(kline[5]),
                is_closed=(server_time > kline[6]),  # Determine if kline is closed
                symbol=ticker,
                interval=interval,
            )
            for kline in klines
        ]

        # Check if the last kline is open
#         commented out for analysis
#         if kline_messages and kline_messages[-1].is_closed:
#             raise RuntimeError(
#                 f"Unexpected rare case: the last kline for {ticker} at interval {interval} is closed."
#             )

        return kline_messages

    def fetch_last_n_klines(self, ticker: str, interval: str, n_candles: int) -> list[KlineMessage]:
        """
        Fetch the last `n_candles` candlesticks from Binance.

        :param ticker: Symbol of the trading pair (e.g., 'BTCUSDT').
        :param interval: Candle interval (e.g., '1m', '1h').
        :param n_candles: Number of candles to fetch.
        :return: List of KlineMessage objects.
        """
        if interval not in INTERVALS_TO_MS:
            raise ValueError(f"Unsupported interval: {interval}")

        interval_ms = INTERVALS_TO_MS[interval]

        # Fetch server time for consistent time alignment
        server_time = int(self.client.get_server_time()['serverTime'])
        endTime = server_time
        startTime = endTime - (n_candles * interval_ms)

        # Fetch klines
        klines = self.fetch_klines(ticker, interval, startTime, endTime)

        # Check if the last kline is open
        if klines and klines[-1].is_closed:
            raise RuntimeError(
                f"Unexpected rare case: the last kline for {ticker} at interval {interval} is closed."
            )

        return klines
    