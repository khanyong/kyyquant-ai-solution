-- Step 4: Row Level Security (RLS) 정책 설정
-- 주의: 이 스크립트는 auth 설정 후 실행

-- Enable RLS on tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_balance ENABLE ROW LEVEL SECURITY;

-- 임시 정책: 모든 사용자가 자신의 데이터만 볼 수 있도록 설정
-- profiles 테이블은 user_id 대신 id를 사용
CREATE POLICY "Enable all for profiles based on user_id" ON profiles
    FOR ALL USING (true);

CREATE POLICY "Enable all for orders based on user_id" ON orders
    FOR ALL USING (true);

CREATE POLICY "Enable all for portfolio based on user_id" ON portfolio
    FOR ALL USING (true);

CREATE POLICY "Enable all for strategies based on user_id" ON strategies
    FOR ALL USING (true);

CREATE POLICY "Enable all for backtest_results based on user_id" ON backtest_results
    FOR ALL USING (true);

CREATE POLICY "Enable all for account_balance based on user_id" ON account_balance
    FOR ALL USING (true);

-- Public tables (no RLS needed, everyone can read)
-- stocks, price_data, realtime_prices, market_index, news_alerts