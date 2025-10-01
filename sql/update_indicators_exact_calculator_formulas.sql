-- calculator.py의 정확한 구현을 기반으로 한 지표 업데이트
-- 각 지표의 계산식을 정확하게 반영

-- ========================================
-- 1. MA (이동평균) - _calc_legacy의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rolling_mean", "source": "close", "description": "df[\"close\"].rolling(window=period).mean()"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['ma'],
  updated_at = NOW()
WHERE name = 'ma';

-- ========================================
-- 2. SMA (단순이동평균) - MA와 동일
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rolling_mean", "source": "close", "description": "df[\"close\"].rolling(window=period).mean()"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['sma'],
  updated_at = NOW()
WHERE name = 'sma';

-- ========================================
-- 3. EMA (지수이동평균) - _calc_legacy의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "ewm_mean", "source": "close", "description": "df[\"close\"].ewm(span=period, adjust=False).mean()"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['ema'],
  updated_at = NOW()
WHERE name = 'ema';

-- ========================================
-- 4. BB (볼린저밴드) - _calc_bollinger의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "sma = df[\"close\"].rolling(window=params.get(\"period\", 20)).mean(); std = df[\"close\"].rolling(window=params.get(\"period\", 20)).std(); std_dev = params.get(\"std\", 2); result = {\"bb_upper\": sma + (std * std_dev), \"bb_middle\": sma, \"bb_lower\": sma - (std * std_dev)}"
  }',
  default_params = '{"period": 20, "std": 2}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['bb_upper', 'bb_middle', 'bb_lower'],
  updated_at = NOW()
WHERE name = 'bb';

-- ========================================
-- 5. RSI - _calc_rsi의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "delta = df[\"close\"].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=params.get(\"period\", 14)).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=params.get(\"period\", 14)).mean(); rs = gain / loss; result = 100 - (100 / (1 + rs))"
  }',
  default_params = '{"period": 14}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['rsi'],
  updated_at = NOW()
WHERE name = 'rsi';

-- ========================================
-- 6. MACD - _calc_macd의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "exp1 = df[\"close\"].ewm(span=params.get(\"fast\", 12), adjust=False).mean(); exp2 = df[\"close\"].ewm(span=params.get(\"slow\", 26), adjust=False).mean(); macd_line = exp1 - exp2; macd_signal = macd_line.ewm(span=params.get(\"signal\", 9), adjust=False).mean(); macd_hist = macd_line - macd_signal; result = {\"macd_line\": macd_line, \"macd_signal\": macd_signal, \"macd_hist\": macd_hist}"
  }',
  default_params = '{"fast": 12, "slow": 26, "signal": 9}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['macd_line', 'macd_signal', 'macd_hist'],
  updated_at = NOW()
WHERE name = 'macd';

-- ========================================
-- 7. Stochastic - _calc_stochastic의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "k_period = params.get(\"k\", 14) or params.get(\"k_period\", 14); d_period = params.get(\"d\", 3) or params.get(\"d_period\", 3); low_min = df[\"low\"].rolling(window=k_period).min(); high_max = df[\"high\"].rolling(window=k_period).max(); stochastic_k = 100 * ((df[\"close\"] - low_min) / (high_max - low_min)); stochastic_d = stochastic_k.rolling(window=d_period).mean(); result = {\"stochastic_k\": stochastic_k, \"stochastic_d\": stochastic_d}"
  }',
  default_params = '{"k": 14, "d": 3}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['stochastic_k', 'stochastic_d'],
  updated_at = NOW()
WHERE name = 'stochastic';

-- ========================================
-- 8. Ichimoku - _calc_ichimoku의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "tenkan = params.get(\"tenkan\", 9); kijun = params.get(\"kijun\", 26); senkou = params.get(\"senkou\", 52); chikou = params.get(\"chikou\", 26); tenkan_high = df[\"high\"].rolling(window=tenkan).max(); tenkan_low = df[\"low\"].rolling(window=tenkan).min(); tenkan_sen = (tenkan_high + tenkan_low) / 2; kijun_high = df[\"high\"].rolling(window=kijun).max(); kijun_low = df[\"low\"].rolling(window=kijun).min(); kijun_sen = (kijun_high + kijun_low) / 2; senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun); senkou_high = df[\"high\"].rolling(window=senkou).max(); senkou_low = df[\"low\"].rolling(window=senkou).min(); senkou_b = ((senkou_high + senkou_low) / 2).shift(kijun); chikou_span = df[\"close\"].shift(-chikou); result = {\"ichimoku_tenkan\": tenkan_sen, \"ichimoku_kijun\": kijun_sen, \"ichimoku_senkou_a\": senkou_a, \"ichimoku_senkou_b\": senkou_b, \"ichimoku_chikou\": chikou_span}"
  }',
  default_params = '{"tenkan": 9, "kijun": 26, "senkou": 52, "chikou": 26}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou'],
  updated_at = NOW()
WHERE name = 'ichimoku';

-- ========================================
-- 9. Volume - 거래량은 그대로 사용
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "volume", "source": "volume", "description": "df[\"volume\"]"}',
  default_params = '{}',
  required_data = ARRAY['volume'],
  output_columns = ARRAY['volume'],
  updated_at = NOW()
WHERE name = 'volume';

-- ========================================
-- 10. OBV - _calc_obv의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "obv = [0]; for i in range(1, len(df)): obv.append(obv[-1] + df[\"volume\"].iloc[i] if df[\"close\"].iloc[i] > df[\"close\"].iloc[i-1] else (obv[-1] - df[\"volume\"].iloc[i] if df[\"close\"].iloc[i] < df[\"close\"].iloc[i-1] else obv[-1])); result = pd.Series(obv, index=df.index)"
  }',
  default_params = '{}',
  required_data = ARRAY['close', 'volume'],
  output_columns = ARRAY['obv'],
  updated_at = NOW()
WHERE name = 'obv';

-- ========================================
-- 11. VWAP - _calc_vwap의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "typical_price = (df[\"high\"] + df[\"low\"] + df[\"close\"]) / 3; cumulative_volume = df[\"volume\"].cumsum(); cumulative_pv = (typical_price * df[\"volume\"]).cumsum(); result = cumulative_pv / cumulative_volume"
  }',
  default_params = '{}',
  required_data = ARRAY['high', 'low', 'close', 'volume'],
  output_columns = ARRAY['vwap'],
  updated_at = NOW()
WHERE name = 'vwap';

-- ========================================
-- 12. ATR - _calc_atr의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = params.get(\"period\", 14); high_low = df[\"high\"] - df[\"low\"]; high_close = abs(df[\"high\"] - df[\"close\"].shift()); low_close = abs(df[\"low\"] - df[\"close\"].shift()); true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1); result = true_range.rolling(window=period).mean()"
  }',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['atr'],
  updated_at = NOW()
WHERE name = 'atr';

-- ========================================
-- 13. CCI - _calc_cci의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = params.get(\"period\", 20); typical_price = (df[\"high\"] + df[\"low\"] + df[\"close\"]) / 3; sma = typical_price.rolling(window=period).mean(); mad = typical_price.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean()); result = (typical_price - sma) / (0.015 * mad)"
  }',
  default_params = '{"period": 20}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['cci'],
  updated_at = NOW()
WHERE name = 'cci';

-- ========================================
-- 14. Williams %R - _calc_williams의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = params.get(\"period\", 14); highest_high = df[\"high\"].rolling(window=period).max(); lowest_low = df[\"low\"].rolling(window=period).min(); result = -100 * ((highest_high - df[\"close\"]) / (highest_high - lowest_low))"
  }',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['williams_r'],
  updated_at = NOW()
WHERE name = 'williams';

-- ========================================
-- 15. ADX - _calc_adx의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = params.get(\"period\", 14); plus_dm = df[\"high\"].diff(); minus_dm = -df[\"low\"].diff(); plus_dm[plus_dm < 0] = 0; minus_dm[minus_dm < 0] = 0; high_low = df[\"high\"] - df[\"low\"]; high_close = abs(df[\"high\"] - df[\"close\"].shift()); low_close = abs(df[\"low\"] - df[\"close\"].shift()); tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1); plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean()); minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean()); dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di); result = dx.rolling(window=period).mean()"
  }',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['adx'],
  updated_at = NOW()
WHERE name = 'adx';

-- ========================================
-- 16. DMI - _calc_dmi의 정확한 구현
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = params.get(\"period\", 14); plus_dm = df[\"high\"].diff(); minus_dm = -df[\"low\"].diff(); plus_dm[plus_dm < 0] = 0; minus_dm[minus_dm < 0] = 0; high_low = df[\"high\"] - df[\"low\"]; high_close = abs(df[\"high\"] - df[\"close\"].shift()); low_close = abs(df[\"low\"] - df[\"close\"].shift()); tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1); plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean()); minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean()); result = {\"dmi_plus_di\": plus_di, \"dmi_minus_di\": minus_di}"
  }',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['dmi_plus_di', 'dmi_minus_di'],
  updated_at = NOW()
WHERE name = 'dmi';

-- ========================================
-- 17. Parabolic SAR - 복잡한 반복 로직이므로 built-in 사용
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "parabolic_sar", "description": "Parabolic Stop and Reverse with iterative calculation"}',
  default_params = '{"acc": 0.02, "max": 0.2}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['psar'],
  updated_at = NOW()
WHERE name = 'parabolic';

-- ========================================
-- 18. Bollinger (볼린저밴드 별칭) - bb와 동일
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "sma = df[\"close\"].rolling(window=params.get(\"period\", 20)).mean(); std = df[\"close\"].rolling(window=params.get(\"period\", 20)).std(); std_dev = params.get(\"std\", 2); result = {\"bollinger_upper\": sma + (std * std_dev), \"bollinger_middle\": sma, \"bollinger_lower\": sma - (std * std_dev)}"
  }',
  default_params = '{"period": 20, "std": 2}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower'],
  updated_at = NOW()
WHERE name = 'bollinger';

-- ========================================
-- 19. Volume MA - 거래량 이동평균
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rolling_mean", "source": "volume", "description": "df[\"volume\"].rolling(window=period).mean()"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['volume'],
  output_columns = ARRAY['volume_ma'],
  updated_at = NOW()
WHERE name = 'volume_ma';

-- ========================================
-- 20. Price (현재가) - 종가 그대로 사용
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "price", "source": "close", "description": "df[\"close\"]"}',
  default_params = '{}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['price'],
  updated_at = NOW()
WHERE name = 'price';

-- ========================================
-- 21. Close (종가) - 종가 그대로 사용
-- ========================================
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "close", "source": "close", "description": "df[\"close\"]"}',
  default_params = '{}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['close'],
  updated_at = NOW()
WHERE name = 'close';

-- ========================================
-- 실행 확인 쿼리
-- ========================================
SELECT
  name,
  display_name,
  calculation_type,
  CASE
    WHEN calculation_type = 'python_code' THEN
      'Python: ' || left((formula::json->>'code')::text, 50) || '...'
    WHEN calculation_type = 'built-in' THEN
      'Built-in: ' || (formula::json->>'method')::text
  END as formula_summary,
  default_params,
  output_columns
FROM indicators
ORDER BY name;

-- 계산 타입별 카운트
SELECT
  calculation_type,
  COUNT(*) as count
FROM indicators
GROUP BY calculation_type
ORDER BY count DESC;