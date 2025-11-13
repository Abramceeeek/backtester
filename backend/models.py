"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class BacktestConfig(BaseModel):
    """Configuration for a backtest run."""

    strategy_code: str = Field(..., description="Python code defining the strategy function")
    universe: str = Field(default="sp500", description="Stock universe (sp500 or custom)")
    custom_tickers: Optional[List[str]] = Field(default=None, description="Custom ticker list if universe='custom'")
    limit_tickers: Optional[int] = Field(default=None, description="Limit number of tickers for quick testing (e.g., 20)")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    initial_capital: float = Field(default=100000.0, description="Starting capital in USD")
    position_size: float = Field(default=1.0, description="Position size as fraction of available capital (0-1)")
    max_positions: int = Field(default=10, description="Maximum number of concurrent positions")
    commission: float = Field(default=0.001, description="Commission as fraction of trade value")
    slippage: float = Field(default=0.0005, description="Slippage as fraction of price")
    interval: str = Field(default="1d", description="Data interval (1d, 1h, etc)")

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @validator('initial_capital')
    def validate_capital(cls, v):
        if v <= 0:
            raise ValueError('Initial capital must be positive')
        return v

    @validator('position_size')
    def validate_position_size(cls, v):
        if not 0 < v <= 1:
            raise ValueError('Position size must be between 0 and 1')
        return v

    @validator('max_positions')
    def validate_max_positions(cls, v):
        if v < 1:
            raise ValueError('Max positions must be at least 1')
        return v

    class Config:
        schema_extra = {
            "example": {
                "strategy_code": "def strategy(data, state):\n    return {'signal': 'buy'}",
                "universe": "sp500",
                "start_date": "2014-01-01",
                "end_date": "2024-01-01",
                "initial_capital": 100000.0,
                "position_size": 0.1,
                "max_positions": 10,
                "commission": 0.001,
                "slippage": 0.0005
            }
        }


class Trade(BaseModel):
    """Individual trade record."""

    ticker: str
    entry_date: str
    entry_price: float
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    size: float
    direction: str  # 'long' or 'short'
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    exit_reason: Optional[str] = None  # 'signal', 'stop_loss', 'take_profit', 'end_of_backtest'
    bars_held: Optional[int] = None


class TickerPerformance(BaseModel):
    """Performance metrics for a single ticker."""

    ticker: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percent: float
    avg_pnl_per_trade: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    trades: List[Trade] = Field(default_factory=list, description="Sample trades (max 10)")


class EquityPoint(BaseModel):
    """Point on the equity curve."""

    date: str
    equity: float
    daily_return: Optional[float] = None


class BacktestMetrics(BaseModel):
    """Aggregated backtest performance metrics."""

    start_date: str
    end_date: str
    initial_capital: float
    final_equity: float
    total_return: float
    total_return_percent: float
    cagr: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_trade_pnl: float
    avg_win: float
    avg_loss: float
    avg_bars_held: float
    best_trade: float
    worst_trade: float
    consecutive_wins: int
    consecutive_losses: int


class BacktestResult(BaseModel):
    """Complete backtest result."""

    success: bool
    message: Optional[str] = None
    config: Optional[BacktestConfig] = None
    metrics: Optional[BacktestMetrics] = None
    equity_curve: List[EquityPoint] = Field(default_factory=list)
    ticker_performance: List[TickerPerformance] = Field(default_factory=list)
    top_performers: List[TickerPerformance] = Field(default_factory=list, description="Top 10 best performing tickers")
    worst_performers: List[TickerPerformance] = Field(default_factory=list, description="Top 10 worst performing tickers")
    sample_trades: List[Trade] = Field(default_factory=list, description="Sample of recent trades")
    execution_time: Optional[float] = None


class UniverseResponse(BaseModel):
    """Response for universe ticker list."""

    universe: str
    tickers: List[str]
    count: int
    last_updated: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: str
    detail: Optional[str] = None
