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
    print(f"[{datetime.now()}] Starting fetch...")
    new_data = []

    # 1. KOSPI, KOSDAQ, USD/KRW (FinanceDataReader)
    fdr_indices = {
        "KOSPI": "KS11",
        "KOSDAQ": "KQ11", 
        "USD_KRW": "USD/KRW",
        "SPX": "S&P500",
        "COMP": "IXIC"
    }

    for name, ticker in fdr_indices.items():
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
            print(f"  [Fetched] {name}: {current}")
        except Exception as e:
            print(f"  [Error] FDR {name}: {e}")

    # 2. Bonds (yfinance)
    yf_indices = {
        "IEF": "IEF",
        "TLT": "TLT",
        "LQD": "LQD"
    }
    
    session = requests.Session()
    session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

    for name, ticker in yf_indices.items():
        try:
            tick = yf.Ticker(ticker, session=session)
            hist = tick.history(period="5d")
            if hist.empty:
                continue
            
            last_row = hist.iloc[-1]
            prev_row = hist.iloc[-2] if len(hist) > 1 else last_row
            
            current = float(last_row['Close'])
            prev_close = float(prev_row['Close'])
            change = current - prev_close
            change_rate = (change / prev_close) * 100 if prev_close != 0 else 0

            new_data.append({
                "index_code": name,
                "current_value": round(current, 2),
                "change_value": round(change, 2),
                "change_rate": round(change_rate, 2),
                "updated_at": pd.Timestamp.now().isoformat()
            })
            print(f"  [Fetched] {name}: {current}")
        except Exception as e:
            print(f"  [Error] YF {name}: {e}")

    return new_data

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
