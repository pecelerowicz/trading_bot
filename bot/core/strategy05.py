from bot.core.candle_store import CandleStore
from bot.core.utils import Utils  # Importing the Utils class

class Strategy05:
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
        print("****strategy05****")
        self.candle_store.update(data)
        for ticker in self.tickers:
            print("---" + ticker + "---")
            df_large = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '5m'))
            df_small = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '1m')) # to tylko służy jako zegar
            
            self.notify("test")
            if self.utils.is_closed(df_small): #and not self.utils.is_closed(df_large):
                print("closed short candle, open long candle")
                val_1 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=1, only_closed=False)
                val_2 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=2, only_closed=False)
                val_3 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=3, only_closed=False)
                val_4 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=4, only_closed=False)
                print(val_1)
                print(val_2)
                print(val_3)
                print(val_4)
                
                if val_1 > val_2 and val_2 <= val_3 and val_3 <= val_4 and val_4 < 20 and val_1 < 5:
                    self.notify("BUY " + ticker)
                elif val_1 < val_2 and val_2 >= val_3 and val_3 >= val_4 and val_4 > 80 and val_1 > 95:
                    self.notify("SELL " + ticker)
                
                
#             if self.utils.is_closed(df_small) and self.utils.is_closed(df_large):
#                 print("closed short candle, closed long candle")
                
#                 previous_value_k = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=2, only_closed=False)
#                 current_value_k = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=1, only_closed=False)
            

        print("****end of strategy05****")        
                
        

            
            
 