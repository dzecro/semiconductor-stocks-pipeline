import yfinance as yf
import pandas as pd
import time


# Leading Semiconductor companies to track stock data
# Display name: Stock Ticker Symbol
COMPANIES = {
    "NVIDIA":               "NVDA",
    "Texas Instruments":    "TXN",
    "Analog Devices":       "ADI",
    "Qualcomm":             "QCOM",
    "Intel":                "INTC",
    "TSMC":                 "TSM"
}

#Set how far back data to retrieve
PERIOD = "1y"   #Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y


def fetch_stock(company_name: str, ticker: str) -> pd.DataFrame:

    """
    This function fetches historical OHLCV (Open, High, Low, Close, Volume) data for a single company using yfinance.
    Returns a raw DataFrame or None if the fetch fails.
    """

    print(f"  Fetching {company_name} ({ticker})...")

    stock = yf.Ticker(ticker)
    df = stock.history(period=PERIOD)

    if df.empty:
        print(f"   ERROR: No data returned for {ticker}")
        return None


    # yfinance returns a DataFrame indexed by date
    # We reset the index so 'Date' becomes a regular column
    df = df.reset_index()

    # Add company identifiers as columns
    df["company"] = company_name
    df["ticker"] = ticker


    time.sleep(2)

    return df



def extract_all() -> dict:
    """
    Fetches all tickers in one batched request using yf.download().
    More reliable than 5 separate requests.
    """
    tickers = list(COMPANIES.values())

    print(f"  Fetching all tickers in one request: {tickers}")

    raw = yf.download(
        tickers=tickers,
        period=PERIOD,
        group_by="ticker",  # Organizes data by ticker symbol
        auto_adjust=True,   # Adjusts prices for splits/dividends
        progress=False      # Suppresses the download progress bar
    )

    all_data = {}

    # Build a reverse lookup: ticker symbol → company name
    ticker_to_company = {v: k for k, v in COMPANIES.items()}

    for ticker in tickers:
        # Extract this ticker's slice from the multi-ticker DataFrame
        df = raw[ticker].copy()

        if df.empty:
            print(f"  WARNING: No data returned for {ticker}")
            continue

        df = df.reset_index()
        df["company"] = ticker_to_company[ticker]
        df["ticker"] = ticker

        all_data[ticker_to_company[ticker]] = df
        print(f"  ✓ {ticker_to_company[ticker]}: {len(df)} rows")

    print(f"\n Extracted data for {len(all_data)} companies.")
    return all_data


if __name__ == "__main__":
    data = extract_all()

    print(f"\nTickers loaded: {list(data.keys())}")

    sample = data["NVIDIA"]

    # Dynamically find the date column regardless of what yfinance names it
    date_col = [col for col in sample.columns if "date" in col.lower()][0]

    print(f"\nNVIDIA sample — {len(sample)} rows")
    print(f"Date column detected as: '{date_col}'")
    print(sample[[date_col, "Open", "High", "Low", "Close", "Volume"]].tail())

    print("\nAll columns returned by yfinance:")
    print(sample.columns.tolist())


'''Functionality test
    #Print sample data to verify shape
    sample = data["NVIDIA"]
    print(f"\nNVIDIA sample - {len(sample)} rows")
    print(sample[["Date", "Open", "High", "Low", "Close", "Volume"]].tail())
'''



