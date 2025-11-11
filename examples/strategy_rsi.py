"""
Example Strategy: RSI Mean Reversion

This strategy uses the Relative Strength Index (RSI) for mean reversion trades.
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought) or when RSI crosses back above 50
- Uses 3% stop loss and 8% take profit
"""

def strategy(data, state):
    """
    RSI mean reversion strategy.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    # Need at least 20 bars for RSI calculation
    if len(close) < 20:
        return {'signal': None}

    # Calculate RSI (pd and np are already available, no import needed)
    period = 14
    delta = pd.Series(close).diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]

    # Store previous RSI for trend detection
    if 'prev_rsi' not in state:
        state['prev_rsi'] = current_rsi
        return {'signal': None}

    prev_rsi = state['prev_rsi']
    state['prev_rsi'] = current_rsi

    # Check if we have an open position
    has_position = state.get('has_position', False)

    if not has_position:
        # Look for oversold conditions (RSI < 30)
        if current_rsi < 30:
            state['has_position'] = True
            return {
                'signal': 'buy',
                'stop_loss': 0.97,      # 3% stop loss
                'take_profit': 1.08     # 8% take profit
            }
    else:
        # Exit conditions:
        # 1. RSI becomes overbought (> 70)
        # 2. RSI crosses back above 50 (momentum turning)
        if current_rsi > 70 or (prev_rsi < 50 and current_rsi >= 50):
            state['has_position'] = False
            return {'signal': 'sell'}

    return {'signal': None}
