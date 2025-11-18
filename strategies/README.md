# Strategies Folder

Place your trading strategy files here. Each strategy should be a Python file with a `strategy()` function.

## Strategy Template

```python
def strategy(data, state):
    """
    Your strategy logic here.

    Args:
        data: pandas DataFrame with OHLCV columns (open, high, low, close, volume)
              - All data up to current bar is available
              - Use data.iloc[-1] for current bar
              - pd and np are available (no need to import)

        state: dict for persisting variables across bars
               - Use this to track indicators, positions, etc.
               - Gets reset for each ticker

    Returns:
        dict with:
            - signal: 'buy', 'sell', or None
            - stop_loss (optional): price or multiplier (< 1 means %)
            - take_profit (optional): price or multiplier (> 1 means price, < 1 means %)
    """
    close = data['close'].values

    # Your logic here

    return {
        'signal': 'buy',  # or 'sell' or None
        'stop_loss': 0.98,  # 2% stop loss
        'take_profit': 1.05  # 5% take profit
    }
```

## Notes

- All `.py` files in this folder will be automatically discovered
- Strategy files should contain a `strategy(data, state)` function
- Use descriptive filenames (e.g., `macd_crossover.py`, `bollinger_bands.py`)
- Test your strategies with the batch runner: `python batch_backtest.py`
