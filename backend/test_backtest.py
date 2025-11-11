"""
Quick end-to-end backtest test with a few tickers.
"""

from models import BacktestConfig
from engine import BacktestEngine
import json

# Simple strategy code
strategy_code = """
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

    prev_sma_20 = state['prev_sma_20']
    prev_sma_50 = state['prev_sma_50']

    state['prev_sma_20'] = sma_20
    state['prev_sma_50'] = sma_50

    if prev_sma_20 <= prev_sma_50 and sma_20 > sma_50:
        return {'signal': 'buy', 'stop_loss': 0.95, 'take_profit': 1.10}
    elif prev_sma_20 >= prev_sma_50 and sma_20 < sma_50:
        return {'signal': 'sell'}

    return {'signal': None}
"""

# Create config with just 3 tickers and 1 year
config = BacktestConfig(
    strategy_code=strategy_code,
    custom_tickers=["AAPL", "MSFT", "GOOGL"],
    universe="custom",
    start_date="2023-01-01",
    end_date="2024-01-01",
    initial_capital=100000,
    position_size=0.3
)

print("Running backtest...")
print(f"Tickers: {config.custom_tickers}")
print(f"Period: {config.start_date} to {config.end_date}")
print()

# Run backtest
engine = BacktestEngine(config)
result = engine.run_backtest()

if result.success:
    print("=== BACKTEST RESULTS ===")
    print(f"Total Return: {result.metrics.total_return_percent:.2f}%")
    print(f"CAGR: {result.metrics.cagr:.2f}%")
    print(f"Sharpe Ratio: {result.metrics.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {result.metrics.max_drawdown_percent:.2f}%")
    print(f"Win Rate: {result.metrics.win_rate*100:.1f}%")
    print(f"Total Trades: {result.metrics.total_trades}")
    print(f"Profit Factor: {result.metrics.profit_factor:.2f}")
    print()
    print(f"Execution time: {result.execution_time:.2f}s")
    print()
    print("Top performers:")
    for perf in result.top_performers[:3]:
        print(f"  {perf.ticker}: ${perf.total_pnl:,.2f} ({perf.win_rate*100:.1f}% win rate)")
else:
    print(f"Backtest failed: {result.message}")
