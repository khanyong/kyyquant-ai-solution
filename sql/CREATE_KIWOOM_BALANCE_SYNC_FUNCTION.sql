-- 키움 계좌 잔고 동기화 함수
-- 이 함수는 Edge Function에서 호출되어 키움 API 응답을 DB에 저장합니다

-- 1. 계좌 잔고 업데이트 함수
CREATE OR REPLACE FUNCTION sync_kiwoom_account_balance(
  p_user_id uuid,
  p_account_number varchar,
  p_balance_data jsonb
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_total_cash bigint;
  v_available_cash bigint;
  v_order_cash bigint;
  v_deposit bigint;
  v_substitute_money bigint;
BEGIN
  -- JSON에서 값 추출 (키움 API 응답 구조에 맞게 조정)
  v_total_cash := (p_balance_data->>'dnca_tot_amt')::bigint;
  v_available_cash := (p_balance_data->>'nxdy_excc_amt')::bigint;
  v_order_cash := (p_balance_data->>'ord_psbl_cash')::bigint;
  v_deposit := (p_balance_data->>'prvs_rcdl_excc_amt')::bigint;
  v_substitute_money := COALESCE((p_balance_data->>'pchs_amt_smtl_amt')::bigint, 0);

  -- 계좌 잔고 업데이트 (UPSERT)
  INSERT INTO kw_account_balance (
    user_id,
    account_number,
    total_cash,
    available_cash,
    order_cash,
    deposit,
    substitute_money,
    updated_at
  ) VALUES (
    p_user_id,
    p_account_number,
    v_total_cash,
    v_available_cash,
    v_order_cash,
    v_deposit,
    v_substitute_money,
    now()
  )
  ON CONFLICT (user_id, account_number)
  DO UPDATE SET
    total_cash = EXCLUDED.total_cash,
    available_cash = EXCLUDED.available_cash,
    order_cash = EXCLUDED.order_cash,
    deposit = EXCLUDED.deposit,
    substitute_money = EXCLUDED.substitute_money,
    updated_at = now();
END;
$$;

-- 2. 보유 종목 동기화 함수
CREATE OR REPLACE FUNCTION sync_kiwoom_portfolio(
  p_user_id uuid,
  p_account_number varchar,
  p_portfolio_data jsonb
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_item jsonb;
  v_stock_code varchar(20);
  v_stock_name varchar(100);
  v_quantity integer;
  v_available_quantity integer;
  v_avg_price decimal(15, 2);
  v_current_price decimal(15, 2);
  v_purchase_amount bigint;
  v_evaluated_amount bigint;
  v_profit_loss bigint;
  v_profit_loss_rate decimal(10, 4);
BEGIN
  -- 기존 포트폴리오 삭제 (동기화)
  DELETE FROM kw_portfolio
  WHERE user_id = p_user_id AND account_number = p_account_number;

  -- 새 데이터 삽입
  FOR v_item IN SELECT * FROM jsonb_array_elements(p_portfolio_data)
  LOOP
    v_stock_code := v_item->>'pdno';
    v_stock_name := v_item->>'prdt_name';
    v_quantity := (v_item->>'hldg_qty')::integer;
    v_available_quantity := (v_item->>'ord_psbl_qty')::integer;
    v_avg_price := (v_item->>'pchs_avg_pric')::decimal;
    v_current_price := (v_item->>'prpr')::decimal;
    v_purchase_amount := (v_item->>'pchs_amt')::bigint;
    v_evaluated_amount := (v_item->>'evlu_amt')::bigint;
    v_profit_loss := (v_item->>'evlu_pfls_amt')::bigint;
    v_profit_loss_rate := (v_item->>'evlu_pfls_rt')::decimal;

    INSERT INTO kw_portfolio (
      user_id,
      account_number,
      stock_code,
      stock_name,
      quantity,
      available_quantity,
      avg_price,
      purchase_amount,
      current_price,
      evaluated_amount,
      profit_loss,
      profit_loss_rate,
      updated_at
    ) VALUES (
      p_user_id,
      p_account_number,
      v_stock_code,
      v_stock_name,
      v_quantity,
      v_available_quantity,
      v_avg_price,
      v_purchase_amount,
      v_current_price,
      v_evaluated_amount,
      v_profit_loss,
      v_profit_loss_rate,
      now()
    );
  END LOOP;
END;
$$;

-- 3. 계좌 잔고 + 보유 종목 통합 업데이트 함수
CREATE OR REPLACE FUNCTION update_account_totals(
  p_user_id uuid,
  p_account_number varchar
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_stock_value bigint;
  v_total_profit_loss bigint;
  v_total_cash bigint;
  v_total_asset bigint;
  v_profit_loss_rate decimal(10, 4);
  v_total_purchase bigint;
BEGIN
  -- 보유 주식에서 총 평가액 및 손익 계산
  SELECT
    COALESCE(SUM(evaluated_amount), 0),
    COALESCE(SUM(profit_loss), 0),
    COALESCE(SUM(purchase_amount), 0)
  INTO
    v_stock_value,
    v_total_profit_loss,
    v_total_purchase
  FROM kw_portfolio
  WHERE user_id = p_user_id AND account_number = p_account_number;

  -- 현금 조회
  SELECT total_cash INTO v_total_cash
  FROM kw_account_balance
  WHERE user_id = p_user_id AND account_number = p_account_number;

  -- 총 자산 = 현금 + 주식평가액
  v_total_asset := COALESCE(v_total_cash, 0) + v_stock_value;

  -- 수익률 계산 (매입금액 대비)
  IF v_total_purchase > 0 THEN
    v_profit_loss_rate := (v_total_profit_loss::decimal / v_total_purchase::decimal) * 100;
  ELSE
    v_profit_loss_rate := 0;
  END IF;

  -- 계좌 잔고 테이블 업데이트
  UPDATE kw_account_balance
  SET
    total_asset = v_total_asset,
    stock_value = v_stock_value,
    profit_loss = v_total_profit_loss,
    profit_loss_rate = v_profit_loss_rate,
    updated_at = now()
  WHERE user_id = p_user_id AND account_number = p_account_number;
END;
$$;

-- 권한 부여
GRANT EXECUTE ON FUNCTION sync_kiwoom_account_balance TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION sync_kiwoom_portfolio TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION update_account_totals TO authenticated, service_role;

-- 사용 예시:
-- 1. 키움 API로부터 잔고 데이터를 받아서 동기화
/*
SELECT sync_kiwoom_account_balance(
  auth.uid(),
  '계좌번호',
  '{"dnca_tot_amt": "50000000", "nxdy_excc_amt": "45000000", ...}'::jsonb
);
*/

-- 2. 키움 API로부터 보유 종목 데이터를 받아서 동기화
/*
SELECT sync_kiwoom_portfolio(
  auth.uid(),
  '계좌번호',
  '[{"pdno": "005930", "prdt_name": "삼성전자", "hldg_qty": "100", ...}]'::jsonb
);
*/

-- 3. 합계 업데이트
/*
SELECT update_account_totals(auth.uid(), '계좌번호');
*/
