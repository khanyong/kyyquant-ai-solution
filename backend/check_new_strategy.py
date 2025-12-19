
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    print("Error: SUPABASE_URL not found")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_strategy():
    print("=== Checking Strategy: 스캘핑테스트 전략 ===")
    
    # Search for the strategy
    response = supabase.table('strategies').select('*').ilike('name', '%스캘핑테스트%').execute()
    
    if not response.data:
        print("Strategy not found.")
        return

    for s in response.data:
        print(f"\n[Found Strategy]")
        print(f"Name: {s['name']}")
        print(f"ID: {s['id']}")
        print(f"Active: {s.get('is_active')}")
        print(f"Universe ID: {s.get('universe_id')}")
        
        config = s.get('config') or s
        print("\n[Configuration]")
        print(f"Indicators: {json.dumps(config.get('indicators'), indent=2, ensure_ascii=False)}")
        print(f"Buy Conditions: {json.dumps(config.get('buyConditions'), indent=2, ensure_ascii=False)}")
        print(f"Sell Conditions: {json.dumps(config.get('sellConditions'), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(check_strategy())
