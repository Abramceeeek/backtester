# Trading Strategy Backtester

A comprehensive web-based platform for backtesting trading strategies on S&P 500 stocks with 10+ years of historical data.

## Features

- **Custom Strategy Execution**: Write and test your own trading strategies in Python
- **S&P 500 Universe**: Backtest across all current S&P 500 stocks
- **10+ Years of Data**: Access historical OHLCV data via yfinance
- **Comprehensive Metrics**:
  - Total Return, CAGR, Sharpe Ratio, Sortino Ratio
  - Max Drawdown, Win Rate, Profit Factor
  - Trade-level analysis with P&L tracking
- **Risk Management**: Built-in support for stop-loss and take-profit orders
- **Interactive Frontend**: React-based UI with real-time results visualization
- **Secure Sandbox**: User strategies run in a sandboxed environment

## Architecture

### Backend (Python + FastAPI)

```
backend/
├── api.py              # FastAPI endpoints
├── engine.py           # Core backtest logic
├── data_loader.py      # Historical data fetching and caching
├── sandbox.py          # Secure strategy execution
├── models.py           # Pydantic schemas
└── requirements.txt    # Python dependencies
```

### Frontend (React/Next.js)

```
frontend/
├── pages/
│   └── backtest.js           # Main backtest page
└── components/
    ├── BacktestForm.js       # Strategy input and configuration
    ├── ResultsDisplay.js     # Metrics and performance display
    └── EquityChart.js        # Equity curve visualization
```

### Example Strategies

```
examples/
├── strategy_sma_crossover.py   # Moving average crossover
├── strategy_rsi.py             # RSI mean reversion
└── strategy_breakout.py        # Breakout strategy
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd trading-backtester/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API server:
```bash
python api.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd trading-backtester/frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Documentation

### Endpoints

#### `POST /api/backtest`
Run a trading strategy backtest.

**Request Body:**
```json
{
  "strategy_code": "def strategy(data, state): ...",
  "universe": "sp500",
  "start_date": "2014-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000.0,
  "position_size": 0.1,
  "max_positions": 10,
  "commission": 0.001,
  "slippage": 0.0005
}
```

**Response:**
```json
{
  "success": true,
  "metrics": {
    "total_return": 50000.0,
    "total_return_percent": 50.0,
    "cagr": 4.2,
    "sharpe_ratio": 1.5,
    "max_drawdown_percent": -15.2,
    "win_rate": 0.58,
    ...
  },
  "equity_curve": [...],
  "top_performers": [...],
  "sample_trades": [...]
}
```

#### `GET /api/universe/sp500`
Get the list of S&P 500 tickers.

**Response:**
```json
{
  "universe": "sp500",
  "tickers": ["AAPL", "MSFT", "GOOGL", ...],
  "count": 503
}
```

#### `GET /api/strategy/template`
Get a strategy code template.

**Response:**
```json
{
  "template": "def strategy(data, state): ...",
  "documentation": {...}
}
```

## Strategy API

### Writing Strategies

Strategies must define a `strategy` function with the following signature:

```python
def strategy(data, state):
    """
    Args:
        data: pandas DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
              Index is DatetimeIndex
        state: dict for persisting variables between calls

    Returns:
        dict with:
            - 'signal': 'buy', 'sell', 'flat', or None
            - 'size': optional, position size (default: based on config)
            - 'stop_loss': optional, as multiplier (0.98 = 2% below) or absolute price
            - 'take_profit': optional, as multiplier (1.05 = 5% above) or absolute price
    """
    # Your strategy logic here
    return {'signal': 'buy', 'stop_loss': 0.98, 'take_profit': 1.05}
```

### Allowed Modules

Strategies can use:
- `pandas` / `pd` (pre-loaded, no import needed)
- `numpy` / `np` (pre-loaded, no import needed)
- Standard Python math and datetime functions

**Important:** Do NOT use `import` statements in your strategy code. The modules `pd`, `pandas`, `np`, and `numpy` are already available in the execution environment. Using import statements will cause validation errors.

### Example Strategy

```python
def strategy(data, state):
    """Simple SMA crossover (no imports needed - pd is pre-loaded)"""
    close = data['close'].values

    if len(close) < 50:
        return {'signal': None}

    # Use pd directly - it's already available
    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    # Initialize state
    if 'prev_sma_20' not in state:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': None}

    # Check for crossover
    if state['prev_sma_20'] <= state['prev_sma_50'] and sma_20 > sma_50:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': 'buy', 'stop_loss': 0.98, 'take_profit': 1.10}

    if state['prev_sma_20'] >= state['prev_sma_50'] and sma_20 < sma_50:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': 'sell'}

    state['prev_sma_20'] = sma_20
    state['prev_sma_50'] = sma_50
    return {'signal': None}
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy_code` | string | - | Python code defining the strategy function |
| `universe` | string | "sp500" | Stock universe to backtest |
| `start_date` | string | "2014-01-01" | Backtest start date (YYYY-MM-DD) |
| `end_date` | string | "2024-01-01" | Backtest end date (YYYY-MM-DD) |
| `initial_capital` | float | 100000.0 | Starting capital in USD |
| `position_size` | float | 0.1 | Position size as fraction of capital (0-1) |
| `max_positions` | int | 10 | Maximum concurrent positions |
| `commission` | float | 0.001 | Commission as fraction of trade value |
| `slippage` | float | 0.0005 | Slippage as fraction of price |
| `interval` | string | "1d" | Data interval (1d for daily) |

## Performance Metrics

The backtester calculates comprehensive performance metrics:

- **Returns**: Total Return, CAGR (Compound Annual Growth Rate)
- **Risk-Adjusted**: Sharpe Ratio, Sortino Ratio, Volatility
- **Drawdown**: Maximum Drawdown (absolute and percentage)
- **Trade Statistics**: Win Rate, Profit Factor, Average Win/Loss
- **Trade Analysis**: Best/Worst Trades, Consecutive Wins/Losses
- **Position Metrics**: Average Bars Held

## Data Caching

The system caches:
- S&P 500 ticker list (30 days)
- Historical OHLCV data (7 days)

Clear cache via:
```bash
DELETE /api/cache/clear
```

## Security Features

- **AST-based code validation**: Blocks dangerous operations
- **Restricted globals**: Only whitelisted modules available
- **No filesystem/network access**: Strategies cannot access external resources
- **Execution timeout**: 5 seconds per strategy call
- **Memory limits**: 500MB max memory usage

## Production Considerations

1. **Scaling**: Use multiprocessing/async for parallel ticker backtests
2. **Rate Limiting**: Implement rate limits on API endpoints
3. **Authentication**: Add user authentication and authorization
4. **Data Source**: Consider paid data providers for production
5. **Worker Queue**: Use Celery/RQ for long-running backtests
6. **Database**: Store results in PostgreSQL/MongoDB
7. **Frontend**: Configure CORS for specific domains
8. **Monitoring**: Add logging and error tracking (Sentry, etc.)

## Example Usage

### Python (Direct API)

```python
import requests

config = {
    "strategy_code": """
def strategy(data, state):
    if len(data) < 50:
        return {'signal': None}
    # Your strategy logic
    return {'signal': 'buy', 'stop_loss': 0.95}
    """,
    "start_date": "2014-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000
}

response = requests.post('http://localhost:8000/api/backtest', json=config)
result = response.json()

if result['success']:
    print(f"Total Return: {result['metrics']['total_return_percent']:.2f}%")
    print(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
```

### JavaScript (Frontend)

```javascript
const runBacktest = async (config) => {
  const response = await fetch('http://localhost:8000/api/backtest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });

  const result = await response.json();

  if (result.success) {
    console.log('Backtest completed:', result.metrics);
  }
};
```

## Troubleshooting

### Common Issues

1. **"No data returned for ticker"**: Ticker may be delisted or not available in yfinance
2. **"Strategy validation failed"**: Check for forbidden operations (imports, file access, etc.)
3. **"Insufficient data"**: Increase date range or check data availability
4. **Slow backtests**: Enable parallel processing or reduce universe size

### Debug Mode

Enable debug logging in `api.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - feel free to use for personal or commercial projects.

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/api/strategy/template` endpoint
- Examples: Check `examples/` directory

## Roadmap

- [ ] Support for intraday data (1h, 15m intervals)
- [ ] Portfolio-level backtesting (simultaneous positions)
- [ ] Advanced order types (trailing stops, limit orders)
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Machine learning integration
- [ ] Real-time paper trading
- [ ] Custom universe support (upload ticker lists)
- [ ] Export results to CSV/PDF reports
