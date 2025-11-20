-- 키움 계좌 잔고 동기화 함수
-- Edge Function: sync-kiwoom-balance에서 호출

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

  RAISE LOG 'sync_kiwoom_account_balance: user=%, account=%, total_cash=%',
    p_user_id, p_account_number, v_total_cash;

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

  RAISE LOG 'sync_kiwoom_account_balance: completed successfully';
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
  v_count integer := 0;
BEGIN
  RAISE LOG 'sync_kiwoom_portfolio: user=%, account=%, items=%',
    p_user_id, p_account_number, jsonb_array_length(p_portfolio_data);

  -- 기존 포트폴리오 삭제 (동기화)
  DELETE FROM kw_portfolio
  WHERE user_id = p_user_id AND account_number = p_account_number;

  -- 새 데이터 삽입
  FOR v_item IN SELECT * FROM jsonb_array_elements(p_portfolio_data)
  LOOP
    v_stock_code := v_item->>'pdno';
    v_stock_name := v_item->>'prdt_name';
    v_quantity := (v_item->>'hldg_qty')::integer;
    v_available_quantity := COALESCE((v_item->>'ord_psbl_qty')::integer, v_quantity);
    v_avg_price := (v_item->>'pchs_avg_pric')::decimal;
    v_current_price := (v_item->>'prpr')::decimal;

    -- 매입금액: API에서 제공되면 사용, 없으면 평균가 × 수량으로 계산
    v_purchase_amount := COALESCE(
      (v_item->>'pchs_amt')::bigint,
      (v_avg_price * v_quantity)::bigint
    );

    v_evaluated_amount := (v_item->>'evlu_amt')::bigint;

    -- 손익: API에서 제공되면 사용, 없으면 평가금액 - 매입금액으로 계산
    v_profit_loss := COALESCE(
      (v_item->>'evlu_pfls_amt')::bigint,
      v_evaluated_amount - v_purchase_amount
    );

    -- 손익률: API에서 제공되면 사용, 없으면 계산
    v_profit_loss_rate := COALESCE(
      (v_item->>'evlu_pfls_rt')::decimal,
      CASE
        WHEN v_purchase_amount > 0 THEN (v_profit_loss::decimal / v_purchase_amount::decimal) * 100
        ELSE 0
      END
    );

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

    v_count := v_count + 1;
  END LOOP;

  RAISE LOG 'sync_kiwoom_portfolio: inserted % items', v_count;
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
  RAISE LOG 'update_account_totals: user=%, account=%', p_user_id, p_account_number;

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

  RAISE LOG 'update_account_totals: total_asset=%, stock_value=%, profit_loss=%',
    v_total_asset, v_stock_value, v_total_profit_loss;

  -- 계좌 잔고 테이블 업데이트
  UPDATE kw_account_balance
  SET
    total_asset = v_total_asset,
    stock_value = v_stock_value,
    profit_loss = v_total_profit_loss,
    profit_loss_rate = v_profit_loss_rate,
    updated_at = now()
  WHERE user_id = p_user_id AND account_number = p_account_number;

  RAISE LOG 'update_account_totals: completed successfully';
END;
$$;

-- 권한 부여
GRANT EXECUTE ON FUNCTION sync_kiwoom_account_balance TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION sync_kiwoom_portfolio TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION update_account_totals TO authenticated, service_role;

-- 주석
COMMENT ON FUNCTION sync_kiwoom_account_balance IS '키움 API 응답에서 계좌 잔고 정보를 kw_account_balance 테이블에 동기화';
COMMENT ON FUNCTION sync_kiwoom_portfolio IS '키움 API 응답에서 보유 종목 정보를 kw_portfolio 테이블에 동기화';
COMMENT ON FUNCTION update_account_totals IS '보유 종목 정보를 기반으로 계좌 잔고의 합계 정보 업데이트';
