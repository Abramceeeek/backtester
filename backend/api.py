"""
FastAPI application for the trading strategy backtester.
Exposes endpoints for running backtests and retrieving universe data.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict
import uuid
from datetime import datetime

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

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store running/completed backtests
backtest_jobs: Dict[str, BacktestResult] = {}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Trading Strategy Backtester API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/backtest": "Run a backtest",
            "GET /api/universe/sp500": "Get S&P 500 ticker list",
            "GET /api/strategy/template": "Get strategy code template",
            "GET /api/backtest/{job_id}": "Get backtest result by ID",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/universe/sp500", response_model=UniverseResponse)
async def get_sp500_universe(force_refresh: bool = False):
    """
    Get the list of S&P 500 tickers.

    Args:
        force_refresh: Force refresh the ticker list from source

    Returns:
        UniverseResponse with ticker list
    """
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
    """
    Get a template for writing trading strategies.

    Returns:
        Dict with template code and documentation
    """
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


@app.post("/api/backtest", response_model=BacktestResult)
async def run_backtest(config: BacktestConfig):
    """
    Run a trading strategy backtest.

    Args:
        config: BacktestConfig with strategy code and parameters

    Returns:
        BacktestResult with metrics, equity curve, and trades
    """
    job_id = str(uuid.uuid4())
    logger.info(f"Starting backtest job {job_id}")

    try:
        # Validate strategy code first
        sandbox = get_sandbox()
        try:
            sandbox.validate(config.strategy_code)
        except Exception as e:
            logger.error(f"Strategy validation failed: {e}")
            return BacktestResult(
                success=False,
                message=f"Strategy validation failed: {str(e)}"
            )

        # Create and run backtest engine
        engine = BacktestEngine(config)
        result = engine.run_backtest()

        # Store result
        backtest_jobs[job_id] = result

        logger.info(f"Backtest job {job_id} completed: {result.success}")

        return result

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        return BacktestResult(
            success=False,
            message=f"Backtest failed: {str(e)}"
        )


@app.get("/api/backtest/{job_id}", response_model=BacktestResult)
async def get_backtest_result(job_id: str):
    """
    Get backtest result by job ID.

    Args:
        job_id: Backtest job ID

    Returns:
        BacktestResult
    """
    if job_id not in backtest_jobs:
        raise HTTPException(status_code=404, detail="Backtest job not found")

    return backtest_jobs[job_id]


@app.post("/api/backtest/validate")
async def validate_strategy(strategy_code: str):
    """
    Validate strategy code without running backtest.

    Args:
        strategy_code: Python code to validate

    Returns:
        Validation result
    """
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
    """
    Clear all cached data (data cache and backtest jobs).

    Returns:
        Success message
    """
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
    """Global exception handler."""
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

    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
