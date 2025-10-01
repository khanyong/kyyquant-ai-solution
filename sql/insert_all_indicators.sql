-- 전략빌더에서 사용하는 모든 지표 데이터 삽입
-- AVAILABLE_INDICATORS 배열의 모든 지표 포함

-- 1. MA (이동평균)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'ma',
  'MA (이동평균)',
  '단순 이동평균선',
  'trend',
  'built-in',
  '{"method": "rolling_mean", "source": "close", "calculation": "df[source].rolling(window=period).mean()"}',
  '{"period": 20}',
  ARRAY['close'],
  ARRAY['ma']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 2. SMA (단순이동평균)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'sma',
  'SMA (단순이동평균)',
  'Simple Moving Average',
  'trend',
  'built-in',
  '{"method": "rolling_mean", "source": "close"}',
  '{"period": 20}',
  ARRAY['close'],
  ARRAY['sma']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 3. EMA (지수이동평균)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'ema',
  'EMA (지수이동평균)',
  'Exponential Moving Average',
  'trend',
  'built-in',
  '{"method": "ewm_mean", "source": "close", "calculation": "df[source].ewm(span=period, adjust=False).mean()"}',
  '{"period": 20}',
  ARRAY['close'],
  ARRAY['ema']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 4. BB (볼린저밴드)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'bb',
  '볼린저밴드',
  'Bollinger Bands',
  'volatility',
  'built-in',
  '{"method": "bollinger", "source": "close"}',
  '{"period": 20, "std": 2}',
  ARRAY['close'],
  ARRAY['bb_upper', 'bb_middle', 'bb_lower']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 5. RSI
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'rsi',
  'RSI',
  'Relative Strength Index',
  'momentum',
  'built-in',
  '{"method": "rsi", "source": "close", "calculation": "100 - (100 / (1 + RS))", "description": "RS = Average Gain / Average Loss over period"}',
  '{"period": 14}',
  ARRAY['close'],
  ARRAY['rsi']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 6. MACD
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'macd',
  'MACD',
  'Moving Average Convergence Divergence',
  'momentum',
  'built-in',
  '{"method": "macd", "source": "close", "calculation": "EMA(12) - EMA(26), Signal = EMA(9) of MACD, Histogram = MACD - Signal"}',
  '{"fast": 12, "slow": 26, "signal": 9}',
  ARRAY['close'],
  ARRAY['macd_line', 'macd_signal', 'macd_hist']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 7. Stochastic (스토캐스틱)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'stochastic',
  '스토캐스틱',
  'Stochastic Oscillator',
  'momentum',
  'built-in',
  '{"method": "stochastic"}',
  '{"k": 14, "d": 3}',
  ARRAY['high', 'low', 'close'],
  ARRAY['stochastic_k', 'stochastic_d']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 8. Ichimoku (일목균형표)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'ichimoku',
  '일목균형표',
  'Ichimoku Cloud',
  'trend',
  'built-in',
  '{"method": "ichimoku"}',
  '{"tenkan": 9, "kijun": 26, "senkou": 52, "chikou": 26}',
  ARRAY['high', 'low', 'close'],
  ARRAY['tenkan', 'kijun', 'senkou_a', 'senkou_b', 'chikou']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 9. Volume (거래량)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'volume',
  '거래량',
  'Trading Volume',
  'volume',
  'built-in',
  '{"method": "volume", "source": "volume"}',
  '{"period": 20}',
  ARRAY['volume'],
  ARRAY['volume', 'volume_ma']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 10. OBV (On Balance Volume)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'obv',
  'OBV (누적거래량)',
  'On Balance Volume',
  'volume',
  'built-in',
  '{"method": "obv"}',
  '{}',
  ARRAY['close', 'volume'],
  ARRAY['obv']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 11. VWAP (Volume Weighted Average Price)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'vwap',
  'VWAP (거래량가중평균)',
  'Volume Weighted Average Price',
  'volume',
  'built-in',
  '{"method": "vwap"}',
  '{}',
  ARRAY['high', 'low', 'close', 'volume'],
  ARRAY['vwap']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 12. ATR (Average True Range)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'atr',
  'ATR (변동성)',
  'Average True Range',
  'volatility',
  'built-in',
  '{"method": "atr"}',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['atr']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 13. CCI (Commodity Channel Index)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'cci',
  'CCI',
  'Commodity Channel Index',
  'momentum',
  'built-in',
  '{"method": "cci"}',
  '{"period": 20}',
  ARRAY['high', 'low', 'close'],
  ARRAY['cci']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 14. Williams %R
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'williams',
  'Williams %R',
  'Williams Percent Range',
  'momentum',
  'built-in',
  '{"method": "williams"}',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['williams_r']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 15. ADX (Average Directional Index)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'adx',
  'ADX (추세강도)',
  'Average Directional Index',
  'trend',
  'built-in',
  '{"method": "adx"}',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['adx']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 16. DMI (Directional Movement Index)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'dmi',
  'DMI (+DI/-DI)',
  'Directional Movement Index',
  'trend',
  'built-in',
  '{"method": "dmi"}',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['plus_di', 'minus_di']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 17. Parabolic SAR
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'parabolic',
  'Parabolic SAR',
  'Parabolic Stop and Reverse',
  'trend',
  'built-in',
  '{"method": "parabolic_sar"}',
  '{"acc": 0.02, "max": 0.2}',
  ARRAY['high', 'low'],
  ARRAY['psar']
) ON CONFLICT (name) DO UPDATE SET
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 18. 추가 기본 지표들
-- Price (현재가)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'price',
  '현재가',
  'Current Price',
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

-- Close (종가)
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

-- bollinger (별칭)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'bollinger',
  '볼린저밴드',
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

-- volume_ma (거래량 이동평균)
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