from bot.data.historic.binance_data_fetcher import BinanceDataFetcher
from bot.models.kline_message import KlineMessage
import pandas as pd

class CandleStore:
    def __init__(self, tickers, intervals, number_candles):
        self.tickers = tickers
        self.intervals = intervals
        self.number_candles = number_candles
        self.binance_data_fetcher = BinanceDataFetcher()

        # Initialize the structure to store candles
        self.windows = {interval: {ticker: [] for ticker in tickers} for interval in intervals}

        # Populate the structure with historical data
        self._load_candles()

    def _load_candles(self):
        """Fetch and store the initial set of candles for all intervals and tickers."""
        for interval in self.intervals:
            for ticker in self.tickers:
                candles = self.binance_data_fetcher.fetch_last_n_klines(
                    ticker=ticker,
                    interval=interval,
                    n_candles=self.number_candles
                )
                self.windows[interval][ticker] = candles                

    def _update_1m(self, data):
        """Update the 1m interval with new data from the input stream."""
        interval = '1m'

        for ticker, new_kline in data.items():
            # Access the current list of candles for the ticker
            ticker_candles = self.windows[interval][ticker]

            if not ticker_candles:
                raise ValueError(f"No existing candles found for ticker {ticker} in interval {interval}.")

            # Get the last candle in the list
            last_candle = ticker_candles[-1]

            if new_kline.timestamp == last_candle.timestamp:
                # Replace the last candle if timestamps match
                ticker_candles[-1] = new_kline
            elif new_kline.timestamp == last_candle.timestamp + 60000:
                # Check if the last candle is closed before adding the new one
                if not last_candle.is_closed:
                    raise ValueError(
                        f"Previous candle for ticker {ticker} in interval {interval} is not closed. Cannot add new candle."
                    )
                # Add the new candle to the list
                ticker_candles.append(new_kline)
                # Maintain the rolling window size
                self.windows[interval][ticker] = ticker_candles[-self.number_candles:]
            else:
                # Throw an error for invalid timestamp sequences
                raise ValueError(
                    f"Timestamp mismatch for ticker {ticker} in interval {interval}. "
                    f"Expected {last_candle.timestamp + 60000}, got {new_kline.timestamp}."
                )

    def _update_larger_interval(self, shorter_frame, larger_frame):
        shorter_frame_ms = self._interval_to_ms(shorter_frame)
        larger_frame_ms = self._interval_to_ms(larger_frame)
    
        for ticker, shorter_candles in self.windows[shorter_frame].items():
            # Identify the current larger frame candle
            larger_candles = self.windows[larger_frame][ticker]
            current_larger = larger_candles[-1] if larger_candles else None
    
            # Determine the start time of the current larger frame
            start_time = (shorter_candles[-1].timestamp // larger_frame_ms) * larger_frame_ms
    
            # If the current larger frame candle exists and is closed, skip it
            if current_larger and current_larger.is_closed:
                current_larger = None
    
            # If there's no current open larger frame candle, create a new one
            if not current_larger or current_larger.timestamp < start_time:
                if current_larger and not current_larger.is_closed:
                    current_larger.is_closed = True  # Finalize the existing larger frame candle
                
                # Create a new larger frame candle
                new_larger = KlineMessage(
                    timestamp=start_time,
                    open=shorter_candles[-1].open,
                    high=shorter_candles[-1].high,
                    low=shorter_candles[-1].low,
                    close=shorter_candles[-1].close,
                    volume=shorter_candles[-1].volume,
                    is_closed=False,
                    symbol=ticker,
                    interval=larger_frame
                )
                larger_candles.append(new_larger)
                current_larger = new_larger
    
            # Aggregate all relevant shorter frame candles for the current larger frame
            relevant_candles = [c for c in shorter_candles if start_time <= c.timestamp < start_time + larger_frame_ms]
            
            if relevant_candles:
                current_larger.high = max(current_larger.high, *(c.high for c in relevant_candles))
                current_larger.low = min(current_larger.low, *(c.low for c in relevant_candles))
                current_larger.close = relevant_candles[-1].close
                current_larger.volume = sum(c.volume for c in relevant_candles)
    
            # Close the larger frame candle if the last shorter frame candle is both the last in the frame and closed
            last_shorter = shorter_candles[-1]
            if last_shorter.timestamp >= start_time + larger_frame_ms - shorter_frame_ms and last_shorter.is_closed:
                current_larger.is_closed = True
    
            # Maintain the rolling window size
            self.windows[larger_frame][ticker] = larger_candles[-self.number_candles:]

    def _interval_to_ms(self, interval):
        """Convert interval string to milliseconds."""
        mapping = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000
        }
        return mapping.get(interval, 0)
        
    def update(self, data):
        self._update_1m(data)
        self._update_larger_interval('1m', '5m')
        self._update_larger_interval('5m', '15m')
        self._update_larger_interval('15m', '1h')
        self._update_larger_interval('1h', '4h')
        self._update_larger_interval('4h', '1d')

    def get_candles(self, ticker, interval, fields=None):
        """
        Retrieve the list of candles for a specific ticker and interval as a DataFrame.
        Optionally include only specific fields in the specified order.
    
        :param ticker: The ticker symbol.
        :param interval: The interval string (e.g., '1m', '5m').
        :param fields: List of fields to include in the DataFrame in the specified order. If None, include all fields.
        :return: A DataFrame containing the candles for the specified ticker and interval.
        """
        candles = self.windows.get(interval, {}).get(ticker, [])
        if not candles:
            return pd.DataFrame()  # Return an empty DataFrame if no data is available
    
        # Convert list of candle objects into a DataFrame
        data = {
            'timestamp': [candle.timestamp for candle in candles],
            'open': [candle.open for candle in candles],
            'high': [candle.high for candle in candles],
            'low': [candle.low for candle in candles],
            'close': [candle.close for candle in candles],
            'volume': [candle.volume for candle in candles],
            'is_closed': [candle.is_closed for candle in candles],
            'symbol': [candle.symbol for candle in candles],
            'interval': [candle.interval for candle in candles]
        }
    
        df = pd.DataFrame(data)
    
        # If fields are specified, filter the DataFrame to include only those fields in the specified order
        if fields:
            available_fields = list(data.keys())
            valid_fields = [field for field in fields if field in available_fields]
    
            if not valid_fields:
                raise ValueError(f"No valid fields selected. Available fields are: {available_fields}")
    
            return df[valid_fields]  # Return DataFrame with the requested fields in the specified order
    
        return df

    def get_tickers(self):
        return self.tickers
    
    def add_new_candle(self, ticker, interval, new_candle):
        """Add a new candle and maintain the fixed length of the list."""
        if interval in self.windows and ticker in self.windows[interval]:
            self.windows[interval][ticker].append(new_candle)
            # Keep only the last `number_candles` items
            self.windows[interval][ticker] = self.windows[interval][ticker][-self.number_candles:]