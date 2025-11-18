"""
Short-Horizon Mean Reversion
Contrarian to short-term moves: buy losers / sell winners.
Adapted from TradingStrategiesLibrary strategy_short_reversion
"""

def strategy(data, state):
    """
    Mean reversion using z-score of recent returns.

    Args:
        data: pandas DataFrame with OHLCV columns
        state: dict for persisting variables

    Returns:
        dict with signal and risk parameters
    """
    close = data['close'].values

    lookback = 20  # Window for z-score calculation
    if len(close) < lookback + 5:
        return {'signal': None}

    # Calculate returns
    returns = pd.Series(close).pct_change().fillna(0)

    # Calculate z-score of recent returns
    recent_rets = returns.iloc[-lookback:]
    mean = recent_rets.mean()
    std = recent_rets.std()

    if std < 1e-8:  # Avoid division by zero
        return {'signal': None}

    current_return = returns.iloc[-1]
    z_score = (current_return - mean) / std

    # Track position state
    has_position = state.get('has_position', False)
    position_type = state.get('position_type', None)

    z_entry = 1.5  # Entry threshold
    z_exit = 0.3   # Exit threshold

    # Buy when price has dropped significantly (negative z-score)
    if not has_position and z_score < -z_entry:
        state['has_position'] = True
        state['position_type'] = 'long'
        return {
            'signal': 'buy',
            'stop_loss': 0.96,      # 4% stop
            'take_profit': 1.06     # 6% target
        }

    # Exit when z-score returns toward mean
    elif has_position and position_type == 'long' and z_score > -z_exit:
        state['has_position'] = False
        state['position_type'] = None
        return {'signal': 'sell'}

    return {'signal': None}
