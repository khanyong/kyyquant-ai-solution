-- kw_account_balance 테이블에 UNIQUE 제약 조건 추가
-- 문제: user_id + account_number 조합의 유니크 제약이 없으면 중복 데이터가 생길 수 있음

-- 1. 기존 중복 데이터 확인
SELECT
  user_id,
  account_number,
  COUNT(*) as count
FROM kw_account_balance
GROUP BY user_id, account_number
HAVING COUNT(*) > 1;

-- 중복 데이터가 있다면, 최신 것만 남기고 삭제
WITH ranked_balances AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      PARTITION BY user_id, account_number
      ORDER BY updated_at DESC
    ) as rn
  FROM kw_account_balance
)
DELETE FROM kw_account_balance
WHERE id IN (
  SELECT id FROM ranked_balances WHERE rn > 1
);

-- 2. UNIQUE 제약 조건 추가 (없는 경우)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uq_kw_account_balance_user_account'
      AND conrelid = 'kw_account_balance'::regclass
  ) THEN
    ALTER TABLE kw_account_balance
    ADD CONSTRAINT uq_kw_account_balance_user_account
    UNIQUE (user_id, account_number);

    RAISE NOTICE 'UNIQUE constraint added successfully';
  ELSE
    RAISE NOTICE 'UNIQUE constraint already exists';
  END IF;
END $$;

-- 3. kw_portfolio 테이블도 동일하게 처리
WITH ranked_portfolio AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      PARTITION BY user_id, account_number, stock_code
      ORDER BY updated_at DESC
    ) as rn
  FROM kw_portfolio
)
DELETE FROM kw_portfolio
WHERE id IN (
  SELECT id FROM ranked_portfolio WHERE rn > 1
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uq_kw_portfolio_user_account_stock'
      AND conrelid = 'kw_portfolio'::regclass
  ) THEN
    ALTER TABLE kw_portfolio
    ADD CONSTRAINT uq_kw_portfolio_user_account_stock
    UNIQUE (user_id, account_number, stock_code);

    RAISE NOTICE 'UNIQUE constraint added to kw_portfolio';
  ELSE
    RAISE NOTICE 'UNIQUE constraint already exists on kw_portfolio';
  END IF;
END $$;

-- 4. 결과 확인
SELECT
  conname as constraint_name,
  contype as type,
  pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid IN ('kw_account_balance'::regclass, 'kw_portfolio'::regclass)
  AND contype = 'u';  -- UNIQUE constraints only
