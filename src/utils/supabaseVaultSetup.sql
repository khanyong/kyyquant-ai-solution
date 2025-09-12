-- Supabase Vault를 사용한 민감한 정보 암호화 저장
-- Vault는 PostgreSQL의 pgsodium extension을 사용하여 암호화를 제공합니다

-- 1. Vault 활성화 (Supabase 대시보드에서 이미 활성화되어 있어야 함)
-- Extensions > pgsodium 활성화 필요

-- 2. 암호화된 계좌 정보 테이블 생성
CREATE TABLE IF NOT EXISTS user_trading_accounts_secure (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  account_type VARCHAR(20) CHECK (account_type IN ('mock', 'real')),
  account_number VARCHAR(20) NOT NULL,
  account_name VARCHAR(100),
  broker VARCHAR(20) DEFAULT 'kiwoom',
  
  -- Vault로 암호화될 민감한 정보들
  -- 이 컬럼들은 자동으로 암호화/복호화됩니다
  encrypted_access_token TEXT, -- Vault 암호화
  encrypted_refresh_token TEXT, -- Vault 암호화
  encrypted_client_secret TEXT, -- Vault 암호화
  
  -- 일반 정보 (암호화 불필요)
  token_expires_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT false,
  is_connected BOOLEAN DEFAULT false,
  is_default BOOLEAN DEFAULT false,
  last_sync_at TIMESTAMP WITH TIME ZONE,
  
  -- 계좌 정보
  initial_balance DECIMAL(15, 2),
  current_balance DECIMAL(15, 2),
  available_balance DECIMAL(15, 2),
  
  -- 거래 설정
  max_trade_amount DECIMAL(15, 2),
  max_position_size INTEGER DEFAULT 10,
  allow_auto_trading BOOLEAN DEFAULT false,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, account_number, broker)
);

-- 3. Vault 시크릿 테이블 생성 (사용자별 암호화 키 관리)
CREATE TABLE IF NOT EXISTS vault_secrets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  secret_name VARCHAR(255) NOT NULL,
  secret_value TEXT, -- 이 값은 pgsodium으로 암호화됨
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 암호화/복호화 함수 생성

-- 토큰 암호화 함수
CREATE OR REPLACE FUNCTION encrypt_token(
  p_user_id UUID,
  p_token TEXT,
  p_token_type TEXT DEFAULT 'access_token'
) RETURNS TEXT AS $$
DECLARE
  v_key_id UUID;
  v_encrypted TEXT;
BEGIN
  -- 사용자별 고유 키 ID 생성 또는 조회
  SELECT id INTO v_key_id 
  FROM vault.secrets 
  WHERE name = p_user_id::TEXT || '_' || p_token_type
  LIMIT 1;
  
  -- 키가 없으면 생성
  IF v_key_id IS NULL THEN
    INSERT INTO vault.secrets (name, secret)
    VALUES (p_user_id::TEXT || '_' || p_token_type, gen_random_bytes(32))
    RETURNING id INTO v_key_id;
  END IF;
  
  -- pgsodium을 사용한 암호화
  SELECT pgsodium.crypto_aead_det_encrypt(
    p_token::bytea,
    p_user_id::TEXT::bytea,
    v_key_id
  )::TEXT INTO v_encrypted;
  
  RETURN v_encrypted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 토큰 복호화 함수
CREATE OR REPLACE FUNCTION decrypt_token(
  p_user_id UUID,
  p_encrypted_token TEXT,
  p_token_type TEXT DEFAULT 'access_token'
) RETURNS TEXT AS $$
DECLARE
  v_key_id UUID;
  v_decrypted TEXT;
BEGIN
  -- 사용자별 키 ID 조회
  SELECT id INTO v_key_id 
  FROM vault.secrets 
  WHERE name = p_user_id::TEXT || '_' || p_token_type
  LIMIT 1;
  
  IF v_key_id IS NULL THEN
    RETURN NULL;
  END IF;
  
  -- pgsodium을 사용한 복호화
  SELECT convert_from(
    pgsodium.crypto_aead_det_decrypt(
      p_encrypted_token::bytea,
      p_user_id::TEXT::bytea,
      v_key_id
    ),
    'UTF8'
  ) INTO v_decrypted;
  
  RETURN v_decrypted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. 계좌 정보 저장 함수 (자동 암호화)
CREATE OR REPLACE FUNCTION save_trading_account(
  p_user_id UUID,
  p_account_type VARCHAR(20),
  p_account_number VARCHAR(20),
  p_account_name VARCHAR(100),
  p_access_token TEXT,
  p_refresh_token TEXT,
  p_token_expires_at TIMESTAMP WITH TIME ZONE
) RETURNS UUID AS $$
DECLARE
  v_account_id UUID;
BEGIN
  -- 토큰 암호화 후 저장
  INSERT INTO user_trading_accounts_secure (
    user_id,
    account_type,
    account_number,
    account_name,
    encrypted_access_token,
    encrypted_refresh_token,
    token_expires_at,
    is_connected,
    is_active
  ) VALUES (
    p_user_id,
    p_account_type,
    p_account_number,
    p_account_name,
    encrypt_token(p_user_id, p_access_token, 'access_token'),
    encrypt_token(p_user_id, p_refresh_token, 'refresh_token'),
    p_token_expires_at,
    true,
    true
  )
  ON CONFLICT (user_id, account_number, broker) 
  DO UPDATE SET
    encrypted_access_token = EXCLUDED.encrypted_access_token,
    encrypted_refresh_token = EXCLUDED.encrypted_refresh_token,
    token_expires_at = EXCLUDED.token_expires_at,
    is_connected = true,
    is_active = true,
    last_sync_at = NOW(),
    updated_at = NOW()
  RETURNING id INTO v_account_id;
  
  RETURN v_account_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6. 계좌 정보 조회 함수 (자동 복호화)
CREATE OR REPLACE FUNCTION get_trading_account_with_tokens(
  p_account_id UUID,
  p_user_id UUID
) RETURNS TABLE (
  id UUID,
  account_type VARCHAR(20),
  account_number VARCHAR(20),
  account_name VARCHAR(100),
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  is_connected BOOLEAN,
  is_active BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    a.id,
    a.account_type,
    a.account_number,
    a.account_name,
    decrypt_token(p_user_id, a.encrypted_access_token, 'access_token') as access_token,
    decrypt_token(p_user_id, a.encrypted_refresh_token, 'refresh_token') as refresh_token,
    a.token_expires_at,
    a.is_connected,
    a.is_active
  FROM user_trading_accounts_secure a
  WHERE a.id = p_account_id 
    AND a.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. RLS 정책 설정
ALTER TABLE user_trading_accounts_secure ENABLE ROW LEVEL SECURITY;
ALTER TABLE vault_secrets ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 계좌만 볼 수 있음
CREATE POLICY "Users can view own secure accounts" 
  ON user_trading_accounts_secure FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own secure accounts" 
  ON user_trading_accounts_secure FOR ALL 
  USING (auth.uid() = user_id);

-- Vault secrets는 함수를 통해서만 접근
CREATE POLICY "Vault secrets are only accessible via functions" 
  ON vault_secrets FOR ALL 
  USING (false); -- 직접 접근 차단

-- 8. 보안 뷰 생성 (민감한 정보 제외)
CREATE OR REPLACE VIEW user_trading_accounts_view AS
SELECT 
  id,
  user_id,
  account_type,
  account_number,
  account_name,
  broker,
  is_active,
  is_connected,
  is_default,
  last_sync_at,
  current_balance,
  available_balance,
  max_trade_amount,
  max_position_size,
  allow_auto_trading,
  created_at,
  updated_at,
  CASE 
    WHEN token_expires_at > NOW() THEN 'valid'
    WHEN token_expires_at <= NOW() THEN 'expired'
    ELSE 'unknown'
  END as token_status
FROM user_trading_accounts_secure;

-- 9. 토큰 갱신 함수
CREATE OR REPLACE FUNCTION refresh_account_token(
  p_account_id UUID,
  p_user_id UUID,
  p_new_access_token TEXT,
  p_new_refresh_token TEXT,
  p_new_expires_at TIMESTAMP WITH TIME ZONE
) RETURNS BOOLEAN AS $$
BEGIN
  UPDATE user_trading_accounts_secure
  SET 
    encrypted_access_token = encrypt_token(p_user_id, p_new_access_token, 'access_token'),
    encrypted_refresh_token = encrypt_token(p_user_id, p_new_refresh_token, 'refresh_token'),
    token_expires_at = p_new_expires_at,
    last_sync_at = NOW(),
    updated_at = NOW()
  WHERE id = p_account_id AND user_id = p_user_id;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. 주기적 토큰 정리 (만료된 토큰 제거)
CREATE OR REPLACE FUNCTION cleanup_expired_tokens() RETURNS void AS $$
BEGIN
  UPDATE user_trading_accounts_secure
  SET 
    is_connected = false,
    encrypted_access_token = NULL,
    encrypted_refresh_token = NULL
  WHERE token_expires_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 11. 감사 로그 테이블
CREATE TABLE IF NOT EXISTS token_access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  account_id UUID REFERENCES user_trading_accounts_secure(id),
  action VARCHAR(50), -- 'encrypt', 'decrypt', 'refresh', 'revoke'
  ip_address INET,
  user_agent TEXT,
  success BOOLEAN,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_secure_accounts_user_id ON user_trading_accounts_secure(user_id);
CREATE INDEX idx_secure_accounts_token_expires ON user_trading_accounts_secure(token_expires_at);
CREATE INDEX idx_token_access_logs_user_id ON token_access_logs(user_id);
CREATE INDEX idx_token_access_logs_created_at ON token_access_logs(created_at);