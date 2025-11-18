"""
Bollinger Bands Strategy

Buy when price touches lower band (oversold)
Sell when price touches upper band (overbought)
"""

def strategy(data, state):
    """
    Bollinger Bands mean reversion strategy.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    window = 20
    num_std = 2.0

    if len(close) < window + 5:
        return {'signal': None}

    # Calculate Bollinger Bands
    close_series = pd.Series(close)
    sma = close_series.rolling(window).mean()
    std = close_series.rolling(window).std()

    upper_band = sma + (num_std * std)
    lower_band = sma - (num_std * std)

    current_price = close[-1]
    current_upper = upper_band.iloc[-1]
    current_lower = lower_band.iloc[-1]
    current_sma = sma.iloc[-1]

    # Track position
    has_position = state.get('has_position', False)
    position_type = state.get('position_type', None)

    # Buy at lower band (oversold)
    if not has_position and current_price <= current_lower:
        state['has_position'] = True
        state['position_type'] = 'long'
        return {
            'signal': 'buy',
            'stop_loss': 0.96,      # 4% stop
            'take_profit': current_sma / current_price  # Target the middle band
        }

    # Exit at upper band or middle
    elif has_position and position_type == 'long' and current_price >= current_sma:
        state['has_position'] = False
        state['position_type'] = None
        return {'signal': 'sell'}

    return {'signal': None}
