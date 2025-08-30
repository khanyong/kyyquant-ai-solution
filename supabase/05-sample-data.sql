-- Step 5: 샘플 데이터 삽입 (테스트용)

-- 샘플 종목 데이터
INSERT INTO stocks (code, name, market, sector) VALUES
    ('005930', '삼성전자', 'KOSPI', '전기전자'),
    ('000660', 'SK하이닉스', 'KOSPI', '전기전자'),
    ('035720', '카카오', 'KOSPI', 'IT'),
    ('035420', 'NAVER', 'KOSPI', 'IT'),
    ('051910', 'LG화학', 'KOSPI', '화학'),
    ('006400', '삼성SDI', 'KOSPI', '전기전자'),
    ('028260', '삼성물산', 'KOSPI', '유통'),
    ('105560', 'KB금융', 'KOSPI', '금융'),
    ('055550', '신한지주', 'KOSPI', '금융'),
    ('003550', 'LG', 'KOSPI', '지주회사')
ON CONFLICT (code) DO NOTHING;

-- 샘플 시장 지수 데이터
INSERT INTO market_index (index_code, index_name, current_value, change_value, change_rate) VALUES
    ('KOSPI', '코스피', 2500.00, 15.50, 0.62),
    ('KOSDAQ', '코스닥', 850.00, -3.20, -0.38)
ON CONFLICT (index_code) 
DO UPDATE SET 
    current_value = EXCLUDED.current_value,
    change_value = EXCLUDED.change_value,
    change_rate = EXCLUDED.change_rate,
    timestamp = CURRENT_TIMESTAMP;

-- 샘플 프로필 (테스트용)
INSERT INTO profiles (email, name, kiwoom_account) VALUES
    ('demo@example.com', '데모 사용자', 'DEMO001')
ON CONFLICT (email) DO NOTHING;