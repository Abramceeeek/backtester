"""
Strategy Template - Use this as a starting point for your own strategies

Copy this file and modify the strategy() function with your own logic.
"""

def strategy(data, state):
    """
    Your strategy logic here.

    Args:
        data: pandas DataFrame with OHLCV columns
              Columns: open, high, low, close, volume
              - data.iloc[-1] gives you the current bar
              - data['close'].values gives you numpy array of all close prices
              - pd (pandas) and np (numpy) are already available

        state: dict for persisting variables across bars
               - Use this to track previous values, positions, etc.
               - State is maintained across bars but reset for each ticker
               - Example: state['sma'] = current_sma

    Returns:
        dict with signal and optional risk parameters:
            {
                'signal': 'buy' | 'sell' | None,
                'stop_loss': price or multiplier (optional),
                'take_profit': price or multiplier (optional)
            }

        Stop Loss / Take Profit formats:
            - Multiplier < 1: interpreted as percentage (e.g., 0.98 = 2% stop loss)
            - Price > 1: interpreted as absolute price
    """

    # Example: Access price data
    close = data['close'].values
    high = data['high'].values
    low = data['low'].values
    volume = data['volume'].values

    # Need minimum bars for calculations
    if len(close) < 50:
        return {'signal': None}

    # Example: Calculate indicators using pandas (pd is available)
    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    current_price = close[-1]

    # Example: Use state to track previous values
    if 'prev_sma_20' not in state:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': None}

    prev_sma_20 = state['prev_sma_20']
    prev_sma_50 = state['prev_sma_50']

    # Update state for next iteration
    state['prev_sma_20'] = sma_20
    state['prev_sma_50'] = sma_50

    # Example: Simple crossover logic
    # Buy when fast MA crosses above slow MA
    if prev_sma_20 <= prev_sma_50 and sma_20 > sma_50:
        return {
            'signal': 'buy',
            'stop_loss': 0.98,      # 2% stop loss
            'take_profit': 1.10     # 10% take profit
        }

    # Sell when fast MA crosses below slow MA
    elif prev_sma_20 >= prev_sma_50 and sma_20 < sma_50:
        return {'signal': 'sell'}

    # No signal - hold current position
    return {'signal': None}


# Optional: Add strategy metadata as comments
"""
Strategy Name: Template Strategy
Description: Simple moving average crossover example
Timeframes: Works on all timeframes
Parameters:
    - Fast SMA: 20 periods
    - Slow SMA: 50 periods
    - Stop Loss: 2%
    - Take Profit: 10%

Notes:
    - This is just an example template
    - Replace the logic with your own strategy
    - Test thoroughly before using real money!
"""
