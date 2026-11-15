import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import urllib.request
import io

st.set_page_config(page_title="NSE India Live Flow & Fundamental Terminal", layout="wide")

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
            "BEL | Bharat Electronics Limited",
            "NTPC | NTPC Limited",
            "ONGC | Oil and Natural Gas Corporation",
            "COALINDIA | Coal India Limited",
            "SUNPHARMA | Sun Pharmaceutical Industries Limited"
        ]
        return indices + fallback

nse_catalog = get_all_nse_stocks()

# --- 2. CACHED FUNDAMENTAL FETCHER ---
@st.cache_data(ttl=900)
def fetch_fundamentals(ticker_sym):
    tk = yf.Ticker(ticker_sym)
    info = {}
    try:
        info = tk.info or {}
    except Exception:
        info = {}

    q_inc, a_inc, bal_sheet = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        q_inc = tk.quarterly_income_stmt
    except Exception:
        pass
    try:
        a_inc = tk.income_stmt
    except Exception:
        pass
    try:
        bal_sheet = tk.balance_sheet
    except Exception:
        pass

    return info, q_inc, a_inc, bal_sheet

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🇮🇳 NSE Flow & Fundamentals")

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

mode = st.sidebar.radio("Analysis Mode", ["Intraday Live (Minutes)", "Historical Swing (Daily)"], index=0)

if mode == "Intraday Live (Minutes)":
    interval = st.sidebar.selectbox("Candle Interval", ["1m", "5m", "15m"], index=1)
    period = "1d" if interval == "1m" else "5d"
else:
    period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    interval = "1d"

refresh_rate = st.sidebar.slider("Live Refresh (Seconds)", min_value=5, max_value=60, value=10)
show_sma = st.sidebar.checkbox("Show 20, 50 & 200 SMA", value=True)
show_bb = st.sidebar.checkbox("Show Bollinger Bands (20, 2)", value=False)
show_cvd = st.sidebar.checkbox("Show Cumulative Volume Delta (CVD)", value=True)
show_rsi = st.sidebar.checkbox("Show RSI & Money Flow (MFI)", value=True)

st.title(f"🇮🇳 {company_name} ({raw_symbol})")

# --- 4. TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Live Chart, Volume Flow & Fundamentals",
    "🏛️ Financial Statements & Valuation Deep-Dive",
    "🔍 Quick Watchlist Volume Scanner",
    "🎯 Strategy Screener (Value, Breakout & CANSLIM)"
])

# === TAB 1: LIVE CHART, INFLOW/OUTFLOW & INTEGRATED FUNDAMENTALS ===
with tab1:
    @st.fragment(run_every=f"{refresh_rate}s")
    def render_live_flow_tab():
        try:
            stock = yf.Ticker(yf_ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                st.warning("No price data returned. Switch to 'Historical Swing (Daily)' if markets are closed.")
                return

            # --- A. VOLUME INFLOW & OUTFLOW CALCULATIONS ---
            hl_spread = (df['High'] - df['Low']).replace(0, np.nan)
            buy_ratio = ((df['Close'] - df['Low']) / hl_spread).fillna(0.5).clip(0.0, 1.0)
            sell_ratio = 1.0 - buy_ratio

            df['Buy_Vol'] = (df['Volume'] * buy_ratio).round(0)
            df['Sell_Vol'] = (df['Volume'] * sell_ratio).round(0)
            df['Net_Delta'] = df['Buy_Vol'] - df['Sell_Vol']
            df['CVD'] = df['Net_Delta'].cumsum()

            # Turnover Inflow & Outflow in ₹ Crores (1 Cr = 1e7)
            df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3.0
            df['Inflow_Cr'] = (df['Buy_Vol'] * df['Typical_Price']) / 1e7
            df['Outflow_Cr'] = (df['Sell_Vol'] * df['Typical_Price']) / 1e7
            df['Net_Flow_Cr'] = df['Inflow_Cr'] - df['Outflow_Cr']

            # --- B. TECHNICAL & MONEY FLOW INDICATORS ---
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()

            std_20 = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
            df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

            # RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = (100 - (100 / (1 + rs))).fillna(50)

            # Money Flow Index - MFI (14)
            raw_mf = df['Typical_Price'] * df['Volume']
            pos_mf = raw_mf.where(df['Typical_Price'] >= df['Typical_Price'].shift(1), 0).rolling(14).sum()
            neg_mf = raw_mf.where(df['Typical_Price'] < df['Typical_Price'].shift(1), 0).rolling(14).sum()
            mfr = pos_mf / neg_mf.replace(0, np.nan)
            df['MFI'] = (100 - (100 / (1 + mfr))).fillna(50)

            # --- C. SUMMARY METRICS ---
            latest = df['Close'].iloc[-1]
            prev = df['Open'].iloc[0] if mode.startswith("Intraday") else (df['Close'].iloc[-2] if len(df) > 1 else latest)
            chg = latest - prev
            pct = (chg / prev) * 100

            total_vol = df['Volume'].sum()
            total_inflow_vol = df['Buy_Vol'].sum()
            total_outflow_vol = df['Sell_Vol'].sum()
            net_vol_delta = total_inflow_vol - total_outflow_vol

            inflow_pct = (total_inflow_vol / total_vol * 100) if total_vol > 0 else 50.0
            outflow_pct = 100.0 - inflow_pct

            inflow_cr_sum = df['Inflow_Cr'].sum()
            outflow_cr_sum = df['Outflow_Cr'].sum()
            net_cr_sum = inflow_cr_sum - outflow_cr_sum

            latest_bar_inflow = df['Buy_Vol'].iloc[-1]
            latest_bar_outflow = df['Sell_Vol'].iloc[-1]
            latest_bar_net = df['Net_Delta'].iloc[-1]

            rsi_val = df['RSI'].iloc[-1]
            mfi_val = df['MFI'].iloc[-1]

            # --- D. TOP ROW: PRICE & LIVE VOLUME INFLOW / OUTFLOW SCOREBOARD ---
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Live NSE Price (₹)", f"₹{latest:,.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
            c2.metric("🟢 Volume Inflow (Buy)", f"{int(total_inflow_vol):,}", f"₹{inflow_cr_sum:,.2f} Cr ({inflow_pct:.1f}%)")
            c3.metric("🔴 Volume Outflow (Sell)", f"{int(total_outflow_vol):,}", f"-₹{outflow_cr_sum:,.2f} Cr ({outflow_pct:.1f}%)", delta_color="inverse")
            c4.metric(
                "⚡ Net Volume Delta",
                f"{int(net_vol_delta):+,}",
                f"Net ₹{net_cr_sum:+,.2f} Cr",
                delta_color="normal"
            )
            flow_verdict = "🟢 Net Accumulation" if net_vol_delta > 0 else "🔴 Net Distribution"
            c5.metric("Money Flow (MFI 14)", f"{mfi_val:.1f}", flow_verdict, delta_color="off")

            # Visual Buyer Inflow vs Seller Outflow Tug-of-War Bar
            st.markdown(
                f"""
                <div style="background:#1e293b; padding:10px 14px; border-radius:8px; margin-bottom:12px; border:1px solid #334155;">
                    <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-bottom:5px;">
                        <span style="color:#10b981;">🟢 BUYER INFLOW: {inflow_pct:.1f}% ({int(total_inflow_vol):,} shares | ₹{inflow_cr_sum:,.2f} Cr)</span>
                        <span style="color:#94a3b8;">Latest Candle Net Delta: {int(latest_bar_net):+,} (Buy: {int(latest_bar_inflow):,} / Sell: {int(latest_bar_outflow):,})</span>
                        <span style="color:#ef4444;">🔴 SELLER OUTFLOW: {outflow_pct:.1f}% ({int(total_outflow_vol):,} shares | ₹{outflow_cr_sum:,.2f} Cr)</span>
                    </div>
                    <div style="width:100%; height:12px; background:#ef4444; border-radius:6px; overflow:hidden;">
                        <div style="width:{inflow_pct:.1f}%; height:100%; background:#10b981;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # --- E. ALWAYS-VISIBLE FUNDAMENTAL SNAPSHOT STRIP ON MAIN PAGE ---
            if not raw_symbol.startswith("^"):
                info, _, _, _ = fetch_fundamentals(yf_ticker)
                mcap_cr = info.get("marketCap", 0) / 1e7 if info.get("marketCap") else None
                pe = info.get("trailingPE")
                pb = info.get("priceToBook")
                bv = info.get("bookValue")
                roe = info.get("returnOnEquity")
                de = info.get("debtToEquity")
                div_y = info.get("dividendYield")
                high_52 = info.get("fiftyTwoWeekHigh")
                low_52 = info.get("fiftyTwoWeekLow")

                with st.container(border=True):
                    st.caption(f"🏛️ **Key Fundamentals Snapshot ({company_name})** — Sector: `{info.get('sector', 'NSE Equity')}` | Industry: `{info.get('industry', 'N/A')}`")
                    f1, f2, f3, f4, f5, f6, f7, f8 = st.columns(8)
                    f1.metric("Market Cap", f"₹{mcap_cr:,.0f} Cr" if mcap_cr else "N/A")
                    f2.metric("P/E Ratio", f"{pe:.2f}" if pe else "N/A")
                    f3.metric("P/B Ratio", f"{pb:.2f}" if pb else "N/A")
                    f4.metric("Book Value", f"₹{bv:,.1f}" if bv else "N/A")
                    f5.metric("ROE (%)", f"{roe*100:.1f}%" if roe else "N/A")
                    f6.metric("Debt/Equity", f"{de:.1f}%" if de else "N/A")
                    f7.metric("52W High", f"₹{high_52:,.1f}" if high_52 else "N/A")
                    f8.metric("52W Low", f"₹{low_52:,.1f}" if low_52 else "N/A")

            # --- F. MULTI-PANE INTERACTIVE CHART (PRICE + INFLOW/OUTFLOW + CVD + RSI/MFI) ---
            subplot_titles = ["Price & Moving Averages (₹)", "Volume Inflow (Green) vs. Outflow (Red)"]
            row_heights = [0.50, 0.20]
            total_rows = 2

            if show_cvd:
                subplot_titles.append("Cumulative Volume Delta (CVD - Net Institutional Flow)")
                row_heights.append(0.15)
                total_rows += 1
            if show_rsi:
                subplot_titles.append("RSI (14) & Money Flow Index (MFI 14)")
                row_heights.append(0.15)
                total_rows += 1

            # Normalize row heights
            total_h = sum(row_heights)
            row_heights = [h / total_h for h in row_heights]

            fig = make_subplots(
                rows=total_rows, cols=1, shared_xaxes=True,
                vertical_spacing=0.03, row_heights=row_heights,
                subplot_titles=subplot_titles
            )

            # Row 1: Candlestick + SMAs
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Price (₹)"
            ), row=1, col=1)

            if show_sma:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#f59e0b', width=1.5), name="20 SMA"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#38bdf8', width=1.5), name="50 SMA"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#ec4899', width=1.8, dash='dot'), name="200 SMA"), row=1, col=1)

            if show_bb:
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(148,163,184,0.4)', width=1), name="BB Upper"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(148,163,184,0.4)', width=1), fill='tonexty', fillcolor='rgba(148,163,184,0.07)', name="BB Lower"), row=1, col=1)

            # Row 2: Stacked Volume Inflow (Green) vs Volume Outflow (Red)
            fig.add_trace(go.Bar(
                x=df.index, y=df['Buy_Vol'],
                marker_color='#10b981', name="Buy Volume (Inflow)"
            ), row=2, col=1)
            fig.add_trace(go.Bar(
                x=df.index, y=-df['Sell_Vol'],
                marker_color='#ef4444', name="Sell Volume (Outflow)"
            ), row=2, col=1)

            curr_row = 3
            # Row 3 (Optional): Cumulative Volume Delta (CVD)
            if show_cvd:
                cvd_color = '#10b981' if df['CVD'].iloc[-1] >= 0 else '#ef4444'
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['CVD'],
                    mode='lines', line=dict(color=cvd_color, width=2),
                    fill='tozeroy', fillcolor='rgba(16,185,129,0.12)' if df['CVD'].iloc[-1] >= 0 else 'rgba(239,68,68,0.12)',
                    name="Cumulative Volume Delta"
                ), row=curr_row, col=1)
                curr_row += 1

            # Row 4 (Optional): RSI & MFI
            if show_rsi:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#a855f7', width=1.5), name="RSI (14)"), row=curr_row, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MFI'], line=dict(color='#22d3ee', width=1.5, dash='dot'), name="MFI (14)"), row=curr_row, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=curr_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="#10b981", row=curr_row, col=1)

            fig.update_layout(
                height=780, template="plotly_dark",
                barmode="relative",
                xaxis_rangeslider_visible=False,
                margin=dict(l=15, r=15, t=30, b=15),
                uirevision=f"{yf_ticker}_{mode}_{period}_{interval}"
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- G. LIVE CANDLE-BY-CANDLE VOLUME INFLOW/OUTFLOW TABLE ---
            with st.expander("📊 View Candle-by-Candle Volume Inflow & Outflow Log", expanded=False):
                flow_log = df[['Close', 'Volume', 'Buy_Vol', 'Sell_Vol', 'Net_Delta', 'Inflow_Cr', 'Outflow_Cr', 'Net_Flow_Cr', 'MFI']].copy()
                flow_log.columns = [
                    'Close (₹)', 'Total Vol', '🟢 Inflow Vol (Buy)', '🔴 Outflow Vol (Sell)',
                    '⚡ Net Vol Delta', 'Inflow (₹ Cr)', 'Outflow (₹ Cr)', 'Net Flow (₹ Cr)', 'MFI (14)'
                ]
                st.dataframe(flow_log.sort_index(ascending=False).round(2), use_container_width=True)

        except Exception as e:
            st.error(f"Live chart error: {e}")

    render_live_flow_tab()

# === TAB 2: COMPLETE FUNDAMENTALS & FINANCIAL STATEMENTS ===
with tab2:
    st.subheader(f"🏛️ Complete Fundamental Analysis: {company_name} ({raw_symbol})")
    if raw_symbol.startswith("^"):
        st.info("Indices (like Nifty 50) do not have company financial statements. Select any NSE stock from the sidebar.")
    else:
        info, q_inc, a_inc, bal_sheet = fetch_fundamentals(yf_ticker)

        mcap_cr = info.get("marketCap", 0) / 1e7 if info.get("marketCap") else None
        ent_val_cr = info.get("enterpriseValue", 0) / 1e7 if info.get("enterpriseValue") else None
        pe = info.get("trailingPE")
        fwd_pe = info.get("forwardPE")
        pb = info.get("priceToBook")
        bv = info.get("bookValue")
        eps = info.get("trailingEps")
        roe = info.get("returnOnEquity")
        roa = info.get("returnOnAssets")
        op_margin = info.get("operatingMargins")
        prof_margin = info.get("profitMargins")
        de = info.get("debtToEquity")
        curr_ratio = info.get("currentRatio")
        div_yield = info.get("dividendYield")
        promoter_hold = info.get("heldPercentInsiders")
        inst_hold = info.get("heldPercentInstitutions")

        # Automated Fundamental Score Calculation (Out of 100)
        score = 50
        if pe and 0 < pe <= 25: score += 12
        elif pe and pe > 50: score -= 8
        if pb and 0 < pb <= 3.5: score += 10
        if roe and roe >= 0.15: score += 15
        if prof_margin and prof_margin >= 0.10: score += 8
        if de is not None and de <= 50: score += 10
        elif de is not None and de > 150: score -= 10
        score = max(10, min(98, score))

        verdict = "🟢 Strong Fundamental Quality" if score >= 70 else ("🟡 Moderate / Fair Valuation" if score >= 50 else "🔴 High Valuation or High Debt")
        st.info(f"**Fundamental Health Score:** `{score} / 100` — **{verdict}**")

        st.markdown("#### 1. Valuation & Shareholding Metrics")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Market Cap", f"₹{mcap_cr:,.0f} Cr" if mcap_cr else "N/A")
        k2.metric("Enterprise Value", f"₹{ent_val_cr:,.0f} Cr" if ent_val_cr else "N/A")
        k3.metric("Trailing P/E", f"{pe:.2f}" if pe else "N/A")
        k4.metric("Forward P/E", f"{fwd_pe:.2f}" if fwd_pe else "N/A")
        k5.metric("Price to Book (P/B)", f"{pb:.2f}" if pb else "N/A")
        k6.metric("Book Value / Share", f"₹{bv:,.2f}" if bv else "N/A")

        st.markdown("#### 2. Profitability, Solvency & Ownership")
        p1, p2, p3, p4, p5, p6 = st.columns(6)
        p1.metric("ROE (%)", f"{roe*100:.1f}%" if roe else "N/A")
        p2.metric("Operating Margin", f"{op_margin*100:.1f}%" if op_margin else "N/A")
        p3.metric("Net Profit Margin", f"{prof_margin*100:.1f}%" if prof_margin else "N/A")
        p4.metric("Debt to Equity", f"{de:.1f}%" if de is not None else "N/A")
        p5.metric("Promoter / Insider %", f"{promoter_hold*100:.1f}%" if promoter_hold else "N/A")
        p6.metric("Institutional %", f"{inst_hold*100:.1f}%" if inst_hold else "N/A")

        st.markdown("---")
        ch1, ch2 = st.columns(2)

        # Chart A: Quarterly Revenue vs Net Income (₹ Crores)
        with ch1:
            st.markdown("##### 📊 Quarterly Revenue vs. Net Profit (₹ Crores)")
            if not q_inc.empty:
                q_df = q_inc.T.sort_index()
                rev_col = next((c for c in ['Total Revenue', 'Operating Revenue'] if c in q_df.columns), None)
                net_col = next((c for c in ['Net Income', 'Net Income Common Stockholders'] if c in q_df.columns), None)
                if rev_col and net_col:
                    dates = [d.strftime('%b %Y') if hasattr(d, 'strftime') else str(d) for d in q_df.index]
                    fig_q = go.Figure()
                    fig_q.add_trace(go.Bar(x=dates, y=q_df[rev_col] / 1e7, name="Revenue (₹ Cr)", marker_color="#38bdf8"))
                    fig_q.add_trace(go.Bar(x=dates, y=q_df[net_col] / 1e7, name="Net Profit (₹ Cr)", marker_color="#10b981"))
                    fig_q.update_layout(height=350, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig_q, use_container_width=True)
                else:
                    st.caption("Quarterly revenue/profit breakdown not available for this stock.")
            else:
                st.caption("Quarterly income statement not available.")

        # Chart B: Balance Sheet Assets vs Total Liabilities / Debt (₹ Crores)
        with ch2:
            st.markdown("##### 🏦 Annual Balance Sheet: Assets vs. Debt (₹ Crores)")
            if not bal_sheet.empty:
                b_df = bal_sheet.T.sort_index()
                asset_col = next((c for c in ['Total Assets'] if c in b_df.columns), None)
                debt_col = next((c for c in ['Total Debt', 'Long Term Debt'] if c in b_df.columns), None)
                eq_col = next((c for c in ['Stockholders Equity', 'Total Equity Gross Minority Interest'] if c in b_df.columns), None)
                if asset_col:
                    b_dates = [d.strftime('%Y') if hasattr(d, 'strftime') else str(d) for d in b_df.index]
                    fig_b = go.Figure()
                    fig_b.add_trace(go.Bar(x=b_dates, y=b_df[asset_col] / 1e7, name="Total Assets (₹ Cr)", marker_color="#6366f1"))
                    if eq_col:
                        fig_b.add_trace(go.Bar(x=b_dates, y=b_df[eq_col] / 1e7, name="Net Worth / Equity (₹ Cr)", marker_color="#10b981"))
                    if debt_col:
                        fig_b.add_trace(go.Bar(x=b_dates, y=b_df[debt_col] / 1e7, name="Total Debt (₹ Cr)", marker_color="#ef4444"))
                    fig_b.update_layout(height=350, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig_b, use_container_width=True)
            else:
                st.caption("Balance sheet data not available.")

        if info.get("longBusinessSummary"):
            with st.expander("📖 Read Company Business Profile"):
                st.write(info.get("longBusinessSummary"))

# === TAB 3: MULTI-STOCK VOLUME INFLOW/OUTFLOW SCANNER ===
with tab3:
    st.subheader("🔍 Multi-Stock Volume Inflow vs. Outflow Scanner")
    default_basket = "RELIANCE, TCS, HDFCBANK, INFY, SBIN, ICICIBANK, TATAMOTORS, LT, HAL, BAJFINANCE"
    basket_input = st.text_input("Enter NSE Symbols separated by commas:", value=default_basket)

    if st.button("🚀 Scan Live Volume Inflow & Outflow"):
        symbols = [s.strip().upper().replace(".NS", "") for s in basket_input.split(",") if s.strip()]
        results = []
        progress = st.progress(0)

        for idx, sym in enumerate(symbols):
            try:
                t_sym = sym if sym.startswith("^") else f"{sym}.NS"
                hist = yf.Ticker(t_sym).history(period="5d", interval="15m")
                if not hist.empty:
                    today_df = hist.tail(25)  # Last trading session bars
                    close = today_df['Close'].iloc[-1]
                    open_p = today_df['Open'].iloc[0]
                    day_pct = ((close - open_p) / open_p) * 100

                    hl = (today_df['High'] - today_df['Low']).replace(0, np.nan)
                    b_rat = ((today_df['Close'] - today_df['Low']) / hl).fillna(0.5).clip(0, 1)
                    inflow_v = (today_df['Volume'] * b_rat).sum()
                    outflow_v = (today_df['Volume'] * (1 - b_rat)).sum()
                    tot_v = today_df['Volume'].sum()
                    inflow_p = (inflow_v / tot_v * 100) if tot_v > 0 else 50.0

                    typ_p = (today_df['High'] + today_df['Low'] + today_df['Close']) / 3.0
                    net_cr = (((today_df['Volume'] * b_rat) - (today_df['Volume'] * (1 - b_rat))) * typ_p).sum() / 1e7

                    results.append({
                        "NSE Symbol": sym,
                        "Live Price (₹)": round(close, 2),
                        "Change (%)": round(day_pct, 2),
                        "🟢 Buy Inflow (%)": round(inflow_p, 1),
                        "🔴 Sell Outflow (%)": round(100 - inflow_p, 1),
                        "Net Volume Delta": int(inflow_v - outflow_v),
                        "Net Money Flow (₹ Cr)": round(net_cr, 2),
                        "Flow Signal": "🟢 Strong Inflow" if inflow_p >= 55 else ("🔴 Heavy Outflow" if inflow_p <= 45 else "🟡 Balanced")
                    })
            except Exception:
                pass
            progress.progress((idx + 1) / len(symbols))

        if results:
            scan_df = pd.DataFrame(results).sort_values(by="Net Money Flow (₹ Cr)", ascending=False)
            st.dataframe(scan_df, use_container_width=True, hide_index=True)

# === TAB 4: STRATEGY SCREENER (VALUE, 52W BREAKOUT & CANSLIM) ===
with tab4:
    st.subheader("🎯 Institutional Strategy Screener (NSE India)")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        strategy_choice = st.radio(
            "Select Screening Strategy:",
            [
                "📊 All Metrics Scorecard (No Filter)",
                "💎 Low P/B & Value Picks",
                "🚀 52-Week High Breakouts",
                "🏆 CANSLIM Growth & Momentum"
            ]
        )

    with col_b:
        preset_universe = st.selectbox(
            "Choose NSE Stock Basket to Scan:",
            [
                "Nifty Bluechip & Sector Leaders (20 Stocks)",
                "PSU & Deep Value Basket (15 Stocks)",
                "Defense, Railways & Capex Momentum (15 Stocks)",
                "Custom Symbol List"
            ]
        )
        baskets = {
            "Nifty Bluechip & Sector Leaders (20 Stocks)": "RELIANCE, TCS, HDFCBANK, ICICIBANK, INFY, SBIN, BHARTIARTL, ITC, LT, TATAMOTORS, BAJFINANCE, SUNPHARMA, MARUTI, M&M, NTPC, POWERGRID, HINDUNILVR, AXISBANK, KOTAKBANK, ULTRACEMCO",
            "PSU & Deep Value Basket (15 Stocks)": "SBIN, ONGC, COALINDIA, NTPC, POWERGRID, BANKBARODA, PNB, CANBK, IOC, BPCL, GAIL, NMDC, BHEL, NALCO, PFC",
            "Defense, Railways & Capex Momentum (15 Stocks)": "HAL, BEL, MAZDOCK, BDL, COCHINSHIP, IRFC, RVNL, IRCON, TITAGARH, SIEMENS, ABB, CUMMINSIND, LT, TRENT, DIXON",
            "Custom Symbol List": "RELIANCE, SBIN, HAL, BEL, ONGC, COALINDIA, TRENT, TATAMOTORS, NTPC, ITC"
        }
        custom_strategy_symbols = st.text_area("NSE Symbols to Scan:", value=baskets[preset_universe], height=68)

    with st.expander("⚙️ Customize Strategy Filter Thresholds", expanded=False):
        s1, s2, s3, s4 = st.columns(4)
        max_pb = s1.slider("Max Price-to-Book (Value)", 0.5, 10.0, 3.0, 0.5)
        max_pe = s2.slider("Max P/E Ratio (Value)", 5, 80, 25, 1)
        max_dist_52w = s3.slider("Max Distance from 52W High (%)", 2, 30, 15, 1)
        min_roe = s4.slider("Min ROE (%)", 0, 40, 12, 1)

    if st.button("🎯 Run Strategy Screener Now", type="primary"):
        sym_list = [s.strip().upper().replace(".NS", "") for s in custom_strategy_symbols.split(",") if s.strip()]
        strategy_rows = []
        prog_bar = st.progress(0)

        for i, sym in enumerate(sym_list):
            try:
                tk = yf.Ticker(f"{sym}.NS")
                hist = tk.history(period="1y", interval="1d")
                info = tk.info
                if not hist.empty and len(hist) >= 50:
                    cmp_price = hist['Close'].iloc[-1]
                    sma_50 = hist['Close'].rolling(50).mean().iloc[-1]
                    sma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else sma_50
                    high_52w = info.get("fiftyTwoWeekHigh") or hist['High'].max()
                    dist_from_high_pct = ((high_52w - cmp_price) / high_52w) * 100 if high_52w else 99.0

                    pb_val = info.get("priceToBook")
                    pe_val = info.get("trailingPE")
                    book_val = info.get("bookValue")
                    roe_val = (info.get("returnOnEquity") * 100) if info.get("returnOnEquity") else None
                    qtr_eps_growth = (info.get("earningsQuarterlyGrowth") * 100) if info.get("earningsQuarterlyGrowth") else None

                    is_value = (pb_val is not None and pb_val <= max_pb) and (pe_val is None or pe_val <= max_pe)
                    is_breakout = (dist_from_high_pct <= max_dist_52w) and (cmp_price >= sma_50)
                    is_canslim = is_breakout and (cmp_price >= sma_200) and (roe_val is not None and roe_val >= min_roe)

                    badges = []
                    if is_value: badges.append("💎 Value")
                    if is_breakout: badges.append("🚀 Breakout")
                    if is_canslim: badges.append("🏆 CANSLIM")

                    strategy_rows.append({
                        "NSE Symbol": sym,
                        "CMP (₹)": round(cmp_price, 2),
                        "P/B": round(pb_val, 2) if pb_val else None,
                        "Book Value (₹)": round(book_val, 1) if book_val else None,
                        "P/E": round(pe_val, 2) if pe_val else None,
                        "ROE (%)": round(roe_val, 1) if roe_val is not None else None,
                        "Qtr Profit Gr (%)": round(qtr_eps_growth, 1) if qtr_eps_growth is not None else None,
                        "Off 52W High (%)": round(dist_from_high_pct, 2),
                        "Qualifies For": " | ".join(badges) if badges else "⚪ Watchlist",
                        "_is_value": is_value,
                        "_is_breakout": is_breakout,
                        "_is_canslim": is_canslim
                    })
            except Exception:
                pass
            prog_bar.progress((i + 1) / len(sym_list))

        prog_bar.empty()
        if strategy_rows:
            df_strat = pd.DataFrame(strategy_rows)
            if strategy_choice == "💎 Low P/B & Value Picks":
                df_strat = df_strat[df_strat["_is_value"] == True].sort_values(by="P/B", ascending=True)
            elif strategy_choice == "🚀 52-Week High Breakouts":
                df_strat = df_strat[df_strat["_is_breakout"] == True].sort_values(by="Off 52W High (%)", ascending=True)
            elif strategy_choice == "🏆 CANSLIM Growth & Momentum":
                df_strat = df_strat[df_strat["_is_canslim"] == True]

            display_cols = [c for c in df_strat.columns if not c.startswith("_")]
            st.dataframe(df_strat[display_cols], use_container_width=True, hide_index=True)
