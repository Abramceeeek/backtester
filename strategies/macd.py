"""
MACD Strategy (Moving Average Convergence Divergence)

Buy when MACD crosses above signal line
Sell when MACD crosses below signal line
"""

def strategy(data, state):
    """
    MACD crossover strategy.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    fast_period = 12
    slow_period = 26
    signal_period = 9

    if len(close) < slow_period + signal_period + 5:
        return {'signal': None}

    # Calculate MACD
    close_series = pd.Series(close)
    ema_fast = close_series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = close_series.ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]

    # Initialize state
    if 'prev_macd' not in state:
        state['prev_macd'] = current_macd
        state['prev_signal'] = current_signal
        return {'signal': None}

    prev_macd = state['prev_macd']
    prev_signal = state['prev_signal']

    # Update state
    state['prev_macd'] = current_macd
    state['prev_signal'] = current_signal

    # Bullish crossover (MACD crosses above signal)
    if prev_macd <= prev_signal and current_macd > current_signal:
        return {
            'signal': 'buy',
            'stop_loss': 0.97,      # 3% stop
            'take_profit': 1.09     # 9% target
        }

    # Bearish crossover (MACD crosses below signal)
    elif prev_macd >= prev_signal and current_macd < current_signal:
        return {'signal': 'sell'}

    return {'signal': None}
