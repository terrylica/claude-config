"""
Simple Moving Average (SMA) - Python Implementation
Test indicator for workflow validation
"""
import pandas as pd
import numpy as np


def calculate_sma(
    df: pd.DataFrame,
    period: int = 14,
    price_col: str = 'close'
) -> pd.DataFrame:
    """
    Calculate Simple Moving Average.

    Args:
        df: DataFrame with OHLC data
        period: SMA period
        price_col: Column to use for calculation (default: close)

    Returns:
        DataFrame with 'sma' column
    """
    result = pd.DataFrame(index=df.index)

    # Calculate SMA matching MQL5 behavior
    # MQL5: SMA[i] = sum(close[i-period+1 .. i]) / period
    sma = pd.Series(index=df.index, dtype=float)

    prices = df[price_col].values

    for i in range(len(prices)):
        if i < period - 1:
            # Not enough data for full period - set to NaN or 0
            sma.iloc[i] = np.nan
        else:
            # Calculate sum of last 'period' bars
            sma.iloc[i] = np.sum(prices[i-period+1:i+1]) / period

    result['sma'] = sma

    return result
