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
            df_huge = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '4h')) #4h
            df_large = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '1h')) #1h
            df_small = self.utils.add_stoch_rsi(self.candle_store.get_candles(ticker, '15m')) # 15m

            print('-' + ticker)
            print(self.utils.find_value_at_distance(df_small, 'stoch_rsi_k', distance=1, only_closed=False))
            print(self.utils.find_value_at_distance(df_small, 'stoch_rsi_k', distance=2, only_closed=False))
            print(self.utils.find_value_at_distance(df_small, 'stoch_rsi_k', distance=3, only_closed=False))
            print(data)
       
            if self.utils.is_closed(df_small): #and not self.utils.is_closed(df_large):
                print("closed short candle, open long candle")

                s_1 = self.utils.find_value_at_distance(df_small, 'stoch_rsi_k', distance=1, only_closed=False)
                s_2 = self.utils.find_value_at_distance(df_small, 'stoch_rsi_k', distance=2, only_closed=False)
                s_3 = self.utils.find_value_at_distance(df_small, 'stoch_rsi_k', distance=3, only_closed=False)

                l_1 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=1, only_closed=False)
                l_2 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=2, only_closed=False)
                l_3 = self.utils.find_value_at_distance(df_large, 'stoch_rsi_k', distance=3, only_closed=False)

                h_1 = self.utils.find_value_at_distance(df_huge, 'stoch_rsi_k', distance=1, only_closed=False)
                h_2 = self.utils.find_value_at_distance(df_huge, 'stoch_rsi_k', distance=2, only_closed=False)
                h_3 = self.utils.find_value_at_distance(df_huge, 'stoch_rsi_k', distance=3, only_closed=False)
                #print(s_1)
                #print(s_2)
                #print(s_3)
                #print('-')
                #print(l_1)
                #print(l_2)
                #print(l_3)
                #print('--')
                #print(h_1)
                #print(h_2)
                #print(h_3)
                #print('---')

                #if val_1 > val_2 and val_2 <= val_3 and val_3 <= val_4 and val_4 < 20 and val_1 < 5:
                #    self.notify("BUY " + ticker)
                #elif val_1 < val_2 and val_2 >= val_3 and val_3 >= val_4 and val_4 > 80 and val_1 > 95:
                #    self.notify("SELL " + ticker)

                info_s_1 = False
                info_s_2 = False
                info_s_3 = False

                info_b_1 = False
                info_b_2 = False
                info_b_3 = False

                info_s_1 = h_1 >= 80 and s_2 >= 80 and s_2 >= s_1 and s_2 >= s_3
                info_s_2 = h_1 >= 80 and s_1 >= 99
                info_s_3 = l_2 >= 99 and l_1 <= l_2
                info_b_1 = h_1 <= 20 and s_2 <= 20 and s_2 <= s_1 and s_2 <= s_3
                info_b_2 = h_1 <= 20 and s_1 <= 1
                info_b_3 = l_2 <= 1 and l_1 >=l_2

                #print('----' + ticker)
                #print(s_1)
                #print(s_2)
                #print(s_3)

                if info_s_1 or info_s_2 or info_s_3:
                    message = 'SELL'
                    if info_s_1:
                        message = message + ' (1)'
                    if info_s_2:
                        message = message + ' (2)'
                    if info_s_3:
                        message = message + ' (3)'
                    self.notify(message + ' ' + ticker)

                if info_b_1 or info_b_2 or info_b_3:
                    message = 'BUY'
                    if info_b_1:
                        message = message + ' (1)'
                    if info_b_2:
                        message = message + ' (2)'
                    if info_b_3:
                        message = message + ' (3)'
                    self.notify(message + ' ' + ticker)



        print("****end of strategy05****")

        

            
            
 