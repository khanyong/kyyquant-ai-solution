import os
import sys

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

def manual_load_env():
    env_paths = ['.env', '.env.development']
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()

def apply_fix():
    print("Loading environment...")
    manual_load_env()
    
    # Try to find DB URL
    db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("SUPABASE_DB_URL")
    
    if not db_url:
        print("❌ DATABASE_URL not found in .env")
        # Try to construct from components if available
        host = os.getenv("POSTGRES_HOST") or os.getenv("DB_HOST")
        user = os.getenv("POSTGRES_USER") or os.getenv("DB_USER") or "postgres"
        password = os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD")
        port = os.getenv("POSTGRES_PORT") or "5432"
        db = os.getenv("POSTGRES_DB") or "postgres"
        
        if host and password:
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
            print(f"Constructed DB URL: postgresql://{user}:***@{host}:{port}/{db}")
        else:
            print("❌ Could not construct DB URL. Missing credentials.")
            return

    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 module not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2

    print("Connecting to Database...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        sql_file = 'sql/FIX_RPC_WITH_USER_ID.sql'
        print(f"Reading {sql_file}...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        print("Executing SQL Patch...")
        cur.execute(sql_content)
        
        print("✅ SQL Patch Applied Successfully!")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    apply_fix()
