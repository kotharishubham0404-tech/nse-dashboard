import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import urllib.request
import io

st.set_page_config(page_title="NSE India Pro Research Terminal", layout="wide")

# --- 1. LOAD ALL NSE LISTED EQUITIES ---
@st.cache_data(ttl=86400)
def get_all_nse_stocks():
    indices = [
        "^NSEI | NIFTY 50 INDEX",
        "^NSEBANK | NIFTY BANK INDEX",
        "^CNXIT | NIFTY IT INDEX"
    ]
    try:
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
            "HAL | Hindustan Aeronautics Limited",
            "TRENT | Trent Limited",
            "BEL | Bharat Electronics Limited"
        ]
        return indices + fallback

nse_catalog = get_all_nse_stocks()

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.header("🇮🇳 NSE Pro Terminal")

selected_item = st.sidebar.selectbox(
    f"Search NSE Stock ({len(nse_catalog):,} Listed)",
    options=nse_catalog,
    index=3
)

raw_symbol = selected_item.split(" | ")[0].strip()
company_name = selected_item.split(" | ")[1].strip()
yf_ticker = raw_symbol if raw_symbol.startswith("^") else f"{raw_symbol}.NS"

custom_nse = st.sidebar.text_input("Or type NSE Symbol manually", value="").upper().strip()
if custom_nse:
    clean_sym = custom_nse.replace(".NS", "")
    yf_ticker = clean_sym if clean_sym.startswith("^") else f"{clean_sym}.NS"
    raw_symbol = clean_sym
    company_name = f"{clean_sym} (NSE)"

mode = st.sidebar.radio("Analysis Mode", ["Historical Swing (Daily)", "Intraday Live (Minutes)"], index=0)

if mode == "Intraday Live (Minutes)":
    interval = st.sidebar.selectbox("Candle Interval", ["1m", "5m", "15m"], index=1)
    period = "1d" if interval == "1m" else "5d"
else:
    period = st.sidebar.selectbox("Time Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
    interval = "1d"

refresh_rate = st.sidebar.slider("Live Refresh (Seconds)", min_value=5, max_value=60, value=10)
show_sma = st.sidebar.checkbox("20, 50 & 200 Moving Averages", value=True)
show_bb = st.sidebar.checkbox("Bollinger Bands (20, 2)", value=False)
show_rsi = st.sidebar.checkbox("RSI (14) Momentum", value=True)

st.title(f"🇮🇳 {company_name} ({raw_symbol})")

# --- 3. CREATE 3 ORGANIZED TABS ---
tab1, tab2, tab3 = st.tabs([
    "📈 Live Technical Chart & Signals",
    "🏛️ Fundamental Ratios & Valuation",
    "🔍 Multi-Stock NSE Screener"
])

# === TAB 1: TECHNICAL CHART & AUTO SIGNALS ===
with tab1:
    @st.fragment(run_every=f"{refresh_rate}s")
    def render_chart_tab():
        try:
            stock = yf.Ticker(yf_ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                st.warning("No price data returned. Try switching to 'Historical Swing (Daily)' mode during non-market hours.")
                return

            # Calculate Indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()

            # Bollinger Bands
            std_20 = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
            df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

            # RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            latest = df['Close'].iloc[-1]
            prev = df['Open'].iloc[0] if mode.startswith("Intraday") else (df['Close'].iloc[-2] if len(df) > 1 else latest)
            chg = latest - prev
            pct = (chg / prev) * 100
            rsi_val = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50.0
            sma20_val = df['SMA_20'].iloc[-1]
            sma50_val = df['SMA_50'].iloc[-1]

            # Automated Technical Verdict
            if not pd.isna(sma20_val) and not pd.isna(sma50_val):
                if latest > sma20_val and sma20_val > sma50_val:
                    signal_text = "🟢 BULLISH UPTREND (Price > 20 SMA > 50 SMA)"
                elif latest < sma20_val and sma20_val < sma50_val:
                    signal_text = "🔴 BEARISH DOWNTREND (Price < 20 SMA < 50 SMA)"
                else:
                    signal_text = "🟡 SIDEWAYS / CONSOLIDATION (Watch for Breakout)"
            else:
                signal_text = "⚪ INSUFFICIENT BARS FOR 50 SMA SIGNAL"

            st.info(f"**Automated Technical Scan:** {signal_text}  |  **RSI (14):** `{rsi_val:.1f}`  |  **Updated:** `{datetime.now().strftime('%H:%M:%S')}`")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Live Price (₹)", f"₹{latest:,.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
            c2.metric("Period High", f"₹{df['High'].max():,.2f}")
            c3.metric("Period Low", f"₹{df['Low'].min():,.2f}")
            c4.metric("20 SMA Trend", f"₹{sma20_val:,.2f}" if not pd.isna(sma20_val) else "N/A")
            c5.metric("RSI (14)", f"{rsi_val:.1f}", "Overbought" if rsi_val > 70 else ("Oversold" if rsi_val < 30 else "Neutral"), delta_color="off")

            rows = 3 if show_rsi else 2
            heights = [0.62, 0.18, 0.20] if show_rsi else [0.75, 0.25]
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights)

            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Price (₹)"
            ), row=1, col=1)

            if show_sma:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#f59e0b', width=1.5), name="20 SMA"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#38bdf8', width=1.5), name="50 SMA"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#ec4899', width=1.8, dash='dot'), name="200 SMA"), row=1, col=1)

            if show_bb:
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(148,163,184,0.5)', width=1), name="BB Upper"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(148,163,184,0.5)', width=1), fill='tonexty', fillcolor='rgba(148,163,184,0.08)', name="BB Lower"), row=1, col=1)

            colors = ['#ef4444' if r['Open'] > r['Close'] else '#10b981' for _, r in df.iterrows()]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

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

        except Exception as e:
            st.error(f"Chart error: {e}")

    render_chart_tab()

# === TAB 2: FUNDAMENTAL RATIOS & VALUATION ===
with tab2:
    st.subheader(f"🏛️ Key Fundamentals: {company_name}")
    try:
        info = yf.Ticker(yf_ticker).info
        mcap_cr = info.get("marketCap", 0) / 1e7 if info.get("marketCap") else None
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        book_val = info.get("bookValue")
        roe = info.get("returnOnEquity")
        debt_eq = info.get("debtToEquity")
        high_52 = info.get("fiftyTwoWeekHigh")
        low_52 = info.get("fiftyTwoWeekLow")
        div_yield = info.get("dividendYield")

        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Market Cap", f"₹{mcap_cr:,.0f} Cr" if mcap_cr else "N/A")
        f2.metric("Trailing P/E Ratio", f"{pe:.2f}" if pe else "N/A")
        f3.metric("Price to Book (P/B)", f"{pb:.2f}" if pb else "N/A")
        f4.metric("Book Value / Share", f"₹{book_val:,.2f}" if book_val else "N/A")

        f5, f6, f7, f8 = st.columns(4)
        f5.metric("Return on Equity (ROE)", f"{roe*100:.1f}%" if roe else "N/A")
        f6.metric("Debt to Equity (%)", f"{debt_eq:.1f}%" if debt_eq else "N/A")
        f7.metric("52-Week High", f"₹{high_52:,.2f}" if high_52 else "N/A")
        f8.metric("52-Week Low", f"₹{low_52:,.2f}" if low_52 else "N/A")

        st.markdown("---")
        st.write("**Sector:**", info.get("sector", "N/A"), " | **Industry:**", info.get("industry", "N/A"))
        if info.get("longBusinessSummary"):
            with st.expander("Read Company Business Profile"):
                st.write(info.get("longBusinessSummary"))
    except Exception as e:
        st.warning(f"Fundamental data unavailable for this symbol: {e}")

# === TAB 3: MULTI-STOCK NSE SCREENER ===
with tab3:
    st.subheader("🔍 Custom NSE Watchlist & Momentum Scanner")
    default_basket = "RELIANCE, TCS, HDFCBANK, INFY, SBIN, ICICIBANK, TATAMOTORS, LT, HAL, BAJFINANCE"
    basket_input = st.text_input("Enter NSE Symbols separated by commas:", value=default_basket)

    if st.button("🚀 Scan NSE Watchlist Now"):
        symbols = [s.strip().upper().replace(".NS", "") for s in basket_input.split(",") if s.strip()]
        results = []
        progress = st.progress(0)

        for idx, sym in enumerate(symbols):
            try:
                t_sym = sym if sym.startswith("^") else f"{sym}.NS"
                hist = yf.Ticker(t_sym).history(period="3mo", interval="1d")
                if len(hist) >= 20:
                    close = hist['Close'].iloc[-1]
                    prev_c = hist['Close'].iloc[-2]
                    day_pct = ((close - prev_c) / prev_c) * 100
                    sma20 = hist['Close'].rolling(20).mean().iloc[-1]
                    sma50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else sma20

                    d = hist['Close'].diff()
                    g = (d.where(d > 0, 0)).rolling(14).mean().iloc[-1]
                    l = (-d.where(d < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi_14 = 100 - (100 / (1 + (g / l))) if l != 0 else 50

                    trend = "🟢 Bullish (Above 20 & 50 SMA)" if (close > sma20 and sma20 >= sma50) else ("🔴 Bearish (Below 20 SMA)" if close < sma20 else "🟡 Neutral")
                    results.append({
                        "NSE Symbol": sym,
                        "Live Price (₹)": round(close, 2),
                        "1D Change (%)": round(day_pct, 2),
                        "RSI (14)": round(rsi_14, 1),
                        "20 DMA (₹)": round(sma20, 2),
                        "Trend Signal": trend
                    })
            except Exception:
                pass
            progress.progress((idx + 1) / len(symbols))

        if results:
            scan_df = pd.DataFrame(results).sort_values(by="1D Change (%)", ascending=False)
            st.dataframe(scan_df, use_container_width=True, hide_index=True)
