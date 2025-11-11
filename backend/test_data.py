"""
Quick test script to verify data fetching works.
"""

from data_loader import get_loader
import logging

logging.basicConfig(level=logging.INFO)

def test_single_ticker():
    """Test fetching data for a single ticker."""
    loader = get_loader()

    print("\n=== Testing single ticker (AAPL) ===")
    df = loader.get_historical_data(
        ticker="AAPL",
        start_date="2023-01-01",
        end_date="2024-01-01"
    )

    if df is not None:
        print(f"[SUCCESS] Fetched {len(df)} bars for AAPL")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.head())
    else:
        print("[FAILED] Could not fetch data for AAPL")

def test_multiple_tickers():
    """Test fetching data for multiple tickers."""
    loader = get_loader()

    print("\n=== Testing multiple tickers ===")
    test_tickers = ["AAPL", "MSFT", "GOOGL"]

    data_dict = loader.get_bulk_data(
        tickers=test_tickers,
        start_date="2023-01-01",
        end_date="2024-01-01"
    )

    print(f"\n[SUCCESS] Fetched {len(data_dict)}/{len(test_tickers)} tickers")
    for ticker, df in data_dict.items():
        print(f"  - {ticker}: {len(df)} bars")

if __name__ == "__main__":
    print("Testing data loader...")
    test_single_ticker()
    test_multiple_tickers()
    print("\n[DONE] All tests completed!")
