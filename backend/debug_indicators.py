import asyncio
import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.strategy import check_strategy_signal, StrategySignalRequest, get_supabase_client
from dotenv import load_dotenv

load_dotenv()

async def debug_indicators():
    print("Debugging indicators for active strategy...")
    
    supabase = get_supabase_client()
    
    # 1. Fetch active strategy
    strategies = supabase.table('strategies').select('*').eq('is_active', True).limit(1).execute()
    if not strategies.data:
        print("No active strategy.")
        return
        
    strategy = strategies.data[0]
    strategy_id = strategy['id']
    print(f"Strategy: {strategy.get('name')} ({strategy_id})")
    
    # 2. Pick a stock that surely has data (Samsung)
    stock_code = "005930" 
    
    # 3. Call API logic manualy (to inspect internals better, but calling the function is easier)
    req = StrategySignalRequest(
        strategy_id=strategy_id,
        stock_code=stock_code
    )
    
    try:
        response = await check_strategy_signal(req)
        print(f"\n[Result for {stock_code}]")
        print(f"Stock Name: {response.stock_name}")
        print(f"Date: {response.debug_info.get('latest_date')}")
        print(f"Current Price: {response.current_price}")
        print(f"Signal: {response.signal_type}")
        print(f"Info: {response.debug_info}")
        
        # Print Indicators
        inds = response.indicators
        print("\n--- Calculated Indicators (Latest) ---")
        for k, v in inds.items():
            print(f"{k}: {v}")
            
        # Print Conditions vs Values
        # We need to manually match them to debug
        print("\n--- Conditions Evaluation ---")
        config = strategy.get('config') or strategy
        stages = config.get('buyStageStrategy', {}).get('stages', [])
        if stages:
            stage1 = stages[0]
            print("Stage 1 Conditions:")
            for cond in stage1.get('conditions', []):
                left_key = cond.get('left')
                right_key = cond.get('right')
                op = cond.get('operator')
                
                left_val = inds.get(left_key, 'N/A')
                right_val = inds.get(right_key, cond.get('right')) # value might be literal
                
                print(f"  {left_key}({left_val}) {op} {right_key}({right_val})")
        else:
            print("Not stage based?")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_indicators())
