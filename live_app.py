import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import urllib.parse
import gzip
import io

st.set_page_config(page_title="NSE & BSE 360° Upstox Pro Terminal", layout="wide")

# ==============================================================================
# 0. PRE-CONFIGURED UPSTOX EXTENDED API TOKEN
# ==============================================================================
DEFAULT_UPSTOX_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ."
    "eyJzdWIiOiI3SkI1NEwiLCJqdGkiOiI2YWY5OTU5ZTk0MGI1ZTc2ZDBhZTkzYjgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlzRXh0ZW5kZWQiOnRydWUsImlhdCI6MTc5NDc0MTY2MiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxODI2MzE2MDAwfQ."
    "S_UNBE3KkJIFXH7kNbsSK1Sae6MBh9ad-vp8sgnrxKA"
)

# ==============================================================================
# 1. VERIFIED NSE & BSE CATALOG + BUILT-IN UPSTOX INSTRUMENT KEY DIRECTORY
# ==============================================================================

COMPANY_NAMES = {
    "RELIANCE": "Reliance Industries Ltd", "TCS": "Tata Consultancy Services Ltd",
    "HDFCBANK": "HDFC Bank Ltd", "ICICIBANK": "ICICI Bank Ltd", "SBIN": "State Bank of India",
    "INFY": "Infosys Ltd", "BHARTIARTL": "Bharti Airtel Ltd", "ITC": "ITC Ltd",
    "LT": "Larsen & Toubro Ltd", "TATAMOTORS": "Tata Motors Ltd", "BAJFINANCE": "Bajaj Finance Ltd",
    "HAL": "Hindustan Aeronautics Ltd", "BEL": "Bharat Electronics Ltd", "TRENT": "Trent Ltd",
    "SUNPHARMA": "Sun Pharmaceutical Industries", "MARUTI": "Maruti Suzuki India Ltd",
    "M&M": "Mahindra & Mahindra Ltd", "NTPC": "NTPC Ltd", "POWERGRID": "Power Grid Corp of India",
    "ONGC": "Oil & Natural Gas Corp", "COALINDIA": "Coal India Ltd", "TATASTEEL": "Tata Steel Ltd",
    "JSWSTEEL": "JSW Steel Ltd", "HINDALCO": "Hindalco Industries Ltd", "VEDL": "Vedanta Ltd",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd", "AXISBANK": "Axis Bank Ltd", "INDUSINDBK": "IndusInd Bank Ltd",
    "BANKBARODA": "Bank of Baroda", "PNB": "Punjab National Bank", "CANBK": "Canara Bank",
    "FEDERALBNK": "Federal Bank Ltd", "IDFCFIRSTB": "IDFC First Bank Ltd", "AUBANK": "AU Small Finance Bank",
    "BANDHANBNK": "Bandhan Bank Ltd", "UNIONBANK": "Union Bank of India", "INDIANB": "Indian Bank",
    "HCLTECH": "HCL Technologies Ltd", "WIPRO": "Wipro Ltd", "TECHM": "Tech Mahindra Ltd",
    "LTIM": "LTIMindtree Ltd", "PERSISTENT": "Persistent Systems Ltd", "COFORGE": "Coforge Ltd",
    "KPITTECH": "KPIT Technologies Ltd", "TATAELXSI": "Tata Elxsi Ltd", "DIXON": "Dixon Technologies",
    "ULTRACEMCO": "UltraTech Cement Ltd", "AMBUJACEM": "Ambuja Cements Ltd", "GRASIM": "Grasim Industries",
    "TITAN": "Titan Company Ltd", "ASIANPAINT": "Asian Paints Ltd", "HINDUNILVR": "Hindustan Unilever Ltd",
    "NESTLEIND": "Nestle India Ltd", "BRITANNIA": "Britannia Industries", "TATACONSUM": "Tata Consumer Products",
    "VBL": "Varun Beverages Ltd", "ZOMATO": "Zomato Ltd", "DMART": "Avenue Supermarts (DMart)",
    "DLF": "DLF Ltd", "LODHA": "Macrotech Developers (Lodha)", "GODREJPROP": "Godrej Properties Ltd",
    "OBEROIRLTY": "Oberoi Realty Ltd", "PRESTIGE": "Prestige Estates Projects",
    "ADANIENT": "Adani Enterprises Ltd", "ADANIPORTS": "Adani Ports & SEZ Ltd", "ADANIGREEN": "Adani Green Energy",
    "ADANIPOWER": "Adani Power Ltd", "TATAPOWER": "Tata Power Co Ltd", "JSWENERGY": "JSW Energy Ltd",
    "PFC": "Power Finance Corporation", "RECLTD": "REC Ltd", "IRFC": "Indian Railway Finance Corp",
    "RVNL": "Rail Vikas Nigam Ltd", "MAZDOCK": "Mazagon Dock Shipbuilders", "BDL": "Bharat Dynamics Ltd",
    "COCHINSHIP": "Cochin Shipyard Ltd", "BHEL": "Bharat Heavy Electricals", "SIEMENS": "Siemens Ltd",
    "ABB": "ABB India Ltd", "CGPOWER": "CG Power & Industrial Solutions", "CUMMINSIND": "Cummins India Ltd",
    "POLYCAB": "Polycab India Ltd", "SUZLON": "Suzlon Energy Ltd", "BAJAJ-AUTO": "Bajaj Auto Ltd",
    "EICHERMOT": "Eicher Motors Ltd", "HEROMOTOCO": "Hero MotoCorp Ltd", "TVSMOTOR": "TVS Motor Company",
    "ASHOKLEY": "Ashok Leyland Ltd", "BHARATFORG": "Bharat Forge Ltd", "MRF": "MRF Ltd",
    "APOLLOHOSP": "Apollo Hospitals Enterprise", "MAXHEALTH": "Max Healthcare Institute",
    "DRREDDY": "Dr. Reddy's Laboratories", "CIPLA": "Cipla Ltd", "DIVISLAB": "Divi's Laboratories",
    "LUPIN": "Lupin Ltd", "ZYDUSLIFE": "Zydus Lifesciences", "BSE": "BSE Ltd", "MCX": "Multi Commodity Exchange",
    "CDSL": "Central Depository Services", "ANGELONE": "Angel One Ltd", "JIOFIN": "Jio Financial Services",
    "CHOLAFIN": "Cholamandalam Investment", "SHRIRAMFIN": "Shriram Finance Ltd", "BAJAJFINSV": "Bajaj Finserv Ltd",
    "BPCL": "Bharat Petroleum Corp", "IOC": "Indian Oil Corporation", "GAIL": "GAIL (India) Ltd",
    "NMDC": "NMDC Ltd", "SAIL": "Steel Authority of India", "NATIONALUM": "National Aluminium Co",
    "^NSEI": "NSE Nifty 50 Index", "^BSESN": "BSE Sensex 30 Index", "^NSEBANK": "NSE Nifty Bank Index",
    "^CNXIT": "NSE Nifty IT Index", "^CNXPHARMA": "NSE Nifty Pharma Index", "^CNXAUTO": "NSE Nifty Auto Index"
}

CORE_UPSTOX_KEYS = {
    "^NSEI": "NSE_INDEX|Nifty 50", "^BSESN": "BSE_INDEX|SENSEX", "^NSEBANK": "NSE_INDEX|Nifty Bank",
    "^CNXIT": "NSE_INDEX|Nifty IT", "^CNXPHARMA": "NSE_INDEX|Nifty Pharma", "^CNXAUTO": "NSE_INDEX|Nifty Auto",
    "RELIANCE": "NSE_EQ|INE002A01018", "TCS": "NSE_EQ|INE467B01029", "HDFCBANK": "NSE_EQ|INE040A01034",
    "ICICIBANK": "NSE_EQ|INE090A01021", "SBIN": "NSE_EQ|INE062A01020", "INFY": "NSE_EQ|INE009A01021",
    "BHARTIARTL": "NSE_EQ|INE397D01024", "ITC": "NSE_EQ|INE154A01025", "LT": "NSE_EQ|INE018A01030",
    "TATAMOTORS": "NSE_EQ|INE155A01022", "BAJFINANCE": "NSE_EQ|INE296A01024", "HAL": "NSE_EQ|INE066F01020",
    "BEL": "NSE_EQ|INE263A01024", "TRENT": "NSE_EQ|INE849A01020", "SUNPHARMA": "NSE_EQ|INE044A01036",
    "MARUTI": "NSE_EQ|INE585B01010", "M&M": "NSE_EQ|INE101A01026", "NTPC": "NSE_EQ|INE733E01010",
    "POWERGRID": "NSE_EQ|INE752E01010", "ONGC": "NSE_EQ|INE213A01029", "COALINDIA": "NSE_EQ|INE522F01014",
    "TATASTEEL": "NSE_EQ|INE081A01020", "JSWSTEEL": "NSE_EQ|INE019A01038", "HINDALCO": "NSE_EQ|INE038A01020",
    "VEDL": "NSE_EQ|INE205A01025", "KOTAKBANK": "NSE_EQ|INE237A01028", "AXISBANK": "NSE_EQ|INE238A01034",
    "INDUSINDBK": "NSE_EQ|INE095A01012", "BANKBARODA": "NSE_EQ|INE028A01039", "PNB": "NSE_EQ|INE160A01022",
    "CANBK": "NSE_EQ|INE476A01022", "HCLTECH": "NSE_EQ|INE860A01027", "WIPRO": "NSE_EQ|INE075A01022",
    "TECHM": "NSE_EQ|INE669C01036", "LTIM": "NSE_EQ|INE214T01019", "ULTRACEMCO": "NSE_EQ|INE481G01011",
    "TITAN": "NSE_EQ|INE280A01028", "ASIANPAINT": "NSE_EQ|INE021A01026", "HINDUNILVR": "NSE_EQ|INE030A01027",
    "NESTLEIND": "NSE_EQ|INE239A01024", "BRITANNIA": "NSE_EQ|INE216A01030", "ADANIENT": "NSE_EQ|INE423A01024",
    "ADANIPORTS": "NSE_EQ|INE742F01042", "BAJAJ-AUTO": "NSE_EQ|INE917I01010", "EICHERMOT": "NSE_EQ|INE066A01021",
    "HEROMOTOCO": "NSE_EQ|INE158A01026", "APOLLOHOSP": "NSE_EQ|INE437A01024", "DRREDDY": "NSE_EQ|INE089A01031",
    "CIPLA": "NSE_EQ|INE059A01026", "DIVISLAB": "NSE_EQ|INE361B01024", "BPCL": "NSE_EQ|INE029A01011",
    "SHRIRAMFIN": "NSE_EQ|INE721A01013", "BAJAJFINSV": "NSE_EQ|INE918I01026", "DLF": "NSE_EQ|INE271C01023",
    "PFC": "NSE_EQ|INE134E01011", "RECLTD": "NSE_EQ|INE020B01018", "IRFC": "NSE_EQ|INE053F01010",
    "RVNL": "NSE_EQ|INE415G01027", "BHEL": "NSE_EQ|INE257A01026", "SUZLON": "NSE_EQ|INE040H01021",
    "ZOMATO": "NSE_EQ|INE758T01015", "JIOFIN": "NSE_EQ|INE758E01017", "BSE": "NSE_EQ|INE118H01025"
}

INDEX_GROUPS = {
    "🇮🇳 NSE NIFTY 50 (50 Stocks)": ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "SBIN", "INFY", "BHARTIARTL", "ITC", "LT", "TATAMOTORS", "BAJFINANCE", "SUNPHARMA", "MARUTI", "M&M", "NTPC", "POWERGRID", "ONGC", "COALINDIA", "TATASTEEL", "JSWSTEEL", "HINDALCO", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "HCLTECH", "WIPRO", "TECHM", "LTIM", "ULTRACEMCO", "GRASIM", "TITAN", "ASIANPAINT", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "TATACONSUM", "ADANIENT", "ADANIPORTS", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "APOLLOHOSP", "DRREDDY", "CIPLA", "DIVISLAB", "BEL", "BPCL", "TRENT", "SHRIRAMFIN", "BAJAJFINSV"],
    "🇮🇳 BSE SENSEX 30 (30 Stocks)": ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "ITC", "LT", "HCLTECH", "AXISBANK", "BAJFINANCE", "MARUTI", "SUNPHARMA", "TATAMOTORS", "KOTAKBANK", "ULTRACEMCO", "NTPC", "M&M", "TITAN", "POWERGRID", "ASIANPAINT", "BAJAJFINSV", "NESTLEIND", "INDUSINDBK", "ADANIPORTS", "TATASTEEL", "JSWSTEEL", "TECHM", "HINDUNILVR"],
    "🏦 NIFTY BANK (12 Stocks)": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "BANKBARODA", "PNB", "FEDERALBNK", "IDFCFIRSTB", "AUBANK", "BANDHANBNK"],
    "🏛️ NIFTY PSU BANK (10 Stocks)": ["SBIN", "BANKBARODA", "PNB", "CANBK", "UNIONBANK", "INDIANB", "IOB", "CENTRALBK", "UCOBANK", "MAHABANK"],
    "💻 NIFTY IT (12 Stocks)": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "PERSISTENT", "COFORGE", "KPITTECH", "TATAELXSI", "MPHASIS", "LTTS"],
    "🚗 NIFTY AUTO (12 Stocks)": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY", "BHARATFORG", "MRF", "MOTHERSON", "BOSCHLTD"],
    "💊 NIFTY PHARMA & HEALTHCARE (10 Stocks)": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP", "MAXHEALTH", "LUPIN", "ZYDUSLIFE", "AUROPHARMA", "ALKEM"],
    "🛒 NIFTY FMCG & CONSUMER (10 Stocks)": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "TATACONSUM", "VBL", "DMART", "ZOMATO", "GODREJCP", "DABUR"],
    "⛏️ NIFTY METAL (10 Stocks)": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA", "NMDC", "SAIL", "NATIONALUM", "JINDALSTEL", "HINDZINC"],
    "⚡ NIFTY ENERGY, OIL & POWER (14 Stocks)": ["RELIANCE", "NTPC", "ONGC", "POWERGRID", "COALINDIA", "TATAPOWER", "ADANIGREEN", "ADANIPOWER", "JSWENERGY", "BPCL", "IOC", "GAIL", "PFC", "RECLTD"],
    "🛡️ NIFTY DEFENSE, RAILWAYS & CAPEX (14 Stocks)": ["HAL", "BEL", "MAZDOCK", "BDL", "COCHINSHIP", "IRFC", "RVNL", "BHEL", "SIEMENS", "ABB", "CGPOWER", "CUMMINSIND", "POLYCAB", "SUZLON"],
    "🏢 NIFTY REALTY & INFRA (10 Stocks)": ["DLF", "LODHA", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "LT", "ULTRACEMCO", "AMBUJACEM", "GRASIM", "IRB"],
    "💰 NIFTY FIN SERVICES & CAPITAL MARKETS (12 Stocks)": ["BAJFINANCE", "BAJAJFINSV", "JIOFIN", "CHOLAFIN", "SHRIRAMFIN", "PFC", "RECLTD", "BSE", "MCX", "CDSL", "ANGELONE", "MUTHOOTFIN"],
    "🌐 All Listed Stocks & Indices (Full Catalog)": list(COMPANY_NAMES.keys()),
    "📊 Benchmark Indices Only": ["^NSEI", "^BSESN", "^NSEBANK", "^CNXIT", "^CNXPHARMA", "^CNXAUTO"]
}

# ==============================================================================
# 2. UPSTOX API v2 ENGINE (PRE-LOADED EXTENDED TOKEN + WEEKEND INTRADAY RESAMPLER)
# ==============================================================================

@st.cache_data(ttl=86400, show_spinner=False)
def load_upstox_instrument_map():
    inst_map = dict(CORE_UPSTOX_KEYS)
    try:
        url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
                df_inst = pd.read_csv(gz)
            eq_df = df_inst[df_inst['instrument_type'].isin(['EQ', 'BE', 'INDEX'])]
            for _, row in eq_df.iterrows():
                sym = str(row.get('tradingsymbol', '')).strip().upper()
                ikey = str(row.get('instrument_key', '')).strip()
                if sym and ikey:
                    inst_map[sym] = ikey
    except Exception:
        pass
    return inst_map

UPSTOX_INST_MAP = load_upstox_instrument_map()

def clean_token(raw_tok):
    if not raw_tok:
        return ""
    t = raw_tok.strip()
    if t.lower().startswith("bearer "):
        t = t[7:].strip()
    return t

def fetch_upstox_live_quote(instrument_key, access_token):
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    url = "https://api.upstox.com/v2/market-quote/quotes"
    try:
        r = requests.get(url, headers=headers, params={"instrument_key": instrument_key}, timeout=6)
        if r.status_code == 200:
            data = r.json().get("data", {})
            if data:
                return list(data.values())[0], None
        elif r.status_code == 401:
            return None, "Token expired or invalid (401 Unauthorized)."
    except Exception:
        pass
    return None, None

def fetch_upstox_candles(instrument_key, period, interval, access_token):
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    encoded_key = urllib.parse.quote(instrument_key, safe="")
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        if interval in ["1m", "5m", "15m"]:
            up_int = "1minute" if interval in ["1m", "5m"] else "30minute"
            url = f"https://api.upstox.com/v2/historical-candle/intraday/{encoded_key}/{up_int}"
            r = requests.get(url, headers=headers, timeout=8)
            candles = r.json().get("data", {}).get("candles", []) if r.status_code == 200 else []

            # Weekend / After-Hours Fallback: Pull last 7 days of 1minute or 30minute candles from Upstox Historical API
            if not candles:
                from_d = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                url_h = f"https://api.upstox.com/v2/historical-candle/{encoded_key}/{up_int}/{today_str}/{from_d}"
                r_h = requests.get(url_h, headers=headers, timeout=8)
                candles = r_h.json().get("data", {}).get("candles", []) if r_h.status_code == 200 else []
        else:
            days_map = {"3mo": 90, "6mo": 180, "1y": 365, "5y": 1825}
            days_back = days_map.get(period, 180)
            from_d = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            up_int = "week" if interval == "1wk" else "day"
            url = f"https://api.upstox.com/v2/historical-candle/{encoded_key}/{up_int}/{today_str}/{from_d}"
            r = requests.get(url, headers=headers, timeout=8)
            candles = r.json().get("data", {}).get("candles", []) if r.status_code == 200 else []

        if candles:
            df = pd.DataFrame(candles, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume", "OI"])
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            df = df.sort_values("Timestamp").set_index("Timestamp")
            if interval == "5m" and len(df) > 25:
                df = df.resample("5min").agg({
                    "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum", "OI": "last"
                }).dropna(subset=["Open", "Close"])
            return df
    except Exception:
        pass
    return pd.DataFrame()

# ==============================================================================
# 3. SELF-HEALING FALLBACK & FUNDAMENTAL ENGINE
# ==============================================================================

@st.cache_data(ttl=45, show_spinner=False)
def fetch_yf_price_history(yf_ticker, period, interval):
    tk = yf.Ticker(yf_ticker)
    df = pd.DataFrame()
    used_fallback = False
    try:
        df = tk.history(period=period, interval=interval, auto_adjust=False)
    except Exception:
        df = pd.DataFrame()

    if df is None or df.empty or len(df) < 5:
        try:
            df = tk.history(period="6mo", interval="1d", auto_adjust=False)
            used_fallback = True
        except Exception:
            df = pd.DataFrame()
    return df, used_fallback

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_360_fundamentals(yf_ticker):
    tk = yf.Ticker(yf_ticker)
    hist_1y = pd.DataFrame()
    try:
        hist_1y = tk.history(period="1y", interval="1d", auto_adjust=False)
    except Exception:
        pass

    if yf_ticker.startswith("^"):
        return hist_1y, {}, pd.DataFrame(), pd.DataFrame()

    info = {}
    try:
        info = tk.info or {}
    except Exception:
        info = {}

    fast = {}
    try:
        f_obj = tk.fast_info
        fast = {
            "marketCap": getattr(f_obj, "market_cap", None),
            "fiftyTwoWeekHigh": getattr(f_obj, "year_high", None),
            "fiftyTwoWeekLow": getattr(f_obj, "year_low", None),
            "shares": getattr(f_obj, "shares", None),
            "lastPrice": getattr(f_obj, "last_price", None)
        }
    except Exception:
        pass

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

    cmp_val = fast.get("lastPrice") or (hist_1y['Close'].iloc[-1] if not hist_1y.empty else None)
    shares = info.get("sharesOutstanding") or fast.get("shares")
    mcap = info.get("marketCap") or fast.get("marketCap") or ((cmp_val * shares) if (cmp_val and shares) else None)
    high_52 = info.get("fiftyTwoWeekHigh") or fast.get("fiftyTwoWeekHigh") or (hist_1y['High'].max() if not hist_1y.empty else None)
    low_52 = info.get("fiftyTwoWeekLow") or fast.get("fiftyTwoWeekLow") or (hist_1y['Low'].min() if not hist_1y.empty else None)

    stmt_equity, stmt_debt, stmt_net_inc, stmt_rev = None, None, None, None
    if not bal_sheet.empty:
        b_df = bal_sheet.T.sort_index()
        eq_col = next((c for c in ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity'] if c in b_df.columns), None)
        dt_col = next((c for c in ['Total Debt', 'Long Term Debt', 'Net Debt'] if c in b_df.columns), None)
        if eq_col and not b_df[eq_col].dropna().empty:
            stmt_equity = float(b_df[eq_col].dropna().iloc[-1])
        if dt_col and not b_df[dt_col].dropna().empty:
            stmt_debt = float(b_df[dt_col].dropna().iloc[-1])

    if not a_inc.empty:
        a_df = a_inc.T.sort_index()
        ni_col = next((c for c in ['Net Income', 'Net Income Common Stockholders'] if c in a_df.columns), None)
        rv_col = next((c for c in ['Total Revenue', 'Operating Revenue'] if c in a_df.columns), None)
        if ni_col and not a_df[ni_col].dropna().empty:
            stmt_net_inc = float(a_df[ni_col].dropna().iloc[-1])
        if rv_col and not a_df[rv_col].dropna().empty:
            stmt_rev = float(a_df[rv_col].dropna().iloc[-1])

    bv = info.get("bookValue") or ((stmt_equity / shares) if (stmt_equity and shares and shares > 0) else None)
    pb = info.get("priceToBook") or ((cmp_val / bv) if (cmp_val and bv and bv > 0) else None)
    pe = info.get("trailingPE") or ((mcap / stmt_net_inc) if (mcap and stmt_net_inc and stmt_net_inc > 0) else None)
    roe = info.get("returnOnEquity")
    if roe is None and stmt_net_inc and stmt_equity and stmt_equity > 0:
        roe = stmt_net_inc / stmt_equity
    net_margin = info.get("profitMargins")
    if net_margin is None and stmt_net_inc and stmt_rev and stmt_rev > 0:
        net_margin = stmt_net_inc / stmt_rev
    de = info.get("debtToEquity")
    if de is None and stmt_debt is not None and stmt_equity and stmt_equity > 0:
        de = (stmt_debt / stmt_equity) * 100.0

    qtr_gr = info.get("earningsQuarterlyGrowth")
    if qtr_gr is None and not q_inc.empty:
        q_df = q_inc.T.sort_index()
        ni_c = next((c for c in ['Net Income', 'Net Income Common Stockholders'] if c in q_df.columns), None)
        if ni_c:
            s_ni = q_df[ni_c].dropna()
            if len(s_ni) >= 2 and s_ni.iloc[-2] != 0:
                qtr_gr = (s_ni.iloc[-1] - s_ni.iloc[-2]) / abs(s_ni.iloc[-2])

    clean_fund = {
        "marketCap_Cr": (mcap / 1e7) if mcap else None,
        "pe": pe,
        "pb": pb,
        "bv": bv,
        "roe_pct": (roe * 100) if roe is not None else None,
        "net_margin_pct": (net_margin * 100) if net_margin is not None else None,
        "de_pct": de,
        "high_52": high_52,
        "low_52": low_52,
        "qtr_gr_pct": (qtr_gr * 100) if qtr_gr is not None else None,
        "div_yield_pct": (info.get("dividendYield") * 100) if info.get("dividendYield") is not None else None,
        "promoter_pct": (info.get("heldPercentInsiders") * 100) if info.get("heldPercentInsiders") is not None else None,
        "sector": info.get("sector", "Indian Listed Equity")
    }
    return hist_1y, clean_fund, q_inc, bal_sheet

# ==============================================================================
# 4. SIDEBAR: PRE-CONNECTED UPSTOX TOKEN & STOCK CONTROLS
# ==============================================================================

secret_token = ""
try:
    secret_token = st.secrets.get("UPSTOX_ACCESS_TOKEN", "")
except Exception:
    secret_token = ""

if "upstox_token" not in st.session_state:
    st.session_state["upstox_token"] = clean_token(secret_token) or DEFAULT_UPSTOX_TOKEN

st.sidebar.header("⚡ Upstox Live API Feed")
st.sidebar.success("🟢 Upstox Extended Token Active (Client: 7JB54L)")

with st.sidebar.expander("🔑 Change or View Upstox Token", expanded=False):
    user_tok = st.text_input(
        "Upstox Access / Extended Token:",
        value=st.session_state["upstox_token"],
        type="password"
    )
    if clean_token(user_tok) != st.session_state["upstox_token"]:
        st.session_state["upstox_token"] = clean_token(user_tok)

active_token = st.session_state["upstox_token"]

st.sidebar.markdown("---")
st.sidebar.header("🇮🇳 Stock Search & Controls")

exchange_choice = st.sidebar.radio("1. Exchange:", ["NSE India (.NS)", "BSE India (.BO)"], horizontal=True)
suffix = ".NS" if "NSE" in exchange_choice else ".BO"

selected_group = st.sidebar.selectbox("2. Filter by Index / Sector:", options=list(INDEX_GROUPS.keys()), index=0)
available_symbols = INDEX_GROUPS[selected_group]
formatted_options = [f"{sym} | {COMPANY_NAMES.get(sym, sym)}" for sym in available_symbols]

selected_stock_option = st.sidebar.selectbox(
    f"3. Select or Type Stock Name ({len(formatted_options)} in list):",
    options=formatted_options,
    index=0,
    key=f"stk_sel_{selected_group}"
)

raw_symbol = selected_stock_option.split(" | ")[0].strip()
company_name = selected_stock_option.split(" | ")[1].strip()
yf_ticker = raw_symbol if raw_symbol.startswith("^") else f"{raw_symbol}{suffix}"
upstox_inst_key = UPSTOX_INST_MAP.get(raw_symbol)

timeframe_label = st.sidebar.selectbox(
    "4. Chart Timeframe:",
    [
        "Intraday Live (1m Candles)",
        "Intraday Live (5m Candles)",
        "Intraday Live (15m / 30m Candles)",
        "Swing (3 Months - Daily)",
        "Positional (6 Months - Daily)",
        "Long Term (1 Year - Daily)",
        "Multi-Year (5 Years - Weekly)"
    ],
    index=1
)

tf_map = {
    "Intraday Live (1m Candles)": ("1d", "1m"),
    "Intraday Live (5m Candles)": ("5d", "5m"),
    "Intraday Live (15m / 30m Candles)": ("5d", "15m"),
    "Swing (3 Months - Daily)": ("3mo", "1d"),
    "Positional (6 Months - Daily)": ("6mo", "1d"),
    "Long Term (1 Year - Daily)": ("1y", "1d"),
    "Multi-Year (5 Years - Weekly)": ("5y", "1wk")
}
period, interval = tf_map[timeframe_label]

overlays = st.sidebar.multiselect(
    "5. Chart Overlays:",
    ["Moving Averages (20, 50, 200)", "Bollinger Bands (20, 2)", "Cumulative Volume Delta (CVD)", "RSI & Money Flow (MFI)"],
    default=["Moving Averages (20, 50, 200)", "Cumulative Volume Delta (CVD)", "RSI & Money Flow (MFI)"]
)

refresh_rate = st.sidebar.slider("6. Auto-Refresh (Seconds):", 5, 120, 15)

# ==============================================================================
# 5. MAIN 360° DASHBOARD (UPSTOX LIVE ORDER BOOK + CANDLES + FUNDAMENTALS)
# ==============================================================================
st.title(f"🇮🇳 {company_name} ({raw_symbol})")

@st.fragment(run_every=f"{refresh_rate}s")
def render_hybrid_terminal():
    up_quote = None
    up_err = None
    df = pd.DataFrame()
    used_fallback = False
    data_source_badge = "Standard Market Feed"

    # --- 1. FETCH FROM UPSTOX API v2 USING EMBEDDED TOKEN ---
    if active_token and upstox_inst_key:
        up_quote, up_err = fetch_upstox_live_quote(upstox_inst_key, active_token)
        df = fetch_upstox_candles(upstox_inst_key, period, interval, active_token)
        if not df.empty or up_quote:
            data_source_badge = f"⚡ Upstox API v2 ({upstox_inst_key})"
        elif up_err:
            st.warning(f"⚠️ Upstox API Notice: {up_err}")

    # --- 2. AUTOMATIC FALLBACK IF UPSTOX CANDLES EMPTY ---
    if df.empty:
        df, used_fallback = fetch_yf_price_history(yf_ticker, period, interval)

    hist_1y, fund, q_inc, bal_sheet = fetch_360_fundamentals(yf_ticker)

    if df is None or df.empty:
        st.error(f"Market data unavailable for {raw_symbol}. Check symbol or market connection.")
        return

    df = df.dropna(subset=['Open', 'High', 'Low', 'Close']).copy()
    if df['Volume'].sum() == 0:
        df['Volume'] = ((df['High'] - df['Low']).abs() * 1000).clip(lower=100).round(0)

    # --- 3. VOLUME INFLOW & OUTFLOW CALCULATIONS ---
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

    # --- 4. TECHNICAL INDICATORS ---
    df['SMA_20'] = df['Close'].rolling(20, min_periods=1).mean()
    df['SMA_50'] = df['Close'].rolling(50, min_periods=1).mean()
    df['SMA_200'] = df['Close'].rolling(200, min_periods=1).mean()

    std_20 = df['Close'].rolling(20, min_periods=2).std().fillna(0)
    df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
    df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
    df['RSI'] = (100 - (100 / (1 + (gain / loss.replace(0, np.nan))))).fillna(50)

    raw_mf = df['Typical_Price'] * df['Volume']
    pos_mf = raw_mf.where(df['Typical_Price'] >= df['Typical_Price'].shift(1), 0).rolling(14, min_periods=1).sum()
    neg_mf = raw_mf.where(df['Typical_Price'] < df['Typical_Price'].shift(1), 0).rolling(14, min_periods=1).sum()
    df['MFI'] = (100 - (100 / (1 + (pos_mf / neg_mf.replace(0, np.nan))))).fillna(50)

    # --- 5. LIVE SCOREBOARD ---
    latest = float(up_quote.get("last_price", df['Close'].iloc[-1])) if up_quote else float(df['Close'].iloc[-1])
    prev = float(df['Close'].iloc[-2]) if len(df) > 1 else float(df['Open'].iloc[0])
    net_chg = float(up_quote.get("net_change", latest - prev)) if up_quote else (latest - prev)
    pct = (net_chg / (latest - net_chg) * 100) if (latest - net_chg) != 0 else 0.0

    tot_vol = float(df['Volume'].sum())
    in_vol = float(df['Buy_Vol'].sum())
    out_vol = float(df['Sell_Vol'].sum())
    net_vol = in_vol - out_vol
    in_pct = (in_vol / tot_vol * 100) if tot_vol > 0 else 50.0
    out_pct = 100.0 - in_pct

    in_cr = float(df['Inflow_Cr'].sum())
    out_cr = float(df['Outflow_Cr'].sum())
    net_cr = in_cr - out_cr
    rsi_val = float(df['RSI'].iloc[-1])
    mfi_val = float(df['MFI'].iloc[-1])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Live Price (₹)", f"₹{latest:,.2f}", f"{net_chg:+.2f} ({pct:+.2f}%)")
    c2.metric("🟢 Buyer Volume Inflow", f"{int(in_vol):,}", f"₹{in_cr:,.2f} Cr ({in_pct:.1f}%)")
    c3.metric("🔴 Seller Volume Outflow", f"{int(out_vol):,}", f"-₹{out_cr:,.2f} Cr ({out_pct:.1f}%)", delta_color="inverse")
    c4.metric("⚡ Net Volume Flow", f"{int(net_vol):+,}", f"Net ₹{net_cr:+,.2f} Cr")
    c5.metric("RSI (14) / MFI (14)", f"{rsi_val:.1f} / {mfi_val:.1f}", "🟢 Accumulation" if net_vol >= 0 else "🔴 Distribution", delta_color="off")

    st.markdown(
        f"""
        <div style="background:#1e293b; padding:9px 14px; border-radius:8px; margin-bottom:12px; border:1px solid #334155;">
            <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-bottom:4px;">
                <span style="color:#10b981;">🟢 CANDLE BUY INFLOW: {in_pct:.1f}% ({int(in_vol):,} | ₹{in_cr:,.2f} Cr)</span>
                <span style="color:#94a3b8;">Source: {data_source_badge} | Updated: {datetime.now().strftime('%H:%M:%S')}</span>
                <span style="color:#ef4444;">🔴 CANDLE SELL OUTFLOW: {out_pct:.1f}% ({int(out_vol):,} | ₹{out_cr:,.2f} Cr)</span>
            </div>
            <div style="width:100%; height:10px; background:#ef4444; border-radius:5px; overflow:hidden;">
                <div style="width:{in_pct:.1f}%; height:100%; background:#10b981;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- 6. EXCLUSIVE UPSTOX LIVE LEVEL-2 ORDER BOOK & VWAP PANEL ---
    if up_quote:
        tbq = int(up_quote.get("total_buy_quantity", 0) or 0)
        tsq = int(up_quote.get("total_sell_quantity", 0) or 0)
        vwap = float(up_quote.get("average_price", 0) or 0)
        oi = int(up_quote.get("oi", 0) or 0)
        lower_c = up_quote.get("lower_circuit_limit")
        upper_c = up_quote.get("upper_circuit_limit")
        ob_tot = tbq + tsq
        tbq_pct = (tbq / ob_tot * 100) if ob_tot > 0 else 50.0

        with st.container(border=True):
            st.markdown("#### ⚡ Upstox Live Exchange Order Book & Level-2 Market Depth")
            u1, u2, u3, u4, u5 = st.columns(5)
            u1.metric("VWAP (Avg Trade Price)", f"₹{vwap:,.2f}" if vwap else "N/A", "Above VWAP (Bullish)" if (vwap and latest >= vwap) else "Below VWAP")
            u2.metric("Pending Buy Orders (TBQ)", f"{tbq:,}", f"{tbq_pct:.1f}% of Order Book")
            u3.metric("Pending Sell Orders (TSQ)", f"{tsq:,}", f"{100-tbq_pct:.1f}% of Order Book", delta_color="inverse")
            u4.metric("Circuit Limits (L / U)", f"₹{lower_c} - ₹{upper_c}" if (lower_c and upper_c) else "N/A")
            u5.metric("Open Interest (OI)", f"{oi:,}" if oi else "Equity Spot")

            depth = up_quote.get("depth", {})
            buy_depth = depth.get("buy", [])
            sell_depth = depth.get("sell", [])
            if buy_depth and sell_depth:
                with st.expander("📖 View Live Top 5 Bid vs. Ask Market Depth Table (Level 2)", expanded=True):
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        st.markdown("**🟢 Top 5 Buyers (Bid Orders)**")
                        st.dataframe(pd.DataFrame(buy_depth)[["orders", "quantity", "price"]].rename(
                            columns={"orders": "Orders", "quantity": "Bid Qty", "price": "Bid Price (₹)"}
                        ), use_container_width=True, hide_index=True)
                    with d_col2:
                        st.markdown("**🔴 Top 5 Sellers (Ask Orders)**")
                        st.dataframe(pd.DataFrame(sell_depth)[["price", "quantity", "orders"]].rename(
                            columns={"price": "Ask Price (₹)", "quantity": "Ask Qty", "orders": "Orders"}
                        ), use_container_width=True, hide_index=True)

    # --- 7. GAP-FREE INTERACTIVE MULTI-PANE CHART ---
    if interval in ["1m", "5m", "15m"] and not used_fallback:
        x_labels = [ts.strftime('%d %b %H:%M') for ts in df.index]
    else:
        x_labels = [ts.strftime('%d %b %Y') for ts in df.index]

    show_sma = "Moving Averages (20, 50, 200)" in overlays
    show_bb = "Bollinger Bands (20, 2)" in overlays
    show_cvd = "Cumulative Volume Delta (CVD)" in overlays
    show_osc = "RSI & Money Flow (MFI)" in overlays

    titles = ["Price Action & Moving Averages (₹)", "Volume Inflow (Green) vs. Outflow (Red)"]
    heights = [0.52, 0.18]
    if show_cvd:
        titles.append("Cumulative Volume Delta (CVD - Net Institutional Flow)")
        heights.append(0.15)
    if show_osc:
        titles.append("Momentum: RSI (14) & Money Flow Index (MFI 14)")
        heights.append(0.15)

    heights = [h / sum(heights) for h in heights]
    fig = make_subplots(rows=len(heights), cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights, subplot_titles=titles)

    fig.add_trace(go.Candlestick(x=x_labels, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="OHLC (₹)"), row=1, col=1)
    if show_sma:
        fig.add_trace(go.Scatter(x=x_labels, y=df['SMA_20'], line=dict(color='#f59e0b', width=1.5), name="20 SMA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=x_labels, y=df['SMA_50'], line=dict(color='#38bdf8', width=1.5), name="50 SMA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=x_labels, y=df['SMA_200'], line=dict(color='#ec4899', width=1.8, dash='dot'), name="200 SMA"), row=1, col=1)
    if show_bb:
        fig.add_trace(go.Scatter(x=x_labels, y=df['BB_Upper'], line=dict(color='rgba(148,163,184,0.4)', width=1), name="BB Upper"), row=1, col=1)
        fig.add_trace(go.Scatter(x=x_labels, y=df['BB_Lower'], line=dict(color='rgba(148,163,184,0.4)', width=1), fill='tonexty', fillcolor='rgba(148,163,184,0.07)', name="BB Lower"), row=1, col=1)

    fig.add_trace(go.Bar(x=x_labels, y=df['Buy_Vol'], marker_color='#10b981', name="Inflow Vol (Buy)"), row=2, col=1)
    fig.add_trace(go.Bar(x=x_labels, y=-df['Sell_Vol'], marker_color='#ef4444', name="Outflow Vol (Sell)"), row=2, col=1)

    r_idx = 3
    if show_cvd:
        cvd_col = '#10b981' if df['CVD'].iloc[-1] >= 0 else '#ef4444'
        fig.add_trace(go.Scatter(
            x=x_labels, y=df['CVD'], mode='lines', line=dict(color=cvd_col, width=2),
            fill='tozeroy', fillcolor='rgba(16,185,129,0.12)' if df['CVD'].iloc[-1] >= 0 else 'rgba(239,68,68,0.12)',
            name="CVD"
        ), row=r_idx, col=1)
        r_idx += 1

    if show_osc:
        fig.add_trace(go.Scatter(x=x_labels, y=df['RSI'], line=dict(color='#a855f7', width=1.5), name="RSI (14)"), row=r_idx, col=1)
        fig.add_trace(go.Scatter(x=x_labels, y=df['MFI'], line=dict(color='#22d3ee', width=1.5, dash='dot'), name="MFI (14)"), row=r_idx, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=r_idx, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#10b981", row=r_idx, col=1)

    fig.update_xaxes(type='category', nticks=12)
    fig.update_layout(height=700, template="plotly_dark", barmode="relative", xaxis_rangeslider_visible=False, margin=dict(l=15, r=15, t=25, b=10), uirevision=f"{yf_ticker}_{timeframe_label}")
    st.plotly_chart(fig, use_container_width=True)

    # --- 8. STRATEGY SCORECARD & FUNDAMENTALS ---
    if not raw_symbol.startswith("^"):
        base_df = hist_1y if not hist_1y.empty else df
        d_close = latest
        dma_50 = float(base_df['Close'].rolling(50, min_periods=1).mean().iloc[-1])
        dma_200 = float(base_df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        high_52 = fund.get("high_52") or float(base_df['High'].max())
        low_52 = fund.get("low_52") or float(base_df['Low'].min())
        dist_52h = ((high_52 - d_close) / high_52 * 100) if high_52 else 0.0

        mcap_cr = fund.get("marketCap_Cr")
        pe = fund.get("pe")
        pb = fund.get("pb")
        bv = fund.get("bv")
        roe = fund.get("roe_pct")
        net_m = fund.get("net_margin_pct")
        de = fund.get("de_pct")
        qtr_gr = fund.get("qtr_gr_pct")
        div_y = fund.get("div_yield_pct")
        prom = fund.get("promoter_pct")

        pass_value = (pb is not None and pb <= 3.5) and (pe is None or pe <= 28)
        pass_breakout = (dist_52h <= 15.0) and (d_close >= dma_50) and (in_pct >= 50.0)
        pass_canslim = (d_close >= dma_50) and (d_close >= dma_200) and (dist_52h <= 15.0) and (roe is None or roe >= 14.0)

        st.markdown("### 🎯 Strategy Scorecard & Qualification")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            with st.container(border=True):
                st.markdown(f"**💎 Low P/B Value Strategy:** {'🟢 **QUALIFIES**' if pass_value else '⚪ **Watchlist**'}")
                st.caption(f"• P/B Ratio: **{f'{pb:.2f}x' if pb else 'N/A'}** | Book Value: **{f'₹{bv:,.1f}' if bv else 'N/A'}** | P/E: **{f'{pe:.1f}x' if pe else 'N/A'}**")
        with sc2:
            with st.container(border=True):
                st.markdown(f"**🚀 52-Week High Breakout:** {'🟢 **QUALIFIES**' if pass_breakout else '⚪ **Watchlist**'}")
                st.caption(f"• Off 52W High (₹{high_52:,.1f}): **{dist_52h:.1f}%** | Above 50 DMA (₹{dma_50:,.1f}): **{'Yes' if d_close >= dma_50 else
