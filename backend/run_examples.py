"""
Run example strategies (SMA crossover, RSI mean reversion, Breakout)
on a small custom universe and print comparative metrics.
"""

import os
import sys
from pathlib import Path

from models import BacktestConfig
from engine import BacktestEngine


def load_strategy_code(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_strategy(name: str, code: str, tickers, start_date, end_date) -> None:
    print(f"\n=== Running: {name} ===")
    config = BacktestConfig(
        strategy_code=code,
        universe="custom",
        custom_tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
        position_size=0.33,
        commission=0.001,
        slippage=0.0005,
        interval="1d",
    )

    engine = BacktestEngine(config)
    result = engine.run_backtest()

    if not result.success or not result.metrics:
        print(f"[FAILED] {result.message}")
        return

    m = result.metrics
    print("Results:")
    print(f"  Total Return: {m.total_return_percent:.2f}%")
    print(f"  CAGR: {m.cagr:.2f}%")
    print(f"  Sharpe: {m.sharpe_ratio:.2f}")
    print(f"  Max Drawdown: {m.max_drawdown_percent:.2f}%")
    print(f"  Win Rate: {m.win_rate*100:.1f}%")
    print(f"  Profit Factor: {m.profit_factor:.2f}")
    print(f"  Total Trades: {m.total_trades}")


def main():
    repo_root = Path(__file__).resolve().parents[1]
    examples = repo_root / "examples"

    sma_code = load_strategy_code(examples / "strategy_sma_crossover.py")
    rsi_code = load_strategy_code(examples / "strategy_rsi.py")
    brk_code = load_strategy_code(examples / "strategy_breakout.py")

    tickers = ["AAPL", "MSFT", "GOOGL"]
    start_date = "2023-01-01"
    end_date = "2024-01-01"

    run_strategy("SMA Crossover (stateful example)", sma_code, tickers, start_date, end_date)
    run_strategy("RSI Mean Reversion (stateful example)", rsi_code, tickers, start_date, end_date)
    run_strategy("Breakout (ATR)", brk_code, tickers, start_date, end_date)

    # Stateless variants (do not rely on 'state' persistence in sandbox)
    sma_stateless = '''def strategy(data, state):
    close = data['close'].values
    if len(close) < 50:
        return {'signal': None}

    s20 = pd.Series(close).rolling(20).mean()
    s50 = pd.Series(close).rolling(50).mean()

    if len(s50) < 2 or pd.isna(s20.iloc[-1]) or pd.isna(s50.iloc[-1]) or pd.isna(s20.iloc[-2]) or pd.isna(s50.iloc[-2]):
        return {'signal': None}

    prev20, prev50 = s20.iloc[-2], s50.iloc[-2]
    cur20, cur50 = s20.iloc[-1], s50.iloc[-1]

    if prev20 <= prev50 and cur20 > cur50:
        return {'signal': 'buy', 'stop_loss': 0.98, 'take_profit': 1.10}
    if prev20 >= prev50 and cur20 < cur50:
        return {'signal': 'sell'}
    return {'signal': None}
'''

    rsi_stateless = '''def strategy(data, state):
    close = data['close'].values
    if len(close) < 20:
        return {'signal': None}

    period = 14
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    if len(rsi) < 2 or pd.isna(rsi.iloc[-1]) or pd.isna(rsi.iloc[-2]):
        return {'signal': None}

    prev_rsi = rsi.iloc[-2]
    cur_rsi = rsi.iloc[-1]

    if cur_rsi < 30:
        return {'signal': 'buy', 'stop_loss': 0.97, 'take_profit': 1.08}
    if cur_rsi > 70 or (prev_rsi < 50 and cur_rsi >= 50):
        return {'signal': 'sell'}
    return {'signal': None}
'''

    run_strategy("SMA Crossover (stateless)", sma_stateless, tickers, start_date, end_date)
    run_strategy("RSI Mean Reversion (stateless)", rsi_stateless, tickers, start_date, end_date)


if __name__ == "__main__":
    main()
