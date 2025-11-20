"""
Backtest engine - Core logic for running trading strategy backtests.
Handles position management, order execution, risk management, and metrics calculation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import (
    BacktestConfig, BacktestResult, BacktestMetrics,
    Trade, TickerPerformance, EquityPoint
)
from sandbox import get_sandbox
from data_loader import get_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an open position."""
    ticker: str
    entry_date: str
    entry_price: float
    size: float
    direction: str = 'long'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    entry_bar: int = 0


@dataclass
class PortfolioState:
    """Tracks portfolio state during backtest."""
    cash: float
    equity: float
    positions: Dict[str, Position] = field(default_factory=dict)
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[EquityPoint] = field(default_factory=list)


class BacktestEngine:
    """Core backtesting engine."""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.sandbox = get_sandbox()
        self.loader = get_loader()

    def run_backtest(self) -> BacktestResult:
        """
        Execute the complete backtest.

        Returns:
            BacktestResult with all metrics and trades
        """
        start_time = datetime.now()

        try:
            # Validate strategy code first
            self.sandbox.validate(self.config.strategy_code)

            # Get tickers
            if self.config.universe == 'sp500':
                tickers = self.loader.get_sp500_tickers()
                # Apply limit BEFORE data loading
                if self.config.limit_tickers and self.config.limit_tickers > 0:
                    tickers = tickers[:self.config.limit_tickers]
                    logger.info(f"Limited to first {len(tickers)} tickers for quick testing")
            elif self.config.custom_tickers:
                tickers = self.config.custom_tickers
            else:
                return BacktestResult(
                    success=False,
                    message="Must specify universe='sp500' or provide custom_tickers"
                )

            # Load historical data for all tickers
            logger.info(f"Loading data for {len(tickers)} tickers...")
            data_dict = self.loader.get_bulk_data(
                tickers,
                self.config.start_date,
                self.config.end_date,
                self.config.interval
            )

            if not data_dict:
                return BacktestResult(
                    success=False,
                    message="Failed to load any ticker data"
                )

            logger.info(f"Loaded data for {len(data_dict)} tickers")

            # Run backtest for each ticker
            ticker_results, all_trades_dict = self._run_multi_ticker_backtest(data_dict)

            # Aggregate results using all trades
            result = self._aggregate_results(ticker_results, all_trades_dict)
            result.config = self.config
            result.execution_time = (datetime.now() - start_time).total_seconds()

            return result

        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            return BacktestResult(
                success=False,
                message=f"Backtest failed: {str(e)}"
            )

    def _run_multi_ticker_backtest(
        self,
        data_dict: Dict[str, pd.DataFrame]
    ) -> tuple[List[TickerPerformance], Dict[str, List[Trade]]]:
        """
        Run backtest across multiple tickers in parallel.

        Args:
            data_dict: Dictionary mapping tickers to DataFrames

        Returns:
            List of TickerPerformance results
        """
        results = []
        all_trades_dict = {}  # Store all trades by ticker

        # Use ThreadPoolExecutor for parallel execution
        max_workers = min(10, len(data_dict))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._run_single_ticker_backtest, ticker, data): ticker
                for ticker, data in data_dict.items()
            }

            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    result = future.result()
                    if result:
                        performance, trades = result
                        results.append(performance)
                        all_trades_dict[ticker] = trades
                except Exception as e:
                    logger.error(f"Failed to backtest {ticker}: {e}")

        return results, all_trades_dict

    def _run_single_ticker_backtest(
        self,
        ticker: str,
        data: pd.DataFrame
    ) -> Optional[tuple[TickerPerformance, List[Trade]]]:
        """
        Run backtest for a single ticker.

        Args:
            ticker: Stock ticker symbol
            data: Historical OHLCV data

        Returns:
            TickerPerformance or None if failed
        """
        try:
            portfolio = PortfolioState(
                cash=self.config.initial_capital,
                equity=self.config.initial_capital
            )

            strategy_state = {}
            current_position = None
            trades = []

            # Pre-extract numpy views for hot columns to minimize pandas overhead
            close_prices = data['close'].to_numpy(copy=False)
            high_prices = data['high'].to_numpy(copy=False)
            low_prices = data['low'].to_numpy(copy=False)
            index_values = data.index
            total_bars = len(data)

            # Bar-by-bar simulation
            for i in range(total_bars):
                current_date = index_values[i].strftime('%Y-%m-%d')
                current_close = close_prices[i]

                # Check for stop loss / take profit on existing position
                if current_position:
                    exit_reason = None
                    exit_price = None

                    # Check stop loss
                    if current_position.stop_loss:
                        if low_prices[i] <= current_position.stop_loss:
                            exit_reason = 'stop_loss'
                            exit_price = current_position.stop_loss

                    # Check take profit
                    if current_position.take_profit and not exit_reason:
                        if high_prices[i] >= current_position.take_profit:
                            exit_reason = 'take_profit'
                            exit_price = current_position.take_profit

                    # Close position if triggered
                    if exit_reason:
                        if not exit_price:
                            exit_price = current_close

                        trade = self._close_position(
                            current_position,
                            current_date,
                            exit_price,
                            exit_reason,
                            i
                        )
                        # Update portfolio cash with proceeds from closing position
                        proceeds = exit_price * current_position.size
                        exit_commission = proceeds * self.config.commission
                        portfolio.cash += (proceeds - exit_commission)
                        trades.append(trade)
                        current_position = None

                # Run strategy logic if no position or strategy can override
                try:
                    # Avoid slicing for the final bar where full data is already available
                    if i == total_bars - 1:
                        current_bar = data
                    else:
                        current_bar = data.iloc[:i+1]
                    signal = self.sandbox.execute(
                        self.config.strategy_code,
                        current_bar,
                        strategy_state
                    )
                except Exception as e:
                    logger.warning(f"Strategy execution failed for {ticker} at {current_date}: {e}")
                    continue

                # Process signal
                if signal['signal'] in ['buy', 'long'] and not current_position:
                    # Open long position
                    position_value = portfolio.cash * self.config.position_size
                    entry_price = current_close * (1 + self.config.slippage)
                    shares = position_value / entry_price

                    # Apply commission
                    commission = position_value * self.config.commission
                    portfolio.cash -= (position_value + commission)

                    # Calculate stop loss and take profit prices
                    stop_loss_price = None
                    take_profit_price = None

                    if 'stop_loss' in signal and signal['stop_loss']:
                        sl = signal['stop_loss']
                        if sl < 1:  # Multiplier format
                            stop_loss_price = entry_price * sl
                        else:  # Absolute price
                            stop_loss_price = sl

                    if 'take_profit' in signal and signal['take_profit']:
                        tp = signal['take_profit']
                        if tp > 1 or tp < 0.5:  # Absolute or multiplier > 1
                            if tp > entry_price * 0.5:
                                take_profit_price = tp
                            else:
                                take_profit_price = entry_price * tp
                        else:
                            take_profit_price = entry_price * tp

                    current_position = Position(
                        ticker=ticker,
                        entry_date=current_date,
                        entry_price=entry_price,
                        size=shares,
                        direction='long',
                        stop_loss=stop_loss_price,
                        take_profit=take_profit_price,
                        entry_bar=i
                    )

                elif signal['signal'] in ['sell', 'flat', 'exit'] and current_position:
                    # Close position on sell signal
                    exit_price = current_close * (1 - self.config.slippage)
                    trade = self._close_position(
                        current_position,
                        current_date,
                        exit_price,
                        'signal',
                        i
                    )
                    # Update portfolio cash with proceeds from closing position
                    proceeds = exit_price * current_position.size
                    exit_commission = proceeds * self.config.commission
                    portfolio.cash += (proceeds - exit_commission)
                    trades.append(trade)
                    current_position = None

            # Close any remaining position at end of backtest
            if current_position:
                final_date = index_values[-1].strftime('%Y-%m-%d')
                final_price = close_prices[-1] * (1 - self.config.slippage)
                trade = self._close_position(
                    current_position,
                    final_date,
                    final_price,
                    'end_of_backtest',
                    total_bars - 1
                )
                # Update portfolio cash with proceeds from closing position
                proceeds = final_price * current_position.size
                exit_commission = proceeds * self.config.commission
                portfolio.cash += (proceeds - exit_commission)
                trades.append(trade)

            # Calculate performance metrics
            if not trades:
                logger.info(f"{ticker}: No trades generated")
                return None

            logger.info(f"{ticker}: Generated {len(trades)} trades")
            performance = self._calculate_ticker_performance(ticker, trades)
            return (performance, trades)  # Return both performance and all trades

        except Exception as e:
            logger.error(f"Error backtesting {ticker}: {e}")
            return None

    def _close_position(
        self,
        position: Position,
        exit_date: str,
        exit_price: float,
        exit_reason: str,
        exit_bar: int
    ) -> Trade:
        """
        Close a position and return the trade record.

        Args:
            position: Position to close
            exit_date: Exit date
            exit_price: Exit price
            exit_reason: Reason for exit
            exit_bar: Bar index of exit

        Returns:
            Trade record
        """
        # Calculate P&L (including both entry and exit commissions)
        if position.direction == 'long':
            pnl = (exit_price - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - exit_price) * position.size

        # Subtract both entry and exit commissions
        entry_commission = position.entry_price * position.size * self.config.commission
        exit_commission = exit_price * position.size * self.config.commission
        pnl -= (entry_commission + exit_commission)

        pnl_percent = (pnl / (position.entry_price * position.size)) * 100

        bars_held = exit_bar - position.entry_bar

        trade = Trade(
            ticker=position.ticker,
            entry_date=position.entry_date,
            entry_price=position.entry_price,
            exit_date=exit_date,
            exit_price=exit_price,
            size=position.size,
            direction=position.direction,
            pnl=pnl,
            pnl_percent=pnl_percent,
            exit_reason=exit_reason,
            bars_held=bars_held
        )

        return trade

    def _calculate_ticker_performance(
        self,
        ticker: str,
        trades: List[Trade]
    ) -> TickerPerformance:
        """
        Calculate performance metrics for a ticker.

        Args:
            ticker: Ticker symbol
            trades: List of trades

        Returns:
            TickerPerformance metrics
        """
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        losing_trades = sum(1 for t in trades if t.pnl <= 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_pnl = sum(t.pnl for t in trades)
        total_pnl_percent = sum(t.pnl_percent for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

        wins = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl <= 0]

        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Calculate max drawdown
        equity = self.config.initial_capital
        peak = equity
        max_dd = 0

        for trade in trades:
            equity += trade.pnl
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)

        # Sample trades (last 10)
        sample_trades = trades[-10:] if len(trades) > 10 else trades

        return TickerPerformance(
            ticker=ticker,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            avg_pnl_per_trade=avg_pnl,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            trades=sample_trades
        )

    def _aggregate_results(
        self,
        ticker_results: List[TickerPerformance],
        all_trades_dict: Dict[str, List[Trade]]
    ) -> BacktestResult:
        """
        Aggregate ticker results into portfolio-level metrics.

        Args:
            ticker_results: List of per-ticker performance

        Returns:
            Complete BacktestResult
        """
        if not ticker_results:
            return BacktestResult(
                success=False,
                message="No ticker results to aggregate"
            )

        # Aggregate ALL trades (not just samples)
        all_trades = []
        for ticker, trades in all_trades_dict.items():
            all_trades.extend(trades)

        # Sort by entry date
        all_trades.sort(key=lambda t: t.entry_date)

        # Calculate portfolio equity curve
        equity = self.config.initial_capital
        equity_curve = [EquityPoint(date=self.config.start_date, equity=equity)]

        # Aggregate by date
        trade_dates = {}
        for trade in all_trades:
            if trade.exit_date:
                if trade.exit_date not in trade_dates:
                    trade_dates[trade.exit_date] = []
                trade_dates[trade.exit_date].append(trade)

        for date in sorted(trade_dates.keys()):
            daily_pnl = sum(t.pnl for t in trade_dates[date])
            equity += daily_pnl
            equity_curve.append(EquityPoint(date=date, equity=equity))

        # Calculate returns
        total_return = equity - self.config.initial_capital
        total_return_percent = (total_return / self.config.initial_capital) * 100

        # Calculate CAGR
        try:
            start = datetime.strptime(self.config.start_date, '%Y-%m-%d')
            end = datetime.strptime(self.config.end_date, '%Y-%m-%d')
            years = (end - start).days / 365.25
            cagr = ((equity / self.config.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        except:
            cagr = 0

        # Calculate metrics
        total_trades = len(all_trades)
        winning_trades = sum(1 for t in all_trades if t.pnl > 0)
        losing_trades = sum(1 for t in all_trades if t.pnl <= 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        wins = [t.pnl for t in all_trades if t.pnl > 0]
        losses = [t.pnl for t in all_trades if t.pnl <= 0]

        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        avg_trade_pnl = sum(t.pnl for t in all_trades) / total_trades if total_trades > 0 else 0

        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Calculate drawdown
        peak = self.config.initial_capital
        max_dd = 0
        max_dd_percent = 0

        for point in equity_curve:
            if point.equity > peak:
                peak = point.equity
            dd = peak - point.equity
            dd_percent = (dd / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)
            max_dd_percent = max(max_dd_percent, dd_percent)

        # Calculate volatility and Sharpe
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i].equity - equity_curve[i-1].equity) / equity_curve[i-1].equity
            returns.append(ret)
            equity_curve[i].daily_return = ret * 100

        volatility = np.std(returns) * np.sqrt(252) * 100 if returns else 0
        avg_return = np.mean(returns) * 252 if returns else 0
        sharpe = (avg_return * 100) / volatility if volatility > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = [r for r in returns if r < 0]
        downside_std = np.std(downside_returns) * np.sqrt(252) if downside_returns else volatility
        sortino = (avg_return * 100) / downside_std if downside_std > 0 else 0

        # Consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        current_wins = 0
        current_losses = 0

        for trade in all_trades:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                consecutive_wins = max(consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                consecutive_losses = max(consecutive_losses, current_losses)

        # Best/worst trades
        best_trade = max((t.pnl for t in all_trades), default=0)
        worst_trade = min((t.pnl for t in all_trades), default=0)

        # Avg bars held
        avg_bars_held = sum(t.bars_held for t in all_trades if t.bars_held) / total_trades if total_trades > 0 else 0

        metrics = BacktestMetrics(
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            initial_capital=self.config.initial_capital,
            final_equity=equity,
            total_return=total_return,
            total_return_percent=total_return_percent,
            cagr=cagr,
            volatility=volatility,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            max_drawdown_percent=max_dd_percent,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_trade_pnl=avg_trade_pnl,
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_bars_held=avg_bars_held,
            best_trade=best_trade,
            worst_trade=worst_trade,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses
        )

        # Sort ticker results by total P&L
        ticker_results.sort(key=lambda x: x.total_pnl, reverse=True)

        top_performers = ticker_results[:10]
        worst_performers = ticker_results[-10:][::-1]

        # Sample trades
        sample_trades = all_trades[-20:] if len(all_trades) > 20 else all_trades

        return BacktestResult(
            success=True,
            message="Backtest completed successfully",
            metrics=metrics,
            equity_curve=equity_curve,
            ticker_performance=ticker_results,
            top_performers=top_performers,
            worst_performers=worst_performers,
            sample_trades=sample_trades
        )
