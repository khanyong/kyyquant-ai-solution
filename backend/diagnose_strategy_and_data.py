
import os
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv()

def main():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("Error: Supabase credentials not found")
        return

    with open('diagnose_output.txt', 'w', encoding='utf-8') as f:
        try:
            supabase = create_client(url, key)
            f.write("="*60 + "\n")
            f.write("DIAGNOSING STRATEGY, CONDITIONS, AND DATA\n")
            f.write("="*60 + "\n")

            # 1. Get Strategy Details (Conditions)
            f.write("\n[1] Active Strategy Logic\n")
            response = supabase.rpc('get_active_strategies_with_universe').execute()
            strategies = response.data
            
            target_universe = []
            
            if strategies:
                for s in strategies:
                    f.write(f"Strategy: {s.get('strategy_name')} (ID: {s.get('strategy_id')})\n")
                    f.write("Buy Conditions:\n")
                    f.write(json.dumps(s.get('entry_conditions'), indent=2, ensure_ascii=False) + "\n")
                    
                    target_universe = s.get('filtered_stocks', [])
                    f.write(f"Universe Size: {len(target_universe)}\n")
            else:
                f.write("No active strategy found.\n")
                return

            # 2. Check Data Availability for a sample stock
            sample_code = target_universe[0] if target_universe else "005930"
            if sample_code in ['100250', '108320', '101530'] and len(target_universe) > 3:
                sample_code = target_universe[3]
                
            f.write(f"\n[2] Data Check for Sample Stock: {sample_code}\n")
            # Check kw_price_daily for today
            price_res = supabase.table('kw_price_daily').select('*').eq('stock_code', sample_code).order('trade_date', desc=True).limit(3).execute()
            
            if price_res.data:
                f.write(f"Found {len(price_res.data)} recent records.\n")
                for row in price_res.data:
                    f.write(f" - Date: {row.get('trade_date')} | Close: {row.get('close')} | Vol: {row.get('volume')}\n")
            else:
                f.write("No price data found.\n")

            # 3. Check Debug Indicators for Monitored Stocks
            f.write("\n[3] Debug Indicators for Monitored Stocks (Score 0)\n")
            monitored = supabase.table('strategy_monitoring').select('*').execute()
            
            if monitored.data:
                for row in monitored.data:
                    f.write(f"Stock: {row.get('stock_code')} | Score: {row.get('condition_match_score')}\n")
                    f.write(f"Row Keys: {list(row.keys())}\n")
                    f.write(f"Conditions Met: {json.dumps(row.get('conditions_met'), indent=2, ensure_ascii=False)}\n")
            else:
                f.write("No monitored data.\n")

        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    main()
