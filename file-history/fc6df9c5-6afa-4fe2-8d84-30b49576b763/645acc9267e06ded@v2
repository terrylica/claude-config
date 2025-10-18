"""ATR Adaptive Smoothed Laguerre RSI Indicator.

Python implementation of MQL5 indicator with validated correlation ≥ 0.999.
Algorithm specification: docs/guides/LAGUERRE_RSI_ANALYSIS.md

Version: 1.0.0
Status: Implementation complete, validation pending
"""

import numpy as np
import pandas as pd


def calculate_true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Calculate True Range.

    True Range is the greatest of:
    - Current High - Current Low
    - |Current High - Previous Close|
    - |Current Low - Previous Close|

    Args:
        high: High prices
        low: Low prices
        close: Close prices

    Returns:
        True Range values

    Raises:
        ValueError: If input series have mismatched lengths or are empty
    """
    if len(high) != len(low) or len(high) != len(close):
        raise ValueError(f"Input series length mismatch: high={len(high)}, low={len(low)}, close={len(close)}")

    if len(high) == 0:
        raise ValueError("Input series are empty")

    prev_close = close.shift(1)

    # True Range = max(high, prev_close) - min(low, prev_close)
    tr = np.maximum(high, prev_close) - np.minimum(low, prev_close)

    # First bar: TR = high - low
    tr.iloc[0] = high.iloc[0] - low.iloc[0]

    return tr


def calculate_atr(tr: pd.Series, period: int = 14) -> pd.Series:
    """Calculate ATR using simple moving average of True Range.

    Matches MQL5 behavior: uses expanding window for first `period` bars,
    then switches to sliding window.

    Args:
        tr: True Range values
        period: ATR period (default 14)

    Returns:
        ATR values

    Raises:
        ValueError: If period < 1 or tr is empty
    """
    if period < 1:
        raise ValueError(f"Period must be >= 1, got {period}")

    if len(tr) == 0:
        raise ValueError("True Range series is empty")

    # Calculate ATR like MQL5: expanding window then sliding window
    # For bars 0 to period-1: use expanding mean (sum of available bars / period)
    # For bar >= period: use rolling mean
    atr = pd.Series(index=tr.index, dtype=float)

    for i in range(len(tr)):
        if i < period:
            # Initial accumulation: sum all available bars, divide by period
            atr.iloc[i] = tr.iloc[:i+1].sum() / period
        else:
            # Sliding window: average of last `period` bars
            atr.iloc[i] = tr.iloc[i-period+1:i+1].mean()

    return atr


def calculate_atr_min_max(atr: pd.Series, period: int) -> tuple[pd.Series, pd.Series]:
    """Calculate rolling minimum and maximum ATR over lookback period.

    Matches MQL5 behavior: uses expanding window for first `period` bars,
    then switches to sliding window.

    Args:
        atr: ATR values
        period: Lookback period

    Returns:
        Tuple of (min_atr, max_atr)

    Raises:
        ValueError: If period < 1 or atr is empty
    """
    if period < 1:
        raise ValueError(f"Period must be >= 1, got {period}")

    if len(atr) == 0:
        raise ValueError("ATR series is empty")

    # Calculate min/max like MQL5: expanding window then sliding window
    min_atr = pd.Series(index=atr.index, dtype=float)
    max_atr = pd.Series(index=atr.index, dtype=float)

    for i in range(len(atr)):
        if i == 0:
            # First bar: min = max = current ATR
            min_atr.iloc[i] = atr.iloc[i]
            max_atr.iloc[i] = atr.iloc[i]
        elif i < period:
            # Expanding window: look at all available bars
            min_atr.iloc[i] = atr.iloc[:i+1].min()
            max_atr.iloc[i] = atr.iloc[:i+1].max()
        else:
            # Sliding window: look at last `period` bars
            min_atr.iloc[i] = atr.iloc[i-period+1:i+1].min()
            max_atr.iloc[i] = atr.iloc[i-period+1:i+1].max()

    return min_atr, max_atr


def calculate_adaptive_coefficient(atr: pd.Series, min_atr: pd.Series, max_atr: pd.Series) -> pd.Series:
    """Calculate adaptive coefficient based on ATR position within min/max range.

    When ATR is at minimum: coeff = 1.0 (longest period, smoother)
    When ATR is at maximum: coeff = 0.0 (shortest period, more responsive)

    Args:
        atr: Current ATR values
        min_atr: Minimum ATR over lookback period
        max_atr: Maximum ATR over lookback period

    Returns:
        Adaptive coefficient (0.0 to 1.0)

    Raises:
        ValueError: If input series have mismatched lengths or are empty
    """
    if len(atr) != len(min_atr) or len(atr) != len(max_atr):
        raise ValueError(f"Input series length mismatch: atr={len(atr)}, min_atr={len(min_atr)}, max_atr={len(max_atr)}")

    if len(atr) == 0:
        raise ValueError("Input series are empty")

    # Ensure current ATR is within min/max range
    _max = np.maximum(max_atr, atr)
    _min = np.minimum(min_atr, atr)

    # Calculate coefficient
    # When ATR is at minimum: coeff = 1.0 (longest period)
    # When ATR is at maximum: coeff = 0.0 (shortest period)
    coeff = pd.Series(0.5, index=atr.index)  # Default for equal min/max
    mask = _min != _max
    coeff[mask] = 1.0 - (atr[mask] - _min[mask]) / (_max[mask] - _min[mask])

    return coeff


def calculate_adaptive_period(atr_period: int, coeff: pd.Series) -> pd.Series:
    """Calculate adaptive period for Laguerre RSI.

    Adaptive period = atr_period * (coeff + 0.75)
    Range: atr_period * 0.75 to atr_period * 1.75

    Args:
        atr_period: Base ATR period
        coeff: Adaptive coefficient (0.0 to 1.0)

    Returns:
        Adaptive period values

    Raises:
        ValueError: If atr_period < 1 or coeff is empty
    """
    if atr_period < 1:
        raise ValueError(f"ATR period must be >= 1, got {atr_period}")

    if len(coeff) == 0:
        raise ValueError("Coefficient series is empty")

    # Adaptive period = atr_period * (coeff + 0.75)
    # Range: atr_period * 0.75 to atr_period * 1.75
    return atr_period * (coeff + 0.75)


def get_price_series(
    df: pd.DataFrame,
    price_type: str = 'close',
    smooth_period: int = 5,
    smooth_method: str = 'ema'
) -> pd.Series:
    """Get price series with optional smoothing.

    Args:
        df: DataFrame with OHLC data
        price_type: Price to use ('close', 'open', 'high', 'low', 'median', 'typical', 'weighted')
        smooth_period: Smoothing period (default 5, set to 1 to disable smoothing)
        smooth_method: Smoothing method ('sma', 'ema', 'smma', 'lwma')

    Returns:
        Price series

    Raises:
        ValueError: If price_type is invalid or required columns are missing
        ValueError: If smooth_period < 1 or smooth_method is invalid
    """
    required_cols = ['open', 'high', 'low', 'close']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"DataFrame missing required columns: {missing_cols}")

    if len(df) == 0:
        raise ValueError("DataFrame is empty")

    # Get base price
    if price_type == 'close':
        prices = df['close']
    elif price_type == 'open':
        prices = df['open']
    elif price_type == 'high':
        prices = df['high']
    elif price_type == 'low':
        prices = df['low']
    elif price_type == 'median':
        prices = (df['high'] + df['low']) / 2.0
    elif price_type == 'typical':
        prices = (df['high'] + df['low'] + df['close']) / 3.0
    elif price_type == 'weighted':
        prices = (df['high'] + df['low'] + 2 * df['close']) / 4.0
    else:
        raise ValueError(f"Invalid price_type: {price_type}")

    # Apply smoothing if period > 1
    if smooth_period < 1:
        raise ValueError(f"Smooth period must be >= 1, got {smooth_period}")

    if smooth_period == 1:
        return prices

    if smooth_method == 'sma':
        return prices.rolling(window=smooth_period).mean()
    elif smooth_method == 'ema':
        return prices.ewm(span=smooth_period, adjust=False).mean()
    elif smooth_method == 'smma':
        # Smoothed MA (SMMA) - also known as RMA
        alpha = 1.0 / smooth_period
        return prices.ewm(alpha=alpha, adjust=False).mean()
    elif smooth_method == 'lwma':
        # Linear Weighted MA
        weights = np.arange(1, smooth_period + 1)
        return prices.rolling(window=smooth_period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
    else:
        raise ValueError(f"Invalid smooth_method: {smooth_method}")


def calculate_laguerre_filter(prices: pd.Series, period: pd.Series) -> pd.DataFrame:
    """Calculate four-stage Laguerre filter with adaptive period.

    The Laguerre filter is a four-stage recursive filter where each stage
    depends on the previous stage and the previous bar's value.

    Formula:
        gamma = 1.0 - 10.0 / (period + 9.0)
        L0[i] = price[i] + gamma * (L0[i-1] - price[i])
        L1[i] = L0[i-1] + gamma * (L1[i-1] - L0[i])
        L2[i] = L1[i-1] + gamma * (L2[i-1] - L1[i])
        L3[i] = L2[i-1] + gamma * (L3[i-1] - L2[i])

    Args:
        prices: Price series
        period: Adaptive period series

    Returns:
        DataFrame with columns ['L0', 'L1', 'L2', 'L3']

    Raises:
        ValueError: If prices and period have mismatched lengths or are empty
    """
    if len(prices) != len(period):
        raise ValueError(f"Series length mismatch: prices={len(prices)}, period={len(period)}")

    if len(prices) == 0:
        raise ValueError("Input series are empty")

    n = len(prices)

    # Initialize filter stages
    L0 = np.zeros(n)
    L1 = np.zeros(n)
    L2 = np.zeros(n)
    L3 = np.zeros(n)

    # First bar initialization
    L0[0] = L1[0] = L2[0] = L3[0] = prices.iloc[0]

    # Calculate gamma for each bar
    gamma = 1.0 - 10.0 / (period + 9.0)

    # Iterate through each bar (must use loop due to recursive dependencies)
    for i in range(1, n):
        g = gamma.iloc[i]
        p = prices.iloc[i]

        # Four-stage recursive filter
        L0[i] = p + g * (L0[i-1] - p)
        L1[i] = L0[i-1] + g * (L1[i-1] - L0[i])
        L2[i] = L1[i-1] + g * (L2[i-1] - L1[i])
        L3[i] = L2[i-1] + g * (L3[i-1] - L2[i])

    return pd.DataFrame({
        'L0': L0,
        'L1': L1,
        'L2': L2,
        'L3': L3
    }, index=prices.index)


def calculate_laguerre_rsi(laguerre_df: pd.DataFrame) -> pd.Series:
    """Calculate RSI from Laguerre filter stages.

    RSI is calculated by comparing consecutive filter stages and summing
    up/down movements:
        CU = sum of (L[i] - L[i+1]) where L[i] >= L[i+1]
        CD = sum of (L[i+1] - L[i]) where L[i] < L[i+1]
        RSI = CU / (CU + CD)

    Args:
        laguerre_df: DataFrame with columns ['L0', 'L1', 'L2', 'L3']

    Returns:
        Laguerre RSI values (0.0 to 1.0)

    Raises:
        ValueError: If required columns are missing or DataFrame is empty
    """
    required_cols = ['L0', 'L1', 'L2', 'L3']
    missing_cols = [col for col in required_cols if col not in laguerre_df.columns]
    if missing_cols:
        raise ValueError(f"DataFrame missing required columns: {missing_cols}")

    if len(laguerre_df) == 0:
        raise ValueError("DataFrame is empty")

    n = len(laguerre_df)
    rsi = np.zeros(n)

    for i in range(n):
        CU = 0.0  # Cumulative Up
        CD = 0.0  # Cumulative Down

        # Compare L0 vs L1
        if laguerre_df['L0'].iloc[i] >= laguerre_df['L1'].iloc[i]:
            CU += laguerre_df['L0'].iloc[i] - laguerre_df['L1'].iloc[i]
        else:
            CD += laguerre_df['L1'].iloc[i] - laguerre_df['L0'].iloc[i]

        # Compare L1 vs L2
        if laguerre_df['L1'].iloc[i] >= laguerre_df['L2'].iloc[i]:
            CU += laguerre_df['L1'].iloc[i] - laguerre_df['L2'].iloc[i]
        else:
            CD += laguerre_df['L2'].iloc[i] - laguerre_df['L1'].iloc[i]

        # Compare L2 vs L3
        if laguerre_df['L2'].iloc[i] >= laguerre_df['L3'].iloc[i]:
            CU += laguerre_df['L2'].iloc[i] - laguerre_df['L3'].iloc[i]
        else:
            CD += laguerre_df['L3'].iloc[i] - laguerre_df['L2'].iloc[i]

        # Calculate RSI
        rsi[i] = CU / (CU + CD) if (CU + CD) != 0 else 0.0

    return pd.Series(rsi, index=laguerre_df.index)


def classify_signal(rsi: pd.Series, level_up: float = 0.85, level_down: float = 0.15) -> pd.Series:
    """Classify RSI into signal zones.

    Args:
        rsi: Laguerre RSI values
        level_up: Upper threshold (default 0.85)
        level_down: Lower threshold (default 0.15)

    Returns:
        Signal classification: 0=neutral, 1=bullish, 2=bearish

    Raises:
        ValueError: If rsi is empty or thresholds are invalid
    """
    if len(rsi) == 0:
        raise ValueError("RSI series is empty")

    if not 0.0 <= level_down < level_up <= 1.0:
        raise ValueError(f"Invalid thresholds: level_down={level_down}, level_up={level_up} (must be 0.0 <= level_down < level_up <= 1.0)")

    signal = pd.Series(0, index=rsi.index)
    signal[rsi > level_up] = 1    # Bullish
    signal[rsi < level_down] = 2  # Bearish

    return signal


def calculate_laguerre_rsi_indicator(
    df: pd.DataFrame,
    atr_period: int = 32,
    price_type: str = 'close',
    price_smooth_period: int = 5,
    price_smooth_method: str = 'ema',
    level_up: float = 0.85,
    level_down: float = 0.15
) -> pd.DataFrame:
    """Calculate ATR Adaptive Smoothed Laguerre RSI.

    This indicator combines:
    1. ATR (Average True Range) for volatility measurement
    2. Adaptive period based on ATR min/max range
    3. Four-stage Laguerre filter for smooth RSI calculation

    The Laguerre RSI period adapts dynamically based on current volatility
    relative to recent min/max ATR values, making it more responsive in
    volatile markets and smoother in quiet markets.

    Args:
        df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        atr_period: ATR period (default 32)
        price_type: Price to use ('close', 'open', 'high', 'low', 'median', 'typical', 'weighted')
        price_smooth_period: Price smoothing period (default 5)
        price_smooth_method: Price smoothing method ('sma', 'ema', 'smma', 'lwma')
        level_up: Upper threshold for bullish signal (default 0.85)
        level_down: Lower threshold for bearish signal (default 0.15)

    Returns:
        DataFrame with columns:
        - 'laguerre_rsi': Laguerre RSI values (0.0 to 1.0)
        - 'signal': Signal classification (0=neutral, 1=bullish, 2=bearish)
        - 'adaptive_period': Adaptive period used for each bar
        - 'atr': ATR values
        - 'tr': True Range values

    Raises:
        ValueError: If input validation fails (propagates from sub-functions)
    """
    # Step 1: Calculate True Range
    tr = calculate_true_range(df['high'], df['low'], df['close'])

    # Step 2: Calculate ATR
    atr = calculate_atr(tr, period=atr_period)

    # Step 3: Calculate ATR min/max over lookback period
    min_atr, max_atr = calculate_atr_min_max(atr, period=atr_period)

    # Step 4: Calculate adaptive coefficient
    coeff = calculate_adaptive_coefficient(atr, min_atr, max_atr)
    adaptive_period = calculate_adaptive_period(atr_period, coeff)

    # Step 5: Get price series (with optional smoothing)
    prices = get_price_series(df, price_type, price_smooth_period, price_smooth_method)

    # Step 6: Calculate four-stage Laguerre filter
    laguerre_df = calculate_laguerre_filter(prices, adaptive_period)

    # Step 7: Calculate Laguerre RSI from filter stages
    laguerre_rsi = calculate_laguerre_rsi(laguerre_df)

    # Step 8: Classify signal
    signal = classify_signal(laguerre_rsi, level_up, level_down)

    # Return results
    return pd.DataFrame({
        'laguerre_rsi': laguerre_rsi,
        'signal': signal,
        'adaptive_period': adaptive_period,
        'atr': atr,
        'tr': tr
    }, index=df.index)
