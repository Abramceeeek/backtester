"""
Data loader module for fetching and caching historical stock data.
Handles S&P 500 ticker list and historical OHLCV data using yfinance.
"""

import yfinance as yf
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(__file__).parent / "data_cache"
CACHE_DIR.mkdir(exist_ok=True)

# Cache expiry (7 days for data, 30 days for ticker list)
DATA_CACHE_DAYS = 7
TICKER_CACHE_DAYS = 30


class DataLoader:
    """Loads and caches historical stock data for backtesting."""

    def __init__(self):
        self.sp500_tickers = None
        self.cache_dir = CACHE_DIR

    def get_sp500_tickers(self, force_refresh: bool = False) -> List[str]:
        """
        Fetch current S&P 500 ticker list from Wikipedia.

        Args:
            force_refresh: Force refresh even if cache exists

        Returns:
            List of ticker symbols
        """
        cache_file = self.cache_dir / "sp500_tickers.pkl"
        cache_meta = self.cache_dir / "sp500_tickers_meta.pkl"

        # Check cache
        if not force_refresh and cache_file.exists() and cache_meta.exists():
            try:
                with open(cache_meta, 'rb') as f:
                    meta = pickle.load(f)
                    cache_date = meta['date']
                    if datetime.now() - cache_date < timedelta(days=TICKER_CACHE_DAYS):
                        with open(cache_file, 'rb') as f:
                            tickers = pickle.load(f)
                            logger.info(f"Loaded {len(tickers)} S&P 500 tickers from cache")
                            self.sp500_tickers = tickers
                            return tickers
            except Exception as e:
                logger.warning(f"Failed to load ticker cache: {e}")

        # Fetch from Wikipedia
        try:
            logger.info("Fetching S&P 500 tickers from Wikipedia...")
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})

            if not table:
                raise Exception("Could not find S&P 500 table on Wikipedia")

            tickers = []
            for row in table.findAll('tr')[1:]:
                cols = row.findAll('td')
                if cols:
                    ticker = cols[0].text.strip()
                    # Handle special characters (e.g., BRK.B -> BRK-B for yfinance)
                    ticker = ticker.replace('.', '-')
                    tickers.append(ticker)

            logger.info(f"Fetched {len(tickers)} S&P 500 tickers")

            # Cache the results
            with open(cache_file, 'wb') as f:
                pickle.dump(tickers, f)
            with open(cache_meta, 'wb') as f:
                pickle.dump({'date': datetime.now()}, f)

            self.sp500_tickers = tickers
            return tickers

        except Exception as e:
            logger.error(f"Failed to fetch S&P 500 tickers: {e}")
            # Fallback to a hardcoded list of major tickers
            fallback = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
                'JPM', 'JNJ', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
                'COST', 'AVGO', 'KO', 'WMT', 'MCD', 'CSCO', 'ACN', 'TMO', 'LIN',
                'ABT', 'DHR', 'VZ', 'NKE', 'CMCSA', 'ADBE', 'NEE', 'TXN', 'PM'
            ]
            logger.warning(f"Using fallback list of {len(fallback)} tickers")
            self.sp500_tickers = fallback
            return fallback

    def get_historical_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        force_refresh: bool = False,
        retry_count: int = 3
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for a ticker with retry logic.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (1d, 1h, etc.)
            force_refresh: Force refresh even if cache exists
            retry_count: Number of retries on failure

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        cache_file = self.cache_dir / f"{ticker}_{start_date}_{end_date}_{interval}.pkl"
        cache_meta = self.cache_dir / f"{ticker}_{start_date}_{end_date}_{interval}_meta.pkl"

        # Check cache
        if not force_refresh and cache_file.exists() and cache_meta.exists():
            try:
                with open(cache_meta, 'rb') as f:
                    meta = pickle.load(f)
                    cache_date = meta['date']
                    if datetime.now() - cache_date < timedelta(days=DATA_CACHE_DAYS):
                        with open(cache_file, 'rb') as f:
                            df = pickle.load(f)
                            logger.debug(f"Loaded {ticker} from cache")
                            return df
            except Exception as e:
                logger.warning(f"Failed to load cache for {ticker}: {e}")

        # Fetch from yfinance with retries
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    logger.info(f"Retry {attempt + 1}/{retry_count} for {ticker}")
                    time.sleep(2 * attempt)  # Progressive backoff

                logger.info(f"Fetching {ticker} data from {start_date} to {end_date}")

                # Use download method for better reliability
                df = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    progress=False,
                    auto_adjust=False  # Get raw OHLC data
                )

                if df.empty:
                    if attempt < retry_count - 1:
                        continue
                    logger.warning(f"No data returned for {ticker}")
                    return None

                # Handle multi-level columns from yfinance (newer versions)
                if isinstance(df.columns, pd.MultiIndex):
                    # Flatten multi-index columns
                    df.columns = df.columns.get_level_values(0)

                # Standardize column names
                df.columns = [col.lower().replace(' ', '_') for col in df.columns]

                # Ensure required columns exist
                required_cols = ['open', 'high', 'low', 'close', 'volume']

                # Map alternative column names
                col_mapping = {
                    'adj_close': 'close' if 'close' not in df.columns else None
                }
                for old_col, new_col in col_mapping.items():
                    if new_col and old_col in df.columns:
                        df[new_col] = df[old_col]

                if not all(col in df.columns for col in required_cols):
                    logger.error(f"Missing required columns for {ticker}. Available: {list(df.columns)}")
                    return None

                # Keep only required columns
                df = df[required_cols]

                # Remove any NaN rows
                df = df.dropna()

                if len(df) < 100:
                    logger.warning(f"Insufficient data for {ticker}: only {len(df)} bars")
                    return None

                # Cache the results
                with open(cache_file, 'wb') as f:
                    pickle.dump(df, f)
                with open(cache_meta, 'wb') as f:
                    pickle.dump({'date': datetime.now()}, f)

                logger.info(f"Fetched {len(df)} bars for {ticker}")
                return df

            except Exception as e:
                if attempt < retry_count - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                    continue
                logger.error(f"Failed to fetch data for {ticker} after {retry_count} attempts: {e}")
                return None

        return None

    def get_bulk_data(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        interval: str = '1d',
        force_refresh: bool = False,
        delay: float = 0.5
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple tickers with rate limiting.

        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            force_refresh: Force refresh cache
            delay: Delay between requests in seconds

        Returns:
            Dictionary mapping tickers to DataFrames
        """
        data = {}
        failed = []

        logger.info(f"Fetching data for {len(tickers)} tickers...")

        for i, ticker in enumerate(tickers):
            # Add delay between requests to avoid rate limiting
            if i > 0:
                time.sleep(delay)

            df = self.get_historical_data(
                ticker, start_date, end_date, interval, force_refresh
            )
            if df is not None:
                data[ticker] = df
            else:
                failed.append(ticker)

            # Progress update every 10 tickers
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(tickers)} tickers processed")

        logger.info(f"Successfully loaded {len(data)}/{len(tickers)} tickers")
        if failed:
            logger.warning(f"Failed tickers: {', '.join(failed[:10])}" +
                          (f" and {len(failed)-10} more" if len(failed) > 10 else ""))

        return data

    def clear_cache(self):
        """Clear all cached data."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)
            logger.info("Cache cleared")


# Singleton instance
_loader = DataLoader()


def get_loader() -> DataLoader:
    """Get the singleton DataLoader instance."""
    return _loader
