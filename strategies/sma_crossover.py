"""
Example Strategy: Simple Moving Average Crossover

This strategy uses two moving averages (fast and slow) to generate buy/sell signals.
- Buy when fast MA crosses above slow MA
- Sell when fast MA crosses below slow MA
- Uses 2% stop loss and 10% take profit
"""

def strategy(data, state):
    """
    Simple moving average crossover strategy.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    # Need at least 50 bars to calculate slow MA
    if len(close) < 50:
        return {'signal': None}

    # Calculate moving averages (pd is already available, no import needed)
    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    # Initialize state on first call
    if 'prev_sma_20' not in state:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': None}

    # Get previous MA values
    prev_sma_20 = state['prev_sma_20']
    prev_sma_50 = state['prev_sma_50']

    # Update state for next iteration
    state['prev_sma_20'] = sma_20
    state['prev_sma_50'] = sma_50

    # Check for crossover
    if prev_sma_20 <= prev_sma_50 and sma_20 > sma_50:
        # Bullish crossover - BUY
        return {
            'signal': 'buy',
            'stop_loss': 0.98,      # 2% stop loss
            'take_profit': 1.10     # 10% take profit
        }
    elif prev_sma_20 >= prev_sma_50 and sma_20 < sma_50:
        # Bearish crossover - SELL
        return {'signal': 'sell'}

    # No crossover - hold current position
    return {'signal': None}
