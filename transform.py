import pandas as pd

def transform_company(company_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans one company's raw DataFrame and adds derived financial metrics.
    """

    # Select and rename necessary columns
    df = df[[
        "Date", "company", "ticker",
        "Open", "High", "Low", "Close", "Volume"
    ]].copy()

    df.columns = [
        "date", "company", "ticker",
        "open", "high", "low", "close", "volume"
    ]


    #Clean the date column
    #Strip timezone info for SQLite
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)


    #Sort by date - for rolling calculations
    df = df.sort_values("date").reset_index(drop=True)


    #Round prices to 2 decimal places
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].round(2)


    #Daily return percentage
    #.shift(1) gets the previous row's value for yesterday's close starting from row 2
    df["daily_return_pct"] = (
        (df["close"] - df["close"].shift(1))/df["close"].shift(1) * 100
    ).round(4)


    #Moving Average
    #.rolling(window=N) calculate over last N rows
    # min_periods=1 means: start calculating even if fewer than N rows exist
    df["ma_20"] = df["close"].rolling(window=20, min_periods=1).mean().round(2)
    df["ma_50"] = df["close"].rolling(window=50, min_periods=1).mean().round(2)


    #Daily Price Range
    df["price_range"] = (df["high"] - df["low"]).round(2)


    #Drop rows with daily_return NaN -
    df = df.dropna(subset=["daily_return_pct"])


    return df


def transform_all(raw_all: dict) -> pd.DataFrame:
    """
    Transforms all companies and combines into one master DataFrame.
    """

    all_frames = []

    for company_name, df in raw_all.items():
        transformed = transform_company(company_name, df)
        all_frames.append(transformed)
        print(f"{company_name}: {len(transformed)} rows")

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["date", "ticker"]).reset_index(drop=True)

    print(f"\n Transform complete - {len(combined)} total rows, "
          f"{combined['ticker'].nunique()} tickers")

    return combined





if __name__ == "__main__":
    from extract import extract_all
    raw = extract_all()
    df = transform_all(raw)

#Testing the transformation function
"""
    print("\nColumn types:")
    print(df.dtypes)
    print("\nSample row:")
    print(df[df["ticker"] == "NVDA"].tail(3).to_string())
"""