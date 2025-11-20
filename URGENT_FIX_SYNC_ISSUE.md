# 🚨 긴급 수정: 키움 계좌 동기화 문제 해결

## 문제 원인
**`kw_account_balance`와 `kw_portfolio` 테이블이 데이터베이스에 존재하지 않습니다.**

Edge Function `sync-kiwoom-balance`가 이 테이블들을 사용하려고 하지만, 실제로는 생성되지 않아서 동기화 버튼이 작동하지 않습니다.

## ✅ 즉시 해결 방법

### 1단계: Supabase SQL Editor 열기

1. Supabase 대시보드 접속
2. 좌측 메뉴에서 **SQL Editor** 클릭
3. **New Query** 클릭

### 2단계: 테이블 생성 (필수)

다음 파일의 SQL을 **순서대로** 실행하세요:

#### A. 테이블 생성
[supabase/migrations/06_create_kiwoom_balance_tables.sql](supabase/migrations/06_create_kiwoom_balance_tables.sql) 파일 내용을 복사하여 실행

**확인**:
```sql
-- 테이블이 생성되었는지 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('kw_account_balance', 'kw_portfolio');
```

**예상 결과**: 2개의 행 반환 (kw_account_balance, kw_portfolio)

#### B. 함수 생성
[supabase/migrations/07_create_kiwoom_sync_functions.sql](supabase/migrations/07_create_kiwoom_sync_functions.sql) 파일 내용을 복사하여 실행

**확인**:
```sql
-- 함수가 생성되었는지 확인
SELECT proname
FROM pg_proc
WHERE proname IN (
  'sync_kiwoom_account_balance',
  'sync_kiwoom_portfolio',
  'update_account_totals'
);
```

**예상 결과**: 3개의 행 반환

### 3단계: 테스트

#### A. 샘플 데이터로 테스트

```sql
-- 1. 샘플 계좌 잔고 데이터 삽입
SELECT sync_kiwoom_account_balance(
  auth.uid(),
  '8112-5100',
  '{"dnca_tot_amt": "50000000", "nxdy_excc_amt": "45000000", "ord_psbl_cash": "45000000", "prvs_rcdl_excc_amt": "50000000", "pchs_amt_smtl_amt": "0"}'::jsonb
);

-- 2. 결과 확인
SELECT * FROM kw_account_balance WHERE user_id = auth.uid();
```

**예상 결과**: 1개의 행이 삽입되어야 함 (total_cash = 50000000)

#### B. 프론트엔드에서 "키움 계좌 동기화" 버튼 테스트

1. 브라우저에서 포트폴리오 패널 접속
2. F12 (개발자 도구) 열기
3. Console 탭 선택
4. **"키움 계좌 동기화"** 버튼 클릭
5. 콘솔에서 로그 확인:

```
✅ 기대하는 로그:
🔑 키움 API 연동 시작
📡 토큰 응답 상태: 200
✅ 토큰 발급 성공
📊 계좌평가잔고내역 조회 시작
✅ 잔고 정보 조회 성공
✅ 보유 종목 조회 성공
✅ 키움 계좌 동기화 완료

❌ 에러 예시:
relation "kw_account_balance" does not exist
→ 테이블이 생성되지 않음 (위 2단계 A 다시 실행)

function sync_kiwoom_account_balance does not exist
→ 함수가 생성되지 않음 (위 2단계 B 다시 실행)
```

### 4단계: 계좌 정보 설정 확인

```sql
-- 1. 프로필에 키움 계좌번호 확인
SELECT id, kiwoom_account
FROM profiles
WHERE id = auth.uid();
```

**kiwoom_account가 NULL이라면**:
```sql
UPDATE profiles
SET kiwoom_account = '8112-5100'  -- 본인의 키움 계좌번호로 변경
WHERE id = auth.uid();
```

```sql
-- 2. 키움 API 키 확인
SELECT key_type, is_active, is_test_mode
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';
```

**결과가 없거나 is_active=false라면**: API 키를 다시 등록해야 합니다.

## 🎯 완료 후 확인사항

### ✅ 체크리스트

- [ ] `kw_account_balance` 테이블 생성 확인
- [ ] `kw_portfolio` 테이블 생성 확인
- [ ] `sync_kiwoom_account_balance` 함수 생성 확인
- [ ] `sync_kiwoom_portfolio` 함수 생성 확인
- [ ] `update_account_totals` 함수 생성 확인
- [ ] 샘플 데이터 테스트 성공
- [ ] 프로필에 `kiwoom_account` 설정 확인
- [ ] `user_api_keys`에 키움 API 키 등록 확인
- [ ] 프론트엔드에서 "키움 계좌 동기화" 버튼 클릭 시 정상 작동

## 📊 최종 확인 쿼리

모든 설정이 완료되었는지 한 번에 확인:

```sql
-- 1. 테이블 확인
SELECT 'Tables' as check_type, table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('kw_account_balance', 'kw_portfolio')

UNION ALL

-- 2. 함수 확인
SELECT 'Functions' as check_type, proname
FROM pg_proc
WHERE proname IN (
  'sync_kiwoom_account_balance',
  'sync_kiwoom_portfolio',
  'update_account_totals'
)

UNION ALL

-- 3. 프로필 확인
SELECT 'Profile' as check_type,
  CASE WHEN kiwoom_account IS NOT NULL THEN 'OK: ' || kiwoom_account ELSE 'Missing' END
FROM profiles
WHERE id = auth.uid()

UNION ALL

-- 4. API 키 확인
SELECT 'API Keys' as check_type,
  key_type || ' (' || CASE WHEN is_active THEN 'Active' ELSE 'Inactive' END || ')'
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';
```

**예상 결과**:
```
check_type | table_name / proname / etc
-----------+----------------------------------------
Tables     | kw_account_balance
Tables     | kw_portfolio
Functions  | sync_kiwoom_account_balance
Functions  | sync_kiwoom_portfolio
Functions  | update_account_totals
Profile    | OK: 8112-5100
API Keys   | app_key (Active)
API Keys   | app_secret (Active)
```

## ⚠️ 주의사항

### RLS (Row Level Security)

테이블에는 RLS가 활성화되어 있습니다. 만약 여전히 데이터가 보이지 않는다면:

```sql
-- 임시로 RLS 비활성화 (테스트용)
ALTER TABLE kw_account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio DISABLE ROW LEVEL SECURITY;

-- 테스트 후 다시 활성화
ALTER TABLE kw_account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio ENABLE ROW LEVEL SECURITY;
```

### Edge Function 로그 확인

Supabase 대시보드 → Functions → sync-kiwoom-balance → Logs에서 에러 메시지 확인

## 🔍 트러블슈팅

### 문제: "키움 API 키가 설정되지 않았습니다"

**해결**:
```sql
-- API 키 등록 (예시 - 실제 키로 교체)
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_test_mode, is_active)
VALUES
  (auth.uid(), 'kiwoom', 'app_key', encode('YOUR_APP_KEY'::bytea, 'base64'), true, true),
  (auth.uid(), 'kiwoom', 'app_secret', encode('YOUR_APP_SECRET'::bytea, 'base64'), true, true);
```

### 문제: "토큰 발급 실패"

**원인**:
1. API 키가 잘못됨
2. 키움 모의투자 서버 점검 중
3. 장 마감 시간

**해결**:
- API 키 재확인
- 키움증권 OpenAPI 사이트에서 새 키 발급
- 장중 시간에 다시 시도

### 문제: 데이터가 삽입되지 않음

**확인**:
```sql
-- RLS 정책 확인
SELECT tablename, policyname, permissive, cmd
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('kw_account_balance', 'kw_portfolio');
```

## 📝 다음 단계

모든 것이 정상 작동하면:

1. ✅ 프론트엔드의 Realtime 구독이 자동으로 포트폴리오 업데이트
2. ✅ 주문 체결 시 수동으로 "키움 계좌 동기화" 버튼 클릭
3. ⏳ 향후 n8n 워크플로우에서 자동 동기화 구현 (Phase 2)

## 관련 파일

- [supabase/migrations/06_create_kiwoom_balance_tables.sql](supabase/migrations/06_create_kiwoom_balance_tables.sql)
- [supabase/migrations/07_create_kiwoom_sync_functions.sql](supabase/migrations/07_create_kiwoom_sync_functions.sql)
- [supabase/functions/sync-kiwoom-balance/index.ts](supabase/functions/sync-kiwoom-balance/index.ts)
- [src/components/trading/PortfolioPanel.tsx](src/components/trading/PortfolioPanel.tsx)
- [DEBUG_SYNC_ISSUE.md](DEBUG_SYNC_ISSUE.md) - 상세 디버깅 가이드
