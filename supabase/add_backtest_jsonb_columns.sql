-- backtest_results 테이블에 JSONB 컬럼 추가
-- 이미 존재하는 컬럼은 무시됨

-- Step 1: 현재 컬럼 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'backtest_results'
ORDER BY ordinal_position;

-- Step 2: JSONB 컬럼들 추가
-- trades: 거래 내역 저장
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS trades JSONB DEFAULT '[]'::jsonb;

-- daily_returns: 일별 수익률 저장
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS daily_returns JSONB DEFAULT '[]'::jsonb;

-- equity_curve: 자산 곡선 데이터
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS equity_curve JSONB;

-- investment_settings: 투자 설정 (초기자본, 수수료, 슬리피지 등)
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS investment_settings JSONB;

-- strategy_conditions: 전략 조건 (매수/매도 조건)
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS strategy_conditions JSONB;

-- filter_conditions: 필터 조건 (종목 필터링 조건)
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS filter_conditions JSONB;

-- metadata: 기타 메타데이터
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Step 3: 인덱스 추가 (JSONB 검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_backtest_metadata_gin ON backtest_results USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_backtest_strategy_conditions_gin ON backtest_results USING gin(strategy_conditions);

-- Step 4: 컬럼 추가 확인
SELECT
    column_name,
    data_type,
    CASE
        WHEN column_name IN ('trades', 'daily_returns', 'equity_curve', 'investment_settings', 'strategy_conditions', 'filter_conditions', 'metadata')
        THEN '✅ JSONB column'
        ELSE ''
    END as note
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'backtest_results'
ORDER BY ordinal_position;

-- Step 5: 코멘트 추가
COMMENT ON COLUMN backtest_results.trades IS '거래 내역 (JSONB)';
COMMENT ON COLUMN backtest_results.daily_returns IS '일별 수익률 데이터 (JSONB)';
COMMENT ON COLUMN backtest_results.equity_curve IS '자산 곡선 데이터 (JSONB)';
COMMENT ON COLUMN backtest_results.investment_settings IS '투자 설정 (초기자본, 수수료, 슬리피지 등)';
COMMENT ON COLUMN backtest_results.strategy_conditions IS '전략 조건 (매수/매도 조건)';
COMMENT ON COLUMN backtest_results.filter_conditions IS '필터 조건 (종목 필터링)';
COMMENT ON COLUMN backtest_results.metadata IS '기타 메타데이터 (필터링 모드, 종목 코드 등)';
