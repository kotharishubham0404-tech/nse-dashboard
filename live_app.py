import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import urllib.request
import io

st.set_page_config(page_title="NSE & BSE 360° Stock Analyzer", layout="wide")

# ==============================================================================
# 1. VERIFIED NSE & BSE INDEX CATALOG (CLEAN, ZERO-CLUTTER)
# ==============================================================================

COMPANY_NAMES = {
    "^NSEI": "NSE Nifty 50 Index", "^BSESN": "BSE Sensex 30 Index", "^NSEBANK": "NSE Nifty Bank Index",
    "^CNXIT": "NSE Nifty IT Index", "^CNXPHARMA": "NSE Nifty Pharma Index", "^CNXAUTO": "NSE Nifty Auto Index",
    "^CNXFMCG": "NSE Nifty FMCG Index", "^CNXMETAL": "NSE Nifty Metal Index", "^CNXPSUBANK": "NSE Nifty PSU Bank Index",
    "HDFCBANK": "HDFC Bank Ltd", "ICICIBANK": "ICICI Bank Ltd", "SBIN": "State Bank of India",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd", "AXISBANK": "Axis Bank Ltd", "INDUSINDBK": "IndusInd Bank Ltd",
    "BANKBARODA": "Bank of Baroda", "PNB": "Punjab National Bank", "FEDERALBNK": "Federal Bank Ltd",
    "IDFCFIRSTB": "IDFC First Bank Ltd", "AUBANK": "AU Small Finance Bank Ltd", "BANDHANBNK": "Bandhan Bank Ltd",
    "CANBK": "Canara Bank", "UNIONBANK": "Union Bank of India", "INDIANB": "Indian Bank",
    "RELIANCE": "Reliance Industries Ltd", "TCS": "Tata Consultancy Services Ltd", "INFY": "Infosys Ltd",
    "BHARTIARTL": "Bharti Airtel Ltd", "ITC": "ITC Ltd", "LT": "Larsen & Toubro Ltd",
    "HCLTECH": "HCL Technologies Ltd", "BAJFINANCE": "Bajaj Finance Ltd", "MARUTI": "Maruti Suzuki India Ltd",
    "SUNPHARMA": "Sun Pharmaceutical Industries", "TATAMOTORS": "Tata Motors Ltd", "ULTRACEMCO": "UltraTech Cement Ltd",
    "NTPC": "NTPC Ltd", "M&M": "Mahindra & Mahindra Ltd", "TITAN": "Titan Company Ltd",
    "POWERGRID": "Power Grid Corp of India", "ASIANPAINT": "Asian Paints Ltd", "BAJAJFINSV": "Bajaj Finserv Ltd",
    "NESTLEIND": "Nestle India Ltd", "ADANIPORTS": "Adani Ports & SEZ Ltd", "TATASTEEL": "Tata Steel Ltd",
    "JSWSTEEL": "JSW Steel Ltd", "TECHM": "Tech Mahindra Ltd", "HINDUNILVR": "Hindustan Unilever Ltd",
    "ADANIENT": "Adani Enterprises Ltd", "APOLLOHOSP": "Apollo Hospitals Enterprise", "BAJAJ-AUTO": "Bajaj Auto Ltd",
    "BEL": "Bharat Electronics Ltd", "BPCL": "Bharat Petroleum Corp", "BRITANNIA": "Britannia Industries Ltd",
    "CIPLA": "Cipla Ltd", "COALINDIA": "Coal India Ltd", "DRREDDY": "Dr. Reddy's Laboratories",
    "EICHERMOT": "Eicher Motors Ltd", "GRASIM": "Grasim Industries Ltd", "HDFCLIFE": "HDFC Life Insurance",
    "HEROMOTOCO": "Hero MotoCorp Ltd", "HINDALCO": "Hindalco Industries Ltd", "ONGC": "Oil & Natural Gas Corp",
    "SBILIFE": "SBI Life Insurance", "SHRIRAMFIN": "Shriram Finance Ltd", "TATACONSUM": "Tata Consumer Products",
    "TRENT": "Trent Ltd", "WIPRO": "Wipro Ltd", "HAL": "Hindustan Aeronautics Ltd",
    "DLF": "DLF Ltd", "ZOMATO": "Zomato Ltd", "JIOFIN": "Jio Financial Services",
    "PFC": "Power Finance Corporation", "RECLTD": "REC Ltd", "IRFC": "Indian Railway Finance Corp",
    "RVNL": "Rail Vikas Nigam Ltd", "MAZDOCK": "Mazagon Dock Shipbuilders", "BDL": "Bharat Dynamics Ltd",
    "DIXON": "Dixon Technologies", "POLYCAB": "Polycab India Ltd", "PERSISTENT": "Persistent Systems Ltd",
    "SUZLON": "Suzlon Energy Ltd", "BSE": "BSE Ltd", "CDSL": "Central Depository Services", "ANGELONE": "Angel One Ltd"
}

INDEX_GROUPS = {
    "🌐 All NSE & BSE Listed Stocks (Full Search)": "ALL",
    "📊 Benchmark Indices (Nifty 50, Sensex, Bank Nifty)": ["^NSEI", "^BSESN", "^NSEBANK", "^CNXIT", "^CNXPHARMA", "^CNXAUTO", "^CNXFMCG", "^CNXMETAL", "^CNXPSUBANK"],
    "🏦 NIFTY BANK (12 Stocks)": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "BANKBARODA", "PNB", "FEDERALBNK", "IDFCFIRSTB", "AUBANK", "BANDHANBNK"],
    "🏛️ NIFTY PSU BANK (12 Stocks)": ["SBIN", "BANKBARODA", "PNB", "CANBK", "UNIONBANK", "INDIANB", "BANKINDIA", "MAHABANK", "IOB", "CENTRALBK", "UCOBANK", "PSB"],
    "🇮🇳 BSE SENSEX 30 (30 Stocks)": ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "ITC", "LT", "HCLTECH", "AXISBANK", "BAJFINANCE", "MARUTI", "SUNPHARMA", "TATAMOTORS", "KOTAKBANK", "ULTRACEMCO", "NTPC", "M&M", "TITAN", "POWERGRID", "ASIANPAINT", "BAJAJFINSV", "NESTLEIND", "INDUSINDBK", "ADANIPORTS", "TATASTEEL", "JSWSTEEL", "TECHM", "HINDUNILVR"],
    "🇮🇳 NSE NIFTY 50 (50 Stocks)": ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BPCL", "BHARTIARTL", "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SHRIRAMFIN", "SBIN", "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO"],
    "🇮🇳 NSE NIFTY NEXT 50 (50 Stocks)": ["ABB", "ADANIENSOL", "ADANIGREEN", "ADANIPOWER", "ATGL", "AMBUJACEM", "DMART", "BAJAJHLDNG", "BANKBARODA", "BHEL", "BOSCHLTD", "CANBK", "CHOLAFIN", "COLPAL", "DLF", "DABUR", "DIVISLAB", "GAIL", "GODREJCP", "HAL", "HAVELLS", "HINDZINC", "ICICIGI", "ICICIPRULI", "IOC", "IRCTC", "IRFC", "JINDALSTEL", "JIOFIN", "JSWENERGY", "LICI", "LODHA", "LTIM", "MARICO", "MOTHERSON", "NAUKRI", "NHPC", "PIDILITIND", "PFC", "PNB", "RECLTD", "SIEMENS", "SRF", "SHREECEM", "TATAPOWER", "TORNTPHARM", "TVSMOTOR", "UNITDSPR", "VBL", "VEDL", "ZOMATO", "ZYDUSLIFE"],
    "💻 NIFTY IT (17 Stocks)": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "PERSISTENT", "OFSS", "COFORGE", "MPHASIS", "LTTS", "TATAELXSI", "KPITTECH", "CYIENT", "ZENSARTECH", "SONATSOFTW", "BIRLASOFT"],
    "🚗 NIFTY AUTO (17 Stocks)": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY", "BHARATFORG", "MOTHERSON", "BOSCHLTD", "MRF", "BALKRISIND", "APOLLOTYRE", "EXIDEIND", "SONACOMS", "TIINDIA"],
    "💊 NIFTY PHARMA & HEALTHCARE (18 Stocks)": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP", "LUPIN", "AUROPHARMA", "TORNTPHARM", "ZYDUSLIFE", "ALKEM", "MANKIND", "MAXHEALTH", "FORTIS", "BIOCON", "LAURUSLABS", "GLENMARK", "IPCALAB", "SYNGENE"],
    "🛒 NIFTY FMCG (18 Stocks)": ["ITC", "HINDUNILVR", "NESTLEIND", "VBL", "BRITANNIA", "GODREJCP", "TATACONSUM", "DABUR", "MARICO", "COLPAL", "UNITDSPR", "UBL", "PGHH", "EMAMILTD", "RADICO", "PATANJALI", "JYOTHYLAB", "BIKAJI"],
    "⛏️ NIFTY METAL (16 Stocks)": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA", "HINDZINC", "JINDALSTEL", "NMDC", "SAIL", "NATIONALUM", "APLAPOLLO", "JSL", "RATNAMANI", "WELCORP", "HINDCOPPER", "MOIL"],
    "⚡ NIFTY ENERGY, OIL & GAS (21 Stocks)": ["RELIANCE", "NTPC", "ONGC", "POWERGRID", "COALINDIA", "ADANIGREEN", "ADANIPOWER", "TATAPOWER", "IOC", "BPCL", "GAIL", "JSWENERGY", "NHPC", "SJVN", "TORNTPOWER", "CESC", "PETRONET", "OIL", "HPCL", "IGL", "MGL"],
    "🛡️ NIFTY PSE, DEFENSE & RAILWAYS (21 Stocks)": ["HAL", "BEL", "MAZDOCK", "BDL", "COCHINSHIP", "GRSE", "SOLARINDS", "IRFC", "RVNL", "IRCON", "TITAGARH", "RAILTEL", "RITES", "BEML", "BHEL", "NTPC", "ONGC", "COALINDIA", "POWERGRID", "PFC", "RECLTD"],
    "🚀 NIFTY MIDCAP & SMALLCAP LEADERS (40 Stocks)": ["DIXON", "POLYCAB", "PERSISTENT", "CUMMINSIND", "CGPOWER", "SUPREMEIND", "ASTRAL", "COFORGE", "VOLTAS", "PAGEIND", "PIIND", "INDHOTEL", "CONCOR", "OBEROIRLTY", "GODREJPROP", "PRESTIGE", "PETRONET", "HPCL", "GMRINFRA", "YESBANK", "TATACOMM", "JUBLFOOD", "MUTHOOTFIN", "SBICARD", "BSE", "MCX", "CDSL", "ANGELONE", "SUZLON", "KAYNES", "DELHIVERY", "PAYTM", "POLICYBZR", "NYKAA", "CAMS", "KFINTECH", "DATAPATTNS", "TEJASNET", "HFCL", "PRAJIND"]
}

@st.cache_data(ttl=86400)
def load_master_stock_dict():
    master = dict(COMPANY_NAMES)
    try:
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as response:
            csv_text = response.read().decode('utf-8')
        nse_df = pd.read_csv(io.StringIO(csv_text))
        nse_df.columns = nse_df.columns.str.strip()
        for _, row in nse_df.iterrows():
            master[row['SYMBOL'].strip()] = row['NAME OF COMPANY'].strip()
    except Exception:
        for grp in INDEX_GROUPS.values():
            if isinstance(grp, list):
                for s in grp:
                    if s not in master:
                        master[s] = f"{s} India Ltd"
    return master

MASTER_STOCK_DICT = load_master_stock_dict()

@st.cache_data(ttl=600)
def get_stock_360_data(yf_ticker):
    tk = yf.Ticker(yf_ticker)
    hist_1y = pd.DataFrame()
    info = {}
    q_inc = pd.DataFrame()
    bal_sheet = pd.DataFrame()
    try:
        hist_1y = tk.history(period="1y", interval="1d")
    except Exception:
        pass
    if not yf_ticker.startswith("^"):
        try:
            info = tk.info or {}
        except Exception:
            info = {}
        try:
            q_inc = tk.quarterly_income_stmt
        except Exception:
            pass
        try:
            bal_sheet = tk.balance_sheet
        except Exception:
            pass
    return hist_1y, info, q_inc, bal_sheet

# ==============================================================================
# 2. CLEAN, UNIFIED SIDEBAR (NO DUPLICATE FIELDS)
# ==============================================================================
st.sidebar.header("🇮🇳 Stock Search & Controls")

exchange_choice = st.sidebar.radio(
    "1. Exchange:",
    ["NSE India (.NS)", "BSE India (.BO)"],
    horizontal=True
)
suffix = ".NS" if "NSE" in exchange_choice else ".BO"

selected_group = st.sidebar.selectbox(
    "2. Filter by Index / Sector:",
    options=list(INDEX_GROUPS.keys()),
    index=0
)

if INDEX_GROUPS[selected_group] == "ALL":
    available_symbols = list(MASTER_STOCK_DICT.keys())
else:
    available_symbols = INDEX_GROUPS[selected_group]

formatted_options = [
    f"{sym} | {MASTER_STOCK_DICT.get(sym, sym)}"
    for sym in available_symbols
]

selected_stock_option = st.sidebar.selectbox(
    f"3. Search or Select Stock ({len(formatted_options):,} available):",
    options=formatted_options,
    index=min(10, len(formatted_options) - 1) if selected_group.startswith("🌐") else 0,
    key=f"stock_select_{selected_group}"
)

raw_symbol = selected_stock_option.split(" | ")[0].strip()
company_name = selected_stock_option.split(" | ")[1].strip()
yf_ticker = raw_symbol if raw_symbol.startswith("^") else f"{raw_symbol}{suffix}"

st.sidebar.markdown("---")
timeframe_label = st.sidebar.selectbox(
    "4. Chart Timeframe:",
    [
        "Intraday Live (5m Candles - 5 Days)",
        "Intraday Live (1m Candles - Today)",
        "Intraday Live (15m Candles - 5 Days)",
        "Swing (3 Months - Daily)",
        "Swing (6 Months - Daily)",
        "Positional (1 Year - Daily)",
        "Long Term (5 Years - Weekly)"
    ],
    index=0
)

tf_map = {
    "Intraday Live (5m Candles - 5 Days)": ("5d", "5m"),
    "Intraday Live (1m Candles - Today)": ("1d", "1m"),
    "Intraday Live (15m Candles - 5 Days)": ("5d", "15m"),
    "Swing (3 Months - Daily)": ("3mo", "1d"),
    "Swing (6 Months - Daily)": ("6mo", "1d"),
    "Positional (1 Year - Daily)": ("1y", "1d"),
    "Long Term (5 Years - Weekly)": ("5y", "1wk")
}
period, interval = tf_map[timeframe_label]

overlays = st.sidebar.multiselect(
    "5. Chart Overlays & Subplots:",
    ["Moving Averages (20, 50, 200)", "Bollinger Bands (20, 2)", "Cumulative Volume Delta (CVD)", "RSI & Money Flow (MFI)"],
    default=["Moving Averages (20, 50, 200)", "Cumulative Volume Delta (CVD)", "RSI & Money Flow (MFI)"]
)

refresh_rate = st.sidebar.slider("6. Auto-Refresh (Seconds):", 5, 60, 10)

# ==============================================================================
# 3. MAIN 360° STOCK VIEW (ALL DETAILS ON SINGLE STOCK SELECTION)
# ==============================================================================
st.title(f"🇮🇳 {company_name} ({yf_ticker})")

@st.fragment(run_every=f"{refresh_rate}s")
def render_360_stock_dashboard():
    stock = yf.Ticker(yf_ticker)
    df = stock.history(period=period, interval=interval)
    hist_1y, info, q_inc, bal_sheet = get_stock_360_data(yf_ticker)

    # Fallback to 1Y daily data if market is closed or intraday is empty
    if df.empty and not hist_1y.empty:
        df = hist_1y.copy()
        st.caption("ℹ️ Intraday feed unavailable for this symbol right now; displaying Daily chart.")
    elif df.empty:
        st.error(f"Could not load market data for {yf_ticker}. Try switching Exchange or selecting another stock.")
        return

    # --- A. VOLUME INFLOW & OUTFLOW CALCULATIONS ---
    hl_spread = (df['High'] - df['Low']).replace(0, np.nan)
    buy_ratio = ((df['Close'] - df['Low']) / hl_spread).fillna(0.5).clip(0.0, 1.0)
    sell_ratio = 1.0 - buy_ratio

    df['Buy_Vol'] = (df['Volume'] * buy_ratio).round(0)
    df['Sell_Vol'] = (df['Volume'] * sell_ratio).round(0)
    df['Net_Delta'] = df['Buy_Vol'] - df['Sell_Vol']
    df['CVD'] = df['Net_Delta'].cumsum()

    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3.0
    df['Inflow_Cr'] = (df['Buy_Vol'] * df['Typical_Price']) / 1e7
    df['Outflow_Cr'] = (df['Sell_Vol'] * df['Typical_Price']) / 1e7

    # --- B. TECHNICAL INDICATORS ---
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()

    std_20 = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
    df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = (100 - (100 / (1 + (gain / loss.replace(0, np.nan))))).fillna(50)

    raw_mf = df['Typical_Price'] * df['Volume']
    pos_mf = raw_mf.where(df['Typical_Price'] >= df['Typical_Price'].shift(1), 0).rolling(14).sum()
    neg_mf = raw_mf.where(df['Typical_Price'] < df['Typical_Price'].shift(1), 0).rolling(14).sum()
    df['MFI'] = (100 - (100 / (1 + (pos_mf / neg_mf.replace(0, np.nan))))).fillna(50)

    # --- C. SECTION 1: LIVE PRICE & VOLUME INFLOW/OUTFLOW SCOREBOARD ---
    latest = df['Close'].iloc[-1]
    prev = df['Open'].iloc[0] if interval in ["1m", "5m", "15m"] else (df['Close'].iloc[-2] if len(df) > 1 else latest)
    chg = latest - prev
    pct = (chg / prev) * 100

    tot_vol = df['Volume'].sum()
    in_vol = df['Buy_Vol'].sum()
    out_vol = df['Sell_Vol'].sum()
    net_vol = in_vol - out_vol
    in_pct = (in_vol / tot_vol * 100) if tot_vol > 0 else 50.0
    out_pct = 100.0 - in_pct

    in_cr = df['Inflow_Cr'].sum()
    out_cr = df['Outflow_Cr'].sum()
    net_cr = in_cr - out_cr
    mfi_val = df['MFI'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Live Price (₹)", f"₹{latest:,.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
    k2.metric("🟢 Buyer Volume Inflow", f"{int(in_vol):,}", f"₹{in_cr:,.2f} Cr ({in_pct:.1f}%)")
    k3.metric("🔴 Seller Volume Outflow", f"{int(out_vol):,}", f"-₹{out_cr:,.2f} Cr ({out_pct:.1f}%)", delta_color="inverse")
    k4.metric("⚡ Net Volume Flow", f"{int(net_vol):+,}", f"Net ₹{net_cr:+,.2f} Cr")
    k5.metric("RSI (14) / MFI (14)", f"{rsi_val:.1f} / {mfi_val:.1f}", "🟢 Accumulation" if net_vol > 0 else "🔴 Distribution", delta_color="off")

    st.markdown(
        f"""
        <div style="background:#1e293b; padding:9px 14px; border-radius:8px; margin-bottom:10px; border:1px solid #334155;">
            <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-bottom:4px;">
                <span style="color:#10b981;">🟢 BUYER INFLOW: {in_pct:.1f}% ({int(in_vol):,} shares | ₹{in_cr:,.2f} Cr)</span>
                <span style="color:#94a3b8;">Updated: {datetime.now().strftime('%H:%M:%S')} | Last Bar Delta: {int(df['Net_Delta'].iloc[-1]):+,}</span>
                <span style="color:#ef4444;">🔴 SELLER OUTFLOW: {out_pct:.1f}% ({int(out_vol):,} shares | ₹{out_cr:,.2f} Cr)</span>
            </div>
            <div style="width:100%; height:10px; background:#ef4444; border-radius:5px; overflow:hidden;">
                <div style="width:{in_pct:.1f}%; height:100%; background:#10b981;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- D. SECTION 2: INTERACTIVE MULTI-PANE CHART ---
    show_sma = "Moving Averages (20, 50, 200)" in overlays
    show_bb = "Bollinger Bands (20, 2)" in overlays
    show_cvd = "Cumulative Volume Delta (CVD)" in overlays
    show_osc = "RSI & Money Flow (MFI)" in overlays

    titles = ["Price Action & Key Moving Averages (₹)", "Volume Inflow (Green) vs. Outflow (Red)"]
    heights = [0.52, 0.18]
    if show_cvd:
        titles.append("Cumulative Volume Delta (CVD - Net Institutional Buying/Selling)")
        heights.append(0.15)
    if show_osc:
        titles.append("Momentum: RSI (14) & Money Flow Index (MFI 14)")
        heights.append(0.15)

    heights = [h / sum(heights) for h in heights]
    fig = make_subplots(rows=len(heights), cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights, subplot_titles=titles)

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="OHLC (₹)"), row=1, col=1)
    if show_sma:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#f59e0b', width=1.5), name="20 SMA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#38bdf8', width=1.5), name="50 SMA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#ec4899', width=1.8, dash='dot'), name="200 SMA"), row=1, col=1)
    if show_bb:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(148,163,184,0.4)', width=1), name="BB Upper"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(148,163,184,0.4)', width=1), fill='tonexty', fillcolor='rgba(148,163,184,0.07)', name="BB Lower"), row=1, col=1)

    fig.add_trace(go.Bar(x=df.index, y=df['Buy_Vol'], marker_color='#10b981', name="Inflow Vol (Buy)"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=-df['Sell_Vol'], marker_color='#ef4444', name="Outflow Vol (Sell)"), row=2, col=1)

    r_idx = 3
    if show_cvd:
        cvd_col = '#10b981' if df['CVD'].iloc[-1] >= 0 else '#ef4444'
        fig.add_trace(go.Scatter(
            x=df.index, y=df['CVD'], mode='lines', line=dict(color=cvd_col, width=2),
            fill='tozeroy', fillcolor='rgba(16,185,129,0.12)' if df['CVD'].iloc[-1] >= 0 else 'rgba(239,68,68,0.12)',
            name="CVD"
        ), row=r_idx, col=1)
        r_idx += 1

    if show_osc:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#a855f7', width=1.5), name="RSI (14)"), row=r_idx, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MFI'], line=dict(color='#22d3ee', width=1.5, dash='dot'), name="MFI (14)"), row=r_idx, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=r_idx, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#10b981", row=r_idx, col=1)

    fig.update_layout(height=700, template="plotly_dark", barmode="relative", xaxis_rangeslider_visible=False, margin=dict(l=15, r=15, t=25, b=10), uirevision=f"{yf_ticker}_{timeframe_label}")
    st.plotly_chart(fig, use_container_width=True)

    # --- E. SECTION 3: INSTANT STRATEGY QUALIFICATION & FUNDAMENTAL 360° REPORT ---
    if not raw_symbol.startswith("^") and not hist_1y.empty:
        d_close = hist_1y['Close'].iloc[-1]
        dma_50 = hist_1y['Close'].rolling(50).mean().iloc[-1] if len(hist_1y) >= 50 else d_close
        dma_200 = hist_1y['Close'].rolling(200).mean().iloc[-1] if len(hist_1y) >= 200 else dma_50
        high_52 = info.get("fiftyTwoWeekHigh") or hist_1y['High'].max()
        low_52 = info.get("fiftyTwoWeekLow") or hist_1y['Low'].min()
        dist_52h = ((high_52 - d_close) / high_52 * 100) if high_52 else 0.0

        mcap_cr = info.get("marketCap", 0) / 1e7 if info.get("marketCap") else None
        pe = info.get("trailingPE")
        fwd_pe = info.get("forwardPE")
        pb = info.get("priceToBook")
        bv = info.get("bookValue")
        roe = (info.get("returnOnEquity") * 100) if info.get("returnOnEquity") else None
        op_margin = (info.get("operatingMargins") * 100) if info.get("operatingMargins") else None
        net_margin = (info.get("profitMargins") * 100) if info.get("profitMargins") else None
        de = info.get("debtToEquity")
        qtr_gr = (info.get("earningsQuarterlyGrowth") * 100) if info.get("earningsQuarterlyGrowth") else None
        div_y = (info.get("dividendYield") * 100) if info.get("dividendYield") else None
        prom_pct = (info.get("heldPercentInsiders") * 100) if info.get("heldPercentInsiders") else None

        # Strategy Evaluations for this Selected Stock
        pass_value = (pb is not None and pb <= 3.5) and (pe is None or pe <= 28)
        pass_breakout = (dist_52h <= 15.0) and (d_close >= dma_50) and (in_pct >= 50.0)
        pass_canslim = (d_close >= dma_50) and (d_close >= dma_200) and (dist_52h <= 15.0) and (roe is None or roe >= 14.0)

        st.markdown("### 🎯 Strategy Scorecard & Qualification for Selected Stock")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            with st.container(border=True):
                st.markdown(f"**💎 Low P/B Value Strategy:** {'🟢 **QUALIFIES**' if pass_value else '⚪ **Does Not Qualify**'}")
                st.caption(f"• Price-to-Book: **{pb:.2f}x** (Target ≤ 3.5x)" if pb else "• P/B: N/A")
                st.caption(f"• Trailing P/E: **{pe:.1f}x** (Target ≤ 28x) | Book Value: **₹{bv:,.1f}**" if (pe and bv) else "• Valuation data partial")
        with sc2:
            with st.container(border=True):
                st.markdown(f"**🚀 52-Week High Breakout:** {'🟢 **QUALIFIES**' if pass_breakout else '⚪ **Does Not Qualify**'}")
                st.caption(f"• Distance from 52W High (₹{high_52:,.1f}): **{dist_52h:.1f}%** (Target ≤ 15%)")
                st.caption(f"• Above 50 DMA (₹{dma_50:,.1f}): **{'Yes' if d_close >= dma_50 else 'No'}** | Buy Inflow: **{in_pct:.1f}%**")
        with sc3:
            with st.container(border=True):
                st.markdown(f"**🏆 CANSLIM Leader Criteria:** {'🟢 **QUALIFIES**' if pass_canslim else '⚪ **Does Not Qualify**'}")
                st.caption(f"• Above 50 & 200 DMA (₹{dma_200:,.1f}): **{'Yes' if (d_close >= dma_50 and d_close >= dma_200) else 'No'}**")
                st.caption(f"• ROE: **{f'{roe:.1f}%' if roe else 'N/A'}** (Target ≥ 14%) | Qtr Profit Growth: **{f'{qtr_gr:+.1f}%' if qtr_gr else 'N/A'}**")

        # --- F. SECTION 4: UNIFIED FUNDAMENTALS & FINANCIAL CHARTS (NO DUPLICATION) ---
        st.markdown(f"### 🏛️ Company Fundamentals & Financial Statements — `{info.get('sector', 'Indian Equity')}` ({info.get('industry', 'NSE/BSE')})")

        f1, f2, f3, f4, f5, f6 = st.columns(6)
        f1.metric("Market Cap", f"₹{mcap_cr:,.0f} Cr" if mcap_cr else "N/A")
        f2.metric("Trailing / Fwd P/E", f"{pe:.1f}x / {fwd_pe:.1f}x" if (pe and fwd_pe) else (f"{pe:.1f}x" if pe else "N/A"))
        f3.metric("P/B & Book Value", f"{pb:.2f}x (₹{bv:,.0f})" if (pb and bv) else "N/A")
        f4.metric("ROE (%)", f"{roe:.1f}%" if roe is not None else "N/A")
        f5.metric("Operating / Net Margin", f"{op_margin:.1f}% / {net_margin:.1f}%" if (op_margin and net_margin) else "N/A")
        f6.metric("Debt to Equity", f"{de:.1f}%" if de is not None else "N/A")

        f7, f8, f9, f10, f11, f12 = st.columns(6)
        f7.metric("52-Week High", f"₹{high_52:,.2f}" if high_52 else "N/A")
        f8.metric("52-Week Low", f"₹{low_52:,.2f}" if low_52 else "N/A")
        f9.metric("50-Day & 200-Day DMA", f"₹{dma_50:,.0f} / ₹{dma_200:,.0f}")
        f10.metric("Qtr Profit Growth", f"{qtr_gr:+.1f}%" if qtr_gr is not None else "N/A")
        f11.metric("Dividend Yield", f"{div_y:.2f}%" if div_y is not None else "N/A")
        f12.metric("Promoter Holding", f"{prom_pct:.1f}%" if prom_pct is not None else "N/A")

        ch1, ch2 = st.columns(2)
        with ch1:
            if not q_inc.empty:
                q_df = q_inc.T.sort_index()
                rev_c = next((c for c in ['Total Revenue', 'Operating Revenue'] if c in q_df.columns), None)
                net_c = next((c for c in ['Net Income', 'Net Income Common Stockholders'] if c in q_df.columns), None)
                if rev_c and net_c:
                    dates = [d.strftime('%b %Y') if hasattr(d, 'strftime') else str(d) for d in q_df.index]
                    fig_q = go.Figure()
                    fig_q.add_trace(go.Bar(x=dates, y=q_df[rev_c] / 1e7, name="Quarterly Revenue (₹ Cr)", marker_color="#38bdf8"))
                    fig_q.add_trace(go.Bar(x=dates, y=q_df[net_c] / 1e7, name="Net Profit (₹ Cr)", marker_color="#10b981"))
                    fig_q.update_layout(title="📊 Quarterly Revenue vs. Net Profit (₹ Crores)", height=320, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_q, use_container_width=True)

        with ch2:
            if not bal_sheet.empty:
                b_df = bal_sheet.T.sort_index()
                as_c = next((c for c in ['Total Assets'] if c in b_df.columns), None)
                eq_c = next((c for c in ['Stockholders Equity', 'Total Equity Gross Minority Interest'] if c in b_df.columns), None)
                dt_c = next((c for c in ['Total Debt', 'Long Term Debt'] if c in b_df.columns), None)
                if as_c:
                    b_dates = [d.strftime('%Y') if hasattr(d, 'strftime') else str(d) for d in b_df.index]
                    fig_b = go.Figure()
                    fig_b.add_trace(go.Bar(x=b_dates, y=b_df[as_c] / 1e7, name="Total Assets (₹ Cr)", marker_color="#6366f1"))
                    if eq_c: fig_b.add_trace(go.Bar(x=b_dates, y=b_df[eq_c] / 1e7, name="Net Worth (₹ Cr)", marker_color="#10b981"))
                    if dt_c: fig_b.add_trace(go.Bar(x=b_dates, y=b_df[dt_c] / 1e7, name="Total Debt (₹ Cr)", marker_color="#ef4444"))
                    fig_b.update_layout(title="🏦 Annual Balance Sheet: Assets, Equity & Debt (₹ Crores)", height=320, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_b, use_container_width=True)

render_360_stock_dashboard()

# ==============================================================================
# 4. OPTIONAL PEER COMPARISON FOR SELECTED INDEX (NO RAW TEXT BOX CLUTTER)
# ==============================================================================
with st.expander(f"🔍 Compare All Peer Stocks in Selected Index [{selected_group}] (Volume Flow + Fundamentals + Strategy)", expanded=False):
    peer_list = available_symbols[:30] if selected_group.startswith("🌐") else available_symbols
    st.caption(f"One-click unified scanner for **{len(peer_list)} stocks** in **{selected_group}**. Combines Volume Inflow/Outflow, Valuation Ratios, and Strategy Badges in a single table.")

    if st.button(f"🚀 Scan All {len(peer_list)} Stocks in {selected_group.split('(')[0].strip()}", type="primary"):
        rows = []
        prog = st.progress(0)
        for i, s in enumerate(peer_list):
            try:
                t_s = s if s.startswith("^") else f"{s}{suffix}"
                tk = yf.Ticker(t_s)
                h = tk.history(period="3mo", interval="1d")
                inf = tk.info if not s.startswith("^") else {}
                if not h.empty and len(h) >= 20:
                    c = h['Close'].iloc[-1]
                    prev_c = h['Close'].iloc[-2]
                    chg_p = (c - prev_c) / prev_c * 100
                    sma50 = h['Close'].rolling(50).mean().iloc[-1] if len(h) >= 50 else c
                    h52 = inf.get("fiftyTwoWeekHigh") or h['High'].max()
                    off_52 = (h52 - c) / h52 * 100 if h52 else 0

                    rec = h.tail(5)
                    hl = (rec['High'] - rec['Low']).replace(0, np.nan)
                    br = ((rec['Close'] - rec['Low']) / hl).fillna(0.5).clip(0, 1)
                    in_v = (rec['Volume'] * br).sum()
                    tot_v = rec['Volume'].sum()
                    in_p = (in_v / tot_v * 100) if tot_v > 0 else 50.0
                    net_cr_5d = (((rec['Volume'] * br) - (rec['Volume'] * (1 - br))) * ((rec['High'] + rec['Low'] + rec['Close']) / 3)).sum() / 1e7

                    pb_v = inf.get("priceToBook")
                    pe_v = inf.get("trailingPE")
                    roe_v = (inf.get("returnOnEquity") * 100) if inf.get("returnOnEquity") else None

                    tags = []
                    if pb_v and pb_v <= 3.5: tags.append("💎 Value")
                    if off_52 <= 15 and c >= sma50: tags.append("🚀 Breakout")
                    if off_52 <= 15 and c >= sma50 and (roe_v and roe_v >= 14): tags.append("🏆 CANSLIM")

                    rows.append({
                        "Symbol": s,
                        "Company": MASTER_STOCK_DICT.get(s, s)[:26],
                        "Price (₹)": round(c, 2),
                        "1D Chg (%)": round(chg_p, 2),
                        "🟢 5D Buy Inflow (%)": round(in_p, 1),
                        "5D Net Flow (₹ Cr)": round(net_cr_5d, 2),
                        "P/E": round(pe_v, 1) if pe_v else None,
                        "P/B": round(pb_v, 2) if pb_v else None,
                        "ROE (%)": round(roe_v, 1) if roe_v else None,
                        "Off 52W High (%)": round(off_52, 1),
                        "Strategy Signals": " | ".join(tags) if tags else "⚪ Neutral"
                    })
            except Exception:
                pass
            prog.progress((i + 1) / len(peer_list))
        prog.empty()
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values(by="5D Net Flow (₹ Cr)", ascending=False), use_container_width=True, hide_index=True)
