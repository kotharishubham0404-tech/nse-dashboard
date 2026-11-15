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
            <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-
