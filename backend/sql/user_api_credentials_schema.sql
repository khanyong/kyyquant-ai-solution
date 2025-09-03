-- 사용자별 API 인증 정보 저장 테이블
CREATE TABLE IF NOT EXISTS user_api_credentials (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) UNIQUE,
    
    -- 한국투자증권 API 정보 (암호화 필요)
    api_key TEXT,  -- 앱키
    api_secret TEXT,  -- 앱시크릿 (암호화 저장)
    account_no TEXT,  -- 계좌번호 (암호화 저장)
    account_product_code TEXT DEFAULT '01',
    
    -- API 모드
    is_demo BOOLEAN DEFAULT TRUE,  -- 모의투자/실거래
    api_url TEXT,
    
    -- 상태
    is_active BOOLEAN DEFAULT TRUE,
    last_connected_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS 정책 - 자신의 인증 정보만 접근
ALTER TABLE user_api_credentials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own credentials" ON user_api_credentials
    FOR ALL USING (auth.uid() = user_id);

-- 암호화 함수 (Supabase Vault 사용 권장)
CREATE OR REPLACE FUNCTION encrypt_sensitive_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Supabase Vault를 사용한 암호화 (실제 구현 시)
    -- NEW.api_secret = vault.encrypt(NEW.api_secret);
    -- NEW.account_no = vault.encrypt(NEW.account_no);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER encrypt_api_credentials
BEFORE INSERT OR UPDATE ON user_api_credentials
FOR EACH ROW EXECUTE FUNCTION encrypt_sensitive_data();