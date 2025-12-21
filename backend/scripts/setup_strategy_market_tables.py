
import os
import sys
from pathlib import Path

# Add backend directory to path to import supabase client
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from supabase import create_client, Client
from dotenv import load_dotenv

# Load key from .env file
load_dotenv(backend_path / '.env')

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

supabase: Client = create_client(url, key)

SQL_COMMANDS = [
    """
    -- 1. user_trading_accounts (Multi-Account Support)
    CREATE TABLE IF NOT EXISTS user_trading_accounts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES auth.users(id),
        account_type VARCHAR(20) CHECK (account_type IN ('mock', 'real')),
        account_number VARCHAR(20) NOT NULL,
        account_name VARCHAR(100),
        broker VARCHAR(20) DEFAULT 'kiwoom',
        
        -- OAuth Info
        access_token TEXT,
        refresh_token TEXT,
        token_expires_at TIMESTAMP WITH TIME ZONE,
        
        -- Status
        is_active BOOLEAN DEFAULT false,
        is_connected BOOLEAN DEFAULT false,
        last_sync_at TIMESTAMP WITH TIME ZONE,
        
        -- Balance Info
        initial_balance DECIMAL(15, 2),
        current_balance DECIMAL(15, 2),
        available_balance DECIMAL(15, 2),
        
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        
        UNIQUE(user_id, account_number)
    );
    """,
    """
    -- 2. strategy_marketplace (Strategy Listings)
    CREATE TABLE IF NOT EXISTS strategy_marketplace (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        strategy_id UUID REFERENCES strategies(strategy_id),
        creator_id UUID REFERENCES auth.users(id),
        
        -- Display Info
        title VARCHAR(100) NOT NULL,
        description TEXT,
        tags TEXT[],
        logo_url TEXT,
        
        -- Fee Structure
        fee_type VARCHAR(20) CHECK (fee_type IN ('monthly_sub', 'profit_share', 'free')),
        fee_amount DECIMAL(10, 2),
        
        -- Constraints
        min_capital DECIMAL(15, 2),
        
        -- Performance Stats (Cached)
        total_return DECIMAL(10, 2),
        cagr DECIMAL(10, 2),
        mdd DECIMAL(10, 2),
        win_rate DECIMAL(5, 2),
        subscriber_count INTEGER DEFAULT 0,
        
        is_public BOOLEAN DEFAULT false,
        is_verified BOOLEAN DEFAULT false,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    """
    -- 3. strategy_subscriptions (Following Logic)
    CREATE TABLE IF NOT EXISTS strategy_subscriptions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        follower_id UUID REFERENCES auth.users(id),
        follower_account_id UUID REFERENCES user_trading_accounts(id),
        market_strategy_id UUID REFERENCES strategy_marketplace(id),
        
        -- Settings
        allocation_amount DECIMAL(15, 2),
        allocation_type VARCHAR(20) DEFAULT 'fixed_amount',
        multiplier DECIMAL(4, 2) DEFAULT 1.0,
        
        status VARCHAR(20) CHECK (status IN ('active', 'paused', 'expired')),
        started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        expires_at TIMESTAMP WITH TIME ZONE,
        
        UNIQUE(follower_id, market_strategy_id)
    );
    """,
    """
    -- 4. strategy_daily_performance (For Sparkline Charts)
    CREATE TABLE IF NOT EXISTS strategy_daily_performance (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        strategy_id UUID REFERENCES strategies(strategy_id),
        date DATE NOT NULL,
        daily_return_pct DECIMAL(5, 2),
        total_return_pct DECIMAL(10, 2),
        equity_value DECIMAL(15, 2),
        
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(strategy_id, date)
    );
    """,
    """
    -- 5. copy_trading_logs (Audit Trail)
    CREATE TABLE IF NOT EXISTS copy_trading_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        subscription_id UUID REFERENCES strategy_subscriptions(id),
        original_signal_id UUID, -- Link to signal if exists
        follower_order_id UUID, -- Link to order if exists
        
        status VARCHAR(20),
        failure_reason TEXT,
        
        execution_price DECIMAL(10, 2),
        slippage DECIMAL(10, 2),
        
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    """
    -- RLS Policies (Basic Setup)
    ALTER TABLE user_trading_accounts ENABLE ROW LEVEL SECURITY;
    
    -- Drop existing policies if any to avoid errors on rerun
    DROP POLICY IF EXISTS "Users can view own accounts" ON user_trading_accounts;
    DROP POLICY IF EXISTS "Users can manage own accounts" ON user_trading_accounts;

    CREATE POLICY "Users can view own accounts" 
      ON user_trading_accounts FOR SELECT 
      USING (auth.uid() = user_id);

    CREATE POLICY "Users can manage own accounts" 
      ON user_trading_accounts FOR ALL 
      USING (auth.uid() = user_id);
      
    -- Strategy Marketplace is readable by everyone
    ALTER TABLE strategy_marketplace ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS "Public can view active strategies" ON strategy_marketplace;
    CREATE POLICY "Public can view active strategies" 
        ON strategy_marketplace FOR SELECT 
        USING (true);
    """
]

def run_migrations():
    print("Starting database migration for Strategy Market...")
    
    for i, sql in enumerate(SQL_COMMANDS):
        print(f"Executing block {i+1}...")
        try:
            # Note: The Supabase python client doesn't support raw SQL execution directly on the 'public' schema 
            # via the `rpc` interface unless a stored procedure is used, usually.
            # However, `supabase-py` wraps postgrest.
            # PostgREST doesn't support raw SQL execution for security reasons.
            # WE MUST USE the 'psycopg2' or similar approach OR use a predefined RPC function 'exec_sql' if it exists.
            # Let's check if 'exec_sql' exists or create it?
            # Actually, standard pattern often involves creating an RPC function via the SQL editor first.
            # But the user asked ME to create the tables.
            
            # Since I am in a dev environment and have the service role key, I should check if there is a 'exec_sql' function.
            # Many helper setups include one. If not, I am limited.
            
            # Let's try calling a known admin function or fallback to just printing the SQL 
            # if we can't execute it, instructing user to run it in SQL user interface.
            
            # BUT, wait. There is a `backend/check_strategy_system.py` that often does direct checks, 
            # maybe it uses `db.execute`? No, it usually uses `supabase.table().select()`.
            
            # CRITICAL: For creating tables, we really need direct SQL access.
            # Since we are an AI agent, we can create a .sql file and tell user to run it, 
            # OR we can try to use `psycopg2` if installed.
            # Let's check requirements.txt for psycopg2.
            pass
        except Exception as e:
            print(f"Error in block {i+1}: {e}")

    # Real python execution logic with psycopg2 (if available) - standard for python backends
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse connection string from DB_URL if available
        # Usually Supabase provides a direct connection string like "postgresql://postgres:[password]@db.supabase.co:5432/postgres"
        # We check provided .env file.
        db_url = os.environ.get("DATABASE_URL") # Often direct connection string
        if not db_url:
            print("DATABASE_URL not found in .env. Attempting to construct from components...")
            # Fallback not reliable without password.
            print("Cannot run migrations without DATABASE_URL (for direct SQL execution).")
            return

        print("Connecting to database via psycopg2...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        for i, sql in enumerate(SQL_COMMANDS):
            print(f"Executing SQL Block {i+1}...")
            cursor.execute(sql)
            
        print("All tables created successfully via direct connection!")
        conn.close()
        
    except ImportError:
        print("psycopg2 not installed. Cannot execute SQL directly.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migrations()
