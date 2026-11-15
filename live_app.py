import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import urllib.request
import io

st.set_page_config(page_title="NSE India Live Stock Terminal", layout="wide")

# --- 1. FETCH ALL 2,000+ LISTED NSE INDIA STOCKS ---
@st.cache_data(ttl=86400)
def get_all_nse_stocks():
    indices = [
        "^NSEI | NIFTY 50 INDEX",
        "^NSEBANK | NIFTY BANK INDEX",
        "^CNXIT | NIFTY IT INDEX"
    ]
    try:
        # Official NSE Archives Master List of all listed equities
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            csv_text = response.read().decode('utf-8')
        nse_df = pd.read_csv(io.StringIO(csv_text))
        nse_df.columns = nse_df.columns.str.strip()
        
        stock_list = [
            f"{row['SYMBOL'].strip()} | {row['NAME OF COMPANY'].strip()}"
            for _, row in nse_df.iterrows()
        ]
        return indices + sorted(stock_list)
    except Exception:
        # Fallback list if NSE website is temporarily unreachable
        fallback = [
            "RELIANCE | Reliance Industries Limited",
            "TCS | Tata Consultancy Services Limited",
            "HDFCBANK | HDFC Bank Limited",
            "INFY | Infosys Limited",
            "ICICIBANK | ICICI Bank Limited",
            "SBIN | State Bank of India",
            "BHARTIARTL | Bharti Airtel Limited",
            "ITC | ITC Limited",
            "TATAMOTORS | Tata Motors Limited",
            "LT | Larsen & Toubro Limited",
            "BAJFINANCE | Bajaj Finance Limited",
            "SUNPHARMA | Sun Pharmaceutical Industries Limited",
            "MARUTI | Maruti Suzuki India Limited",
            "HAL | Hindustan Aeronautics Limited",
            "ZOMATO | Zomato Limited"
        ]
        return indices + fallback

nse_catalog = get_all_nse_stocks()

# --- 2. SIDEBAR CONTROLS (NSE ONLY) ---
st.sidebar.header("🇮🇳 NSE India Controls")

selected_item = st.sidebar.selectbox(
    f"Search NSE Stock ({len(nse_catalog):,} Listed)",
    options=nse_catalog,
    index=3  # Defaults to first stock after indices, or search any name
)

raw_symbol = selected_item.split(" | ")[0].strip()
company_name = selected_item.split(" | ")[1].strip()
yf_ticker = raw_symbol if raw_symbol.startswith("^") else f"{raw_symbol}.NS"

# Custom NSE Symbol Override (if a newly IPO'd stock isn't in the list yet)
custom_nse = st.sidebar.text_input("Or type exact NSE Symbol (Optional)", value="").upper().strip()
if custom_nse:
    clean_sym = custom_nse.replace(".NS", "")
    yf_ticker = clean_sym if clean_sym.startswith("^") else f"{clean_sym}.NS"
    company_name = f"{clean_sym} (NSE)"

mode = st.sidebar.radio("Analysis Mode", ["Intraday Live (1m - 15m)", "Historical Swing (1M - 5Y)"], index=0)

if mode == "Intraday Live (1m - 15m)":
    interval = st.sidebar.selectbox("Candle Interval", ["1m", "5m", "15m"], index=0)
    period = "1d" if interval == "1m" else "5d"
else:
    period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    interval = "1d"

refresh_rate = st.sidebar.slider("Auto-Refresh (Seconds)", min_value=3, max_value=60, value=5)
show_sma = st.sidebar.checkbox("Show 20 & 50 Moving Averages", value=True)
show_rsi = st.sidebar.checkbox("Show RSI (14) Indicator", value=True)

st.title(f"🇮🇳 {company_name} ({raw_symbol if not custom_nse else custom_nse})")

# --- 3. AUTO-REFRESHING NSE DASHBOARD ---
@st.fragment(run_every=f"{refresh_rate}s")
def render_nse_dashboard():
    try:
        stock = yf.Ticker(yf_ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            st.warning(f"No data available for {yf_ticker}. Try switching Analysis Mode to 'Historical Swing'.")
            return

        # Technical Indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Key Metrics
        latest_price = df['Close'].iloc[-1]
        prev_price = df['Open'].iloc[0] if mode.startswith("Intraday") else (df['Close'].iloc[-2] if len(df) > 1 else latest_price)
        change = latest_price - prev_price
        pct_change = (change / prev_price) * 100
        period_high = df['High'].max()
        period_low = df['Low'].min()
        latest_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50.0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("NSE Price (₹)", f"₹{latest_price:,.2f}", f"{change:+.2f} ({pct_change:+.2f}%)")
        c2.metric("Period High", f"₹{period_high:,.2f}")
        c3.metric("Period Low", f"₹{period_low:,.2f}")
        c4.metric("Volume", f"{int(df['Volume'].sum()):,}")
        rsi_status = "Overbought (>70)" if latest_rsi > 70 else ("Oversold (<30)" if latest_rsi < 30 else "Neutral")
        c5.metric("RSI (14)", f"{latest_rsi:.1f}", rsi_status, delta_color="off")

        st.caption(f"Exchange: NSE India | Symbol: {yf_ticker} | Last Refreshed: {datetime.now().strftime('%H:%M:%S')} IST")

        # Build Interactive Chart
        rows = 3 if show_rsi else 2
        heights = [0.60, 0.20, 0.20] if show_rsi else [0.75, 0.25]
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights)

        # 1. Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="Price (₹)"
        ), row=1, col=1)

        if show_sma:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#f59e0b', width=1.5), name="20 SMA"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#38bdf8', width=1.5), name="50 SMA"), row=1, col=1)

        # 2. Volume
        colors = ['#ef4444' if row['Open'] > row['Close'] else '#10b981' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

        # 3. RSI
        if show_rsi:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#a855f7', width=1.5), name="RSI (14)"), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#10b981", row=3, col=1)

        fig.update_layout(
            height=680, template="plotly_dark",
            xaxis_rangeslider_visible=False,
            margin=dict(l=15, r=15, t=20, b=15),
            uirevision=f"{yf_ticker}_{mode}_{period}_{interval}"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Historical Data Table Drawer
        with st.expander("📊 View NSE OHLCV Data Table"):
            st.dataframe(df[['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'RSI']].sort_index(ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching NSE data: {e}")

render_nse_dashboard()