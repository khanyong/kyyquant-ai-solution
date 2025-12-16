
import os
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

load_dotenv()

def main():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    with open('verify_pipeline_output.txt', 'w', encoding='utf-8') as f:
        if not url or not key:
            f.write("Error: Supabase credentials not found in .env\n")
            return

        try:
            supabase = create_client(url, key)
            
            f.write("="*60 + "\n")
            f.write("TRADING PIPELINE VERIFICATION REPORT\n")
            f.write("="*60 + "\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 1. Check Strategy Monitoring
            f.write("[1] Strategy Monitoring Status\n")
            response = supabase.table('strategy_monitoring').select('*', count='exact').execute()
            total_monitored = response.count
            
            response_candidates = supabase.table('strategy_monitoring').select('*', count='exact').gt('condition_match_score', 0).execute()
            candidates_count = response_candidates.count
            
            msg = f"   - Total Monitored Stocks: {total_monitored}\n"
            msg += f"   - Stocks with Positive Score: {candidates_count}\n"
            f.write(msg)
            
            if total_monitored > 0:
                f.write("   - Details of Monitored Stocks:\n")
                all_monitored = supabase.table('strategy_monitoring').select('stock_code, stock_name, current_price, updated_at, condition_match_score').execute()
                for item in all_monitored.data:
                    f.write(f"     * {item['stock_name']} ({item['stock_code']}): Score {item['condition_match_score']} | Updated: {item['updated_at']}\n")
            
            # Show top 5 candidates
            if candidates_count > 0:
                top_candidates = supabase.table('strategy_monitoring').select('stock_code, stock_name, current_price, condition_match_score').order('condition_match_score', desc=True).limit(5).execute()
                f.write("   - Top 5 Candidates:\n")
                for item in top_candidates.data:
                    f.write(f"     * {item['stock_name']} ({item['stock_code']}): Score {item['condition_match_score']}\n")
            f.write("\n")

            # 2. Check Recent Signals
            f.write("[2] Recent Trading Signals (Last 24h)\n")
            one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()
            signals = supabase.table('trading_signals').select('*').gte('created_at', one_day_ago).order('created_at', desc=True).limit(5).execute()
            
            if signals.data:
                for sig in signals.data:
                    f.write(f"   - [{sig['created_at'][11:19]}] {sig['signal_type']} {sig['stock_name']} ({sig['stock_code']}) - Status: {sig['signal_status']}\n")
            else:
                f.write("   - No signals generated in the last 24 hours.\n")
            f.write("\n")

            # 3. Check Recent Orders
            f.write("[3] Recent Orders (Last 24h)\n")
            orders = supabase.table('orders').select('*').gte('created_at', one_day_ago).order('created_at', desc=True).limit(5).execute()
            
            if orders.data:
                for ord in orders.data:
                    f.write(f"   - [{ord['created_at'][11:19]}] {ord['order_type']} {ord['stock_name']} ({ord['stock_code']}) - Status: {ord['status']}\n")
            else:
                f.write("   - No orders created in the last 24 hours.\n")
            f.write("\n")
            
            # 4. Test RPC: get_buy_candidates
            f.write("[4] Testing RPC: get_buy_candidates\n")
            rpc_res = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
            
            if rpc_res.data:
                f.write(f"   - RPC returned {len(rpc_res.data)} candidates for purchase:\n")
                for cand in rpc_res.data:
                    f.write(f"     * {cand.get('stock_name')} ({cand.get('stock_code')}) - Score: {cand.get('condition_match_score')}\n")
            else:
                f.write("   - RPC returned NO candidates.\n")

        except Exception as e:
            f.write(f"\n❌ Error occurred: {e}\n")

if __name__ == "__main__":
    main()
