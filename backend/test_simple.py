"""
Simple test with buy-and-hold strategy to verify the system works.
"""

from models import BacktestConfig
from engine import BacktestEngine

# Simple buy-and-hold strategy that always buys on first bar
strategy_code = """
def strategy(data, state):
    # Buy once and hold
    if 'bought' not in state:
        state['bought'] = True
        return {'signal': 'buy', 'stop_loss': 0.90, 'take_profit': 1.20}

    return {'signal': None}
"""

config = BacktestConfig(
    strategy_code=strategy_code,
    custom_tickers=["AAPL"],
    universe="custom",
    start_date="2023-01-01",
    end_date="2024-01-01",
    initial_capital=100000,
    position_size=0.99  # Almost all capital
)

print("Running simple buy-and-hold backtest on AAPL...")
print()

engine = BacktestEngine(config)
result = engine.run_backtest()

if result.success:
    print("SUCCESS!")
    print(f"Total Return: {result.metrics.total_return_percent:.2f}%")
    print(f"Total Trades: {result.metrics.total_trades}")
    print(f"Win Rate: {result.metrics.win_rate*100:.1f}%")
    if result.sample_trades:
        trade = result.sample_trades[0]
        print(f"\\nTrade details:")
        print(f"  Entry: {trade.entry_date} @ ${trade.entry_price:.2f}")
        print(f"  Exit: {trade.exit_date} @ ${trade.exit_price:.2f}")
        print(f"  P&L: ${trade.pnl:,.2f} ({trade.pnl_percent:.2f}%)")
        print(f"  Exit reason: {trade.exit_reason}")
else:
    print(f"FAILED: {result.message}")
