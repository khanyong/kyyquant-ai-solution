-- ============================================================================
-- 계좌 잔고 확인 및 allocated_capital 동적 계산
-- ============================================================================

-- 1. kw_account_balance 테이블 구조 확인
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'kw_account_balance'
ORDER BY ordinal_position;

-- 2. 현재 계좌 잔고 데이터 확인
SELECT
    '현재 계좌 잔고' as info,
    *
FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 1;

-- 3. 계좌 잔고가 있다면, 이를 기준으로 allocated_capital 계산
-- (주의: 실제 실행 전에 2번 쿼리 결과를 먼저 확인하세요!)

/*
-- 예시: deposit_before_withdraw 컬럼이 예수금이라고 가정
UPDATE strategies
SET allocated_capital = (allocated_percent / 100.0) * (
    SELECT CAST(deposit_before_withdraw AS NUMERIC)
    FROM kw_account_balance
    ORDER BY updated_at DESC
    LIMIT 1
)
WHERE auto_execute = true
AND is_active = true
AND allocated_percent > 0;
*/

-- 4. user_api_keys 테이블 구조 먼저 확인
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'user_api_keys'
ORDER BY ordinal_position;

-- 5. user_api_keys에서 계좌번호 확인
SELECT
    '등록된 계좌' as info,
    *
FROM user_api_keys
WHERE key_type = 'account_number'
ORDER BY created_at DESC;
