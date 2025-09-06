-- ============================================
-- 시장 데이터만 초기화 (사용자 데이터는 유지)
-- ============================================

-- ============================
-- 보존할 테이블 (사용자 관련)
-- ============================
-- ✅ profiles (사용자 프로필)
-- ✅ portfolio (포트폴리오)
-- ✅ orders (주문 기록)
-- ✅ strategies (전략)
-- ✅ backtest_results (백테스트 결과)
-- ✅ trading_signals (매매 신호)
-- ✅ account_balance (계좌 잔고)
-- ✅ positions (포지션)
-- ✅ trades (거래 기록)

-- ============================
-- 삭제할 테이블 (시장 데이터)
-- ============================

-- 1. 외래키 제약 임시 제거 (나중에 재연결)
ALTER TABLE IF EXISTS orders DROP CONSTRAINT IF EXISTS orders_stock_code_fkey;
ALTER TABLE IF EXISTS portfolio DROP CONSTRAINT IF EXISTS portfolio_stock_code_fkey;
ALTER TABLE IF EXISTS trading_signals DROP CONSTRAINT IF EXISTS trading_signals_stock_code_fkey;
ALTER TABLE IF EXISTS positions DROP CONSTRAINT IF EXISTS positions_stock_code_fkey;
ALTER TABLE IF EXISTS trades DROP CONSTRAINT IF EXISTS trades_stock_code_fkey;

-- 2. 시장 데이터 테이블만 삭제
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS stock_master CASCADE;
DROP TABLE IF EXISTS price_data CASCADE;
DROP TABLE IF EXISTS price_daily CASCADE;
DROP TABLE IF EXISTS price_weekly CASCADE;
DROP TABLE IF EXISTS price_monthly CASCADE;
DROP TABLE IF EXISTS price_minute CASCADE;
DROP TABLE IF EXISTS market_data CASCADE;
DROP TABLE IF EXISTS market_data_cache CASCADE;
DROP TABLE IF EXISTS market_index CASCADE;  -- 시장 지수도 새로 받을 예정
DROP TABLE IF EXISTS news_alerts CASCADE;
DROP TABLE IF EXISTS realtime_prices CASCADE;
DROP TABLE IF EXISTS realtime_price CASCADE;
DROP TABLE IF EXISTS financial_ratios CASCADE;
DROP TABLE IF EXISTS financial_statement CASCADE;
DROP TABLE IF EXISTS investor_trading CASCADE;
DROP TABLE IF EXISTS investor_trade CASCADE;
DROP TABLE IF EXISTS technical_indicators CASCADE;
DROP TABLE IF EXISTS orderbook CASCADE;
DROP TABLE IF EXISTS current_price CASCADE;

-- 3. 기존 kw_ 테이블도 삭제 (있다면)
DROP TABLE IF EXISTS kw_stock_master CASCADE;
DROP TABLE IF EXISTS kw_stock_sector CASCADE;
DROP TABLE IF EXISTS kw_stock_theme CASCADE;
DROP TABLE IF EXISTS kw_price_daily CASCADE;
DROP TABLE IF EXISTS kw_price_weekly CASCADE;
DROP TABLE IF EXISTS kw_price_monthly CASCADE;
DROP TABLE IF EXISTS kw_price_minute CASCADE;
DROP TABLE IF EXISTS kw_price_current CASCADE;
DROP TABLE IF EXISTS kw_price_orderbook CASCADE;
DROP TABLE IF EXISTS kw_financial_statement CASCADE;
DROP TABLE IF EXISTS kw_financial_ratio CASCADE;
DROP TABLE IF EXISTS kw_investor_trade CASCADE;
DROP TABLE IF EXISTS kw_investor_holding CASCADE;
DROP TABLE IF EXISTS kw_info_disclosure CASCADE;
DROP TABLE IF EXISTS kw_info_news CASCADE;
DROP TABLE IF EXISTS kw_info_report CASCADE;
DROP TABLE IF EXISTS kw_market_sector CASCADE;
DROP TABLE IF EXISTS kw_market_theme CASCADE;
DROP TABLE IF EXISTS kw_market_program CASCADE;
DROP TABLE IF EXISTS kw_indicator_technical CASCADE;
DROP TABLE IF EXISTS kw_trade_execution CASCADE;

-- 4. 백업 테이블 삭제 (있다면)
DROP TABLE IF EXISTS _old_stocks CASCADE;
DROP TABLE IF EXISTS _old_price_data CASCADE;
DROP TABLE IF EXISTS _old_market_data CASCADE;
DROP TABLE IF EXISTS _old_news_alerts CASCADE;
DROP TABLE IF EXISTS _backup_stocks CASCADE;
DROP TABLE IF EXISTS _backup_price_data CASCADE;
DROP TABLE IF EXISTS _backup_market_data CASCADE;
DROP TABLE IF EXISTS _backup_news_alerts CASCADE;

-- 5. 확인 (보존된 테이블)
SELECT '=== 보존된 사용자 테이블 ===' as status;
SELECT 
    table_name,
    'PRESERVED' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN (
        'profiles', 
        'portfolio', 
        'orders', 
        'strategies', 
        'backtest_results',
        'trading_signals',
        'account_balance',
        'positions',
        'trades'
    )
ORDER BY table_name;

-- 6. 시장 지수 테이블 재생성 (필요)
CREATE TABLE IF NOT EXISTS market_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_code VARCHAR(20) NOT NULL,
    index_name VARCHAR(100) NOT NULL,
    current_value DECIMAL(10, 2) NOT NULL,
    change_value DECIMAL(10, 2),
    change_rate DECIMAL(5, 2),
    trading_volume BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_code)
);

-- 7. 이제 create_all_tables_consistent.sql 실행
-- 다음 명령: kw_ 테이블 생성

SELECT '✅ Market data cleared! User data preserved.' as result;
SELECT '👉 Next: Run create_all_tables_consistent.sql' as next_step;

-- 8. 사용자 데이터 통계
SELECT 
    'User Data Statistics' as category,
    'profiles' as table_name,
    COUNT(*) as count
FROM profiles
UNION ALL
SELECT 
    'User Data Statistics',
    'strategies',
    COUNT(*)
FROM strategies
UNION ALL
SELECT 
    'User Data Statistics',
    'backtest_results',
    COUNT(*)
FROM backtest_results
UNION ALL
SELECT 
    'User Data Statistics',
    'orders',
    COUNT(*)
FROM orders;