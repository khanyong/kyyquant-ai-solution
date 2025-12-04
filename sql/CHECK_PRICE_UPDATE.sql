-- 최근 1시간 내에 업데이트된 종목 수 확인
SELECT 
    COUNT(*) as updated_count,
    MIN(updated_at) as oldest_update,
    MAX(updated_at) as newest_update
FROM kw_price_current
WHERE updated_at >= NOW() - INTERVAL '1 hour';

-- 샘플 데이터 확인 (최신 5개)
SELECT stock_code, current_price, volume, updated_at
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 5;
