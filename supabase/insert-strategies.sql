-- 백테스팅용 전략 등록 SQL
-- Supabase SQL Editor에서 실행하세요

-- 기존 전략 삭제 (선택사항)
-- DELETE FROM strategies;

-- 1. 이동평균선 교차 전략
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  '이동평균선 교차 전략',
  '단기(20일)와 장기(60일) 이동평균선이 교차할 때 매매. 골든크로스시 매수, 데드크로스시 매도',
  'sma',
  '{
    "short_window": 20,
    "long_window": 60,
    "volume_filter": true,
    "volume_threshold": 1.5
  }'::jsonb,
  true,
  NOW()
);

-- 2. RSI 전략
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  'RSI 과매수/과매도',
  'RSI 30 이하에서 매수, 70 이상에서 매도. 다이버전스 신호 포함',
  'rsi',
  '{
    "rsi_period": 14,
    "oversold": 30,
    "overbought": 70,
    "use_divergence": true
  }'::jsonb,
  true,
  NOW()
);

-- 3. 모멘텀 전략
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  '모멘텀 추종',
  '최근 20일 수익률이 높은 종목 매수, 추세 추종 전략',
  'momentum',
  '{
    "lookback_period": 20,
    "threshold": 0.05,
    "stop_loss": 0.03,
    "take_profit": 0.1
  }'::jsonb,
  true,
  NOW()
);

-- 4. 볼린저 밴드 전략
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  '볼린저 밴드',
  '하단 밴드 터치시 매수, 상단 밴드 터치시 매도',
  'bollinger',
  '{
    "period": 20,
    "std_dev": 2,
    "use_middle_exit": true
  }'::jsonb,
  true,
  NOW()
);

-- 5. MACD 전략
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  'MACD 시그널',
  'MACD가 시그널선을 상향 돌파시 매수, 하향 돌파시 매도',
  'macd',
  '{
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9,
    "threshold": 0
  }'::jsonb,
  true,
  NOW()
);

-- 6. 거래량 폭증 전략
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  '거래량 폭증 돌파',
  '평균 거래량의 3배 이상 + 양봉시 매수',
  'volume_breakout',
  '{
    "volume_multiple": 3,
    "price_change_min": 0.02,
    "holding_period": 5
  }'::jsonb,
  true,
  NOW()
);

-- 7. 페어 트레이딩 (삼성전자-SK하이닉스)
INSERT INTO strategies (
  name,
  description,
  type,
  parameters,
  is_active,
  created_at
) VALUES (
  '반도체 페어 트레이딩',
  '삼성전자와 SK하이닉스 스프레드 거래',
  'pair_trading',
  '{
    "stock1": "005930",
    "stock2": "000660",
    "zscore_entry": 2,
    "zscore_exit": 0.5,
    "lookback": 60
  }'::jsonb,
  true,
  NOW()
);

-- 등록된 전략 확인
SELECT 
  id,
  name,
  type,
  description,
  parameters,
  is_active,
  created_at
FROM strategies
WHERE is_active = true
ORDER BY created_at DESC;