import sqlite3
import pandas as pd
import os

DB_PATH = "data/stocks.db"



def load_to_db(df: pd.DataFrame):
    """
    Saves the combined DataFrame to a SQLite table called 'daily_prices'.
    """

    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    df.to_sql(
        name="daily_prices",
        con=conn,
        if_exists="replace",
        index=False
    )

    print(f" Loaded {len(df)} rows into '{DB_PATH}' -> table:daily_prices")
    conn.close()


def verify_load():
    """
    Runs SQL queries to confirm data quality after loading.
    """

    conn = sqlite3.connect(DB_PATH)

    # Query Check 1: Row count and date range per ticker
    summary = pd.read_sql("""
       SELECT
            ticker,
            company,
            COUNT(*)                        AS trading_days,
            MIN(date)                       AS earliest_date,
            MAX(date)                       AS latest_date,
            ROUND(MIN(close), 2)            AS price_52w_low,
            ROUND(MAX(close), 2)            AS price_52w_high,
            ROUND(AVG(daily_return_pct), 4) AS avg_daily_return_pct
        FROM daily_prices
        GROUP BY ticker, company
        ORDER BY avg_daily_return_pct DESC
    """, conn)

    print("\n Stock Summary (past year):")
    print(summary.to_string(index=False))


    #Query Check 2: Most volatile days (largest price range)
    volatile = pd.read_sql("""
        SELECT
            date,
            ticker,
            close,
            price_range,
            daily_return_pct
        FROM daily_prices
        GROUP BY ticker, company
        ORDER BY price_range DESC
        LIMIT 10
    """, conn)

    print("\n Most Volatile Days:")
    print(volatile.to_string(index=False))


    conn.close()


#Testing the transformation function
if __name__ == "__main__":
    from extract import extract_all
    from transform import transform_all


    raw = extract_all()
    df = transform_all(raw)
    load_to_db(df)
    verify_load()

