
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

# Load env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    print("Error: SUPABASE_URL not found in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def update_strategy():
    print("=== Updating Strategy to RSI 2 (High Frequency) ===")
    
    # 1. Find the target strategy
    target_name = 'kyy_short_term_v01'
    print(f"Searching for strategy: {target_name}...")
    
    response = supabase.table('strategies').select('*').ilike('name', f'%{target_name}%').execute()
    
    if not response.data:
        # If not uniquely found, try finding ANY active strategy
        print(f"   '{target_name}' not found. Searching for any active strategy...")
        response = supabase.table('strategies').select('*').eq('is_active', True).limit(1).execute()
        
    if not response.data:
        print("   No strategies found to update.")
        return

    strategy = response.data[0]
    strategy_id = strategy['id']
    print(f"   Target Strategy Found: {strategy['name']} (ID: {strategy_id})")

    # 2. Define new configuration
    new_config = {
        "name": f"{strategy['name']} (RSI 2 Test)",
        "description": "High frequency testing strategy using RSI(2)",
        "indicators": [
            {
                "name": "rsi",
                "period": 2
            }
        ],
        "buyConditions": [
            {
                "indicator": "rsi",
                "operator": "<",
                "value": 15
            }
        ],
        "sellConditions": [
            {
                "indicator": "rsi",
                "operator": ">",
                "value": 85
            }
        ],
        # Preserve other settings if needed, or overwrite
        "useStageBasedStrategy": False,
        "universe_id": strategy.get('universe_id') # Maintain universe
    }

    # 3. Update DB
    print("   Updating configuration in database...")
    
    # Update both the 'config' JSON column and top-level fields if they replicate logic
    # The backend mainly uses 'config' column if present.
    
    update_data = {
        "config": new_config,
        "updated_at": "now()"
    }
    
    result = supabase.table('strategies').update(update_data).eq('id', strategy_id).execute()
    
    if result.data:
        print("   [SUCCESS] Strategy updated successfully.")
        print(f"   New Config: {json.dumps(new_config, indent=2)}")
    else:
        print("   [ERROR] Update failed.")

if __name__ == "__main__":
    asyncio.run(update_strategy())
