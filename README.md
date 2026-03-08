# 📈 Semiconductor Stock Data Pipeline

An end-to-end ETL pipeline that extracts 1 year of daily stock price data
for 6 leading semiconductor companies, stores it in SQLite, and summarizes
it through an interactive Streamlit dashboard.

## Companies Tracked

| Company           | Ticker |
| ----------------- | ------ |
| NVIDIA            | NVDA   |
| Texas Instruments | TXN    |
| Analog Devices    | ADI    |
| Qualcomm          | QCOM   |
| Intel             | INTC   |
| TSMC              | TSM    |

## Architecture

```
Yahoo Finance API → Python ETL → SQLite → Streamlit Dashboard
  (via yfinance)   extract/       stocks     candlestick, indexed
                   transform/     .db        performance, volume,
                   load.py                   return distribution
```

## Dashboard Features

- Live closing price KPI cards with daily return delta
- Candlestick chart with MA20 and MA50 overlays per ticker
- Indexed price comparison chart (base = 100) for fair cross-ticker comparison
- Trading volume bar chart
- Daily return distribution box plot
- Sidebar filters for ticker selection and date range

## Tech Stack

- Python 3.11
- yfinance — stock data extraction
- Pandas — data transformation
- SQLite — local data storage
- Streamlit + Plotly — dashboard and visualization
- Docker + Docker Compose — containerization

## How to Run

### 1 — Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full ETL pipeline
python load.py

# Launch the dashboard
streamlit run dashboard.py
```

### 2 — Run with Docker

```bash
docker compose up --build
```

Then visit http://localhost:8501

## Project Structure

```
semiconductor-stock-pipeline/
├── extract.py        # Fetches OHLCV data from Yahoo Finance
├── transform.py      # Cleans data and adds financial metrics
├── load.py           # Saves to SQLite and verifies load
├── dashboard.py      # Streamlit dashboard
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Design Considerations

- Used `yfinance` over alternatives like Alpha Vantage or Polygon.io for quick
  interfacing requiring no API key, removing onboarding friction for anyone
  cloning this repo.
- Added MA20 and MA50 in the transform step rather than calculating them in
  the dashboard — keeping business logic in the pipeline layer, not the UI.
- Used an indexed price chart (base = 100) to compare stocks fairly, since
  NVDA (~$900) and INTC (~$20) cannot be meaningfully compared on raw price.
- Separated extract, transform, and load into distinct files following the
  Single Responsibility Principle.
- Used `if_exists="replace"` in the load step for simplicity. In a
  production pipeline this would be replaced with upserts to preserve history.

## Future Plans

- Add a scheduling layer (Apache Airflow or cron) to refresh data daily
- Include fundamental data (P/E ratio, market cap) alongside price data
- Add a data quality check step between transform and load
- Deploy to GCP Cloud Run or AWS App Runner with a persistent volume
- Add alerting: flag when any stock crosses its MA50 for the first time
- Store historical pipeline runs instead of replacing data each time
