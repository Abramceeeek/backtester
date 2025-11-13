"""
Streaming backtest engine - Yields results per stock as they complete.
"""

import pandas as pd
import numpy as np
from typing import Dict, AsyncGenerator
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import BacktestConfig
from engine import BacktestEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamingBacktestEngine(BacktestEngine):
    """Backtest engine that streams results as each stock completes."""

    async def run_backtest_streaming(
        self,
        data_dict: Dict[str, pd.DataFrame]
    ) -> AsyncGenerator[Dict, None]:
        """
        Run backtest across multiple tickers and yield results as they complete.

        Args:
            data_dict: Dictionary mapping tickers to DataFrames

        Yields:
            Dict with ticker performance data for each completed stock
        """
        max_workers = min(10, len(data_dict))

        # Create executor and submit all jobs
        executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = {
            executor.submit(self._run_single_ticker_backtest, ticker, data): ticker
            for ticker, data in data_dict.items()
        }

        # Yield results as they complete
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                result = future.result()
                if result:
                    # Convert TickerPerformance to dict for JSON serialization
                    yield {
                        "success": True,
                        "ticker": result.ticker,
                        "total_trades": result.total_trades,
                        "winning_trades": result.winning_trades,
                        "losing_trades": result.losing_trades,
                        "total_pnl": result.total_pnl,
                        "total_pnl_percent": result.total_pnl_percent,
                        "win_rate": result.win_rate,
                        "avg_trade_pnl": result.avg_trade_pnl,
                        "best_trade": result.best_trade,
                        "worst_trade": result.worst_trade,
                        "trades": [
                            {
                                "ticker": t.ticker,
                                "entry_date": t.entry_date,
                                "exit_date": t.exit_date,
                                "entry_price": t.entry_price,
                                "exit_price": t.exit_price,
                                "size": t.size,
                                "pnl": t.pnl,
                                "pnl_percent": t.pnl_percent,
                                "exit_reason": t.exit_reason,
                                "bars_held": t.bars_held
                            }
                            for t in (result.trades or [])
                        ]
                    }
                else:
                    yield {
                        "success": False,
                        "ticker": ticker,
                        "error": "No result returned"
                    }
            except Exception as e:
                logger.error(f"Failed to backtest {ticker}: {e}")
                yield {
                    "success": False,
                    "ticker": ticker,
                    "error": str(e)
                }

            # Allow other tasks to run
            await asyncio.sleep(0)

        executor.shutdown(wait=False)
