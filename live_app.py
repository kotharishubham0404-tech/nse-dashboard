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
import math
import io

st.set_page_config(page_title="NSE & BSE 360° Techno-Fundamental & Power Terminal", layout="wide")

# ==============================================================================
# 0. PRE-CONFIGURED UPSTOX EXTENDED API TOKEN
# ==============================================================================
DEFAULT_UPSTOX_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ."
    "eyJzdWIiOiI3SkI1NEwiLCJqdGkiOiI2YWY5OTU5ZTk0MGI1ZTc2ZDBhZTkzYjgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlzRXh0ZW5kZWQiOnRydWUsImlhdCI6MTc5NDc0MTY2MiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxODI2MzE2MDAwfQ."
    "S_UNBE3KkJIFXH7kNbsSK1Sae6MBh9ad-vp8sgnrxKA"
)

# ==============================================================================
# 1. EXPANDED BSE & NSE STOCK DIRECTORY + ISIN MAP (WORKS FOR BOTH NSE_EQ & BSE_EQ)
# ==============================================================================

COMPANY_NAMES = {
    # --- BSE & NSE BENCHMARK INDICES ---
    "^BSESN": "BSE SENSEX 30 Index", "BSE-BANK": "BSE BANKEX Index",
    "BSE-100": "BSE 100 Index", "BSE-200": "BSE 200 Index", "BSE-500": "BSE 500 Index",
    "BSE-MIDCAP": "BSE MidCap Index", "BSE-SMLCAP": "BSE SmallCap Index",
    "BSE-IPO": "BSE IPO Index", "BSE-SMEIPO": "BSE SME IPO Index",
    "^NSEI": "NSE Nifty 50 Index", "^NSEBANK": "NSE Nifty Bank Index",
    "^CNXIT": "NSE Nifty IT Index", "^CNXPHARMA": "NSE Nifty Pharma Index",
    "^CNXAUTO": "NSE Nifty Auto Index", "^CNXFMCG": "NSE Nifty FMCG Index",
    "^CNXMETAL": "NSE Nifty Metal Index", "^CNXPSUBANK": "NSE Nifty PSU Bank Index",
    "^CNXREALTY": "NSE Nifty Realty Index", "^CNXENERGY": "NSE Nifty Energy Index",
    # --- LARGECAP, MIDCAP & SMALLCAP EQUITIES (BSE & NSE) ---
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
    "BANKINDIA": "Bank of India", "MAHABANK": "Bank of Maharashtra", "IOB": "Indian Overseas Bank",
    "CENTRALBK": "Central Bank of India", "UCOBANK": "UCO Bank", "RBLBANK": "RBL Bank Ltd",
    "KARURVYSYA": "Karur Vysya Bank Ltd", "CITYUNIONBK": "City Union Bank Ltd", "IDBI": "IDBI Bank Ltd",
    "YESBANK": "Yes Bank Ltd", "HCLTECH": "HCL Technologies Ltd", "WIPRO": "Wipro Ltd",
    "TECHM": "Tech Mahindra Ltd", "LTIM": "LTIMindtree Ltd", "PERSISTENT": "Persistent Systems Ltd",
    "COFORGE": "Coforge Ltd", "MPHASIS": "Mphasis Ltd", "LTTS": "L&T Technology Services",
    "KPITTECH": "KPIT Technologies Ltd", "TATAELXSI": "Tata Elxsi Ltd", "OFSS": "Oracle Financial Services",
    "CYIENT": "Cyient Ltd", "ZENSARTECH": "Zensar Technologies", "SONATSOFTW": "Sonata Software Ltd",
    "BIRLASOFT": "Birlasoft Ltd", "LATENTVIEW": "Latent View Analytics", "NETWEB": "Netweb Technologies",
    "DIXON": "Dixon Technologies", "KAYNES": "Kaynes Technology India", "SYRMA": "Syrma SGS Technology",
    "AMBER": "Amber Enterprises India", "PGEL": "PG Electroplast Ltd", "ULTRACEMCO": "UltraTech Cement Ltd",
    "AMBUJACEM": "Ambuja Cements Ltd", "GRASIM": "Grasim Industries", "SHREECEM": "Shree Cement Ltd",
    "ACC": "ACC Ltd", "DALBHARAT": "Dalmia Bharat Ltd", "RAMCOCEM": "The Ramco Cements Ltd",
    "TITAN": "Titan Company Ltd", "ASIANPAINT": "Asian Paints Ltd", "BERGEPAINT": "Berger Paints India",
    "PIDILITIND": "Pidilite Industries Ltd", "HINDUNILVR": "Hindustan Unilever Ltd",
    "NESTLEIND": "Nestle India Ltd", "BRITANNIA": "Britannia Industries", "TATACONSUM": "Tata Consumer Products",
    "VBL": "Varun Beverages Ltd", "DABUR": "Dabur India Ltd", "MARICO": "Marico Ltd",
    "GODREJCP": "Godrej Consumer Products", "COLPAL": "Colgate-Palmolive (India)", "UBL": "United Breweries Ltd",
    "UNITDSPR": "United Spirits Ltd", "RADICO": "Radico Khaitan Ltd", "PATANJALI": "Patanjali Foods Ltd",
    "EMAMILTD": "Emami Ltd", "JYOTHYLAB": "Jyothy Labs Ltd", "BIKAJI": "Bikaji Foods International",
    "ZOMATO": "Zomato Ltd (Eternal)", "DMART": "Avenue Supermarts (DMart)", "NYKAA": "FSN E-Commerce (Nykaa)",
    "DELHIVERY": "Delhivery Ltd", "PAYTM": "One 97 Communications (Paytm)", "POLICYBZR": "PB Fintech (Policybazaar)",
    "NAUKRI": "Info Edge (India) Ltd", "INDHOTEL": "Indian Hotels Co (Taj)", "EIHOTEL": "EIH Ltd (Oberoi)",
    "LEMONTREE": "Lemon Tree Hotels Ltd", "CHALET": "Chalet Hotels Ltd", "IRCTC": "IRCTC Ltd",
    "DLF": "DLF Ltd", "LODHA": "Macrotech Developers (Lodha)", "GODREJPROP": "Godrej Properties Ltd",
    "OBEROIRLTY": "Oberoi Realty Ltd", "PRESTIGE": "Prestige Estates Projects", "PHOENIXLTD": "The Phoenix Mills Ltd",
    "BRIGADE": "Brigade Enterprises Ltd", "SOBHA": "Sobha Ltd", "SUNTECK": "Sunteck Realty Ltd",
    "MAHLIFE": "Mahindra Lifespace Developers", "ANANTRAJ": "Anant Raj Ltd", "NBCC": "NBCC (India) Ltd",
    "HUDCO": "HUDCO Ltd", "IRB": "IRB Infrastructure Developers", "GMRINFRA": "GMR Airports Infrastructure",
    "NCC": "NCC Ltd", "KNRCON": "KNR Constructions Ltd", "PNCINFRA": "PNC Infratech Ltd",
    "ADANIENT": "Adani Enterprises Ltd", "ADANIPORTS": "Adani Ports & SEZ Ltd", "ADANIGREEN": "Adani Green Energy",
    "ADANIPOWER": "Adani Power Ltd", "ADANIENSOL": "Adani Energy Solutions", "ATGL": "Adani Total Gas Ltd",
    "TATAPOWER": "Tata Power Co Ltd", "JSWENERGY": "JSW Energy Ltd", "TORNTPOWER": "Torrent Power Ltd",
    "CESC": "CESC Ltd", "NHPC": "NHPC Ltd", "SJVN": "SJVN Ltd", "NLCINDIA": "NLC India Ltd",
    "SUZLON": "Suzlon Energy Ltd", "INOXWIND": "Inox Wind Ltd", "IREDA": "Indian Renewable Energy Dev (IREDA)",
    "PFC": "Power Finance Corporation", "RECLTD": "REC Ltd", "IRFC": "Indian Railway Finance Corp",
    "RVNL": "Rail Vikas Nigam Ltd", "IRCON": "Ircon International Ltd", "RAILTEL": "RailTel Corp of India",
    "RITES": "RITES Ltd", "TITAGARH": "Titagarh Rail Systems", "JWL": "Jupiter Wagons Ltd",
    "TEXRAIL": "Texmaco Rail & Engineering", "BEML": "BEML Ltd", "MAZDOCK": "Mazagon Dock Shipbuilders",
    "BDL": "Bharat Dynamics Ltd", "COCHINSHIP": "Cochin Shipyard Ltd", "GRSE": "Garden Reach Shipbuilders",
    "SOLARINDS": "Solar Industries India", "DATAPATTNS": "Data Patterns (India)", "ASTRAMICRO": "Astra Microwave Products",
    "PARAS": "Paras Defence & Space Tech", "MTARTECH": "MTAR Technologies Ltd", "AZAD": "Azad Engineering Ltd",
    "BHEL": "Bharat Heavy Electricals", "SIEMENS": "Siemens Ltd", "ABB": "ABB India Ltd",
    "CGPOWER": "CG Power & Industrial Solutions", "CUMMINSIND": "Cummins India Ltd", "THERMAX": "Thermax Ltd",
    "HITACHI": "Hitachi Energy India", "GEVT&D": "GE Vernova T&D India", "TRITURBINE": "Triveni Turbine Ltd",
    "APARINDS": "Apar Industries Ltd", "POLYCAB": "Polycab India Ltd", "KEI": "KEI Industries Ltd",
    "FINCABLES": "Finolex Cables Ltd", "HAVELLS": "Havells India Ltd", "VOLTAS": "Voltas Ltd",
    "BLUESTARCO": "Blue Star Ltd", "CROMPTON": "Crompton Greaves Consumer", "SUPREMEIND": "Supreme Industries Ltd",
    "ASTRAL": "Astral Ltd", "ELECON": "Elecon Engineering Co", "ACE": "Action Construction Equipment",
    "PRAJIND": "Praj Industries Ltd", "IONEXCHANG": "Ion Exchange (India)", "VA TECH": "VA Tech Wabag Ltd",
    "BAJAJ-AUTO": "Bajaj Auto Ltd", "EICHERMOT": "Eicher Motors Ltd", "HEROMOTOCO": "Hero MotoCorp Ltd",
    "TVSMOTOR": "TVS Motor Company", "ASHOKLEY": "Ashok Leyland Ltd", "ESCORTS": "Escorts Kubota Ltd",
    "OLECTRA": "Olectra Greentech Ltd", "JBMA": "JBM Auto Ltd", "BHARATFORG": "Bharat Forge Ltd",
    "MOTHERSON": "Samvardhana Motherson Intl", "BOSCHLTD": "Bosch Ltd", "MRF": "MRF Ltd",
    "BALKRISIND": "Balkrishna Industries", "APOLLOTYRE": "Apollo Tyres Ltd", "CEATLTD": "CEAT Ltd",
    "EXIDEIND": "Exide Industries Ltd", "ARE&M": "Amara Raja Energy & Mobility", "SONACOMS": "Sona BLW Precision",
    "TIINDIA": "Tube Investments of India", "ENDURANCE": "Endurance Technologies", "UNO MINDA": "Uno Minda Ltd",
    "APOLLOHOSP": "Apollo Hospitals Enterprise", "MAXHEALTH": "Max Healthcare Institute", "FORTIS": "Fortis Healthcare Ltd",
    "KIMS": "Krishna Institute of Medical", "NARAYANA": "Narayana Hrudayalaya", "ASTERDM": "Aster DM Healthcare",
    "LALPATHLAB": "Dr. Lal PathLabs Ltd", "METROPOLIS": "Metropolis Healthcare", "DRREDDY": "Dr. Reddy's Laboratories",
    "CIPLA": "Cipla Ltd", "DIVISLAB": "Divi's Laboratories", "LUPIN": "Lupin Ltd",
    "ZYDUSLIFE": "Zydus Lifesciences", "TORNTPHARM": "Torrent Pharmaceuticals", "AUROPHARMA": "Aurobindo Pharma Ltd",
    "ALKEM": "Alkem Laboratories", "MANKIND": "Mankind Pharma Ltd", "BIOCON": "Biocon Ltd",
    "LAURUSLABS": "Laurus Labs Ltd", "GLENMARK": "Glenmark Pharmaceuticals", "IPCALAB": "IPCA Laboratories",
    "SYNGENE": "Syngene International", "NATCOPHARM": "Natco Pharma Ltd", "AJANTPHARM": "Ajanta Pharma Ltd",
    "GRANULES": "Granules India Ltd", "JBCHEPHARM": "J.B. Chemicals & Pharma", "PIRAMALPHR": "Piramal Pharma Ltd",
    "BSE": "BSE Ltd", "MCX": "Multi Commodity Exchange", "CDSL": "Central Depository Services",
    "ANGELONE": "Angel One Ltd", "CAMS": "Computer Age Management (CAMS)", "KFINTECH": "KFin Technologies Ltd",
    "MOTILALOFS": "Motilal Oswal Financial", "IIFL": "IIFL Finance Ltd", "MANAPPURAM": "Manappuram Finance Ltd",
    "MUTHOOTFIN": "Muthoot Finance Ltd", "JIOFIN": "Jio Financial Services", "CHOLAFIN": "Cholamandalam Investment",
    "SHRIRAMFIN": "Shriram Finance Ltd", "BAJAJFINSV": "Bajaj Finserv Ltd", "BAJAJHLDNG": "Bajaj Holdings & Investment",
    "SBILIFE": "SBI Life Insurance", "HDFCLIFE": "HDFC Life Insurance", "ICICIPRULI": "ICICI Prudential Life",
    "ICICIGI": "ICICI Lombard General Ins", "LICI": "Life Insurance Corp (LIC)", "SBICARD": "SBI Cards & Payment",
    "LICHSGFIN": "LIC Housing Finance", "PNBHOUSING": "PNB Housing Finance", "POONAWALLA": "Poonawalla Fincorp",
    "SUNDARMFIN": "Sundaram Finance Ltd", "MFSL": "Max Financial Services", "UTIAMC": "UTI Asset Management",
    "HDFCAMC": "HDFC Asset Management", "NAM-INDIA": "Nippon Life India AMC", "BPCL": "Bharat Petroleum Corp",
    "IOC": "Indian Oil Corporation", "HPCL": "Hindustan Petroleum Corp", "GAIL": "GAIL (India) Ltd",
    "PETRONET": "Petronet LNG Ltd", "OIL": "Oil India Ltd", "IGL": "Indraprastha Gas Ltd",
    "MGL": "Mahanagar Gas Ltd", "GUJGASLTD": "Gujarat Gas Ltd", "GSPL": "Gujarat State Petronet",
    "NMDC": "NMDC Ltd", "SAIL": "Steel Authority of India", "NATIONALUM": "National Aluminium Co",
    "JINDALSTEL": "Jindal Steel & Power", "JSL": "Jindal Stainless Ltd", "APLAPOLLO": "APL Apollo Tubes Ltd",
    "HINDZINC": "Hindustan Zinc Ltd", "HINDCOPPER": "Hindustan Copper Ltd", "MOIL": "MOIL Ltd",
    "RATNAMANI": "Ratnamani Metals & Tubes", "WELCORP": "Welspun Corp Ltd", "VEDL": "Vedanta Ltd",
    "PIIND": "PI Industries Ltd", "SRF": "SRF Ltd", "COROMANDEL": "Coromandel International",
    "UPL": "UPL Ltd", "DEEPAKNTR": "Deepak Nitrite Ltd", "ATUL": "Atul Ltd",
    "NAVINFLUOR": "Navin Fluorine International", "CLEAN": "Clean Science & Technology", "AARTIIND": "Aarti Industries Ltd",
    "TATACHEM": "Tata Chemicals Ltd", "GNFC": "Gujarat Narmada Valley Fert", "CHAMBLFERT": "Chambal Fertilisers",
    "PAGEIND": "Page Industries Ltd", "ABFRL": "Aditya Birla Fashion & Retail", "RAYMOND": "Raymond Ltd",
    "MANYAVAR": "Vedant Fashions (Manyavar)", "TRIDENT": "Trident Ltd", "WELSPUNLIV": "Welspun Living Ltd"
}

# ISIN Directory used to build both NSE_EQ|<ISIN> and BSE_EQ|<ISIN> Upstox keys
STOCK_ISIN_MAP = {
    "RELIANCE": "INE002A01018", "TCS": "INE467B01029", "HDFCBANK": "INE040A01034",
    "ICICIBANK": "INE090A01021", "SBIN": "INE062A01020", "INFY": "INE009A01021",
    "BHARTIARTL": "INE397D01024", "ITC": "INE154A01025", "LT": "INE018A01030",
    "TATAMOTORS": "INE155A01022", "BAJFINANCE": "INE296A01024", "HAL": "INE066F01020",
    "BEL": "INE263A01024", "TRENT": "INE849A01020", "SUNPHARMA": "INE044A01036",
    "MARUTI": "INE585B01010", "M&M": "INE101A01026", "NTPC": "INE733E01010",
    "POWERGRID": "INE752E01010", "ONGC": "INE213A01029", "COALINDIA": "INE522F01014",
    "TATASTEEL": "INE081A01020", "JSWSTEEL": "INE019A01038", "HINDALCO": "INE038A01020",
    "VEDL": "INE205A01025", "KOTAKBANK": "INE237A01028", "AXISBANK": "INE238A01034",
    "INDUSINDBK": "INE095A01012", "BANKBARODA": "INE028A01039", "PNB": "INE160A01022",
    "CANBK": "INE476A01022", "FEDERALBNK": "INE171A01029", "IDFCFIRSTB": "INE092T01019",
    "AUBANK": "INE949L01017", "BANDHANBNK": "INE545U01014", "UNIONBANK": "INE692A01016",
    "INDIANB": "INE562A01011", "BANKINDIA": "INE084A01016", "MAHABANK": "INE457A01014",
    "YESBANK": "INE528G01035", "HCLTECH": "INE860A01027", "WIPRO": "INE075A01022",
    "TECHM": "INE669C01036", "LTIM": "INE214T01019", "PERSISTENT": "INE262H01021",
    "COFORGE": "INE591G01017", "MPHASIS": "INE356A01018", "LTTS": "INE010V01017",
    "KPITTECH": "INE04I401011", "TATAELXSI": "INE670A01012", "DIXON": "INE935N01020",
    "ULTRACEMCO": "INE481G01011", "AMBUJACEM": "INE079A01024", "GRASIM": "INE047A01021",
    "SHREECEM": "INE070A01015", "ACC": "INE012A01025", "TITAN": "INE280A01028",
    "ASIANPAINT": "INE021A01026", "PIDILITIND": "INE318A01026", "HINDUNILVR": "INE030A01027",
    "NESTLEIND": "INE239A01024", "BRITANNIA": "INE216A01030", "TATACONSUM": "INE192A01025",
    "VBL": "INE200M01021", "DABUR": "INE016A01026", "MARICO": "INE196A01026",
    "GODREJCP": "INE102D01028", "COLPAL": "INE259A01022", "ZOMATO": "INE758T01015",
    "DMART": "INE192R01011", "NAUKRI": "INE663F01024", "INDHOTEL": "INE053A01029",
    "IRCTC": "INE335Y01020", "DLF": "INE271C01023", "LODHA": "INE670K01029",
    "GODREJPROP": "INE484J01027", "OBEROIRLTY": "INE093I01010", "PRESTIGE": "INE811K01011",
    "PHOENIXLTD": "INE211B01039", "ADANIENT": "INE423A01024", "ADANIPORTS": "INE742F01042",
    "ADANIGREEN": "INE364U01010", "ADANIPOWER": "INE814H01011", "TATAPOWER": "INE245A01021",
    "JSWENERGY": "INE121E01018", "NHPC": "INE848E01016", "SUZLON": "INE040H01021",
    "PFC": "INE134E01011", "RECLTD": "INE020B01018", "IRFC": "INE053F01010",
    "RVNL": "INE415G01027", "MAZDOCK": "INE249Z01012", "BDL": "INE171Z01026",
    "COCHINSHIP": "INE704P01025", "BHEL": "INE257A01026", "SIEMENS": "INE003A01024",
    "ABB": "INE117A01022", "CGPOWER": "INE067A01029", "CUMMINSIND": "INE298A01020",
    "POLYCAB": "INE455K01017", "HAVELLS": "INE176B01034", "VOLTAS": "INE226A01021",
    "SUPREMEIND": "INE195A01028", "ASTRAL": "INE006I01046", "BAJAJ-AUTO": "INE917I01010",
    "EICHERMOT": "INE066A01021", "HEROMOTOCO": "INE158A01026", "TVSMOTOR": "INE494B01023",
    "ASHOKLEY": "INE208A01029", "BHARATFORG": "INE465A01025", "MOTHERSON": "INE775A01035",
    "BOSCHLTD": "INE323A01026", "MRF": "INE883A01011", "APOLLOHOSP": "INE437A01024",
    "MAXHEALTH": "INE027H01010", "DRREDDY": "INE089A01031", "CIPLA": "INE059A01026",
    "DIVISLAB": "INE361B01024", "LUPIN": "INE326A01037", "ZYDUSLIFE": "INE010B01027",
    "TORNTPHARM": "INE685A01028", "AUROPHARMA": "INE406A01037", "ALKEM": "INE540L01014",
    "MANKIND": "INE634S01028", "BIOCON": "INE376G01013", "LAURUSLABS": "INE947Q01028",
    "BSE": "INE118H01025", "MCX": "INE745G01035", "CDSL": "INE736A01011",
    "ANGELONE": "INE732I01013", "CAMS": "INE596I01012", "MUTHOOTFIN": "INE414G01012",
    "JIOFIN": "INE758E01017", "CHOLAFIN": "INE121A01024", "SHRIRAMFIN": "INE721A01013",
    "BAJAJFINSV": "INE918I01026", "SBILIFE": "INE123W01016", "HDFCLIFE": "INE795G01014",
    "ICICIPRULI": "INE726G01019", "ICICIGI": "INE765G01017", "LICI": "INE0J1Y01017",
    "SBICARD": "INE018E01016", "BPCL": "INE029A01011", "IOC": "INE242A01010",
    "HPCL": "INE094A01015", "GAIL": "INE129A01019", "PETRONET": "INE347G01014",
    "OIL": "INE274J01014", "NMDC": "INE584A01023", "SAIL": "INE114A01011",
    "NATIONALUM": "INE139A01034", "JINDALSTEL": "INE749A01030", "HINDZINC": "INE267A01025"
}

UPSTOX_INDEX_KEYS = {
    "^BSESN": "BSE_INDEX|SENSEX",
    "BSE-BANK": "BSE_INDEX|BANKEX",
    "BSE-100": "BSE_INDEX|BSE100",
    "BSE-200": "BSE_INDEX|BSE200",
    "BSE-500": "BSE_INDEX|BSE500",
    "BSE-MIDCAP": "BSE_INDEX|MIDCAP",
    "BSE-SMLCAP": "BSE_INDEX|SMLCAP",
    "BSE-IPO": "BSE_INDEX|BSEIPO",
    "BSE-SMEIPO": "BSE_INDEX|SMEIPO",
    "^NSEI": "NSE_INDEX|Nifty 50",
    "^NSEBANK": "NSE_INDEX|Nifty Bank",
    "^CNXIT": "NSE_INDEX|Nifty IT",
    "^CNXPHARMA": "NSE_INDEX|Nifty Pharma",
    "^CNXAUTO": "NSE_INDEX|Nifty Auto",
    "^CNXFMCG": "NSE_INDEX|Nifty FMCG",
    "^CNXMETAL": "NSE_INDEX|Nifty Metal",
    "^CNXPSUBANK": "NSE_INDEX|Nifty PSU Bank",
    "^CNXREALTY": "NSE_INDEX|Nifty Realty",
    "^CNXENERGY": "NSE_INDEX|Nifty Energy"
}

YF_INDEX_TICKERS = {
    "^BSESN": "^BSESN",
    "BSE-BANK": "BSE-BANK.BO",
    "BSE-100": "BSE-100.BO",
    "BSE-200": "BSE-200.BO",
    "BSE-500": "BSE-500.BO",
    "BSE-MIDCAP": "BSE-MIDCAP.BO",
    "BSE-SMLCAP": "BSE-SMLCAP.BO",
    "BSE-IPO": "BSE-IPO.BO",
    "BSE-SMEIPO": "BSE-SMEIPO.BO",
    "^NSEI": "^NSEI",
    "^NSEBANK": "^NSEBANK",
    "^CNXIT": "^CNXIT",
    "^CNXPHARMA": "^CNXPHARMA",
    "^CNXAUTO": "^CNXAUTO",
    "^CNXFMCG": "^CNXFMCG",
    "^CNXMETAL": "^CNXMETAL",
    "^CNXPSUBANK": "^CNXPSUBANK",
    "^CNXREALTY": "^CNXREALTY",
    "^CNXENERGY": "^CNXENERGY"
}

BSE_SENSEX_30 = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "ITC", "LT", "HCLTECH",
    "AXISBANK", "BAJFINANCE", "MARUTI", "SUNPHARMA", "TATAMOTORS", "KOTAKBANK", "ULTRACEMCO", "NTPC",
    "M&M", "TITAN", "POWERGRID", "ASIANPAINT", "BAJAJFINSV", "NESTLEIND", "INDUSINDBK", "ADANIPORTS",
    "TATASTEEL", "JSWSTEEL", "TECHM", "HINDUNILVR", "ZOMATO", "BEL", "TRENT"
]

BSE_SENSEX_NEXT_30 = [
    "HAL", "DLF", "ONGC", "COALINDIA", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "APOLLOHOSP", "DRREDDY",
    "CIPLA", "DIVISLAB", "GRASIM", "ADANIENT", "WIPRO", "LTIM", "TATACONSUM", "BRITANNIA", "VBL",
    "PIDILITIND", "SIEMENS", "ABB", "PFC", "RECLTD", "IOC", "BPCL", "GAIL", "HINDALCO", "VEDL",
    "JIOFIN", "CHOLAFIN", "SHRIRAMFIN", "BANKBARODA", "PNB", "CANBK", "TVSMOTOR", "INDHOTEL"
]

BSE_MIDCAP_LEADERS = [
    "DIXON", "POLYCAB", "PERSISTENT", "CUMMINSIND", "CGPOWER", "SUPREMEIND", "ASTRAL", "COFORGE",
    "VOLTAS", "PAGEIND", "PIIND", "FEDERALBNK", "IDFCFIRSTB", "AUBANK", "ASHOKLEY", "BHARATFORG",
    "TIINDIA", "ALKEM", "LUPIN", "AUROPHARMA", "MAXHEALTH", "OBEROIRLTY", "GODREJPROP", "PRESTIGE",
    "PHOENIXLTD", "MRF", "BALKRISIND", "PETRONET", "HPCL", "NMDC", "SAIL", "BHEL", "GMRINFRA",
    "YESBANK", "MPHASIS", "LTTS", "KPITTECH", "TATAELXSI", "MUTHOOTFIN", "SBICARD", "BSE", "MCX",
    "CDSL", "ANGELONE", "SUZLON", "RVNL", "IRFC", "MAZDOCK", "BDL", "COCHINSHIP", "SOLARINDS"
]

BSE_SMALLCAP_MOVERS = [
    "CAMS", "KFINTECH", "KAYNES", "SYRMA", "DATAPATTNS", "NETWEB", "CYIENT", "ZENSARTECH",
    "SONATSOFTW", "BIRLASOFT", "LATENTVIEW", "AMBER", "PGEL", "BLUESTARCO", "CROMPTON",
    "KEI", "FINCABLES", "APARINDS", "THERMAX", "TRITURBINE", "ELECON", "ACE", "PRAJIND",
    "IONEXCHANG", "TITAGARH", "JWL", "TEXRAIL", "IRCON", "RAILTEL", "RITES", "BEML", "GRSE",
    "PARAS", "MTARTECH", "AZAD", "OLECTRA", "JBMA", "SONACOMS", "EXIDEIND", "ARE&M",
    "LALPATHLAB", "FORTIS", "KIMS", "NARAYANA", "ASTERDM", "LAURUSLABS", "GLENMARK",
    "IPCALAB", "NATCOPHARM", "AJANTPHARM", "GRANULES", "JBCHEPHARM", "DEEPAKNTR", "ATUL",
    "NAVINFLUOR", "CLEAN", "AARTIIND", "NBCC", "HUDCO", "IRB", "NCC", "BRIGADE", "SOBHA",
    "ANANTRAJ", "KARURVYSYA", "CITYUNIONBK", "RBLBANK", "MANAPPURAM", "IIFL", "MOTILALOFS"
]

INDEX_GROUPS = {
    "🇮🇳 BSE SENSEX 30 (All 30+ Constituent Leaders)": BSE_SENSEX_30,
    "🇮🇳 BSE SENSEX NEXT 30 (36 LargeCap Stocks)": BSE_SENSEX_NEXT_30,
    "🇮🇳 BSE 100 (Top 100 BSE Large & MidCap Stocks)": list(dict.fromkeys(BSE_SENSEX_30 + BSE_SENSEX_NEXT_30 + BSE_MIDCAP_LEADERS[:34])),
    "🏦 BSE BANKEX (12 Major BSE Banking Stocks)": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "BANKBARODA", "PNB", "CANBK", "FEDERALBNK", "IDFCFIRSTB", "AUBANK"],
    "🚀 BSE MIDCAP INDEX LEADERS (51 Stocks)": BSE_MIDCAP_LEADERS,
    "🔥 BSE SMALLCAP & EXCLUSIVE MOVERS (70 Stocks)": BSE_SMALLCAP_MOVERS,
    "🏭 BSE CAPITAL GOODS, INFRA & ENGINEERING (26 Stocks)": ["LT", "SIEMENS", "ABB", "HAL", "BEL", "BHEL", "CGPOWER", "CUMMINSIND", "THERMAX", "POLYCAB", "KEI", "APARINDS", "HAVELLS", "SUPREMEIND", "ASTRAL", "MAZDOCK", "BDL", "COCHINSHIP", "GRSE", "TITAGARH", "JWL", "BEML", "ELECON", "ACE", "PRAJIND", "IRB"],
    "🏛️ BSE PSU & CPSE BASKET (25 Public Sector Stocks)": ["SBIN", "NTPC", "ONGC", "POWERGRID", "COALINDIA", "BEL", "HAL", "BANKBARODA", "PNB", "CANBK", "UNIONBANK", "INDIANB", "PFC", "RECLTD", "IRFC", "RVNL", "IRCTC", "BHEL", "IOC", "BPCL", "HPCL", "GAIL", "NMDC", "SAIL", "NATIONALUM"],
    "💊 BSE HEALTHCARE & PHARMA (22 Stocks)": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP", "MAXHEALTH", "LUPIN", "ZYDUSLIFE", "TORNTPHARM", "AUROPHARMA", "ALKEM", "MANKIND", "FORTIS", "BIOCON", "LAURUSLABS", "GLENMARK", "IPCALAB", "SYNGENE", "NARAYANA", "KIMS", "NATCOPHARM", "GRANULES"],
    "💻 BSE IT & TECHNOLOGY (18 Stocks)": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "PERSISTENT", "OFSS", "COFORGE", "MPHASIS", "LTTS", "KPITTECH", "TATAELXSI", "CYIENT", "ZENSARTECH", "SONATSOFTW", "BIRLASOFT", "NETWEB"],
    "🚗 BSE AUTO & EV ANCILLARIES (20 Stocks)": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY", "ESCORTS", "BHARATFORG", "MOTHERSON", "BOSCHLTD", "MRF", "BALKRISIND", "APOLLOTYRE", "EXIDEIND", "ARE&M", "SONACOMS", "TIINDIA", "OLECTRA"],
    "⛏️ BSE METALS & MINING (14 Stocks)": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA", "HINDZINC", "JINDALSTEL", "NMDC", "SAIL", "NATIONALUM", "APLAPOLLO", "JSL", "HINDCOPPER", "RATNAMANI"],
    "⚡ BSE OIL, GAS, POWER & ENERGY (20 Stocks)": ["RELIANCE", "NTPC", "ONGC", "POWERGRID", "COALINDIA", "TATAPOWER", "ADANIGREEN", "ADANIPOWER", "JSWENERGY", "TORNTPOWER", "NHPC", "SJVN", "SUZLON", "IOC", "BPCL", "HPCL", "GAIL", "PETRONET", "OIL", "IGL"],
    "🏢 BSE REALTY & CONSTRUCTION (14 Stocks)": ["DLF", "LODHA", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "PHOENIXLTD", "BRIGADE", "SOBHA", "ANANTRAJ", "SUNTECK", "NBCC", "HUDCO", "ULTRACEMCO", "AMBUJACEM"],
    "🛒 BSE FMCG & NEW-AGE CONSUMER (20 Stocks)": ["ITC", "HINDUNILVR", "NESTLEIND", "VBL", "BRITANNIA", "TATACONSUM", "GODREJCP", "DABUR", "MARICO", "COLPAL", "TITAN", "TRENT", "DMART", "ZOMATO", "NYKAA", "INDHOTEL", "UBL", "UNITDSPR", "RADICO", "BIKAJI"],
    "💰 BSE FINANCIAL SERVICES & CAPITAL MARKETS (22 Stocks)": ["BAJFINANCE", "BAJAJFINSV", "JIOFIN", "CHOLAFIN", "SHRIRAMFIN", "PFC", "RECLTD", "MUTHOOTFIN", "SBILIFE", "HDFCLIFE", "ICICIPRULI", "ICICIGI", "LICI", "SBICARD", "BSE", "MCX", "CDSL", "ANGELONE", "CAMS", "KFINTECH", "MOTILALOFS", "POONAWALLA"],
    "🇮🇳 NSE NIFTY 50 (50 Stocks)": ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "SBIN", "INFY", "BHARTIARTL", "ITC", "LT", "TATAMOTORS", "BAJFINANCE", "SUNPHARMA", "MARUTI", "M&M", "NTPC", "POWERGRID", "ONGC", "COALINDIA", "TATASTEEL", "JSWSTEEL", "HINDALCO", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "HCLTECH", "WIPRO", "TECHM", "LTIM", "ULTRACEMCO", "GRASIM", "TITAN", "ASIANPAINT", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "TATACONSUM", "ADANIENT", "ADANIPORTS", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "APOLLOHOSP", "DRREDDY", "CIPLA", "DIVISLAB", "BEL", "BPCL", "TRENT", "SHRIRAMFIN", "BAJAJFINSV"],
    "📊 All BSE & NSE Benchmark Indices (Sensex, Bankex, Nifty 50)": list(UPSTOX_INDEX_KEYS.keys()),
    "🌐 Full Combined BSE & NSE Master Directory (All Stocks)": "ALL_EXCHANGE"
}

# ==============================================================================
# 2. DUAL-EXCHANGE (BSE & NSE) UPSTOX INSTRUMENT DIRECTORY LOADER
# ==============================================================================

@st.cache_data(ttl=86400, show_spinner=False)
def load_dual_exchange_catalog():
    """Downloads both NSE and BSE instrument maps from Upstox so BSE_EQ & NSE_EQ work natively."""
    nse_map = dict(UPSTOX_INDEX_KEYS)
    bse_map = dict(UPSTOX_INDEX_KEYS)
    names_dict = dict(COMPANY_NAMES)

    for sym, isin in STOCK_ISIN_MAP.items():
        nse_map[sym] = f"NSE_EQ|{isin}"
        bse_map[sym] = f"BSE_EQ|{isin}"

    # 1. Load Upstox NSE Instrument Directory
    try:
        r_nse = requests.get("https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz", timeout=10)
        if r_nse.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(r_nse.content)) as gz:
                df_n = pd.read_csv(gz)
            df_n = df_n[df_n['instrument_type'].isin(['EQ', 'BE', 'INDEX'])]
            for _, row in df_n.iterrows():
                sym = str(row.get('tradingsymbol', '')).strip().upper()
                ikey = str(row.get('instrument_key', '')).strip()
                nm = str(row.get('name', sym)).strip()
                if sym and ikey:
                    nse_map[sym] = ikey
                    if sym not in names_dict and nm and nm != 'nan':
                        names_dict[sym] = nm
                    if "|" in ikey and ikey.startswith("NSE_EQ|INE"):
                        bse_map.setdefault(sym, ikey.replace("NSE_EQ|", "BSE_EQ|"))
    except Exception:
        pass

    # 2. Load Upstox BSE Instrument Directory (Captures BSE-exclusive stocks too)
    try:
        r_bse = requests.get("https://assets.upstox.com/market-quote/instruments/exchange/BSE.csv.gz", timeout=10)
        if r_bse.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(r_bse.content)) as gz:
                df_b = pd.read_csv(gz)
            df_b = df_b[df_b['instrument_type'].isin(['A', 'B', 'T', 'X', 'XT', 'Z', 'M', 'EQ', 'INDEX'])]
            for _, row in df_b.iterrows():
                sym = str(row.get('tradingsymbol', '')).strip().upper()
                ikey = str(row.get('instrument_key', '')).strip()
                nm = str(row.get('name', sym)).strip()
                if sym and ikey:
                    bse_map[sym] = ikey
                    if sym not in names_dict and nm and nm != 'nan':
                        names_dict[sym] = nm
    except Exception:
        pass

    return nse_map, bse_map, names_dict

NSE_INST_MAP, BSE_INST_MAP, MASTER_NAMES = load_dual_exchange_catalog()

def resolve_upstox_key(sym, is_bse=False):
    if sym in UPSTOX_INDEX_KEYS:
        return UPSTOX_INDEX_KEYS[sym]
    if is_bse:
        if sym in BSE_INST_MAP:
            return BSE_INST_MAP[sym]
        if sym in NSE_INST_MAP and NSE_INST_MAP[sym].startswith("NSE_EQ|"):
            return NSE_INST_MAP[sym].replace("NSE_EQ|", "BSE_EQ|")
    return NSE_INST_MAP.get(sym) or BSE_INST_MAP.get(sym)

def resolve_yf_ticker(sym, suffix=".NS"):
    if sym in YF_INDEX_TICKERS:
        return YF_INDEX_TICKERS[sym]
    if sym.startswith("^"):
        return sym
    return f"{sym}{suffix}"

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

def calculate_gann_square_of_9(price):
    if not price or price <= 0:
        return {}
    root = math.sqrt(price)
    return {
        "S3 (180°)": round((root - 0.500) ** 2, 2),
        "S2 (90°)": round((root - 0.250) ** 2, 2),
        "S1 (45°)": round((root - 0.125) ** 2, 2),
        "R1 (45°)": round((root + 0.125) ** 2, 2),
        "R2 (90°)": round((root + 0.250) ** 2, 2),
        "R3 (180°)": round((root + 0.500) ** 2, 2),
        "R4 (360°)": round((root + 1.000) ** 2, 2)
    }

def calculate_fibonacci_levels(swing_high, swing_low):
    diff = swing_high - swing_low
    return {
        "Ext 161.8%": round(swing_high + 0.618 * diff, 2),
        "Ext 127.2%": round(swing_high + 0.272 * diff, 2),
        "Swing High (0%)": round(swing_high, 2),
        "Ret 23.6%": round(swing_high - 0.236 * diff, 2),
        "Ret 38.2%": round(swing_high - 0.382 * diff, 2),
        "Ret 50.0%": round(swing_high - 0.500 * diff, 2),
        "Golden 61.8%": round(swing_high - 0.618 * diff, 2),
        "Swing Low (100%)": round(swing_low, 2)
    }

def get_lunar_phase_cycle():
    known_new_moon = datetime(2025, 1, 29, 12, 36)
    synodic_month = 29.530588853
    days_since = (datetime.now() - known_new_moon).total_seconds() / 86400.0
    phase_age = days_since % synodic_month
    if phase_age < 1.85 or phase_age > 27.68:
        return "🌑 New Moon (Cycle Accumulation Window)", round(phase_age, 1)
    elif phase_age < 7.38:
        return "🌒 Waxing Crescent (Early Bullish Expansion)", round(phase_age, 1)
    elif phase_age < 11.07:
        return "🌓 First Quarter (Momentum Acceleration)", round(phase_age, 1)
    elif phase_age < 14.76:
        return "🌔 Waxing Gibbous (Pre-Full Moon Surge)", round(phase_age, 1)
    elif phase_age < 16.61:
        return "🌕 Full Moon (High Volatility / Profit-Booking Pivot)", round(phase_age, 1)
    elif phase_age < 22.14:
        return "🌖 Waning Gibbous (Consolidation / Pullback)", round(phase_age, 1)
    else:
        return "🌘 Waning Crescent (Pre-New Moon Base Building)", round(phase_age, 1)

# ==============================================================================
# 3. COMPREHENSIVE CA-LEVEL 3-STATEMENT & TECHNO-FUNDAMENTAL ENGINE
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

    # If .BO intraday is empty on Yahoo, try .NS fallback for chart continuity
    if (df is None or df.empty) and yf_ticker.endswith(".BO"):
        try:
            df = yf.Ticker(yf_ticker.replace(".BO", ".NS")).history(period=period, interval=interval, auto_adjust=False)
        except Exception:
            pass

    if df is None or df.empty or len(df) < 5:
        try:
            df = tk.history(period="6mo", interval="1d", auto_adjust=False)
            used_fallback = True
        except Exception:
            df = pd.DataFrame()
    return df, used_fallback

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_ca_360_financials(yf_ticker, raw_sym):
    is_idx = (raw_sym in UPSTOX_INDEX_KEYS) or yf_ticker.startswith("^")
    tk = yf.Ticker(yf_ticker)
    hist_1y = pd.DataFrame()
    bench_1y = pd.DataFrame()
    try:
        hist_1y = tk.history(period="1y", interval="1d", auto_adjust=False)
        if hist_1y.empty and yf_ticker.endswith(".BO"):
            hist_1y = yf.Ticker(f"{raw_sym}.NS").history(period="1y", interval="1d", auto_adjust=False)
    except Exception:
        pass
    try:
        bench_sym = "^BSESN" if yf_ticker.endswith(".BO") else "^NSEI"
        bench_1y = yf.Ticker(bench_sym).history(period="1y", interval="1d", auto_adjust=False)
    except Exception:
        pass

    if is_idx:
        return hist_1y, bench_1y, {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    info = {}
    try:
        info = tk.info or {}
        if not info.get("marketCap") and yf_ticker.endswith(".BO"):
            info = yf.Ticker(f"{raw_sym}.NS").info or info
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

    q_inc, a_inc, bal_sheet, cf_stmt = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        q_inc = tk.quarterly_income_stmt
        if q_inc.empty and yf_ticker.endswith(".BO"):
            q_inc = yf.Ticker(f"{raw_sym}.NS").quarterly_income_stmt
    except Exception:
        pass
    try:
        a_inc = tk.income_stmt
        if a_inc.empty and yf_ticker.endswith(".BO"):
            a_inc = yf.Ticker(f"{raw_sym}.NS").income_stmt
    except Exception:
        pass
    try:
        bal_sheet = tk.balance_sheet
        if bal_sheet.empty and yf_ticker.endswith(".BO"):
            bal_sheet = yf.Ticker(f"{raw_sym}.NS").balance_sheet
    except Exception:
        pass
    try:
        cf_stmt = tk.cashflow
        if cf_stmt.empty and yf_ticker.endswith(".BO"):
            cf_stmt = yf.Ticker(f"{raw_sym}.NS").cashflow
    except Exception:
        pass

    cmp_val = fast.get("lastPrice") or (float(hist_1y['Close'].iloc[-1]) if not hist_1y.empty else None)
    shares = info.get("sharesOutstanding") or fast.get("shares")
    mcap = info.get("marketCap") or fast.get("marketCap") or ((cmp_val * shares) if (cmp_val and shares) else None)
    high_52 = info.get("fiftyTwoWeekHigh") or fast.get("fiftyTwoWeekHigh") or (float(hist_1y['High'].max()) if not hist_1y.empty else None)
    low_52 = info.get("fiftyTwoWeekLow") or fast.get("fiftyTwoWeekLow") or (float(hist_1y['Low'].min()) if not hist_1y.empty else None)

    def get_stmt_series(df_stmt, candidates):
        if df_stmt is None or df_stmt.empty:
            return pd.Series(dtype=float)
        t_df = df_stmt.T.sort_index()
        col = next((c for c in candidates if c in t_df.columns), None)
        return t_df[col].dropna().astype(float) if col else pd.Series(dtype=float)

    s_assets = get_stmt_series(bal_sheet, ['Total Assets'])
    s_liab = get_stmt_series(bal_sheet, ['Total Liabilities Net Minority Interest', 'Total Liab'])
    s_equity = get_stmt_series(bal_sheet, ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity'])
    s_ret_earn = get_stmt_series(bal_sheet, ['Retained Earnings'])
    s_debt = get_stmt_series(bal_sheet, ['Total Debt', 'Long Term Debt', 'Net Debt'])
    s_curr_assets = get_stmt_series(bal_sheet, ['Current Assets', 'Total Current Assets'])
    s_curr_liab = get_stmt_series(bal_sheet, ['Current Liabilities', 'Total Current Liabilities'])
    s_inventory = get_stmt_series(bal_sheet, ['Inventory'])
    s_receivables = get_stmt_series(bal_sheet, ['Accounts Receivable', 'Receivables'])
    s_payables = get_stmt_series(bal_sheet, ['Accounts Payable', 'Payables'])
    s_cash = get_stmt_series(bal_sheet, ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments'])
    s_shares_bs = get_stmt_series(bal_sheet, ['Ordinary Shares Number', 'Share Issued'])

    s_rev = get_stmt_series(a_inc, ['Total Revenue', 'Operating Revenue'])
    s_cogs = get_stmt_series(a_inc, ['Cost Of Revenue', 'Reconciled Cost Of Revenue'])
    s_gross_p = get_stmt_series(a_inc, ['Gross Profit'])
    s_ebit = get_stmt_series(a_inc, ['EBIT', 'Operating Income'])
    s_ebitda = get_stmt_series(a_inc, ['EBITDA', 'Normalized EBITDA'])
    s_int_exp = get_stmt_series(a_inc, ['Interest Expense', 'Interest Expense Non Operating'])
    s_net_inc = get_stmt_series(a_inc, ['Net Income', 'Net Income Common Stockholders'])

    s_ocf = get_stmt_series(cf_stmt, ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'])
    s_capex = get_stmt_series(cf_stmt, ['Capital Expenditure', 'Purchase Of PPE'])
    s_fcf = get_stmt_series(cf_stmt, ['Free Cash Flow'])

    tot_assets = float(s_assets.iloc[-1]) if not s_assets.empty else None
    prev_assets = float(s_assets.iloc[-2]) if len(s_assets) >= 2 else tot_assets
    tot_equity = float(s_equity.iloc[-1]) if not s_equity.empty else None
    tot_liab = float(s_liab.iloc[-1]) if not s_liab.empty else ((tot_assets - tot_equity) if (tot_assets and tot_equity) else None)
    ret_earn = float(s_ret_earn.iloc[-1]) if not s_ret_earn.empty else (tot_equity * 0.65 if tot_equity else None)
    tot_debt = float(s_debt.iloc[-1]) if not s_debt.empty else 0.0
    prev_debt = float(s_debt.iloc[-2]) if len(s_debt) >= 2 else tot_debt
    curr_assets = float(s_curr_assets.iloc[-1]) if not s_curr_assets.empty else None
    curr_liab = float(s_curr_liab.iloc[-1]) if not s_curr_liab.empty else None
    inventory = float(s_inventory.iloc[-1]) if not s_inventory.empty else 0.0
    receivables = float(s_receivables.iloc[-1]) if not s_receivables.empty else 0.0
    payables = float(s_payables.iloc[-1]) if not s_payables.empty else 0.0
    cash_val = float(s_cash.iloc[-1]) if not s_cash.empty else 0.0

    rev_val = float(s_rev.iloc[-1]) if not s_rev.empty else None
    prev_rev = float(s_rev.iloc[-2]) if len(s_rev) >= 2 else rev_val
    cogs_val = float(s_cogs.iloc[-1]) if not s_cogs.empty else (rev_val * 0.65 if rev_val else None)
    ebit_val = float(s_ebit.iloc[-1]) if not s_ebit.empty else None
    ebitda_val = float(s_ebitda.iloc[-1]) if not s_ebitda.empty else (info.get("ebitda") or ebit_val)
    int_exp_val = abs(float(s_int_exp.iloc[-1])) if not s_int_exp.empty else None
    net_inc_val = float(s_net_inc.iloc[-1]) if not s_net_inc.empty else None
    prev_net_inc = float(s_net_inc.iloc[-2]) if len(s_net_inc) >= 2 else net_inc_val

    ocf_val = float(s_ocf.iloc[-1]) if not s_ocf.empty else info.get("operatingCashflow")
    capex_val = abs(float(s_capex.iloc[-1])) if not s_capex.empty else 0.0
    fcf_val = float(s_fcf.iloc[-1]) if not s_fcf.empty else ((ocf_val - capex_val) if ocf_val is not None else info.get("freeCashflow"))

    cap_employed = (tot_assets - curr_liab) if (tot_assets and curr_liab and (tot_assets > curr_liab)) else ((tot_equity + tot_debt) if tot_equity else None)
    roce_pct = (ebit_val / cap_employed * 100.0) if (ebit_val and cap_employed and cap_employed > 0) else None

    roe_raw = info.get("returnOnEquity")
    if roe_raw is None and net_inc_val and tot_equity and tot_equity > 0:
        roe_raw = net_inc_val / tot_equity
    roe_pct = (roe_raw * 100.0) if roe_raw is not None else None

    roa_cur = (net_inc_val / tot_assets) if (net_inc_val is not None and tot_assets and tot_assets > 0) else info.get("returnOnAssets")
    roa_prev = (prev_net_inc / prev_assets) if (prev_net_inc is not None and prev_assets and prev_assets > 0) else roa_cur

    net_margin_raw = info.get("profitMargins") or ((net_inc_val / rev_val) if (net_inc_val is not None and rev_val and rev_val > 0) else None)
    net_margin_pct = (net_margin_raw * 100.0) if net_margin_raw is not None else None
    asset_turnover = (rev_val / tot_assets) if (rev_val and tot_assets and tot_assets > 0) else None
    prev_asset_turnover = (prev_rev / prev_assets) if (prev_rev and prev_assets and prev_assets > 0) else asset_turnover
    equity_multiplier = (tot_assets / tot_equity) if (tot_assets and tot_equity and tot_equity > 0) else None

    dso_days = (receivables / rev_val * 365.0) if (receivables and rev_val and rev_val > 0) else None
    dio_days = (inventory / cogs_val * 365.0) if (inventory and cogs_val and cogs_val > 0) else None
    dpo_days = (payables / cogs_val * 365.0) if (payables and cogs_val and cogs_val > 0) else None
    ccc_days = ((dso_days or 0.0) + (dio_days or 0.0) - (dpo_days or 0.0)) if (dso_days is not None or dio_days is not None) else None

    altman_z = None
    if tot_assets and tot_assets > 0 and tot_liab and tot_liab > 0:
        wc = (curr_assets - curr_liab) if (curr_assets is not None and curr_liab is not None) else 0.0
        z_a = wc / tot_assets
        z_b = (ret_earn / tot_assets) if ret_earn is not None else 0.25
        z_c = (ebit_val / tot_assets) if ebit_val is not None else (roa_cur or 0.08)
        z_d = (mcap / tot_liab) if mcap else 1.5
        z_e = (rev_val / tot_assets) if rev_val is not None else 0.8
        altman_z = round((1.2 * z_a) + (1.4 * z_b) + (3.3 * z_c) + (0.6 * z_d) + (1.0 * z_e), 2)

    de_pct = info.get("debtToEquity")
    if de_pct is None and tot_equity and tot_equity > 0:
        de_pct = (tot_debt / tot_equity) * 100.0
    curr_ratio = info.get("currentRatio") or ((curr_assets / curr_liab) if (curr_assets and curr_liab and curr_liab > 0) else None)
    prev_curr_ratio = (float(s_curr_assets.iloc[-2]) / float(s_curr_liab.iloc[-2])) if (len(s_curr_assets) >= 2 and len(s_curr_liab) >= 2 and float(s_curr_liab.iloc[-2]) > 0) else curr_ratio
    int_coverage = (ebit_val / int_exp_val) if (ebit_val and int_exp_val and int_exp_val > 0) else None

    cfo_to_pat_pct = (ocf_val / net_inc_val * 100.0) if (ocf_val is not None and net_inc_val and net_inc_val > 0) else None
    ev_val = info.get("enterpriseValue") or ((mcap + tot_debt - cash_val) if mcap else None)
    ev_ebitda = info.get("enterpriseToEbitda") or ((ev_val / ebitda_val) if (ev_val and ebitda_val and ebitda_val > 0) else None)

    bv = info.get("bookValue") or ((tot_equity / shares) if (tot_equity and shares and shares > 0) else None)
    eps = info.get("trailingEps") or ((net_inc_val / shares) if (net_inc_val and shares and shares > 0) else None)
    pe = info.get("trailingPE") or ((cmp_val / eps) if (cmp_val and eps and eps > 0) else None)
    pb = info.get("priceToBook") or ((cmp_val / bv) if (cmp_val and bv and bv > 0) else None)

    f_score = 0
    f_details = []
    if (roa_cur is not None and roa_cur > 0) or (net_inc_val is not None and net_inc_val > 0):
        f_score += 1; f_details.append("✅ 1. Positive Net Profit & ROA")
    else:
        f_details.append("❌ 1. Negative Net Profit")
    if ocf_val is not None and ocf_val > 0:
        f_score += 1; f_details.append("✅ 2. Positive Operating Cash Flow (CFO > 0)")
    else:
        f_details.append("❌ 2. Weak/Negative Operating Cash Flow")
    if roa_cur is not None and roa_prev is not None and roa_cur >= roa_prev:
        f_score += 1; f_details.append("✅ 3. ROA Improving / Stable YoY")
    else:
        f_details.append("⚪ 3. ROA Moderated YoY")
    if ocf_val is not None and net_inc_val is not None and ocf_val >= net_inc_val:
        f_score += 1; f_details.append("✅ 4. High Earnings Quality (CFO ≥ Net Profit)")
    else:
        f_details.append("⚪ 4. Accrual Heavy (CFO < Net Profit)")

    cur_lev = (tot_debt / tot_assets) if (tot_assets and tot_assets > 0) else 0
    prev_lev = (prev_debt / prev_assets) if (prev_assets and prev_assets > 0) else cur_lev
    if cur_lev <= prev_lev or (de_pct is not None and de_pct <= 40):
        f_score += 1; f_details.append("✅ 5. Controlled / Declining Financial Leverage")
    else:
        f_details.append("⚪ 5. Leverage Increased YoY")
    if (curr_ratio is not None and prev_curr_ratio is not None and curr_ratio >= prev_curr_ratio) or (curr_ratio is not None and curr_ratio >= 1.3):
        f_score += 1; f_details.append("✅ 6. Healthy Working Capital Liquidity")
    else:
        f_details.append("⚪ 6. Tight Short-Term Liquidity")
    if len(s_shares_bs) < 2 or float(s_shares_bs.iloc[-1]) <= float(s_shares_bs.iloc[-2]) * 1.01:
        f_score += 1; f_details.append("✅ 7. Zero / Minimal Equity Dilution")
    else:
        f_details.append("⚪ 7. New Share Issuance Detected")

    cur_gm = (float(s_gross_p.iloc[-1]) / rev_val) if (not s_gross_p.empty and rev_val) else net_margin_raw
    prev_gm = (float(s_gross_p.iloc[-2]) / prev_rev) if (len(s_gross_p) >= 2 and prev_rev) else cur_gm
    if (cur_gm is not None and prev_gm is not None and cur_gm >= prev_gm) or (net_margin_pct is not None and net_margin_pct >= 12):
        f_score += 1; f_details.append("✅ 8. Expanding / Healthy Operating Margins")
    else:
        f_details.append("⚪ 8. Margin Compression YoY")
    if (asset_turnover is not None and prev_asset_turnover is not None and asset_turnover >= prev_asset_turnover) or (roce_pct is not None and roce_pct >= 15):
        f_score += 1; f_details.append("✅ 9. Improving Asset Turnover & Efficiency")
    else:
        f_details.append("⚪ 9. Asset Turnover Moderated")

    graham_num = math.sqrt(22.5 * eps * bv) if (eps and bv and eps > 0 and bv > 0) else None
    warranted_pe = 22.0 if (roe_pct and roe_pct >= 16) else 16.0
    pe_fair_val = (eps * warranted_pe) if (eps and eps > 0) else None
    intrinsic_list = [v for v in [graham_num, pe_fair_val] if v is not None and v > 0]
    intrinsic_val = float(np.mean(intrinsic_list)) if intrinsic_list else None
    margin_of_safety_pct = ((intrinsic_val - cmp_val) / intrinsic_val * 100.0) if (intrinsic_val and cmp_val and intrinsic_val > 0) else None

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
        "pe": pe, "pb": pb, "bv": bv, "eps": eps,
        "roe_pct": roe_pct, "roce_pct": roce_pct, "roa_pct": (roa_cur * 100.0) if roa_cur is not None else None,
        "net_margin_pct": net_margin_pct, "asset_turnover": asset_turnover, "equity_multiplier": equity_multiplier,
        "dso_days": dso_days, "dio_days": dio_days, "dpo_days": dpo_days, "ccc_days": ccc_days,
        "altman_z": altman_z,
        "de_pct": de_pct, "curr_ratio": curr_ratio, "int_coverage": int_coverage, "ev_ebitda": ev_ebitda,
        "ocf_Cr": (ocf_val / 1e7) if ocf_val is not None else None,
        "fcf_Cr": (fcf_val / 1e7) if fcf_val is not None else None,
        "cfo_to_pat_pct": cfo_to_pat_pct,
        "graham_val": graham_num, "intrinsic_val": intrinsic_val, "mos_pct": margin_of_safety_pct,
        "piotroski_score": f_score, "piotroski_details": f_details,
        "high_52": high_52, "low_52": low_52,
        "qtr_gr_pct": (qtr_gr * 100) if qtr_gr is not None else None,
        "div_yield_pct": (info.get("dividendYield") * 100) if info.get("dividendYield") is not None else None,
        "promoter_pct": (info.get("heldPercentInsiders") * 100) if info.get("heldPercentInsiders") is not None else None,
        "sector": info.get("sector", "Indian Listed Equity")
    }
    return hist_1y, bench_1y, clean_fund, q_inc, bal_sheet, cf_stmt

# ==============================================================================
# 4. SIDEBAR: PRE-CONNECTED UPSTOX TOKEN & DUAL BSE/NSE STOCK CONTROLS
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
    user_tok = st.text_input("Upstox Access / Extended Token:", value=st.session_state["upstox_token"], type="password")
    if clean_token(user_tok) != st.session_state["upstox_token"]:
        st.session_state["upstox_token"] = clean_token(user_tok)

active_token = st.session_state["upstox_token"]

st.sidebar.markdown("---")
st.sidebar.header("🇮🇳 BSE & NSE Search Controls")

exchange_choice = st.sidebar.radio("1. Select Exchange Feed:", ["BSE India (.BO)", "NSE India (.NS)"], horizontal=True, index=0)
is_bse = "BSE" in exchange_choice
suffix = ".BO" if is_bse else ".NS"

selected_group = st.sidebar.selectbox("2. Filter by BSE / NSE Index Basket:", options=list(INDEX_GROUPS.keys()), index=0)

if INDEX_GROUPS[selected_group] == "ALL_EXCHANGE":
    if is_bse:
        available_symbols = sorted(list(BSE_INST_MAP.keys()))
    else:
        available_symbols = sorted(list(NSE_INST_MAP.keys()))
else:
    available_symbols = INDEX_GROUPS[selected_group]

formatted_options = [f"{sym} | {MASTER_NAMES.get(sym, sym)}" for sym in available_symbols]

selected_stock_option = st.sidebar.selectbox(
    f"3. Select or Type Stock/Index ({len(formatted_options):,} in list):",
    options=formatted_options,
    index=0,
    key=f"stk_sel_{selected_group}_{suffix}"
)

raw_symbol = selected_stock_option.split(" | ")[0].strip()
company_name = selected_stock_option.split(" | ")[1].strip()
yf_ticker = resolve_yf_ticker(raw_symbol, suffix)
upstox_inst_key = resolve_upstox_key(raw_symbol, is_bse=is_bse)

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
    "5. Chart Overlays & Strategy Lines:",
    [
        "Moving Averages (20, 50, 200)",
        "Gann Square of 9 Levels (S1/R1/R2)",
        "Fibonacci Retracement Lines",
        "Bollinger Bands (20, 2)",
        "Cumulative Volume Delta (CVD)",
        "RSI & Money Flow (MFI)"
    ],
    default=[
        "Moving Averages (20, 50, 200)",
        "Gann Square of 9 Levels (S1/R1/R2)",
        "Cumulative Volume Delta (CVD)",
        "RSI & Money Flow (MFI)"
    ]
)

refresh_rate = st.sidebar.slider("6. Auto-Refresh (Seconds):", 5, 120, 15)

# ==============================================================================
# 5. MAIN 360° DASHBOARD (UPSTOX + CA SHUBHAM POWER STRATEGY + TECHNO-FUNDAMENTAL)
# ==============================================================================
st.title(f"🇮🇳 {company_name} ({raw_symbol} — {'BSE' if is_bse else 'NSE'})")

@st.fragment(run_every=f"{refresh_rate}s")
def render_master_terminal():
    up_quote, up_err = None, None
    df = pd.DataFrame()
    used_fallback = False
    data_source_badge = f"Standard Market Feed ({yf_ticker})"

    if active_token and upstox_inst_key:
        up_quote, up_err = fetch_upstox_live_quote(upstox_inst_key, active_token)
        df = fetch_upstox_candles(upstox_inst_key, period, interval, active_token)
        # If BSE_EQ candle feed is empty for a thinly traded stock, try NSE_EQ candle fallback automatically
        if df.empty and is_bse and upstox_inst_key.startswith("BSE_EQ|"):
            alt_nse_key = upstox_inst_key.replace("BSE_EQ|", "NSE_EQ|")
            df = fetch_upstox_candles(alt_nse_key, period, interval, active_token)
            if not up_quote:
                up_quote, _ = fetch_upstox_live_quote(alt_nse_key, active_token)
        if not df.empty or up_quote:
            data_source_badge = f"⚡ Upstox API v2 ({upstox_inst_key})"

    if df.empty:
        df, used_fallback = fetch_yf_price_history(yf_ticker, period, interval)

    hist_1y, bench_1y, fund, q_inc, bal_sheet, cf_stmt = fetch_ca_360_financials(yf_ticker, raw_symbol)

    if df is None or df.empty:
        st.error(f"Market data unavailable for {raw_symbol}. Check symbol or switch Exchange toggle in the sidebar.")
        return

    df = df.dropna(subset=['Open', 'High', 'Low', 'Close']).copy()
    if df['Volume'].sum() == 0:
        df['Volume'] = ((df['High'] - df['Low']).abs() * 1000).clip(lower=100).round(0)

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

    # --- B. TECHNICAL & CA SHUBHAM POWER STRATEGY INDICATORS ---
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['SMA_20'] = df['Close'].rolling(20, min_periods=1).mean()
    df['SMA_50'] = df['Close'].rolling(50, min_periods=1).mean()
    df['SMA_200'] = df['Close'].rolling(200, min_periods=1).mean()
    df['Rolling_VWAP'] = (df['Typical_Price'] * df['Volume']).rolling(20, min_periods=1).sum() / df['Volume'].rolling(20, min_periods=1).sum()

    std_20 = df['Close'].rolling(20, min_periods=2).std().fillna(0)
    df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
    df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift(1)).abs()
    low_close = (df['Low'] - df['Close'].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR_14'] = tr.rolling(14, min_periods=1).mean()

    up_move = df['High'].diff()
    down_move = -df['Low'].diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    atr_smooth = tr.rolling(14, min_periods=1).sum().replace(0, np.nan)
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(14, min_periods=1).sum() / atr_smooth).fillna(20)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(14, min_periods=1).sum() / atr_smooth).fillna(20)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(20)
    df['ADX_14'] = dx.rolling(14, min_periods=1).mean()

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
    df['RSI'] = (100 - (100 / (1 + (gain / loss.replace(0, np.nan))))).fillna(50)

    raw_mf = df['Typical_Price'] * df['Volume']
    pos_mf = raw_mf.where(df['Typical_Price'] >= df['Typical_Price'].shift(1), 0).rolling(14, min_periods=1).sum()
    neg_mf = raw_mf.where(df['Typical_Price'] < df['Typical_Price'].shift(1), 0).rolling(14, min_periods=1).sum()
    df['MFI'] = (100 - (100 / (1 + (pos_mf / neg_mf.replace(0, np.nan))))).fillna(50)

    vol_avg_20 = float(df['Volume'].rolling(20, min_periods=1).mean().iloc[-1])
    latest_vol_bar = float(df['Volume'].iloc[-1])
    vol_exp_ratio = (latest_vol_bar / vol_avg_20) if vol_avg_20 > 0 else 1.0

    if len(df) >= 12:
        p_now, p_prev = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-10])
        r_now, r_prev = float(df['RSI'].iloc[-1]), float(df['RSI'].iloc[-10])
        if p_now <= p_prev and r_now > r_prev + 3:
            div_status = "🟢 Bullish RSI Divergence"
        elif p_now >= p_prev and r_now < r_prev - 3:
            div_status = "🔴 Bearish RSI Divergence"
        else:
            div_status = "⚪ Aligned with Price"
    else:
        div_status = "⚪ Aligned"

    mansfield_rs = 0.0
    if not hist_1y.empty and not bench_1y.empty and len(hist_1y) >= 50 and len(bench_1y) >= 50:
        common_idx = hist_1y.index.intersection(bench_1y.index)
        if len(common_idx) >= 30:
            rp = hist_1y.loc[common_idx, 'Close'] / bench_1y.loc[common_idx, 'Close']
            rp_sma = rp.rolling(min(50, len(rp)), min_periods=10).mean()
            mansfield_rs = float(((rp.iloc[-1] / rp_sma.iloc[-1]) - 1.0) * 100.0)

    # --- C. LIVE SCOREBOARD ---
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
    adx_val = float(df['ADX_14'].iloc[-1])
    atr_val = float(df['ATR_14'].iloc[-1])
    vwap_val = float(up_quote.get("average_price", 0) or df['Rolling_VWAP'].iloc[-1]) if up_quote else float(df['Rolling_VWAP'].iloc[-1])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"Live {'BSE' if is_bse else 'NSE'} Price (₹)", f"₹{latest:,.2f}", f"{net_chg:+.2f} ({pct:+.2f}%)")
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

    # --- D. UPSTOX LIVE LEVEL-2 ORDER BOOK PANEL ---
    if up_quote:
        tbq = int(up_quote.get("total_buy_quantity", 0) or 0)
        tsq = int(up_quote.get("total_sell_quantity", 0) or 0)
        oi = int(up_quote.get("oi", 0) or 0)
        lower_c = up_quote.get("lower_circuit_limit")
        upper_c = up_quote.get("upper_circuit_limit")
        ob_tot = tbq + tsq
        tbq_pct = (tbq / ob_tot * 100) if ob_tot > 0 else 50.0

        with st.container(border=True):
            st.markdown(f"#### ⚡ Upstox Live {'BSE' if is_bse else 'NSE'} Order Book & Level-2 Market Depth")
            u1, u2, u3, u4, u5 = st.columns(5)
            u1.metric("VWAP (Avg Trade Price)", f"₹{vwap_val:,.2f}", "Above VWAP (Bullish)" if latest >= vwap_val else "Below VWAP")
            u2.metric("Pending Buy Orders (TBQ)", f"{tbq:,}", f"{tbq_pct:.1f}% of Order Book")
            u3.metric("Pending Sell Orders (TSQ)", f"{tsq:,}", f"{100-tbq_pct:.1f}% of Order Book", delta_color="inverse")
            u4.metric("Circuit Limits (L / U)", f"₹{lower_c} - ₹{upper_c}" if (lower_c and upper_c) else "N/A")
            u5.metric("Open Interest (OI)", f"{oi:,}" if oi else "Equity Spot")

            depth = up_quote.get("depth", {})
            buy_depth = depth.get("buy", [])
            sell_depth = depth.get("sell", [])
            if buy_depth and sell_depth:
                with st.expander("📖 View Live Top 5 Bid vs. Ask Market Depth Table (Level 2)", expanded=False):
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

    # --- E. CALCULATE GANN SQUARE OF 9 & FIBONACCI LEVELS ---
    gann_levels = calculate_gann_square_of_9(latest)
    swing_high_p = float(df['High'].max())
    swing_low_p = float(df['Low'].min())
    fib_levels = calculate_fibonacci_levels(swing_high_p, swing_low_p)

    # --- F. INTERACTIVE MULTI-PANE CHART WITH GANN & FIBONACCI OVERLAYS ---
    if interval in ["1m", "5m", "15m"] and not used_fallback:
        x_labels = [ts.strftime('%d %b %H:%M') for ts in df.index]
    else:
        x_labels = [ts.strftime('%d %b %Y') for ts in df.index]

    show_sma = "Moving Averages (20, 50, 200)" in overlays
    show_gann = "Gann Square of 9 Levels (S1/R1/R2)" in overlays
    show_fib = "Fibonacci Retracement Lines" in overlays
    show_bb = "Bollinger Bands (20, 2)" in overlays
    show_cvd = "Cumulative Volume Delta (CVD)" in overlays
    show_osc = "RSI & Money Flow (MFI)" in overlays

    titles = ["Price Action, Moving Averages, Gann & Fibonacci Levels (₹)", "Volume Inflow (Green) vs. Outflow (Red)"]
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

    if show_gann and gann_levels:
        fig.add_hline(y=gann_levels["R2 (90°)"], line_dash="dot", line_color="#10b981", annotation_text=f"Gann R2 ₹{gann_levels['R2 (90°)']}", row=1, col=1)
        fig.add_hline(y=gann_levels["R1 (45°)"], line_dash="dash", line_color="#34d399", annotation_text=f"Gann R1 ₹{gann_levels['R1 (45°)']}", row=1, col=1)
        fig.add_hline(y=gann_levels["S1 (45°)"], line_dash="dash", line_color="#f87171", annotation_text=f"Gann S1 ₹{gann_levels['S1 (45°)']}", row=1, col=1)

    if show_fib and fib_levels:
        fig.add_hline(y=fib_levels["Ret 38.2%"], line_dash="dot", line_color="#fbbf24", annotation_text=f"Fib 38.2% (₹{fib_levels['Ret 38.2%']})", row=1, col=1)
        fig.add_hline(y=fib_levels["Golden 61.8%"], line_dash="dot", line_color="#38bdf8", annotation_text=f"Fib 61.8% Golden (₹{fib_levels['Golden 61.8%']})", row=1, col=1)

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
    fig.update_layout(height=720, template="plotly_dark", barmode="relative", xaxis_rangeslider_visible=False, margin=dict(l=15, r=15, t=25, b=10), uirevision=f"{yf_ticker}_{timeframe_label}")
    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================================
    # G. PROPRIETARY ENGINE 1: "SHORT TERM POWER STRATEGY BY CA SHUBHAM"
    # ==========================================================================
    ema20_v = float(df['EMA_20'].iloc[-1])
    sma50_v = float(df['SMA_50'].iloc[-1])
    bench_name = "BSE Sensex" if is_bse else "Nifty 50"

    power_score = 0
    power_checks = []
    if latest >= ema20_v and ema20_v >= sma50_v:
        power_score += 20; power_checks.append("🟢 Price > 20 EMA > 50 SMA Alignment")
    else:
        power_checks.append("🔴 Moving Averages Not Aligned Bullishly")

    if latest >= vwap_val:
        power_score += 15; power_checks.append(f"🟢 Trading Above VWAP (₹{vwap_val:,.2f})")
    else:
        power_checks.append(f"🔴 Trading Below VWAP (₹{vwap_val:,.2f})")

    if in_pct >= 52.0 or vol_exp_ratio >= 1.25:
        power_score += 20; power_checks.append(f"🟢 Institutional Volume Inflow ({in_pct:.1f}% | {vol_exp_ratio:.2f}x Vol)")
    else:
        power_checks.append(f"🟡 Moderate Volume Flow ({in_pct:.1f}% | {vol_exp_ratio:.2f}x Vol)")

    if 50.0 <= rsi_val <= 75.0 and mfi_val >= 50.0:
        power_score += 20; power_checks.append(f"🟢 RSI ({rsi_val:.1f}) & MFI ({mfi_val:.1f}) in Power Zone (50-75)")
    elif rsi_val > 75.0:
        power_score += 10; power_checks.append(f"🟡 RSI Overbought ({rsi_val:.1f}) — Wait for Pullback")
    else:
        power_checks.append(f"🔴 Weak Momentum (RSI: {rsi_val:.1f}, MFI: {mfi_val:.1f})")

    if adx_val >= 20.0:
        power_score += 15; power_checks.append(f"🟢 Strong Trend Conviction (ADX: {adx_val:.1f} ≥ 20)")
    else:
        power_checks.append(f"🟡 Sideways / Low ADX ({adx_val:.1f})")

    if mansfield_rs >= 0.0:
        power_score += 10; power_checks.append(f"🟢 Outperforming {bench_name} (Mansfield RS: {mansfield_rs:+.2f})")
    else:
        power_checks.append(f"🔴 Lagging {bench_name} (Mansfield RS: {mansfield_rs:+.2f})")

    lunar_label, lunar_day = get_lunar_phase_cycle()
    entry_trigger = gann_levels.get("R1 (45°)", round(latest * 1.005, 2))
    atr_sl = round(min(latest - (1.5 * atr_val), gann_levels.get("S1 (45°)", latest * 0.98)), 2)
    risk_pts = max(0.5, round(latest - atr_sl, 2))
    target_1 = gann_levels.get("R2 (90°)", round(latest + 1.5 * risk_pts, 2))
    target_2 = gann_levels.get("R3 (180°)", round(latest + 2.5 * risk_pts, 2))
    target_3 = max(gann_levels.get("R4 (360°)", 0), fib_levels.get("Ext 127.2%", round(latest + 4.0 * risk_pts, 2)))
    rr_ratio = round((target_2 - latest) / risk_pts, 2) if risk_pts > 0 else 2.0
    rec_shares_1L = max(1, int(1000.0 / risk_pts))

    power_verdict = (
        "🔥 HIGH-CONVICTION POWER BREAKOUT BUY" if power_score >= 75
        else ("🟢 BULLISH ACCUMULATION / BUY ON DIPS" if power_score >= 55 else "🟡 NEUTRAL / WAIT FOR TRIGGER")
    )

    st.markdown("---")
    st.subheader("⚡ Short Term Power Strategy by CA Shubham")
    st.info(
        f"**CA Shubham Power Score:** `{power_score} / 100` — **{power_verdict}**  |  "
        f"**RSI Divergence:** `{div_status}`  |  **Time Cycle:** `{lunar_label} (Day {lunar_day})`"
    )

    ps1, ps2, ps3 = st.columns(3)
    with ps1:
        with st.container(border=True):
            st.markdown("##### 🎯 6-Factor Power Checklist")
            for chk in power_checks:
                st.caption(chk)
    with ps2:
        with st.container(border=True):
            st.markdown("##### 📐 Gann Square of 9 & Fibonacci Pivot Grid")
            st.caption(f"• **Gann Resistances:** R1 (45°): **₹{gann_levels.get('R1 (45°)')}** | R2 (90°): **₹{gann_levels.get('R2 (90°)')}** | R3 (180°): **₹{gann_levels.get('R3 (180°)')}**")
            st.caption(f"• **Gann Supports:** S1 (45°): **₹{gann_levels.get('S1 (45°)')}** | S2 (90°): **₹{gann_levels.get('S2 (90°)')}** | S3 (180°): **₹{gann_levels.get('S3 (180°)')}**")
            st.caption(f"• **Fibonacci Retracements:** 38.2%: **₹{fib_levels.get('Ret 38.2%')}** | 50%: **₹{fib_levels.get('Ret 50.0%')}** | **61.8% Golden Pocket: ₹{fib_levels.get('Golden 61.8%')}**")
            st.caption(f"• **Fibonacci Extensions:** 127.2% Target: **₹{fib_levels.get('Ext 127.2%')}** | 161.8% Target: **₹{fib_levels.get('Ext 161.8%')}**")
    with ps3:
        with st.container(border=True):
            st.markdown("##### 🛡️ ATR & Gann Execution Plan")
            st.caption(f"• **Live CMP:** **₹{latest:,.2f}** | **Breakout Entry Above:** **₹{entry_trigger:,.2f}**")
            st.caption(f"• **Stop-Loss (1.5x ATR / Gann S1):** **₹{atr_sl:,.2f}** *(Risk: ₹{risk_pts:,.2f}/sh)*")
            st.caption(f"• **Target 1 (Gann 90°):** **₹{target_1:,.2f}** | **Target 2 (Gann 180°):** **₹{target_2:,.2f}**")
            st.caption(f"• **Target 3 (Gann 360° / Fib):** **₹{target_3:,.2f}** | **R:R Ratio:** **`1 : {rr_ratio}`** | **Qty (per ₹1L cap @ 1% risk):** **`{rec_shares_1L} sh`**")

    # ==========================================================================
    # H. PROPRIETARY ENGINE 2: TECHNO-FUNDAMENTAL STRATEGY & CA FINANCIAL AUDIT
    # ==========================================================================
    is_idx_sym = (raw_symbol in UPSTOX_INDEX_KEYS) or raw_symbol.startswith("^")
    if not is_idx_sym:
        base_df = hist_1y if not hist_1y.empty else df
        d_close = latest
        dma_50 = float(base_df['Close'].rolling(50, min_periods=1).mean().iloc[-1])
        dma_200 = float(base_df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        high_52 = fund.get("high_52") or float(base_df['High'].max())
        low_52 = fund.get("low_52") or float(base_df['Low'].min())

        mcap_cr = fund.get("marketCap_Cr")
        pe = fund.get("pe")
        pb = fund.get("pb")
        bv = fund.get("bv")
        roe = fund.get("roe_pct")
        roce = fund.get("roce_pct")
        net_m = fund.get("net_margin_pct")
        asset_to = fund.get("asset_turnover")
        eq_mult = fund.get("equity_multiplier")
        dso = fund.get("dso_days")
        dio = fund.get("dio_days")
        dpo = fund.get("dpo_days")
        ccc = fund.get("ccc_days")
        altman_z = fund.get("altman_z")
        de = fund.get("de_pct")
        curr_r = fund.get("curr_ratio")
        int_cov = fund.get("int_coverage")
        ev_ebitda = fund.get("ev_ebitda")
        ocf_cr = fund.get("ocf_Cr")
        fcf_cr = fund.get("fcf_Cr")
        cfo_pat = fund.get("cfo_to_pat_pct")
        graham_v = fund.get("graham_val")
        intrinsic_v = fund.get("intrinsic_val")
        mos_pct = fund.get("mos_pct")
        f_score = fund.get("piotroski_score", 5)
        f_details = fund.get("piotroski_details", [])
        qtr_gr = fund.get("qtr_gr_pct")
        div_y = fund.get("div_yield_pct")
        prom = fund.get("promoter_pct")

        fund_strong = (f_score >= 6) or ((roe is not None and roe >= 14) and (de is None or de <= 100))
        tech_strong = (power_score >= 60) or (d_close >= dma_50 and d_close >= dma_200)

        if fund_strong and tech_strong:
            tf_matrix = "🌟 TIER-1 TECHNO-FUNDAMENTAL CONVICTION BUY (Strong Balance Sheet + High Technical Power)"
        elif fund_strong and not tech_strong:
            tf_matrix = "💎 CONTRARIAN VALUE ACCUMULATION (Strong Fundamentals on Technical Pullback — Accumulate on Support)"
        elif not fund_strong and tech_strong:
            tf_matrix = "⚡ TACTICAL MOMENTUM TRADE ONLY (Strong Price Action but Moderate Fundamentals — Trail Strict Stop-Loss)"
        else:
            tf_matrix = "🛑 AVOID / VALUE TRAP WARNING (Weak Financials & Bearish Price Trend)"

        st.markdown("---")
        st.subheader(f"🏛️ Techno-Fundamental Analysis Strategy & CA Financial Audit — `{fund.get('sector')}`")
        st.success(f"**Techno-Fundamental Matrix Verdict:** {tf_matrix}")

        tf1, tf2, tf3 = st.columns(3)
        with tf1:
            with st.container(border=True):
                st.markdown(f"##### 📋 Piotroski F-Score Audit: `{f_score} / 9`")
                for item in f_details:
                    st.caption(item)
        with tf2:
            with st.container(border=True):
                st.markdown("##### 🔬 3-Step DuPont ROE & Working Capital Cycle")
                st.caption(f"• **ROE:** **{f'{roe:.1f}%' if roe is not None else 'N/A'}** | **ROCE:** **{f'{roce:.1f}%' if roce is not None else 'N/A'}**")
                st.caption(f"• **DuPont 1 (Net Margin):** **{f'{net_m:.1f}%' if net_m is not None else 'N/A'}** | **2 (Asset Turnover):** **{f'{asset_to:.2f}x' if asset_to is not None else 'N/A'}**")
                st.caption(f"• **DuPont 3 (Equity Multiplier):** **{f'{eq_mult:.2f}x' if eq_mult is not None else 'N/A'}** ({'🟢 Low Leverage' if (eq_mult is None or eq_mult <= 2.5) else '🟡 High Leverage'})")
                st.caption(f"• **Working Capital Cycle (CCC):** **{f'{ccc:.0f} Days' if ccc is not None else 'N/A'}** *(DSO: {f'{dso:.0f}d' if dso else '-'} | DIO: {f'{dio:.0f}d' if dio else '-'} | DPO: {f'{dpo:.0f}d' if dpo else '-'})*")
                z_zone = "🟢 Safe (>2.99)" if (altman_z and altman_z > 2.99) else ("🟡 Grey Zone" if (altman_z and altman_z >= 1.81) else ("🔴 Distress" if altman_z is not None else "N/A"))
                st.caption(f"• **Altman Z-Score (Solvency):** **{f'{altman_z:.2f}' if altman_z is not None else 'N/A'}** ({z_zone})")
        with tf3:
            with st.container(border=True):
                st.markdown("##### ⚖️ Intrinsic Valuation & Cash Flow Audit")
                st.caption(f"• **Graham Intrinsic Number:** **{f'₹{graham_v:,.1f}' if graham_v else 'N/A'}** | **Fair Value Est:** **{f'₹{intrinsic_v:,.1f}' if intrinsic_v else 'N/A'}**")
                mos_label = f"{mos_pct:+.1f}% (Undervalued)" if (mos_pct and mos_pct > 0) else (f"{mos_pct:+.1f}% (Growth Premium)" if mos_pct is not None else "N/A")
                st.caption(f"• **Margin of Safety vs CMP:** **{mos_label}**")
                st.caption(f"• **Operating Cash Flow (CFO):** **{f'₹{ocf_cr:,.0f} Cr' if ocf_cr is not None else 'N/A'}** | **Free Cash Flow (FCF):** **{f'₹{fcf_cr:,.0f} Cr' if fcf_cr is not None else 'N/A'}**")
                cfo_badge = "🟢 High Cash Conversion" if (cfo_pat and cfo_pat >= 80) else ("🔴 Low Cash Conversion" if cfo_pat is not None else "⚪ N/A")
                st.caption(f"• **CFO / Net Profit Conversion:** **{f'{cfo_pat:.0f}%' if cfo_pat is not None else 'N/A'}** ({cfo_badge})")

        f1, f2, f3, f4, f5, f6 = st.columns(6)
        f1.metric("Market Cap", f"₹{mcap_cr:,.0f} Cr" if mcap_cr else "N/A")
        f2.metric("Trailing P/E & EV/EBITDA", f"{pe:.1f}x / {ev_ebitda:.1f}x" if (pe and ev_ebitda) else (f"{pe:.1f}x" if pe else "N/A"))
        f3.metric("P/B & Book Value", f"{pb:.2f}x (₹{bv:,.0f})" if (pb and bv) else (f"{pb:.2f}x" if pb else "N/A"))
        f4.metric("ROCE / ROE (%)", f"{roce:.1f}% / {roe:.1f}%" if (roce is not None and roe is not None) else (f"{roe:.1f}%" if roe is not None else "N/A"))
        f5.metric("Debt/Equity & Int. Cov", f"{de:.1f}% / {int_cov:.1f}x" if (de is not None and int_cov is not None) else (f"{de:.1f}%" if de is not None else "N/A"))
        f6.metric("Current Ratio & Z-Score", f"{curr_r:.2f}x / Z:{altman_z:.1f}" if (curr_r and altman_z) else (f"{curr_r:.2f}x" if curr_r else "N/A"))

        f7, f8, f9, f10, f11, f12 = st.columns(6)
        f7.metric("52-Week High", f"₹{high_52:,.2f}" if high_52 else "N/A")
        f8.metric("52-Week Low", f"₹{low_52:,.2f}" if low_52 else "N/A")
        f9.metric("50 & 200 DMA", f"₹{dma_50:,.0f} / ₹{dma_200:,.0f}")
        f10.metric("Qtr Profit Growth", f"{qtr_gr:+.1f}%" if qtr_gr is not None else "N/A")
        f11.metric("Dividend Yield", f"{div_y:.2f}%" if div_y is not None else "N/A")
        f12.metric("Promoter Holding", f"{prom:.1f}%" if prom is not None else "N/A")

        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            if not q_inc.empty:
                q_df = q_inc.T.sort_index()
                rev_c = next((c for c in ['Total Revenue', 'Operating Revenue'] if c in q_df.columns), None)
                net_c = next((c for c in ['Net Income', 'Net Income Common Stockholders'] if c in q_df.columns), None)
                if rev_c and net_c:
                    dates = [d.strftime('%b %Y') if hasattr(d, 'strftime') else str(d) for d in q_df.index]
                    fig_q = go.Figure()
                    fig_q.add_trace(go.Bar(x=dates, y=q_df[rev_c] / 1e7, name="Revenue (₹ Cr)", marker_color="#38bdf8"))
                    fig_q.add_trace(go.Bar(x=dates, y=q_df[net_c] / 1e7, name="Net Profit (₹ Cr)", marker_color="#10b981"))
                    fig_q.update_layout(title="📊 Quarterly P&L: Revenue vs. Profit (₹ Cr)", height=310, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_q, use_container_width=True)

        with ch2:
            if not bal_sheet.empty:
                b_df = bal_sheet.T.sort_index()
                as_c = next((c for c in ['Total Assets'] if c in b_df.columns), None)
                eq_c = next((c for c in ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity'] if c in b_df.columns), None)
                dt_c = next((c for c in ['Total Debt', 'Long Term Debt'] if c in b_df.columns), None)
                if as_c:
                    b_dates = [d.strftime('%Y') if hasattr(d, 'strftime') else str(d) for d in b_df.index]
                    fig_b = go.Figure()
                    fig_b.add_trace(go.Bar(x=b_dates, y=b_df[as_c] / 1e7, name="Assets (₹ Cr)", marker_color="#6366f1"))
                    if eq_c: fig_b.add_trace(go.Bar(x=b_dates, y=b_df[eq_c] / 1e7, name="Net Worth (₹ Cr)", marker_color="#10b981"))
                    if dt_c: fig_b.add_trace(go.Bar(x=b_dates, y=b_df[dt_c] / 1e7, name="Total Debt (₹ Cr)", marker_color="#ef4444"))
                    fig_b.update_layout(title="🏦 Balance Sheet: Assets, Equity & Debt (₹ Cr)", height=310, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_b, use_container_width=True)

        with ch3:
            if not cf_stmt.empty:
                c_df = cf_stmt.T.sort_index()
                ocf_c = next((c for c in ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'] if c in c_df.columns), None)
                fcf_c = next((c for c in ['Free Cash Flow'] if c in c_df.columns), None)
                if ocf_c:
                    c_dates = [d.strftime('%Y') if hasattr(d, 'strftime') else str(d) for d in c_df.index]
                    fig_cf = go.Figure()
                    fig_cf.add_trace(go.Bar(x=c_dates, y=c_df[ocf_c] / 1e7, name="Operating CF (₹ Cr)", marker_color="#10b981"))
                    if fcf_c:
                        fig_cf.add_trace(go.Bar(x=c_dates, y=c_df[fcf_c] / 1e7, name="Free Cash Flow (₹ Cr)", marker_color="#f59e0b"))
                    fig_cf.update_layout(title="💵 Cash Flow: Operating CF vs. FCF (₹ Cr)", height=310, template="plotly_dark", barmode="group", margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_cf, use_container_width=True)

render_master_terminal()

# ==============================================================================
# 6. ONE-CLICK BSE & NSE INDEX PEER SCANNER WITH CA SHUBHAM POWER SCORE
# ==============================================================================
with st.expander(f"🔍 Scan & Compare All Peer Stocks in [{selected_group}] ({'BSE' if is_bse else 'NSE'} Feed)", expanded=False):
    peer_list = available_symbols[:30]
    if st.button(f"🚀 Run CA Shubham Power & Flow Scan on {selected_group.split('(')[0].strip()}", type="primary"):
        rows = []
        prog = st.progress(0)
        for i, s in enumerate(peer_list):
            try:
                t_s = resolve_yf_ticker(s, suffix)
                u_key = resolve_upstox_key(s, is_bse=is_bse)
                h = pd.DataFrame()
                if active_token and u_key:
                    h = fetch_upstox_candles(u_key, "3mo", "1d", active_token)
                if h.empty:
                    h, _ = fetch_yf_price_history(t_s, "3mo", "1d")

                if not h.empty and len(h) >= 20:
                    c = float(h['Close'].iloc[-1])
                    prev_c = float(h['Close'].iloc[-2])
                    chg_p = (c - prev_c) / prev_c * 100
                    ema20 = float(h['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
                    sma50 = float(h['Close'].rolling(50, min_periods=1).mean().iloc[-1])
                    gann_r1 = round((math.sqrt(c) + 0.125) ** 2, 2)
                    gann_s1 = round((math.sqrt(c) - 0.125) ** 2, 2)

                    d = h['Close'].diff()
                    g = float((d.where(d > 0, 0)).rolling(14, min_periods=1).mean().iloc[-1])
                    l = float((-d.where(d < 0, 0)).rolling(14, min_periods=1).mean().iloc[-1])
                    rsi_v = 100 - (100 / (1 + (g / l))) if l != 0 else 50.0

                    rec = h.tail(5)
                    hl = (rec['High'] - rec['Low']).replace(0, np.nan)
                    br = ((rec['Close'] - rec['Low']) / hl).fillna(0.5).clip(0, 1)
                    in_v = float((rec['Volume'] * br).sum())
                    tot_v = float(rec['Volume'].sum())
                    in_p = (in_v / tot_v * 100) if tot_v > 0 else 50.0
                    net_cr_5d = float((((rec['Volume'] * br) - (rec['Volume'] * (1 - br))) * ((rec['High'] + rec['Low'] + rec['Close']) / 3)).sum() / 1e7)

                    p_score = 0
                    if c >= ema20 >= sma50: p_score += 35
                    if in_p >= 52: p_score += 35
                    if 50 <= rsi_v <= 75: p_score += 30

                    rows.append({
                        "Symbol": s,
                        "Exchange": "BSE" if is_bse else "NSE",
                        "Company": MASTER_NAMES.get(s, s)[:24],
                        "Price (₹)": round(c, 2),
                        "1D Chg (%)": round(chg_p, 2),
                        "⚡ Power Score": f"{p_score}/100",
                        "🟢 5D Buy Inflow (%)": round(in_p, 1),
                        "5D Net Flow (₹ Cr)": round(net_cr_5d, 2),
                        "RSI (14)": round(rsi_v, 1),
                        "Gann S1 (₹)": gann_s1,
                        "Gann R1 Target (₹)": gann_r1,
                        "Strategy Signal": "🔥 Power Breakout" if p_score >= 70 else ("🟢 Bullish" if p_score >= 50 else "⚪ Watch")
                    })
            except Exception:
                pass
            prog.progress((i + 1) / len(peer_list))
        prog.empty()
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values(by="5D Net Flow (₹ Cr)", ascending=False), use_container_width=True, hide_index=True)
