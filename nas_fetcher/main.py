import requests
import time
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import os

# AWS Backend Endpoint (Default if not set in env)
AWS_API_URL = os.getenv("AWS_API_URL", "http://13.209.204.159:8001/api/market/update-data")

def fetch_data():
    print(f"[{datetime.now()}] Starting fetch (16 items)...")
    new_data = []

    # 4x4 Grid Definition
    # Row 1: Core (Major Indices)
    # Row 2: Global Pulse
    # Row 3: Money Flow
    # Row 4: Risk & Rates

    # FinanceDataReader Indices (Naver Finance Source is reliable for these)
    fdr_indices = {
        # Row 1
        "KOSPI": "KS11",
        "KOSDAQ": "KQ11",
        "S&P500": "S&P500", # FDR uses symbol 'S&P500' or 'US500' -> let's stick to what worked or standarize
        "NASDAQ": "IXIC",   # FDR 'IXIC' is Nasdaq Composite
        
        # Row 2
        "Nikkei225": "JP225", # Nikkei
        "EuroStoxx50": "STOXX50", # Euro Stoxx
        "DowJones": "DJI",
        "Russell2000": "US2000", # Russell 2000 usually US2000 in FDR/Investing

        # Row 3
        "WTI_Oil": "CL", # Crude Oil (Nymex) -> 'CL' in FDR (if supported) or use YF
        "Gold": "GC",    # Gold (Comex) -> 'GC'
        "USD/KRW": "USD/KRW",
        "Bitcoin": "BTC/KRW", # Or BTC/USD. Let's start with FDR crypto if reliable, else YF.
    }

    # yfinance Fallback/Primary for US Specifics (Bonds, VIX)
    yf_indices = {
        # Row 4
        "US10Y": "^TNX", # CBOE Interest Rate 10 Year T Note
        "US2Y": "^IRX",  # 13 Week?? No, ^IRX is 13 week. 2 Year is "^TU"? No, typically using ETFs or specific tickers. 
                         # Let's use "ZF=F" (2 Year Note Futures) or just "SHY" (ETF). 
                         # Better: Treasury Yields directly: "^TNX" (10Y), "^FVX" (5Y). 
                         # Actually, standard is: ^TNX (10 Yr), ^IRX (13 Wk), ^TYX (30 Yr).
                         # 2 Year Treasury yield ticker on Yahoo is "^UST2Y" (might not be available everywhere) or can use "SHY" as proxy.
                         # Let's use "SHY" (1-3 Year Treasury ETF) for stability if ^UST2Y fails.
        "VIX": "^VIX",
        "TLT": "TLT"
    }
    
    # ---------------------------------------------------------
    # 1. Fetch from FinanceDataReader (FDR)
    # ---------------------------------------------------------
    # Note: FDR symbols for Commodities/Global indices can be tricky.
    # Refined mapping for FDR (using 'investing' convention often needed)
    # Let's stick to known working ones, and move uncertain ones to YF.
    
    # SAFE FDR List (Korean & Major US/FX)
    fdr_safe_map = {
        "KOSPI": "KS11",
        "KOSDAQ": "KQ11",
        "USD/KRW": "USD/KRW",
        "S&P500": "S&P500", # investing.com source usually
        "NASDAQ": "IXIC",
        "DowJones": "DJI",
        "Nikkei225": "JP225", # Investing.com ID
        "EuroStoxx50": "STOXX50",
        "Bitcoin": "BTC/KRW" # Bithumb/Upbit usually
    }
    
    for name, ticker in fdr_safe_map.items():
        try:
            # Last 7 days
            start_date = (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            df = fdr.DataReader(ticker, start_date)
            
            if df is None or df.empty:
                print(f"  [Fail] FDR {name}: No data")
                continue
            
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else last_row 
            
            current = float(last_row['Close'])
            prev_close = float(prev_row['Close'])
            
            change = current - prev_close
            change_rate = (change / prev_close * 100) if prev_close != 0 else 0.0

            new_data.append({
                "index_code": name,
                "current_value": round(current, 2),
                "change_value": round(change, 2),
                "change_rate": round(change_rate, 2),
                "updated_at": pd.Timestamp.now().isoformat()
            })
            print(f"  [Fetched] {name} (FDR): {current}")
        except Exception as e:
            print(f"  [Error] FDR {name}: {e}")

    # ---------------------------------------------------------
    # 2. Robust Fetching Strategy (Dual Source)
    # ---------------------------------------------------------
    
    # Define Tasks: {Code: (Primary_Source, Primary_Ticker, Backup_Source, Backup_Ticker)}
    # Sources: 'FDR' (FinanceDataReader), 'YF' (yfinance)
    tasks = {
        # --- Row 1: Core ---
        "KOSPI":       ("FDR", "KS11", "YF", "^KS11"),
        "KOSDAQ":      ("FDR", "KQ11", "YF", "^KQ11"),
        "S&P500":      ("FDR", "S&P500", "YF", "^GSPC"),
        "NASDAQ":      ("FDR", "IXIC", "YF", "^IXIC"),

        # --- Row 2: Global ---
        "Nikkei225":   ("YF", "^N225", "FDR", "JP225"),       # YF usually better for Nikkei
        "EuroStoxx50": ("YF", "^STOXX50E", "FDR", "STOXX50"), # YF major symbol
        "DowJones":    ("FDR", "DJI", "YF", "^DJI"),
        "Russell2000": ("YF", "^RUT", "FDR", "US2000"),

        # --- Row 3: Money ---
        "WTI_Oil":     ("YF", "CL=F", "FDR", "CL"),
        "Gold":        ("YF", "GC=F", "FDR", "GC"),
        "USD/KRW":     ("FDR", "USD/KRW", "YF", "KRW=X"),
        "Bitcoin":     ("FDR", "BTC/KRW", "YF", "BTC-USD"),

        # --- Row 4: Risk ---
        "US10Y":       ("YF", "^TNX", "FDR", "US10YT"),
        "US2Y_ETF":    ("YF", "SHY", "YF", "IEF"), # Fallback to 7-10y if 1-3y fails
        "VIX":         ("YF", "^VIX", "FDR", "VIX"),
        "TLT":         ("YF", "TLT", "FDR", "TLT"),
    }
    
    session = requests.Session()
    session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

    for name, (src1, tick1, src2, tick2) in tasks.items():
        val, chg, rate = None, None, None
        
        # Try Primary
        try:
            val, chg, rate = fetch_single_item(name, src1, tick1, session)
        except Exception as e:
            print(f"  [Warn] Primary {name} ({tick1}) failed: {e}. Trying backup...")
        
        # Try Backup if Primary failed
        if val is None:
            try:
                val, chg, rate = fetch_single_item(name, src2, tick2, session)
            except Exception as e:
                print(f"  [Error] Backup {name} ({tick2}) failed: {e}")
        
        # Determine Success/Fail
        if val is not None:
             new_data.append({
                "index_code": name,
                "current_value": round(val, 2),
                "change_value": round(chg, 2),
                "change_rate": round(rate, 2),
                "updated_at": pd.Timestamp.now().isoformat()
            })
             print(f"  [Fetched] {name}: {val}")
        else:
             print(f"  [Fail] All sources failed for {name}")

    return new_data

def fetch_single_item(name, source, ticker, session):
    """Helper to fetch from specific source"""
    current, change, change_rate = None, None, None
    
    if source == 'FDR':
        # Limit start date to improve speed
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=10)).strftime('%Y-%m-%d')
        df = fdr.DataReader(ticker, start_date)
        if df is None or df.empty: raise Exception("Empty Data")
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        current = float(last['Close'])
        prev_close = float(prev['Close'])
        change = current - prev_close
        change_rate = (change / prev_close * 100) if prev_close != 0 else 0.0

    elif source == 'YF':
        tick = yf.Ticker(ticker, session=session)
        # fast_info often faster/more reliable for current price than history
        # but history needed for change comparison if market closed?
        # Let's stick to history for consistency
        hist = tick.history(period="5d")
        if hist.empty: raise Exception("Empty History")
        last = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else last
        current = float(last['Close'])
        prev_close = float(prev['Close'])
        change = current - prev_close
        change_rate = (change / prev_close) * 100 if prev_close != 0 else 0.0
        
    return current, change, change_rate

def push_to_aws(data):
    if not data:
        print("No data to push.")
        return

    payload = {"data": data}
    try:
        response = requests.post(AWS_API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"  [Success] Pushed {len(data)} items to AWS. code={response.status_code}")
        else:
             print(f"  [Fail] Push failed. code={response.status_code} msg={response.text}")
    except Exception as e:
        print(f"  [Error] Push connection failed: {e}")

if __name__ == "__main__":
    print(f"NAS Fetcher Started. Target: {AWS_API_URL}")
    while True:
        try:
            market_data = fetch_data()
            push_to_aws(market_data)
        except Exception as e:
            print(f"Job Error: {e}")
        
        # Sleep 10 minutes
        print("Sleeping 10 minutes...")
        time.sleep(600)
