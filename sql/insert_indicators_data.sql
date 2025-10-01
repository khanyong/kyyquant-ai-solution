-- 기본 지표 데이터 삽입
-- 기존의 하드코딩된 지표들을 데이터베이스로 이전

-- 1. 이동평균 (MA)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'ma',
  '이동평균 (MA)',
  '단순 이동평균선',
  'trend',
  'built-in',
  '{"method": "rolling_mean", "source": "close"}',
  '{"period": 20}',
  ARRAY['close'],
  ARRAY['ma']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 2. 지수이동평균 (EMA)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'ema',
  '지수이동평균 (EMA)',
  '지수 가중 이동평균선',
  'trend',
  'built-in',
  '{"method": "ewm_mean", "source": "close"}',
  '{"period": 20}',
  ARRAY['close'],
  ARRAY['ema']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 3. RSI
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'rsi',
  'RSI',
  '상대강도지수 (Relative Strength Index)',
  'momentum',
  'built-in',
  '{"method": "rsi", "source": "close"}',
  '{"period": 14}',
  ARRAY['close'],
  ARRAY['rsi']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 4. MACD
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'macd',
  'MACD',
  'Moving Average Convergence Divergence',
  'momentum',
  'built-in',
  '{"method": "macd", "source": "close"}',
  '{"fast": 12, "slow": 26, "signal": 9}',
  ARRAY['close'],
  ARRAY['macd_line', 'macd_signal', 'macd_hist']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 5. 볼린저 밴드
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'bollinger',
  '볼린저 밴드',
  'Bollinger Bands',
  'volatility',
  'built-in',
  '{"method": "bollinger", "source": "close"}',
  '{"period": 20, "std": 2}',
  ARRAY['close'],
  ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 6. 스토캐스틱
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'stochastic',
  '스토캐스틱',
  'Stochastic Oscillator',
  'momentum',
  'built-in',
  '{"method": "stochastic"}',
  '{"k_period": 14, "d_period": 3}',
  ARRAY['high', 'low', 'close'],
  ARRAY['stochastic_k', 'stochastic_d']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 7. 거래량 이동평균
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'volume_ma',
  '거래량 이동평균',
  'Volume Moving Average',
  'volume',
  'built-in',
  '{"method": "rolling_mean", "source": "volume"}',
  '{"period": 20}',
  ARRAY['volume'],
  ARRAY['volume_ma']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 8. 커스텀 지표 예시: 가격 변화율
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'price_change_rate',
  '가격 변화율',
  'Price Change Rate',
  'momentum',
  'custom_formula',
  '{"formula": "(close - close.shift(period)) / close.shift(period) * 100"}',
  '{"period": 5}',
  ARRAY['close'],
  ARRAY['price_change_rate']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 9. 가격 지표 (PRICE/CLOSE)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'price',
  '현재가',
  'Current Price (Close)',
  'price',
  'built-in',
  '{"method": "price", "source": "close"}',
  '{}',
  ARRAY['close'],
  ARRAY['price']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 10. 종가 (CLOSE)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'close',
  '종가',
  'Closing Price',
  'price',
  'built-in',
  '{"method": "close", "source": "close"}',
  '{}',
  ARRAY['close'],
  ARRAY['close']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 11. 거래량 (VOLUME)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'volume',
  '거래량',
  'Trading Volume',
  'volume',
  'built-in',
  '{"method": "volume", "source": "volume"}',
  '{}',
  ARRAY['volume'],
  ARRAY['volume']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 12. Cross Above (교차 상승)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'cross_above',
  '교차 상승',
  'Cross Above Indicator',
  'signal',
  'built-in',
  '{"method": "cross_above"}',
  '{}',
  ARRAY['close'],
  ARRAY['cross_above']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 13. Cross Below (교차 하락)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'cross_below',
  '교차 하락',
  'Cross Below Indicator',
  'signal',
  'built-in',
  '{"method": "cross_below"}',
  '{}',
  ARRAY['close'],
  ARRAY['cross_below']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 14. Python 코드 지표 예시: 커스텀 모멘텀
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'custom_momentum',
  '커스텀 모멘텀',
  'Custom Momentum Indicator',
  'momentum',
  'python_code',
  '{
    "code": "import pandas as pd\nimport numpy as np\n\ndef calculate(df, params):\n    period = params.get(''period'', 10)\n    multiplier = params.get(''multiplier'', 2)\n    \n    # 모멘텀 계산\n    momentum = df[''close''].diff(period)\n    \n    # 스무딩\n    df[''custom_momentum''] = momentum.rolling(window=5).mean() * multiplier\n    \n    return df"
  }',
  '{"period": 10, "multiplier": 2}',
  ARRAY['close'],
  ARRAY['custom_momentum']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();