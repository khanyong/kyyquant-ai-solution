-- SMA, EMA, WMA 지표의 동적 컬럼명 지원
-- formula에 f-string 패턴 추가하여 period별 고유 컬럼명 생성

-- 1. SMA (Simple Moving Average)
UPDATE indicators
SET
  formula = jsonb_build_object(
    'code',
    'period = params.get("period", 20)
sma = df["close"].rolling(window=period).mean()
result = {f"sma_{period}": sma}'
  ),
  output_columns = ARRAY['sma']::text[],
  updated_at = now()
WHERE name = 'sma';

-- 2. EMA (Exponential Moving Average)
UPDATE indicators
SET
  formula = jsonb_build_object(
    'code',
    'period = params.get("period", 20)
ema = df["close"].ewm(span=period, adjust=False).mean()
result = {f"ema_{period}": ema}'
  ),
  output_columns = ARRAY['ema']::text[],
  updated_at = now()
WHERE name = 'ema';

-- 3. WMA (Weighted Moving Average)
UPDATE indicators
SET
  formula = jsonb_build_object(
    'code',
    'import numpy as np
period = params.get("period", 20)
weights = np.arange(1, period + 1)
wma = df["close"].rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
result = {f"wma_{period}": wma}'
  ),
  output_columns = ARRAY['wma']::text[],
  updated_at = now()
WHERE name = 'wma';

-- 검증
SELECT
  name,
  output_columns,
  formula->>'code' as code_preview
FROM indicators
WHERE name IN ('sma', 'ema', 'wma')
ORDER BY name;
