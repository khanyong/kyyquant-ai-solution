-- 데이터베이스 함수 실행 테스트 및 디버깅

-- ========================================
-- 1. 현재 사용자 정보 확인
-- ========================================
SELECT
  '사용자 정보' as check_type,
  auth.uid() as current_user_id,
  (SELECT kiwoom_account FROM profiles WHERE id = auth.uid()) as kiwoom_account,
  (SELECT COUNT(*) FROM user_api_keys WHERE user_id = auth.uid() AND provider = 'kiwoom' AND is_active = true) as active_api_keys;

-- ========================================
-- 2. 기존 데이터 확인
-- ========================================
SELECT '기존 계좌 잔고' as check_type, * FROM kw_account_balance WHERE user_id = auth.uid();
SELECT '기존 포트폴리오' as check_type, * FROM kw_portfolio WHERE user_id = auth.uid();

-- ========================================
-- 3. 함수 실행 테스트 (샘플 데이터)
-- ========================================

-- A. 계좌 잔고 동기화
SELECT sync_kiwoom_account_balance(
  auth.uid(),
  COALESCE((SELECT kiwoom_account FROM profiles WHERE id = auth.uid()), '8112-5100'),
  '{"dnca_tot_amt": "50000000", "nxdy_excc_amt": "45000000", "ord_psbl_cash": "45000000", "prvs_rcdl_excc_amt": "50000000", "pchs_amt_smtl_amt": "0"}'::jsonb
);

-- 결과 확인
SELECT
  '✅ 계좌 잔고 동기화 후' as status,
  user_id,
  account_number,
  total_cash,
  available_cash,
  order_cash,
  total_asset,
  stock_value,
  profit_loss,
  updated_at
FROM kw_account_balance
WHERE user_id = auth.uid()
ORDER BY updated_at DESC
LIMIT 1;

-- B. 포트폴리오 동기화
SELECT sync_kiwoom_portfolio(
  auth.uid(),
  COALESCE((SELECT kiwoom_account FROM profiles WHERE id = auth.uid()), '8112-5100'),
  '[
    {"pdno": "005930", "prdt_name": "삼성전자", "hldg_qty": "10", "ord_psbl_qty": "10", "pchs_avg_pric": "70000", "prpr": "71000", "pchs_amt": "700000", "evlu_amt": "710000", "evlu_pfls_amt": "10000", "evlu_pfls_rt": "1.43"},
    {"pdno": "000660", "prdt_name": "SK하이닉스", "hldg_qty": "5", "ord_psbl_qty": "5", "pchs_avg_pric": "130000", "prpr": "135000", "pchs_amt": "650000", "evlu_amt": "675000", "evlu_pfls_amt": "25000", "evlu_pfls_rt": "3.85"}
  ]'::jsonb
);

-- 결과 확인
SELECT
  '✅ 포트폴리오 동기화 후' as status,
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  avg_price,
  current_price,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at
FROM kw_portfolio
WHERE user_id = auth.uid()
ORDER BY evaluated_amount DESC;

-- C. 계좌 합계 업데이트
SELECT update_account_totals(
  auth.uid(),
  COALESCE((SELECT kiwoom_account FROM profiles WHERE id = auth.uid()), '8112-5100')
);

-- 최종 결과 확인
SELECT
  '✅ 합계 업데이트 후' as status,
  user_id,
  account_number,
  total_cash,
  available_cash,
  total_asset,
  stock_value,
  profit_loss,
  profit_loss_rate,
  updated_at
FROM kw_account_balance
WHERE user_id = auth.uid()
ORDER BY updated_at DESC
LIMIT 1;

-- ========================================
-- 4. RLS 정책 확인
-- ========================================
SELECT
  'RLS 정책' as check_type,
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd as command
FROM pg_policies
WHERE tablename IN ('kw_account_balance', 'kw_portfolio')
ORDER BY tablename, policyname;

-- ========================================
-- 예상 결과
-- ========================================

/*
✅ 정상인 경우:
1. 사용자 정보: user_id, kiwoom_account, active_api_keys=2
2. 계좌 잔고: total_cash = 50,000,000, stock_value = 1,385,000
3. 포트폴리오: 삼성전자 10주, SK하이닉스 5주
4. 합계: total_asset = 51,385,000

❌ 문제가 있는 경우:
1. kiwoom_account가 NULL → 프로필 업데이트 필요
2. active_api_keys = 0 → API 키 등록 필요
3. 데이터가 삽입되지 않음 → RLS 정책 문제
4. 에러 메시지 → 함수 실행 중 에러
*/
