import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from data.provider import DataProvider
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

async def verify_data():
    print("="*50)
    print("DATA INTEGRITY VERIFICATION START")
    print("="*50)

    # 1. Initialize Provider
    provider = DataProvider()
    if not provider.supabase:
        print("[CRITICAL] Supabase NOT connected! Check .env variables.")
        return
    else:
        print("[OK] Supabase connected.")

    # 2. Fetch Data for a major stock (Samsung Electronics: 005930)
    stock_code = '005930'
    start_date = (datetime.now() - timedelta(days=365*4)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\nFetching data for {stock_code} from {start_date} to {end_date}...")
    
    # We use internal method or just call get_historical_data
    # Use get_historical_data to test the actual path used by engine
    df = await provider.get_historical_data(stock_code, start_date, end_date)
    
    if df is None or df.empty:
        print(f"[CRITICAL] No data returned for {stock_code}!")
        return

    # Check if it was mock data (DataProvider prints warnings, but we can check values)
    # Mock data usually has nice round numbers or specific patterns, but let's check count first.
    print(f"\n[INFO] Rows returned: {len(df)}")
    
    # 3. Analyze Data Quality
    print("\n[ANALYSIS]")
    
    # Check for gaps
    df = df.sort_index()
    dates = df.index
    date_diffs = dates.to_series().diff().dt.days
    
    # Gaps larger than 5 days (trading holidays are usually max 5 days like Chuseok/Lunar New Year + Weekend)
    large_gaps = date_diffs[date_diffs > 5]
    
    if not large_gaps.empty:
        print(f"[WARNING] Found {len(large_gaps)} large gaps (> 5 days):")
        for date, gap in large_gaps.items():
            prev_date = date - timedelta(days=int(gap))
            print(f"  - Gap of {int(gap)} days between {prev_date.date()} and {date.date()}")
    else:
        print("[OK] No significant date gaps found.")

    # Check for zero or negative prices
    invalid_prices = df[(df['close'] <= 0) | (df['open'] <= 0) | (df['high'] <= 0) | (df['low'] <= 0)]
    if not invalid_prices.empty:
        print(f"[CRITICAL] Found {len(invalid_prices)} rows with zero or negative prices!")
        print(invalid_prices.head())
    else:
        print("[OK] All prices are positive.")

    # Check statistics
    print(f"\n[STATISTICS]")
    print(df.describe()[['open', 'high', 'low', 'close', 'volume']])

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(verify_data())
