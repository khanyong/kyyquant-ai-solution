import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

def main():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)
    
    print("Checking active strategies...")
    try:
        response = supabase.rpc('get_active_strategies_with_universe').execute()
        strategies = response.data
        print(f"Count: {len(strategies) if strategies else 0}")
        if strategies:
            print(json.dumps(strategies, indent=2, ensure_ascii=False))
        else:
            print("No active strategies returned.")
            
    except Exception as e:
        print(f"RPC Error: {e}")

if __name__ == "__main__":
    main()
