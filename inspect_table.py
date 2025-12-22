
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import datetime # Import missing module

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Handle encoding gracefully if possible, or just let python handle it
try:
    load_dotenv('backend/.env', encoding='utf-8')
except:
    load_dotenv('backend/.env')

def inspect():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    sb = create_client(url, key)
    
    print("Attempting INSERT...")
    try:
        data = {
            'index_id': 'TEST_UUID_OR_STRING', 
            'index_code': 'TEST',
            'current_value': 123.45,
            'change_value': 1.23,
            'change_rate': 1.0,
            'timestamp': datetime.datetime.now().isoformat()
        }
        res = sb.table('market_index').insert(data).execute()
        print("Insert Success:", res.data)
    except Exception as e:
        print("Insert ErrorDetails:", getattr(e, 'details', 'No Details'))
        print("Insert Error:", e)

if __name__ == '__main__':
    inspect()
