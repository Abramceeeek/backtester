"""
EMA Crossover Strategy

Fast EMA crosses above slow EMA = Buy
Fast EMA crosses below slow EMA = Sell
"""

def strategy(data, state):
    """
    Exponential Moving Average crossover strategy.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    fast_period = 12
    slow_period = 26

    if len(close) < slow_period + 5:
        return {'signal': None}

    # Calculate EMAs
    close_series = pd.Series(close)
    ema_fast = close_series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = close_series.ewm(span=slow_period, adjust=False).mean()

    current_fast = ema_fast.iloc[-1]
    current_slow = ema_slow.iloc[-1]

    # Initialize state
    if 'prev_fast' not in state:
        state['prev_fast'] = current_fast
        state['prev_slow'] = current_slow
        return {'signal': None}

    prev_fast = state['prev_fast']
    prev_slow = state['prev_slow']

    # Update state
    state['prev_fast'] = current_fast
    state['prev_slow'] = current_slow

    # Bullish crossover
    if prev_fast <= prev_slow and current_fast > current_slow:
        return {
            'signal': 'buy',
            'stop_loss': 0.97,      # 3% stop
            'take_profit': 1.08     # 8% target
        }

    # Bearish crossover
    elif prev_fast >= prev_slow and current_fast < current_slow:
        return {'signal': 'sell'}

    return {'signal': None}
