-- 모든 지표에서 import 문 제거 (일괄 처리)
-- import numpy as np, import pandas as pd 등 제거

UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        formula->>'code',
                        'import numpy as np, pandas as pd; ',
                        ''
                    ),
                    'import numpy as np; ',
                    ''
                ),
                'import pandas as pd; ',
                ''
            ),
            'import numpy as np',
            ''
        )
    )
)
WHERE formula->>'code' LIKE '%import%';

-- 수정된 지표 확인
SELECT
    name,
    CASE
        WHEN formula->>'code' LIKE '%import%' THEN 'YES - 아직 import 있음'
        ELSE 'NO - import 제거됨'
    END as has_import
FROM indicators
WHERE is_active = true
ORDER BY name;
