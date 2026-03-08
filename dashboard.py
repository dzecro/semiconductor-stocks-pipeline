import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as graph_obj

DB_PATH = "data/stocks.db"

#-----PAGE CONFIG--------------------------------
st.set_page_config(
    page_title="Semiconductor Market Stock Tracker",
    page_icon="📈",
    layout="wide"
)


#-----DATA LOADING-------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM daily_prices", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()


#-----HEADER--------------------------------------
st.title(" Semiconductor Stock Dashboard")
st.caption("Tracking: NVDA - TXN - ADI - QCOM - INTC - TSM - Powered by Yahoo Finance")



#-----SIDEBAR FILTERS-----------------------------
st.sidebar.header("Filters")


tickers = sorted(df["ticker"].unique())
selected_tickers = st.sidebar.multiselect(
    "Select Companies",
    options=tickers,
    default=tickers
)


date_range = st.sidebar.date_input(
    "Date Range",
    value=[df["date"].min(), df["date"].max()]
)


#Apply filters to loaded dataframe
filtered = df[
    (df["ticker"].isin(selected_tickers)) &
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1]))
]

#Debug: Check if tickers are loaded: st.sidebar.write(f"Selected: {selected_tickers}")

#-----KPI CARDS - Latest closing prices----------------
st.subheader("Latest Close Prices")

latest = (
    filtered.sort_values("date")
    .groupby("ticker")
    .last()
    .reset_index()
)

cols = st.columns(len(latest))
for i, row in latest.iterrows():
    delta = f"{row['daily_return_pct']:+.2f}% today"
    cols[i].metric(
        label=f"{row['ticker']}",
        value=f"${row['close']:.2f}",
        delta=delta
    )


st.divider()


# ── CHART 1: Price History (Close) with Moving Averages ───────
st.subheader("Price History with Moving Averages")

# Let user pick one ticker to see candlestick + MAs
focus_ticker = st.selectbox(
    "Select ticker for detailed view",
    options=selected_tickers,
    index=0
)

focus_df = filtered[filtered["ticker"] == focus_ticker]

fig_candle = graph_obj.Figure()

# Candlestick chart — shows open/high/low/close for every day
fig_candle.add_trace(graph_obj.Candlestick(
    x=focus_df["date"],
    open=focus_df["open"],
    high=focus_df["high"],
    low=focus_df["low"],
    close=focus_df["close"],
    name=focus_ticker
))

# Overlay the 20-day moving average
fig_candle.add_trace(graph_obj.Scatter(
    x=focus_df["date"],
    y=focus_df["ma_20"],
    mode="lines",
    name="MA 20",
    line=dict(color="orange", width=1.5)
))

# Overlay the 50-day moving average
fig_candle.add_trace(graph_obj.Scatter(
    x=focus_df["date"],
    y=focus_df["ma_50"],
    mode="lines",
    name="MA 50",
    line=dict(color="blue", width=1.5)
))

fig_candle.update_layout(
    xaxis_rangeslider_visible=False,
    template="plotly_white",
    height=450
)

st.plotly_chart(fig_candle, use_container_width=True)

# ── CHART 2: Normalised Price Comparison ──────────────────────
# Concept: To compare stocks fairly, we index all prices to 100
# on the first day. This shows % growth, not raw price.
st.subheader("Relative Performance (Indexed to 100)")

indexed_frames = []
for ticker in selected_tickers:
    t_df = filtered[filtered["ticker"] == ticker].copy()
    if not t_df.empty:
        base_price = t_df.sort_values("date").iloc[0]["close"]
        t_df["indexed_price"] = (t_df["close"] / base_price) * 100
        indexed_frames.append(t_df)

if indexed_frames:
    indexed_df = pd.concat(indexed_frames)
    fig_index = px.line(
        indexed_df,
        x="date", y="indexed_price", color="ticker",
        labels={"indexed_price": "Indexed Price (Base = 100)", "date": "Date"},
        template="plotly_white"
    )
    fig_index.add_hline(y=100, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_index, use_container_width=True)

# ── CHART 3: Volume ────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Trading Volume")
    fig_vol = px.bar(
        filtered,
        x="date", y="volume", color="ticker",
        labels={"volume": "Volume", "date": "Date"},
        template="plotly_white",
        barmode="group"
    )
    st.plotly_chart(fig_vol, use_container_width=True)

# ── CHART 4: Daily Return Distribution ────────────────────────
with col4:
    st.subheader("Daily Return Distribution (%)")
    fig_ret = px.box(
        filtered,
        x="ticker", y="daily_return_pct", color="ticker",
        labels={"daily_return_pct": "Daily Return (%)", "ticker": "Ticker"},
        template="plotly_white"
    )
    fig_ret.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_ret, use_container_width=True)

# ── RAW DATA ───────────────────────────────────────────────────
with st.expander("View Raw Data"):
    st.dataframe(
        filtered.sort_values("date", ascending=False),
        use_container_width=True
    )

