-- 필수 사전 요구사항 및 공통 함수들
-- 이 파일을 가장 먼저 실행하세요!

-- 1. 필요한 확장 기능 활성화 (Supabase 대시보드에서 활성화 필요)
-- - uuid-ossp (UUID 생성) - 보통 기본 활성화
-- - pgsodium (암호화) - 대시보드에서 활성화 필요

-- 2. updated_at 자동 업데이트 함수
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. 현재 사용자 ID 가져오기 (auth.uid() 대신 사용)
-- Supabase는 이미 auth.uid() 함수를 제공하므로 새로 만들 필요 없음
-- 대신 public 스키마에 wrapper 함수 생성
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
  SELECT auth.uid()
$$ LANGUAGE sql STABLE;

-- 4. 사용자 역할 확인 함수
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = user_id 
    AND (role = 'admin' OR is_admin = true)
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. 현재 사용자가 관리자인지 확인
CREATE OR REPLACE FUNCTION is_current_user_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN is_admin(auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6. 타임스탬프 포맷 함수
CREATE OR REPLACE FUNCTION format_timestamp(ts TIMESTAMP WITH TIME ZONE)
RETURNS TEXT AS $$
BEGIN
  RETURN to_char(ts AT TIME ZONE 'Asia/Seoul', 'YYYY-MM-DD HH24:MI:SS');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 7. 안전한 JSON 추출 함수
CREATE OR REPLACE FUNCTION safe_json_extract(
  json_data JSONB,
  path TEXT,
  default_value TEXT DEFAULT NULL
)
RETURNS TEXT AS $$
BEGIN
  RETURN COALESCE(json_data ->> path, default_value);
EXCEPTION
  WHEN OTHERS THEN
    RETURN default_value;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 8. 배열 중복 제거 함수
CREATE OR REPLACE FUNCTION array_unique(arr ANYARRAY)
RETURNS ANYARRAY AS $$
  SELECT ARRAY(SELECT DISTINCT unnest(arr))
$$ LANGUAGE sql IMMUTABLE;

-- 9. 퍼센트 계산 함수
CREATE OR REPLACE FUNCTION calculate_percentage(
  value NUMERIC,
  total NUMERIC,
  decimal_places INTEGER DEFAULT 2
)
RETURNS NUMERIC AS $$
BEGIN
  IF total = 0 OR total IS NULL THEN
    RETURN 0;
  END IF;
  RETURN ROUND((value / total) * 100, decimal_places);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 10. 수익률 계산 함수
CREATE OR REPLACE FUNCTION calculate_return_rate(
  initial_value NUMERIC,
  final_value NUMERIC,
  decimal_places INTEGER DEFAULT 2
)
RETURNS NUMERIC AS $$
BEGIN
  IF initial_value = 0 OR initial_value IS NULL THEN
    RETURN 0;
  END IF;
  RETURN ROUND(((final_value - initial_value) / initial_value) * 100, decimal_places);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 11. 이메일 유효성 검사 함수
CREATE OR REPLACE FUNCTION is_valid_email(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 12. 전화번호 포맷 함수 (한국)
CREATE OR REPLACE FUNCTION format_phone_number(phone TEXT)
RETURNS TEXT AS $$
DECLARE
  cleaned TEXT;
BEGIN
  -- 숫자만 추출
  cleaned := regexp_replace(phone, '[^0-9]', '', 'g');
  
  -- 한국 전화번호 포맷
  IF length(cleaned) = 11 THEN
    -- 010-1234-5678
    RETURN substr(cleaned, 1, 3) || '-' || 
           substr(cleaned, 4, 4) || '-' || 
           substr(cleaned, 8, 4);
  ELSIF length(cleaned) = 10 THEN
    -- 02-1234-5678 or 031-123-4567
    IF substr(cleaned, 1, 2) = '02' THEN
      RETURN substr(cleaned, 1, 2) || '-' || 
             substr(cleaned, 3, 4) || '-' || 
             substr(cleaned, 7, 4);
    ELSE
      RETURN substr(cleaned, 1, 3) || '-' || 
             substr(cleaned, 4, 3) || '-' || 
             substr(cleaned, 7, 4);
    END IF;
  ELSE
    RETURN phone;
  END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 13. UUID 유효성 검사
CREATE OR REPLACE FUNCTION is_valid_uuid(input TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  PERFORM input::UUID;
  RETURN TRUE;
EXCEPTION
  WHEN OTHERS THEN
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 14. 안전한 숫자 변환
CREATE OR REPLACE FUNCTION safe_to_numeric(
  input TEXT,
  default_value NUMERIC DEFAULT 0
)
RETURNS NUMERIC AS $$
BEGIN
  RETURN input::NUMERIC;
EXCEPTION
  WHEN OTHERS THEN
    RETURN default_value;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 15. 작업일 계산 함수 (주말 제외)
CREATE OR REPLACE FUNCTION add_business_days(
  start_date DATE,
  days_to_add INTEGER
)
RETURNS DATE AS $$
DECLARE
  work_date DATE := start_date;
  days_added INTEGER := 0;
BEGIN
  WHILE days_added < days_to_add LOOP
    work_date := work_date + 1;
    -- 주말이 아닌 경우만 카운트
    IF EXTRACT(DOW FROM work_date) NOT IN (0, 6) THEN
      days_added := days_added + 1;
    END IF;
  END LOOP;
  RETURN work_date;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ Prerequisites and common functions created successfully!';
  RAISE NOTICE '📌 Note: Using Supabase built-in auth.uid() function';
  RAISE NOTICE '📌 Make sure pgsodium extension is enabled for encryption features';
END $$;