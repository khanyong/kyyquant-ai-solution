-- 데이터베이스 함수 직접 테스트

-- ========================================
-- 1. 테스트 잔고 데이터로 sync 함수 호출
-- ========================================
SELECT sync_kiwoom_account_balance(
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,  -- user_id
  '8112-5100',  -- account_number
  '{
    "dnca_tot_amt": "9500000",
    "nxdy_excc_amt": "9500000",
    "scts_evlu_amt": "500000",
    "tot_evlu_amt": "10000000",
    "evlu_pfls_smtl_amt": "50000"
  }'::jsonb  -- 테스트 잔고 데이터
);

-- ========================================
-- 2. 저장된 잔고 확인
-- ========================================
SELECT
  '잔고 데이터 확인' as test_type,
  total_cash,
  available_cash,
  stock_value,
  total_asset,
  profit_loss,
  updated_at,
  NOW() - updated_at as seconds_ago
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- ========================================
-- 3. 테스트 포트폴리오 데이터로 sync 함수 호출
-- ========================================
SELECT sync_kiwoom_portfolio(
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,  -- user_id
  '8112-5100',  -- account_number
  '[
    {
      "pdno": "005930",
      "prdt_name": "삼성전자",
      "hldg_qty": "10",
      "pchs_avg_pric": "70000",
      "prpr": "72000",
      "evlu_amt": "720000"
    }
  ]'::jsonb  -- 테스트 포트폴리오 데이터
);

-- ========================================
-- 4. 저장된 포트폴리오 확인
-- ========================================
SELECT
  '포트폴리오 데이터 확인' as test_type,
  stock_code,
  stock_name,
  quantity,
  avg_price,
  current_price,
  evaluated_amount,
  updated_at,
  NOW() - updated_at as seconds_ago
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC;

-- ========================================
-- 5. update_account_totals 함수 호출
-- ========================================
SELECT update_account_totals(
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
  '8112-5100'
);

-- ========================================
-- 6. 최종 잔고 확인 (합계가 업데이트되었는지)
-- ========================================
SELECT
  '최종 잔고 확인' as test_type,
  total_cash,
  available_cash,
  stock_value,
  total_asset,
  profit_loss,
  updated_at
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;
