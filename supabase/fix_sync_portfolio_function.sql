-- 키움 포트폴리오 동기화 함수 수정
-- 문제: purchase_amount, profit_loss 등이 NULL이 되어 INSERT 실패
-- 해결: COALESCE를 사용해서 API 필드가 없으면 계산하도록 수정

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

-- 테스트 실행
SELECT '✅ 함수 업데이트 완료' as status;
