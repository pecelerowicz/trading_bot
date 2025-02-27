from bot.core.candle_store import CandleStore
from bot.core.utils import Utils  # Importing the Utils class

class Strategy04:
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
        self.cross = {ticker: False for ticker in tickers}

    def subscribe(self, callback):
        """Adds a subscriber to signals."""
        self.subscribers.append(callback)

    def notify(self, signal):
        """Sends a signal to subscribers."""
        for callback in self.subscribers:
            callback(signal)

    def update(self, data):
        print("---strategy04---")
        self.candle_store.update(data)
        for ticker in self.tickers:
            df_large = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '1h'))
            df_small = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '1m')) # to tylko służy jako zegar
            
            if self.utils.is_closed(df_small): # closed short-term candle
                if not self.cross[ticker]: # jeszcze nie było przecięcia
                    current_value_k = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=1, only_closed=False)
                    previous_value_k = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=2, only_closed=False)
                    current_value_d = self.utils.find_value_at_distance(df_large, 'stoch_rsi_d', distance=1, only_closed=False)
                    previous_value_d = self.utils.find_value_at_distance(df_large, 'stoch_rsi_d', distance=2, only_closed=False)
                    if previous_value_k < previous_value_d and current_value_k > current_value_d:
                        self.cross[ticker] = True
                        self.notify(f"Strategy04: Cross on {ticker}")
        print("---end of strategy04---")        
                
        
        
        
#         for ticker in self.tickers:
#             df_large = self.utils.add_indicators(self.candle_store.get_candles(ticker, '4h'))
#             df_small = self.utils.add_indicators(self.candle_store.get_candles(ticker, '15m'))
            
#             last_minimum_large_distance, last_minimum_large_value = self.utils.find_last_local_extremum(df_large, minimum=True)
#             last_maximum_large_distance, last_maximum_large_value = self.utils.find_last_local_extremum(df_large, minimum=False)

#             current_large_value = self.utils.find_value_at_distance(df_large, distance=1)
#             current_small_value = self.utils.find_value_at_distance(df_small, distance=1)
            
#             if last_minimum_large_distance < last_maximum_large_distance and last_minimum_large_value < 20: # global uptrend
#                 if self.utils.is_rsi_in_range(df_large, 5, 95, offset=0): # reasonable range
#                     print(f"{ticker}: global uptrend & reasonable range")
#                     if self.utils.is_closed(df_small): # closed short-term candle
#                         print(f"{ticker}: closed short range candle & global uptrend & reasonable range")
#                         if self.utils.is_rsi_in_range(df_small, 0, 10, offset=0): # local dip
#                             print(f"{ticker}: local dip& closed short range candle & global uptrend & reasonable range")
#                             self.notify(f"4h uptrend on {ticker}: 4h stoch rsi {last_minimum_large_value}->{current_large_value}, 15m stoch rsi={current_small_value}")
#             print("---")            
#         print("--------------------")    
            
            
 
