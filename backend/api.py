"""FastAPI application for trading strategy backtester."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging
from typing import Dict, AsyncGenerator
import uuid
from datetime import datetime
import json
import asyncio

from models import (
    BacktestConfig, BacktestResult, UniverseResponse,
    ErrorResponse
)
from engine import BacktestEngine
from data_loader import get_loader
from sandbox import get_sandbox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Trading Strategy Backtester API",
    description="API for backtesting trading strategies on S&P 500 stocks",
    version="1.0.0"
)

import os
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backtest_jobs: Dict[str, BacktestResult] = {}


@app.get("/")
async def root():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/universe/sp500", response_model=UniverseResponse)
async def get_sp500_universe(force_refresh: bool = False):
    try:
        loader = get_loader()
        tickers = loader.get_sp500_tickers(force_refresh=force_refresh)

        return UniverseResponse(
            universe="sp500",
            tickers=tickers,
            count=len(tickers),
            last_updated=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get S&P 500 universe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch S&P 500 tickers: {str(e)}"
        )


@app.get("/api/strategy/template")
async def get_strategy_template():
    sandbox = get_sandbox()
    template = sandbox.get_strategy_template()

    return {
        "template": template,
        "documentation": {
            "function_name": "strategy",
            "parameters": {
                "data": "pandas DataFrame with columns ['open', 'high', 'low', 'close', 'volume']",
                "state": "dict for persisting variables between calls"
            },
            "returns": {
                "signal": "'buy', 'sell', 'flat', 'hold', or None",
                "size": "optional, position size multiplier (default: 1.0)",
                "stop_loss": "optional, stop loss price or multiplier (e.g., 0.98 = 2% below entry)",
                "take_profit": "optional, take profit price or multiplier (e.g., 1.05 = 5% above entry)"
            },
            "example_signals": [
                {"signal": "buy", "stop_loss": 0.98, "take_profit": 1.05},
                {"signal": "sell"},
                {"signal": None}
            ]
        }
    }


@app.get("/api/strategy/library")
async def get_strategy_library():
    import os

    # Path to examples directory
    examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')

    strategies = []

    # SMA Crossover Strategy
    strategies.append({
        "id": "sma_crossover",
        "name": "SMA Crossover",
        "category": "Trend Following",
        "difficulty": "Beginner",
        "description": "Buy when fast MA crosses above slow MA, sell when it crosses below",
        "code": """def strategy(data, state):
    \"\"\"
    Simple moving average crossover strategy.
    Buy when fast MA crosses above slow MA.
    Sell when fast MA crosses below slow MA.
    \"\"\"
    close = data['close'].values

    if len(close) < 50:
        return {'signal': None}

    # Calculate moving averages
    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    # Initialize state
    if 'prev_sma_20' not in state:
        state['prev_sma_20'] = sma_20
        state['prev_sma_50'] = sma_50
        return {'signal': None}

    prev_sma_20 = state['prev_sma_20']
    prev_sma_50 = state['prev_sma_50']

    state['prev_sma_20'] = sma_20
    state['prev_sma_50'] = sma_50

    # Check for crossover
    if prev_sma_20 <= prev_sma_50 and sma_20 > sma_50:
        return {
            'signal': 'buy',
            'stop_loss': 0.98,
            'take_profit': 1.10
        }
    elif prev_sma_20 >= prev_sma_50 and sma_20 < sma_50:
        return {'signal': 'sell'}

    return {'signal': None}""",
        "parameters": {
            "fast_period": 20,
            "slow_period": 50,
            "stop_loss": "2%",
            "take_profit": "10%"
        }
    })

    # RSI Mean Reversion Strategy
    strategies.append({
        "id": "rsi_mean_reversion",
        "name": "RSI Mean Reversion",
        "category": "Mean Reversion",
        "difficulty": "Beginner",
        "description": "Buy when RSI < 40 (oversold), sell when RSI > 60 (overbought)",
        "code": """def strategy(data, state):
    \"\"\"
    RSI mean reversion strategy.
    Buy when RSI < 40, sell when RSI > 60.
    \"\"\"
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

    has_position = state.get('has_position', False)

    if not has_position and current_rsi < 40:
        state['has_position'] = True
        return {
            'signal': 'buy',
            'stop_loss': 0.97,
            'take_profit': 1.08
        }
    elif has_position and current_rsi > 60:
        state['has_position'] = False
        return {'signal': 'sell'}

    return {'signal': None}""",
        "parameters": {
            "rsi_period": 14,
            "oversold_threshold": 40,
            "overbought_threshold": 60,
            "stop_loss": "3%",
            "take_profit": "8%"
        }
    })

    # Breakout Strategy
    strategies.append({
        "id": "breakout",
        "name": "Breakout Strategy",
        "category": "Momentum",
        "difficulty": "Intermediate",
        "description": "Buy when price breaks above 20-day high with ATR-based stops",
        "code": """def strategy(data, state):
    \"\"\"
    Breakout strategy with ATR-based stops.
    Buy when price breaks above 20-day high.
    \"\"\"
    if len(data) < 25:
        return {'signal': None}

    close = data['close'].values
    high = data['high'].values
    low = data['low'].values
    current_close = close[-1]

    # Calculate 20-day high/low
    lookback = 20
    highest_high = np.max(high[-lookback-1:-1])
    lowest_low = np.min(low[-lookback-1:-1])

    # Calculate ATR
    atr_period = 14
    high_series = pd.Series(high)
    low_series = pd.Series(low)
    close_series = pd.Series(close)

    tr1 = high_series - low_series
    tr2 = abs(high_series - close_series.shift(1))
    tr3 = abs(low_series - close_series.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=atr_period).mean().iloc[-1]

    has_position = state.get('has_position', False)

    if not has_position and current_close > highest_high:
        state['has_position'] = True
        stop_loss_distance = 2 * atr
        stop_loss_price = current_close - stop_loss_distance
        take_profit_price = current_close + (2 * stop_loss_distance)

        return {
            'signal': 'buy',
            'stop_loss': stop_loss_price / current_close,
            'take_profit': take_profit_price / current_close
        }
    elif has_position and current_close < lowest_low:
        state['has_position'] = False
        return {'signal': 'sell'}

    return {'signal': None}""",
        "parameters": {
            "lookback_period": 20,
            "atr_period": 14,
            "atr_multiplier": 2,
            "reward_risk_ratio": "2:1"
        }
    })

    # Bollinger Bands Strategy
    strategies.append({
        "id": "bollinger_bands",
        "name": "Bollinger Bands",
        "category": "Volatility",
        "difficulty": "Beginner",
        "description": "Buy when price touches lower band, sell when it touches upper band",
        "code": """def strategy(data, state):
    \"\"\"
    Bollinger Bands mean reversion strategy.
    Buy at lower band, sell at upper band.
    \"\"\"
    close = data['close'].values

    if len(close) < 25:
        return {'signal': None}

    # Calculate Bollinger Bands
    period = 20
    num_std = 2

    sma = pd.Series(close).rolling(period).mean()
    std = pd.Series(close).rolling(period).std()

    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)

    current_close = close[-1]
    current_upper = upper_band.iloc[-1]
    current_lower = lower_band.iloc[-1]
    current_sma = sma.iloc[-1]

    has_position = state.get('has_position', False)

    if not has_position and current_close <= current_lower:
        state['has_position'] = True
        return {
            'signal': 'buy',
            'stop_loss': 0.97,
            'take_profit': current_sma / current_close
        }
    elif has_position and current_close >= current_upper:
        state['has_position'] = False
        return {'signal': 'sell'}

    return {'signal': None}""",
        "parameters": {
            "period": 20,
            "num_std_dev": 2,
            "stop_loss": "3%"
        }
    })

    # MACD Strategy
    strategies.append({
        "id": "macd",
        "name": "MACD Crossover",
        "category": "Momentum",
        "difficulty": "Intermediate",
        "description": "Buy when MACD crosses above signal line, sell on opposite cross",
        "code": """def strategy(data, state):
    \"\"\"
    MACD crossover strategy.
    Buy when MACD crosses above signal line.
    \"\"\"
    close = data['close'].values

    if len(close) < 35:
        return {'signal': None}

    # Calculate MACD
    close_series = pd.Series(close)
    ema_12 = close_series.ewm(span=12, adjust=False).mean()
    ema_26 = close_series.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal_line = macd.ewm(span=9, adjust=False).mean()

    current_macd = macd.iloc[-1]
    current_signal = signal_line.iloc[-1]

    if 'prev_macd' not in state:
        state['prev_macd'] = current_macd
        state['prev_signal'] = current_signal
        return {'signal': None}

    prev_macd = state['prev_macd']
    prev_signal = state['prev_signal']

    state['prev_macd'] = current_macd
    state['prev_signal'] = current_signal

    # Check for crossover
    if prev_macd <= prev_signal and current_macd > current_signal:
        return {
            'signal': 'buy',
            'stop_loss': 0.97,
            'take_profit': 1.10
        }
    elif prev_macd >= prev_signal and current_macd < current_signal:
        return {'signal': 'sell'}

    return {'signal': None}""",
        "parameters": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9,
            "stop_loss": "3%",
            "take_profit": "10%"
        }
    })

    return {
        "strategies": strategies,
        "count": len(strategies),
        "categories": list(set(s["category"] for s in strategies))
    }


@app.post("/api/backtest", response_model=BacktestResult)
async def run_backtest(config: BacktestConfig):
    job_id = str(uuid.uuid4())
    logger.info(f"Starting backtest job {job_id}")

    try:
        sandbox = get_sandbox()
        try:
            sandbox.validate(config.strategy_code)
        except Exception as e:
            logger.error(f"Strategy validation failed: {e}")
            return BacktestResult(
                success=False,
                message=f"Strategy validation failed: {str(e)}"
            )

        engine = BacktestEngine(config)
        result = engine.run_backtest()
        backtest_jobs[job_id] = result

        logger.info(f"Backtest job {job_id} completed: {result.success}")

        return result

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        return BacktestResult(
            success=False,
            message=f"Backtest failed: {str(e)}"
        )


@app.post("/api/backtest/stream")
async def run_backtest_stream(config: BacktestConfig):
    async def generate_backtest_stream() -> AsyncGenerator[str, None]:
        job_id = str(uuid.uuid4())
        logger.info(f"Starting streaming backtest job {job_id}")

        try:
            sandbox = get_sandbox()
            try:
                sandbox.validate(config.strategy_code)
            except Exception as e:
                error_msg = json.dumps({
                    "type": "error",
                    "message": f"Strategy validation failed: {str(e)}"
                })
                yield f"data: {error_msg}\n\n"
                return

            loader = get_loader()
            if config.universe == 'sp500':
                tickers = loader.get_sp500_tickers()
                if hasattr(config, 'limit_tickers') and config.limit_tickers and config.limit_tickers > 0:
                    tickers = tickers[:config.limit_tickers]
                    logger.info(f"Limited to first {len(tickers)} tickers for testing")
            elif config.custom_tickers:
                tickers = config.custom_tickers
            else:
                error_msg = json.dumps({
                    "type": "error",
                    "message": "Must specify universe='sp500' or provide custom_tickers"
                })
                yield f"data: {error_msg}\n\n"
                return

            init_msg = json.dumps({
                "type": "init",
                "total_tickers": len(tickers),
                "job_id": job_id
            })
            yield f"data: {init_msg}\n\n"

            loading_msg = json.dumps({
                "type": "loading",
                "message": f"Loading historical data for {len(tickers)} stocks... This may take 30-60 seconds.",
                "stage": "data_loading"
            })
            yield f"data: {loading_msg}\n\n"
            await asyncio.sleep(0.01)

            logger.info(f"Loading data for {len(tickers)} tickers...")
            import concurrent.futures
            loop = asyncio.get_event_loop()
            data_dict = await loop.run_in_executor(
                None,
                loader.get_bulk_data,
                tickers,
                config.start_date,
                config.end_date,
                config.interval
            )

            data_loaded_msg = json.dumps({
                "type": "loading",
                "message": f"Data loaded for {len(data_dict)} stocks. Starting backtest...",
                "stage": "backtest_starting"
            })
            yield f"data: {data_loaded_msg}\n\n"
            await asyncio.sleep(0.01)

            if not data_dict:
                error_msg = json.dumps({
                    "type": "error",
                    "message": "Failed to load any ticker data"
                })
                yield f"data: {error_msg}\n\n"
                return

            from engine_streaming import StreamingBacktestEngine
            engine = StreamingBacktestEngine(config)

            backtest_start_msg = json.dumps({
                "type": "loading",
                "message": f"Starting backtest on {len(data_dict)} stocks. This may take 2-5 minutes...",
                "stage": "backtest_running"
            })
            yield f"data: {backtest_start_msg}\n\n"
            await asyncio.sleep(0.01)

            completed_count = 0
            all_ticker_results = []
            all_trades_dict = {}  # Collect all trades

            async for ticker_result in engine.run_backtest_streaming(data_dict):
                # Check if this is the final message with all trades
                if ticker_result.get("_final"):
                    all_trades_dict = ticker_result.get("_all_trades", {})
                    continue
                
                completed_count += 1
                all_ticker_results.append(ticker_result)

                progress_msg = json.dumps({
                    "type": "progress",
                    "ticker": ticker_result.get("ticker"),
                    "completed": completed_count,
                    "total": len(data_dict),
                    "percentage": round((completed_count / len(data_dict)) * 100, 1),
                    "ticker_result": ticker_result
                })
                yield f"data: {progress_msg}\n\n"
                await asyncio.sleep(0.01)

            # Send aggregation start message
            aggregating_msg = json.dumps({
                "type": "loading",
                "message": f"Aggregating results from {len(all_ticker_results)} stocks...",
                "stage": "aggregating"
            })
            yield f"data: {aggregating_msg}\n\n"
            await asyncio.sleep(0.01)
            
            try:
                from engine import BacktestEngine
                regular_engine = BacktestEngine(config)

                from models import TickerPerformance, Trade
                ticker_perfs = []
                for tr in all_ticker_results:
                    if tr.get("success"):
                        try:
                            ticker_perfs.append(TickerPerformance(**tr))
                        except Exception as e:
                            logger.warning(f"Failed to create TickerPerformance for {tr.get('ticker')}: {e}")
                            continue

                if not ticker_perfs:
                    error_msg = json.dumps({
                        "type": "error",
                        "message": "No successful ticker results to aggregate"
                    })
                    yield f"data: {error_msg}\n\n"
                    return

                # Convert all_trades_dict to List[Trade] format if needed
                all_trades_list_dict = {}
                for ticker, trades in all_trades_dict.items():
                    if trades and len(trades) > 0:
                        try:
                            if isinstance(trades[0], dict):
                                # Dict format - convert to Trade objects
                                all_trades_list_dict[ticker] = [Trade(**t) for t in trades]
                            else:
                                # Already Trade objects
                                all_trades_list_dict[ticker] = trades
                        except Exception as e:
                            logger.warning(f"Failed to convert trades for {ticker}: {e}")
                            all_trades_list_dict[ticker] = []
                    else:
                        all_trades_list_dict[ticker] = []

                logger.info(f"Aggregating {len(ticker_perfs)} ticker results with {sum(len(t) for t in all_trades_list_dict.values())} total trades")
                final_result = regular_engine._aggregate_results(ticker_perfs, all_trades_list_dict)
                final_result.config = config

                final_msg = json.dumps({
                    "type": "complete",
                    "result": final_result.dict()
                })
                yield f"data: {final_msg}\n\n"
                logger.info(f"Streaming backtest job {job_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Failed to aggregate results: {e}", exc_info=True)
                error_msg = json.dumps({
                    "type": "error",
                    "message": f"Failed to aggregate results: {str(e)}"
                })
                yield f"data: {error_msg}\n\n"

        except Exception as e:
            logger.error(f"Streaming backtest failed: {e}", exc_info=True)
            error_msg = json.dumps({
                "type": "error",
                "message": f"Backtest failed: {str(e)}"
            })
            yield f"data: {error_msg}\n\n"

    return StreamingResponse(
        generate_backtest_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/backtest/{job_id}", response_model=BacktestResult)
async def get_backtest_result(job_id: str):
    if job_id not in backtest_jobs:
        raise HTTPException(status_code=404, detail="Backtest job not found")

    return backtest_jobs[job_id]


@app.post("/api/backtest/validate")
async def validate_strategy(strategy_code: str):
    try:
        sandbox = get_sandbox()
        sandbox.validate(strategy_code)

        return {
            "valid": True,
            "message": "Strategy code is valid"
        }

    except Exception as e:
        return {
            "valid": False,
            "message": str(e)
        }


@app.delete("/api/cache/clear")
async def clear_cache():
    try:
        loader = get_loader()
        loader.clear_cache()

        global backtest_jobs
        backtest_jobs = {}

        return {
            "success": True,
            "message": "Cache cleared successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
