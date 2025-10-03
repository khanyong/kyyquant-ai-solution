-- OBV 지표에서 import pandas 제거
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb(
        REPLACE(
            formula->>'code',
            E'import pandas as pd\n',
            ''
        )
    )
)
WHERE name = 'obv';

-- 확인
SELECT
    name,
    LEFT(formula->>'code', 150) as code_preview,
    CASE
        WHEN formula->>'code' LIKE '%import%' THEN 'YES - 아직 import 있음'
        ELSE 'NO - import 제거됨'
    END as has_import
FROM indicators
WHERE name = 'obv';
