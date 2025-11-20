"""
기존 지표 하나를 상세히 확인
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

# 환경변수 로드
load_dotenv()

def check_existing():
    """기존 지표 확인"""

    # Supabase 연결
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return

    supabase = create_client(url, key)

    # sma 지표 확인
    try:
        response = supabase.table('indicators').select('*').eq('name', 'sma').execute()
        if response.data:
            indicator = response.data[0]
            print("SMA indicator details:")
            for key, value in indicator.items():
                print(f"{key}: {value}")
                if key == 'formula' and value:
                    try:
                        formula = json.loads(value)
                        print(f"  Parsed formula: {formula}")
                    except:
                        pass
        else:
            print("SMA indicator not found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_existing()