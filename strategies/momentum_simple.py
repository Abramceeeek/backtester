"""
Time-Series Momentum (Trend Following) - Simplified for bar-by-bar execution

Go long if past return > 0, short otherwise.
Adapted from the TradingStrategiesLibrary for intraday backtesting.
"""

def strategy(data, state):
    """
    Simple momentum strategy based on lookback return.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    # Need enough bars for lookback
    lookback_bars = 50  # Adjust based on your timeframe
    if len(close) < lookback_bars + 5:
        return {'signal': None}

    # Calculate past return over lookback period
    past_return = (close[-1] / close[-lookback_bars] - 1.0)

    # Track if we have a position
    has_position = state.get('has_position', False)
    position_type = state.get('position_type', None)

    # Enter long on positive momentum
    if not has_position and past_return > 0.02:  # 2% threshold
        state['has_position'] = True
        state['position_type'] = 'long'
        return {
            'signal': 'buy',
            'stop_loss': 0.97,      # 3% stop
            'take_profit': 1.10     # 10% target
        }

    # Exit long on negative momentum
    elif has_position and position_type == 'long' and past_return < 0:
        state['has_position'] = False
        state['position_type'] = None
        return {'signal': 'sell'}

    return {'signal': None}
