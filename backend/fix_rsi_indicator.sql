-- RSI 지표에서 import numpy as np 제거 및 주석 제거
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb('period = int(params.get(''period'', 14)); period = 1 if period < 1 else period; rt = str(params.get(''realtime'', False)).lower() in (''1'',''true'',''yes''); src_col = str(params.get(''source'', ''close'')); s = df[src_col].shift(1) if rt else df[src_col]; delta = s.diff(); gain = delta.clip(lower=0); loss = (-delta.clip(upper=0)); alpha = 1.0/period; gain_ewm = gain.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); loss_ewm = loss.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); denom = loss_ewm.where(loss_ewm > 0); rs = gain_ewm / denom; rsi = 100.0 - (100.0 / (1.0 + rs)); result = {''rsi'': rsi.clip(0, 100)}'::text)
)
WHERE name = 'rsi';

-- 수정 결과 확인
SELECT
    name,
    LEFT(formula->>'code', 150) as code_preview,
    CASE
        WHEN formula->>'code' LIKE '%import numpy%' THEN 'YES - 아직 import 있음'
        ELSE 'NO - import 제거됨'
    END as has_import_numpy
FROM indicators
WHERE name = 'rsi';
