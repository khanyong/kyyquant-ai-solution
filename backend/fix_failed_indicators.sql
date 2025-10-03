-- 실패한 6개 지표 일괄 수정

-- 1. Williams: 앞의 ', pandas as pd' 제거
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb(LTRIM(REPLACE(formula->>'code', ', pandas as pd', ''), E'\r\n'))
)
WHERE name = 'williams';

-- 2. OBV: 전체 코드 교체 (import 제거)
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb('rt = str(params.get(''realtime'', False)).lower() in (''1'',''true'',''yes'',''y'',''on''); price = df[''close'']; vol = df[''volume'']; obv = [0]; [obv.append(obv[-1] + vol.iloc[i]) if price.iloc[i] > price.iloc[i-1] else obv.append(obv[-1] - vol.iloc[i]) if price.iloc[i] < price.iloc[i-1] else obv.append(obv[-1]) for i in range(1, len(price))]; series = pd.Series(obv, index=df.index); series = series.round(6) if not rt else series; result = {''obv'': series}')
)
WHERE name = 'obv';

-- 3. CCI: result 변수 추가 확인
SELECT name,
       CASE WHEN formula->>'code' LIKE '%result%' THEN 'OK' ELSE 'MISSING result' END as status
FROM indicators
WHERE name = 'cci';

-- 4. Ichimoku: result 변수 추가 확인
SELECT name,
       CASE WHEN formula->>'code' LIKE '%result%' THEN 'OK' ELSE 'MISSING result' END as status
FROM indicators
WHERE name = 'ichimoku';

-- 5. Parabolic: result 변수 추가 확인
SELECT name,
       CASE WHEN formula->>'code' LIKE '%result%' THEN 'OK' ELSE 'MISSING result' END as status
FROM indicators
WHERE name = 'parabolic';

-- 6. VWAP: result 변수 추가 확인
SELECT name,
       CASE WHEN formula->>'code' LIKE '%result%' THEN 'OK' ELSE 'MISSING result' END as status
FROM indicators
WHERE name = 'vwap';

-- 전체 확인
SELECT
    name,
    CASE
        WHEN formula->>'code' LIKE '%import%' THEN 'FAIL: import 있음'
        WHEN formula->>'code' NOT LIKE '%result%' THEN 'FAIL: result 없음'
        WHEN formula->>'code' LIKE E'\r\n,%' OR formula->>'code' LIKE ',%' THEN 'FAIL: 잘못된 시작'
        ELSE 'OK'
    END as status
FROM indicators
WHERE name IN ('cci', 'ichimoku', 'obv', 'parabolic', 'vwap', 'williams')
ORDER BY name;
