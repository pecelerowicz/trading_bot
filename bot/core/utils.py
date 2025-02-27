import pandas as pd
import pandas_ta as ta

class Utils:
    @staticmethod
    def add_stoch_rsi(data):
        """Adds Stochastic RSI indicators to the dataframe."""
        df = pd.DataFrame(data)
        df["stoch_rsi_k"] = ta.stochrsi(df["close"], length=14)["STOCHRSIk_14_14_3_3"]
        df["stoch_rsi_d"] = df["stoch_rsi_k"].rolling(window=3).mean()
        return df

    @staticmethod
    def is_closed(df):
        """Checks if the last candle is closed."""
        return df.iloc[-1]['is_closed']

    @staticmethod
    def is_rsi_in_range(df, lower, upper, offset=0):
        """Checks if the RSI is within a specific range."""
        if lower > upper:
            raise ValueError("Lower bound cannot be greater than upper bound.")
        last_rsi = df.iloc[-1 - offset]["stoch_rsi_k"]
        return lower <= last_rsi <= upper

    @staticmethod
    def is_rsi_cross_from_below(df):
        """Checks if RSI crosses the moving average from below."""
        if "stoch_rsi_k" not in df.columns or "stoch_rsi_d" not in df.columns:
            raise ValueError("Input data must contain 'stoch_rsi_k' and 'stoch_rsi_d' columns.")
        if len(df) < 2:
            return False
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        return prev_row["stoch_rsi_k"] < prev_row["stoch_rsi_d"] and last_row["stoch_rsi_k"] > last_row["stoch_rsi_d"]

    @staticmethod
    def find_last_local_extremum(df, minimum):
        """
        Finds the last local extremum (minimum or maximum) of `stoch_rsi_k` and its distance from the last closed candle.
    
        Parameters:
        df (pd.DataFrame): DataFrame containing 'is_closed' and 'stoch_rsi_k' columns.
        minimum (bool): If True, finds the last local minimum; if False, finds the last local maximum.
    
        Returns:
        tuple: (distance_extremum, value_extremum), or (-1, None) if no local extremum exists.
        """
        if "is_closed" not in df.columns or "stoch_rsi_k" not in df.columns:
            raise ValueError("The DataFrame must contain 'is_closed' and 'stoch_rsi_k' columns.")
    
        # Filter only closed candles and drop rows with NaN in 'stoch_rsi_k'
        closed_df = df[df["is_closed"]].dropna(subset=["stoch_rsi_k"])
    
        # Ensure there are enough rows to find a local extremum
        if len(closed_df) < 3:
            return -1, None
    
        # Convert the filtered DataFrame to a list for easier manipulation
        closed_values = closed_df["stoch_rsi_k"].values
    
        # Iterate over the closed candles in reverse, excluding the last valid index
        for i in range(len(closed_values) - 2, 0, -1):
            if minimum:
                # Check if the current value is a local minimum
                if closed_values[i] <= closed_values[i - 1] and closed_values[i] <= closed_values[i + 1]:
                    distance_extremum = len(closed_values) - i
                    value_extremum = closed_values[i]
                    return distance_extremum, value_extremum
            else:
                # Check if the current value is a local maximum
                if closed_values[i] >= closed_values[i - 1] and closed_values[i] >= closed_values[i + 1]:
                    distance_extremum = len(closed_values) - i
                    value_extremum = closed_values[i]
                    return distance_extremum, value_extremum
    
        # If no local extremum is found, return (-1, None)
        return -1, None
    
    @staticmethod
    def find_value_at_distance(df, indicator, distance=1, only_closed=True): # distance liczone od końca (pierwszy pod końca to 1). Tylko zamknięte świece brane pod uwage
        # Validate input is a DataFrame
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Expected df to be a pandas DataFrame, got {}".format(type(df)))
    
        # Ensure required columns exist
        if not {"is_closed", indicator}.issubset(df.columns):
            raise ValueError(f"DataFrame must contain 'is_closed' and {indicator} columns.")
    
        # If only_closed=True, filter closed rows and drop NaNs in 'stoch_rsi_k'
        if only_closed:
            relevant_rows = df[df["is_closed"]].dropna(subset=[indicator])
        else:
            relevant_rows = df.dropna(subset=[indicator])
        relevant_values = relevant_rows[indicator].values
    
        # Check if enough elements are present
        if len(relevant_values) < distance:
            raise ValueError(
                f"Not enough data: requested distance={distance}, but only {len(relevant_values)} values available."
            )
    
        # Return the value at the specified distance
        return relevant_values[-distance]        
        