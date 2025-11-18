"""
Example Strategy: Breakout Strategy

This strategy identifies breakouts from recent price ranges.
- Buy when price breaks above the 20-day high
- Sell when price breaks below the 20-day low
- Uses ATR-based stop loss and 2:1 reward-risk ratio
"""

def strategy(data, state):
    """
    Breakout strategy with ATR-based stops.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    if len(data) < 25:
        return {'signal': None}

    # pd and np are already available, no import needed
    close = data['close'].values
    high = data['high'].values
    low = data['low'].values

    current_close = close[-1]

    # Calculate 20-day high and low
    lookback = 20
    highest_high = np.max(high[-lookback-1:-1])  # Exclude current bar
    lowest_low = np.min(low[-lookback-1:-1])

    # Calculate ATR for dynamic stop loss
    atr_period = 14
    high_series = pd.Series(high)
    low_series = pd.Series(low)
    close_series = pd.Series(close)

    tr1 = high_series - low_series
    tr2 = abs(high_series - close_series.shift(1))
    tr3 = abs(low_series - close_series.shift(1))

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=atr_period).mean().iloc[-1]

    # Track if we have a position
    has_position = state.get('has_position', False)
    position_type = state.get('position_type', None)

    if not has_position:
        # Check for breakout above resistance
        if current_close > highest_high:
            state['has_position'] = True
            state['position_type'] = 'long'

            # Set stop loss at 2 ATR below entry
            stop_loss_distance = 2 * atr
            stop_loss_price = current_close - stop_loss_distance

            # Take profit at 2:1 reward-risk
            take_profit_price = current_close + (2 * stop_loss_distance)

            return {
                'signal': 'buy',
                'stop_loss': stop_loss_price / current_close,  # As multiplier
                'take_profit': take_profit_price / current_close
            }

        # Check for breakdown below support
        elif current_close < lowest_low:
            # For demonstration, we'll exit longs on breakdown
            # In a real strategy, you might implement short positions
            return {'signal': None}

    else:
        # If we have a long position, check for exit on breakdown
        if position_type == 'long' and current_close < lowest_low:
            state['has_position'] = False
            state['position_type'] = None
            return {'signal': 'sell'}

    return {'signal': None}
