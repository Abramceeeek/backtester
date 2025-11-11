# Strategy Writing Guide

A quick reference for writing trading strategies for the backtester.

## Template

```python
def strategy(data, state):
    """
    Your strategy description here.

    Args:
        data: pandas DataFrame with ['open', 'high', 'low', 'close', 'volume']
        state: dict for persisting variables between calls

    Returns:
        dict with 'signal', optional 'stop_loss', 'take_profit'
    """
    close = data['close'].values

    # Your logic here

    return {'signal': 'buy', 'stop_loss': 0.98, 'take_profit': 1.05}
```

## Important Rules

### ✅ DO

- Use `pd` and `np` directly (they're pre-loaded)
- Access data via: `data['close'].values`, `data['high']`, etc.
- Store state: `state['my_var'] = value`
- Return valid signals: `'buy'`, `'sell'`, `'flat'`, `'hold'`, or `None`
- Use multipliers for stops: `0.98` = 2% below, `1.05` = 5% above

### ❌ DON'T

- **DON'T use import statements** (will cause validation errors)
- Don't access filesystem, network, or OS functions
- Don't use eval, exec, or __import__
- Don't return invalid signal types

## Available in Your Strategy

### Pre-loaded Modules
- `pd` or `pandas` - Full pandas library
- `np` or `numpy` - Full numpy library

### Built-in Functions
- Math: `abs()`, `max()`, `min()`, `sum()`, `pow()`, `round()`
- Iteration: `len()`, `range()`, `enumerate()`, `zip()`, `map()`
- Types: `int()`, `float()`, `str()`, `bool()`, `list()`, `dict()`, `tuple()`, `set()`
- Logic: `all()`, `any()`, `sorted()`

## Signal Return Format

```python
{
    'signal': 'buy',           # Required: 'buy', 'sell', 'flat', 'hold', or None
    'size': 1.0,               # Optional: position size multiplier
    'stop_loss': 0.98,         # Optional: 0.98 = 2% below entry
    'take_profit': 1.05        # Optional: 1.05 = 5% above entry
}
```

## Common Patterns

### 1. Simple Moving Average Crossover

```python
def strategy(data, state):
    close = data['close'].values

    if len(close) < 50:
        return {'signal': None}

    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    if 'prev_sma_20' not in state:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': None}

    # Bullish crossover
    if state['prev_sma_20'] <= state['prev_sma_50'] and sma_20 > sma_50:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': 'buy', 'stop_loss': 0.95, 'take_profit': 1.10}

    # Bearish crossover
    if state['prev_sma_20'] >= state['prev_sma_50'] and sma_20 < sma_50:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': 'sell'}

    state['prev_sma_20'] = sma_20
    state['prev_sma_50'] = sma_50
    return {'signal': None}
```

### 2. RSI Oversold/Overbought

```python
def strategy(data, state):
    close = data['close'].values

    if len(close) < 20:
        return {'signal': None}

    # Calculate RSI
    period = 14
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    # Buy when oversold
    if current_rsi < 30:
        return {'signal': 'buy', 'stop_loss': 0.97, 'take_profit': 1.08}

    # Sell when overbought
    if current_rsi > 70:
        return {'signal': 'sell'}

    return {'signal': None}
```

### 3. Bollinger Bands Mean Reversion

```python
def strategy(data, state):
    close = data['close'].values

    if len(close) < 20:
        return {'signal': None}

    # Calculate Bollinger Bands
    period = 20
    std_dev = 2

    sma = pd.Series(close).rolling(period).mean().iloc[-1]
    std = pd.Series(close).rolling(period).std().iloc[-1]

    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    current_price = close[-1]

    # Buy when price touches lower band
    if current_price <= lower_band:
        return {'signal': 'buy', 'stop_loss': 0.96, 'take_profit': 1.08}

    # Sell when price touches upper band
    if current_price >= upper_band:
        return {'signal': 'sell'}

    return {'signal': None}
```

### 4. Momentum Breakout

```python
def strategy(data, state):
    if len(data) < 21:
        return {'signal': None}

    close = data['close'].values
    high = data['high'].values
    low = data['low'].values

    # 20-day high/low
    highest_20 = np.max(high[-21:-1])
    lowest_20 = np.min(low[-21:-1])
    current_close = close[-1]

    # Calculate ATR for stop loss
    high_series = pd.Series(high)
    low_series = pd.Series(low)
    close_series = pd.Series(close)

    tr = pd.concat([
        high_series - low_series,
        abs(high_series - close_series.shift(1)),
        abs(low_series - close_series.shift(1))
    ], axis=1).max(axis=1)

    atr = tr.rolling(14).mean().iloc[-1]

    # Breakout above resistance
    if current_close > highest_20:
        stop_distance = 2 * atr
        return {
            'signal': 'buy',
            'stop_loss': (current_close - stop_distance) / current_close,
            'take_profit': (current_close + 2 * stop_distance) / current_close
        }

    # Breakdown below support
    if current_close < lowest_20:
        return {'signal': 'sell'}

    return {'signal': None}
```

### 5. Volume-Weighted Price Action

```python
def strategy(data, state):
    if len(data) < 20:
        return {'signal': None}

    close = data['close'].values
    volume = data['volume'].values

    # Calculate VWAP
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    vwap = (typical_price * data['volume']).rolling(20).sum() / data['volume'].rolling(20).sum()
    current_vwap = vwap.iloc[-1]
    current_price = close[-1]

    # Calculate average volume
    avg_volume = pd.Series(volume).rolling(20).mean().iloc[-1]
    current_volume = volume[-1]

    # Buy when price below VWAP with high volume
    if current_price < current_vwap * 0.99 and current_volume > avg_volume * 1.5:
        return {'signal': 'buy', 'stop_loss': 0.97, 'take_profit': 1.06}

    # Sell when price above VWAP
    if current_price > current_vwap * 1.01:
        return {'signal': 'sell'}

    return {'signal': None}
```

## Debugging Tips

1. **Check data length**: Always verify `len(data)` before calculations
2. **Use state for memory**: Store indicators in `state` to avoid recalculation
3. **Test locally first**: Use the validation endpoint to check syntax
4. **Start simple**: Begin with basic logic, then add complexity
5. **Handle edge cases**: Return `{'signal': None}` when unsure

## Common Errors

### Error: "Forbidden operation: Import at line X"
**Solution**: Remove all `import` statements. Use `pd` and `np` directly.

```python
# ❌ WRONG
import pandas as pd
sma = pd.Series(close).rolling(20).mean()

# ✅ CORRECT
sma = pd.Series(close).rolling(20).mean()
```

### Error: "Strategy must return a dict"
**Solution**: Always return a dictionary with at least a 'signal' key.

```python
# ❌ WRONG
return None

# ✅ CORRECT
return {'signal': None}
```

### Error: "Invalid signal"
**Solution**: Only use valid signal values.

```python
# ❌ WRONG
return {'signal': 'long'}  # 'long' not valid

# ✅ CORRECT
return {'signal': 'buy'}  # Use 'buy' instead
```

## Performance Tips

1. Use vectorized pandas operations instead of loops
2. Store computed indicators in `state` to avoid recalculation
3. Minimize use of `.apply()` or `.map()` - use native pandas methods
4. Use `.values` to get numpy arrays for faster math operations

## Next Steps

- Check `examples/` directory for complete working strategies
- Use `/api/strategy/template` endpoint to get the base template
- Test with a shorter date range first (1-2 years)
- Start with fewer tickers to validate logic
- Monitor the metrics to understand strategy performance

Happy trading! 📈
