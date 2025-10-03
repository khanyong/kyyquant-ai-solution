-- MACD 시그널 전략의 실제 구조 확인
SELECT
    id,
    name,
    config,
    jsonb_pretty(config) as config_formatted
FROM strategies
WHERE id = 'f77a432a-e2a8-45ef-b2ae-7f5a820fc626';

-- 또는 이름으로 검색
SELECT
    id,
    name,
    config,
    jsonb_pretty(config) as config_formatted
FROM strategies
WHERE name = '[템플릿] MACD 시그널'
LIMIT 1;
