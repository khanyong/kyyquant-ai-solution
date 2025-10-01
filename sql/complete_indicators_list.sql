-- 전략빌더에서 사용하는 모든 지표 완전 목록
-- 프론트엔드 AVAILABLE_INDICATORS와 동기화

-- ========================================
-- 필수 지표 18개 (프론트엔드 AVAILABLE_INDICATORS)
-- ========================================

-- 1. MA (이동평균)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'ma',
  'MA (이동평균)',
  '단순 이동평균선',
  'trend',
  'python_code',
  'def calculate(df, period=20, source="close"):
    return df[source].rolling(window=period).mean()',
  '{"period": 20, "source": "close"}',
  ARRAY['close'],
  ARRAY['ma']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, period=20, source="close"):
    return df[source].rolling(window=period).mean()',
  '{"period": 20, "source": "close"}',
  ARRAY['close'],
  ARRAY['sma']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, period=20, source="close"):
    return df[source].ewm(span=period, adjust=False).mean()',
  '{"period": 20, "source": "close"}',
  ARRAY['close'],
  ARRAY['ema']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, period=20, std=2, source="close"):
    middle = df[source].rolling(window=period).mean()
    std_dev = df[source].rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return {"bb_upper": upper, "bb_middle": middle, "bb_lower": lower}',
  '{"period": 20, "std": 2, "source": "close"}',
  ARRAY['close'],
  ARRAY['bb_upper', 'bb_middle', 'bb_lower']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, period=14, source="close"):
    delta = df[source].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi',
  '{"period": 14, "source": "close"}',
  ARRAY['close'],
  ARRAY['rsi']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, fast=12, slow=26, signal=9, source="close"):
    ema_fast = df[source].ewm(span=fast, adjust=False).mean()
    ema_slow = df[source].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - macd_signal
    return {"macd_line": macd_line, "macd_signal": macd_signal, "macd_hist": macd_hist}',
  '{"fast": 12, "slow": 26, "signal": 9, "source": "close"}',
  ARRAY['close'],
  ARRAY['macd_line', 'macd_signal', 'macd_hist']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, k=14, d=3):
    low_min = df["low"].rolling(window=k).min()
    high_max = df["high"].rolling(window=k).max()
    k_percent = 100 * ((df["close"] - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=d).mean()
    return {"stochastic_k": k_percent, "stochastic_d": d_percent}',
  '{"k": 14, "d": 3}',
  ARRAY['high', 'low', 'close'],
  ARRAY['stochastic_k', 'stochastic_d']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, tenkan=9, kijun=26, senkou=52, chikou=26):
    # 전환선 (Tenkan-sen)
    tenkan_high = df["high"].rolling(window=tenkan).max()
    tenkan_low = df["low"].rolling(window=tenkan).min()
    tenkan_sen = (tenkan_high + tenkan_low) / 2

    # 기준선 (Kijun-sen)
    kijun_high = df["high"].rolling(window=kijun).max()
    kijun_low = df["low"].rolling(window=kijun).min()
    kijun_sen = (kijun_high + kijun_low) / 2

    # 선행스팬A (Senkou Span A)
    senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)

    # 선행스팬B (Senkou Span B)
    senkou_high = df["high"].rolling(window=senkou).max()
    senkou_low = df["low"].rolling(window=senkou).min()
    senkou_b = ((senkou_high + senkou_low) / 2).shift(kijun)

    # 후행스팬 (Chikou Span)
    chikou_span = df["close"].shift(-chikou)

    return {
        "tenkan": tenkan_sen,
        "kijun": kijun_sen,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b,
        "chikou": chikou_span
    }',
  '{"tenkan": 9, "kijun": 26, "senkou": 52, "chikou": 26}',
  ARRAY['high', 'low', 'close'],
  ARRAY['tenkan', 'kijun', 'senkou_a', 'senkou_b', 'chikou']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, period=20):
    volume_ma = df["volume"].rolling(window=period).mean()
    return {"volume": df["volume"], "volume_ma": volume_ma}',
  '{"period": 20}',
  ARRAY['volume'],
  ARRAY['volume', 'volume_ma']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 10. OBV (누적거래량)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'obv',
  'OBV (누적거래량)',
  'On Balance Volume',
  'volume',
  'python_code',
  'def calculate(df):
    import numpy as np
    obv = np.where(df["close"] > df["close"].shift(1), df["volume"],
           np.where(df["close"] < df["close"].shift(1), -df["volume"], 0)).cumsum()
    return obv',
  '{}',
  ARRAY['close', 'volume'],
  ARRAY['obv']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 11. VWAP (거래량가중평균)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'vwap',
  'VWAP (거래량가중평균)',
  'Volume Weighted Average Price',
  'volume',
  'python_code',
  'def calculate(df):
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
    return vwap',
  '{}',
  ARRAY['high', 'low', 'close', 'volume'],
  ARRAY['vwap']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 12. ATR (변동성)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'atr',
  'ATR (변동성)',
  'Average True Range',
  'volatility',
  'python_code',
  'def calculate(df, period=14):
    import numpy as np
    import pandas as pd
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['atr']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 13. CCI
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'cci',
  'CCI',
  'Commodity Channel Index',
  'momentum',
  'python_code',
  'def calculate(df, period=20):
    import numpy as np
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    sma = typical_price.rolling(window=period).mean()
    mad = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    cci = (typical_price - sma) / (0.015 * mad)
    return cci',
  '{"period": 20}',
  ARRAY['high', 'low', 'close'],
  ARRAY['cci']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, period=14):
    high_max = df["high"].rolling(window=period).max()
    low_min = df["low"].rolling(window=period).min()
    williams_r = -100 * ((high_max - df["close"]) / (high_max - low_min))
    return williams_r',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['williams_r']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 15. ADX (추세강도)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'adx',
  'ADX (추세강도)',
  'Average Directional Index',
  'trend',
  'python_code',
  'def calculate(df, period=14):
    import numpy as np
    import pandas as pd
    # True Range 계산
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # Directional Movement 계산
    up_move = df["high"] - df["high"].shift()
    down_move = df["low"].shift() - df["low"]

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Smoothed values
    atr = true_range.rolling(window=period).mean()
    plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)

    # ADX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    return adx',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['adx']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 16. DMI (+DI/-DI)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'dmi',
  'DMI (+DI/-DI)',
  'Directional Movement Index',
  'trend',
  'python_code',
  'def calculate(df, period=14):
    import numpy as np
    import pandas as pd
    # True Range
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # Directional Movement
    up_move = df["high"] - df["high"].shift()
    down_move = df["low"].shift() - df["low"]

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Smoothed values
    atr = true_range.rolling(window=period).mean()
    plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)

    return {"plus_di": plus_di, "minus_di": minus_di}',
  '{"period": 14}',
  ARRAY['high', 'low', 'close'],
  ARRAY['plus_di', 'minus_di']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
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
  'python_code',
  'def calculate(df, acc=0.02, max_acc=0.2):
    import numpy as np
    psar = df["close"].copy()
    bull = True
    af = acc
    ep = df["high"].iloc[0] if bull else df["low"].iloc[0]

    for i in range(1, len(df)):
        psar.iloc[i] = psar.iloc[i-1] + af * (ep - psar.iloc[i-1])

        if bull:
            if df["low"].iloc[i] < psar.iloc[i]:
                bull = False
                psar.iloc[i] = ep
                af = acc
                ep = df["low"].iloc[i]
            else:
                if df["high"].iloc[i] > ep:
                    ep = df["high"].iloc[i]
                    af = min(af + acc, max_acc)
        else:
            if df["high"].iloc[i] > psar.iloc[i]:
                bull = True
                psar.iloc[i] = ep
                af = acc
                ep = df["high"].iloc[i]
            else:
                if df["low"].iloc[i] < ep:
                    ep = df["low"].iloc[i]
                    af = min(af + acc, max_acc)

    return psar',
  '{"acc": 0.02, "max": 0.2}',
  ARRAY['high', 'low', 'close'],
  ARRAY['psar']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- ========================================
-- 추가 보조 지표 (백엔드에서 사용)
-- ========================================

-- 18. Bollinger (볼린저밴드 별칭)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'bollinger',
  '볼린저밴드',
  'Bollinger Bands (Alias)',
  'volatility',
  'python_code',
  'def calculate(df, period=20, std=2, source="close"):
    middle = df[source].rolling(window=period).mean()
    std_dev = df[source].rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return {"bollinger_upper": upper, "bollinger_middle": middle, "bollinger_lower": lower}',
  '{"period": 20, "std": 2, "source": "close"}',
  ARRAY['close'],
  ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 19. Volume MA (거래량 이동평균)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'volume_ma',
  '거래량 이동평균',
  'Volume Moving Average',
  'volume',
  'python_code',
  'def calculate(df, period=20):
    return df["volume"].rolling(window=period).mean()',
  '{"period": 20}',
  ARRAY['volume'],
  ARRAY['volume_ma']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 20. Price (현재가)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'price',
  '현재가',
  'Current Price',
  'price',
  'python_code',
  'def calculate(df):
    return df["close"]',
  '{}',
  ARRAY['close'],
  ARRAY['price']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- 21. Close (종가)
INSERT INTO indicators (name, display_name, description, category, calculation_type, formula, default_params, required_data, output_columns)
VALUES (
  'close',
  '종가',
  'Closing Price',
  'price',
  'python_code',
  'def calculate(df):
    return df["close"]',
  '{}',
  ARRAY['close'],
  ARRAY['close']
) ON CONFLICT (name) DO UPDATE SET
  calculation_type = EXCLUDED.calculation_type,
  formula = EXCLUDED.formula,
  default_params = EXCLUDED.default_params,
  updated_at = NOW();

-- ========================================
-- 통계 확인
-- ========================================
SELECT
  category,
  COUNT(*) as count
FROM indicators
GROUP BY category
ORDER BY category;