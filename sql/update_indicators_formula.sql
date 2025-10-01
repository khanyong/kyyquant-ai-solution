-- 전략빌더에서 사용하는 모든 지표 formula 업데이트
-- formula를 JSONB 형식으로 저장

-- ========================================
-- 필수 지표 (프론트엔드 AVAILABLE_INDICATORS)
-- ========================================

-- 1. MA (이동평균)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rolling_mean", "source": "close"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['ma'],
  updated_at = NOW()
WHERE name = 'ma';

-- 2. SMA (단순이동평균)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rolling_mean", "source": "close"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['sma'],
  updated_at = NOW()
WHERE name = 'sma';

-- 3. EMA (지수이동평균)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "ewm_mean", "source": "close"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['ema'],
  updated_at = NOW()
WHERE name = 'ema';

-- 4. BB (볼린저밴드)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "bollinger", "source": "close"}',
  default_params = '{"period": 20, "std": 2}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['bb_upper', 'bb_middle', 'bb_lower'],
  updated_at = NOW()
WHERE name = 'bb';

-- 5. RSI
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rsi", "source": "close"}',
  default_params = '{"period": 14}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['rsi'],
  updated_at = NOW()
WHERE name = 'rsi';

-- 6. MACD
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "macd", "source": "close"}',
  default_params = '{"fast": 12, "slow": 26, "signal": 9}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['macd_line', 'macd_signal', 'macd_hist'],
  updated_at = NOW()
WHERE name = 'macd';

-- 7. Stochastic (스토캐스틱)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "stochastic"}',
  default_params = '{"k": 14, "d": 3}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['stochastic_k', 'stochastic_d'],
  updated_at = NOW()
WHERE name = 'stochastic';

-- 8. Ichimoku (일목균형표)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "ichimoku"}',
  default_params = '{"tenkan": 9, "kijun": 26, "senkou": 52, "chikou": 26}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['tenkan', 'kijun', 'senkou_a', 'senkou_b', 'chikou'],
  updated_at = NOW()
WHERE name = 'ichimoku';

-- 9. Volume (거래량)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "volume", "source": "volume"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['volume'],
  output_columns = ARRAY['volume', 'volume_ma'],
  updated_at = NOW()
WHERE name = 'volume';

-- 10. OBV (누적거래량)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "obv"}',
  default_params = '{}',
  required_data = ARRAY['close', 'volume'],
  output_columns = ARRAY['obv'],
  updated_at = NOW()
WHERE name = 'obv';

-- 11. VWAP (거래량가중평균)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "vwap"}',
  default_params = '{}',
  required_data = ARRAY['high', 'low', 'close', 'volume'],
  output_columns = ARRAY['vwap'],
  updated_at = NOW()
WHERE name = 'vwap';

-- 12. ATR (변동성)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "atr"}',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['atr'],
  updated_at = NOW()
WHERE name = 'atr';

-- 13. CCI
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "cci"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['cci'],
  updated_at = NOW()
WHERE name = 'cci';

-- 14. Williams %R
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "williams"}',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['williams_r'],
  updated_at = NOW()
WHERE name = 'williams';

-- 15. ADX (추세강도)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "adx"}',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['adx'],
  updated_at = NOW()
WHERE name = 'adx';

-- 16. DMI (+DI/-DI)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "dmi"}',
  default_params = '{"period": 14}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['plus_di', 'minus_di'],
  updated_at = NOW()
WHERE name = 'dmi';

-- 17. Parabolic SAR
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "parabolic_sar"}',
  default_params = '{"acc": 0.02, "max": 0.2}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['psar'],
  updated_at = NOW()
WHERE name = 'parabolic';

-- ========================================
-- 추가 보조 지표 (백엔드에서 사용)
-- ========================================

-- 18. Bollinger (볼린저밴드 별칭)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "bollinger", "source": "close"}',
  default_params = '{"period": 20, "std": 2}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower'],
  updated_at = NOW()
WHERE name = 'bollinger';

-- 19. Volume MA (거래량 이동평균)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "rolling_mean", "source": "volume"}',
  default_params = '{"period": 20}',
  required_data = ARRAY['volume'],
  output_columns = ARRAY['volume_ma'],
  updated_at = NOW()
WHERE name = 'volume_ma';

-- 20. Price (현재가)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "price", "source": "close"}',
  default_params = '{}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['price'],
  updated_at = NOW()
WHERE name = 'price';

-- 21. Close (종가)
UPDATE indicators SET
  calculation_type = 'built-in',
  formula = '{"method": "close", "source": "close"}',
  default_params = '{}',
  required_data = ARRAY['close'],
  output_columns = ARRAY['close'],
  updated_at = NOW()
WHERE name = 'close';

-- ========================================
-- 확인 쿼리
-- ========================================
SELECT
  name,
  display_name,
  category,
  calculation_type,
  formula,
  default_params,
  output_columns
FROM indicators
ORDER BY name;