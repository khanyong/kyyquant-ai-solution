-- Python 코드를 JSON 형식으로 저장하는 방법
-- calculation_type을 'python_code'로 설정하고 formula에 code 필드 포함

-- 예시: RSI with Python code
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "delta = df[\"close\"].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=params.get(\"period\", 14)).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=params.get(\"period\", 14)).mean(); rs = gain / loss; result = 100 - (100 / (1 + rs))"
  }',
  default_params = '{"period": 14}',
  updated_at = NOW()
WHERE name = 'rsi';

-- 예시: MACD with Python code
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "ema_fast = df[\"close\"].ewm(span=params.get(\"fast\", 12), adjust=False).mean(); ema_slow = df[\"close\"].ewm(span=params.get(\"slow\", 26), adjust=False).mean(); macd_line = ema_fast - ema_slow; macd_signal = macd_line.ewm(span=params.get(\"signal\", 9), adjust=False).mean(); macd_hist = macd_line - macd_signal; result = {\"macd_line\": macd_line, \"macd_signal\": macd_signal, \"macd_hist\": macd_hist}"
  }',
  default_params = '{"fast": 12, "slow": 26, "signal": 9}',
  updated_at = NOW()
WHERE name = 'macd';