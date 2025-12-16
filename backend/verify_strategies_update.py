
import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    with open('verify_output.txt', 'w', encoding='utf-8') as f:
        if not url or not key:
            f.write("Error: Supabase credentials not found in .env\n")
            return

        try:
            supabase = create_client(url, key)
            
            f.write("="*60 + "\n")
            f.write("VERIFYING STRATEGIES AND MONITORING STOCKS\n")
            f.write("="*60 + "\n")
            
            # Call the RPC function
            response = supabase.rpc('get_active_strategies_with_universe').execute()
            strategies = response.data
            
            if not strategies:
                f.write("No active strategies found.\n")
                return

            f.write(f"Found {len(strategies)} active strategies.\n\n")
            
            for i, strategy in enumerate(strategies, 1):
                f.write(f"Strategy #{i}\n")
                f.write(f"  ID: {strategy.get('strategy_id')}\n")
                f.write(f"  Name: {strategy.get('strategy_name')}\n")
                f.write(f"  Filter Name: {strategy.get('filter_name')}\n")
                f.write(f"  Allocated Capital: {strategy.get('allocated_capital'):,.0f} KRW ({strategy.get('allocated_percent')}%)\n")
                
                universe = strategy.get('filtered_stocks')
                if universe:
                    count = len(universe)
                    f.write(f"  Monitoring Stock Count: {count}\n")
                    if count > 0:
                        f.write(f"  First 10 Stocks: {universe[:10]}\n")
                        if count > 10:
                            f.write(f"  Last 5 Stocks:  {universe[-5:]}\n")
                else:
                    f.write("  Monitoring Stock Count: 0\n")
                
                f.write("-" * 60 + "\n")

        except Exception as e:
            f.write(f"An error occurred: {e}\n")

if __name__ == "__main__":
    main()
