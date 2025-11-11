# Quick Start Guide

Get the trading strategy backtester running in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Internet connection (for downloading stock data)

## Step 1: Start the Backend API

```bash
# Navigate to backend directory
cd trading-backtester/backend

# Install Python dependencies
pip install -r requirements.txt

# Start the API server
python api.py
```

The API will start on `http://localhost:8000`

You should see output like:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Start the Frontend

Open a new terminal window:

```bash
# Navigate to frontend directory
cd trading-backtester/frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

## Step 3: Run Your First Backtest

1. Open your browser to `http://localhost:3000`
2. You'll see the backtest form with a pre-loaded SMA crossover strategy
3. Adjust the date range if desired (default is 10 years)
4. Click "Run Backtest"
5. Wait 2-3 minutes while the system:
   - Fetches S&P 500 ticker list
   - Downloads historical data
   - Runs your strategy on all tickers
6. View results with metrics, equity curve, and top performers

## Testing the API Directly

You can also test the API using curl or Python:

### Using curl:

```bash
curl -X POST http://localhost:8000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_code": "def strategy(data, state):\n    if len(data) < 50:\n        return {\"signal\": None}\n    import pandas as pd\n    close = data[\"close\"].values\n    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]\n    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]\n    if sma_20 > sma_50:\n        return {\"signal\": \"buy\", \"stop_loss\": 0.95, \"take_profit\": 1.10}\n    return {\"signal\": None}",
    "start_date": "2020-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000
  }'
```

### Using Python:

```python
import requests
import json

config = {
    "strategy_code": """
def strategy(data, state):
    if len(data) < 50:
        return {'signal': None}

    import pandas as pd
    close = data['close'].values
    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    if sma_20 > sma_50:
        return {'signal': 'buy', 'stop_loss': 0.95, 'take_profit': 1.10}

    return {'signal': None}
""",
    "start_date": "2020-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000,
    "position_size": 0.1
}

response = requests.post('http://localhost:8000/api/backtest', json=config)
result = response.json()

if result['success']:
    metrics = result['metrics']
    print(f"Total Return: {metrics['total_return_percent']:.2f}%")
    print(f"CAGR: {metrics['cagr']:.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown_percent']:.2f}%")
    print(f"Win Rate: {metrics['win_rate']*100:.1f}%")
    print(f"Total Trades: {metrics['total_trades']}")
else:
    print(f"Error: {result['message']}")
```

## Example Strategies

Check the `examples/` directory for ready-to-use strategies:

1. **SMA Crossover** (`strategy_sma_crossover.py`)
   - Simple moving average crossover
   - 20/50 period MAs
   - 2% stop loss, 10% take profit

2. **RSI Mean Reversion** (`strategy_rsi.py`)
   - Buy on RSI < 30 (oversold)
   - Sell on RSI > 70 (overbought)
   - 3% stop loss, 8% take profit

3. **Breakout Strategy** (`strategy_breakout.py`)
   - Buy on 20-day high breakout
   - ATR-based stop loss
   - 2:1 reward-risk ratio

## Common Issues

### Port Already in Use

If port 8000 or 3000 is already in use:

**Backend:**
```python
# Edit api.py, change the port:
uvicorn.run("api:app", host="0.0.0.0", port=8001)
```

**Frontend:**
```bash
# Run on different port:
npm run dev -- -p 3001
```

### Module Not Found

Make sure you installed dependencies:
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Data Loading Fails

If yfinance fails to download data:
1. Check your internet connection
2. Try again (rate limits may apply)
3. The system uses a fallback list if Wikipedia fails

### CORS Errors

If you see CORS errors in the browser:
1. Make sure the backend is running
2. Check that the frontend is calling `http://localhost:8000`
3. The API already has CORS enabled for all origins in development

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [Strategy API](#writing-strategies) section
- Check out the [examples/](examples/) directory
- Customize the frontend styling (edit components in `frontend/components/`)
- Add authentication for production use
- Deploy to a cloud provider

## API Endpoints Reference

- `POST /api/backtest` - Run a backtest
- `GET /api/universe/sp500` - Get S&P 500 tickers
- `GET /api/strategy/template` - Get strategy template
- `DELETE /api/cache/clear` - Clear data cache
- `GET /health` - Health check

## Support

For issues:
- Check the logs in your terminal
- Review the [README.md](README.md) troubleshooting section
- Ensure all dependencies are installed
- Verify Python 3.8+ and Node.js 16+ are installed

Happy backtesting!
