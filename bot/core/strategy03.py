from bot.core.candle_store import CandleStore
from bot.core.utils import Utils  # Importing the Utils class

class Strategy03:
    def __init__(self, tickers, intervals, number_candles, display_columns=None):
        """
        Initializes the strategy with default display columns.
        """
        self.subscribers = []
        self.display_columns = display_columns or ['time_utc', 'open', 'close', 'is_closed']  # Default columns
        self.tickers = tickers
        self.intervals = intervals
        self.number_candles = number_candles
        self.candle_store = CandleStore(tickers, intervals, number_candles)
        self.utils = Utils()  # Initialize the Utils class

    def subscribe(self, callback):
        """Adds a subscriber to signals."""
        self.subscribers.append(callback)

    def notify(self, signal):
        """Sends a signal to subscribers."""
        for callback in self.subscribers:
            callback(signal)

    def update(self, data):
        print("---strategy03---")
        self.candle_store.update(data)

        for ticker in self.tickers:
            df_large = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '4h'))
            df_small = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '15m'))
            
            last_minimum_large_distance, last_minimum_large_value = self.utils.find_last_local_extremum(df_large, minimum=True)
            last_maximum_large_distance, last_maximum_large_value = self.utils.find_last_local_extremum(df_large, minimum=False)

            current_large_value = self.utils.find_value_at_distance(df_large, indicator='stoch_rsi_k', distance=1, only_closed=True)
            current_small_value = self.utils.find_value_at_distance(df_small, indicator='stoch_rsi_k', distance=1, only_closed=True)
            
            if last_minimum_large_distance < last_maximum_large_distance: # global uptrend
                if self.utils.is_rsi_in_range(df_large, 5, 95, offset=0): # reasonable range
                    print(f"{ticker}: global uptrend & reasonable range")
                    if self.utils.is_closed(df_small): # closed short-term candle
                        print(f"{ticker}: closed short range candle & global uptrend & reasonable range")
                        if self.utils.is_rsi_in_range(df_small, 0, 10, offset=0): # local dip
                            print(f"{ticker}: local dip& closed short range candle & global uptrend & reasonable range")
                            self.notify(f"Strategy03: 4h uptrend on {ticker}: 4h stoch rsi {last_minimum_large_value}->{current_large_value}, 15m stoch rsi={current_small_value}")
            print("---")            
        print("--------------------")    
        print("---end of strategy03---")    
            