# 키움 계좌 동기화 버튼 작동 안 하는 문제 디버깅

## 문제 증상
"키움 계좌 동기화" 버튼을 눌러도 포트폴리오가 업데이트되지 않음

## 진단 체크리스트

### 1. 브라우저 콘솔 로그 확인

브라우저 개발자 도구(F12)를 열고 다음 로그를 확인하세요:

```javascript
// 버튼 클릭 시 나타나야 할 로그들:
🔑 키움 API 연동 시작
🔑 토큰 발급 요청
📡 토큰 응답 상태
✅ 토큰 발급 성공
📊 계좌평가잔고내역 조회 시작
📈 보유종목 조회 응답 상태
✅ 잔고 정보 조회 성공
✅ 보유 종목 조회 성공
```

**에러가 있다면** 에러 메시지를 확인하세요.

### 2. Supabase 데이터베이스 함수 확인

다음 SQL을 Supabase SQL Editor에서 실행하여 필요한 함수들이 존재하는지 확인:

```sql
-- 함수 존재 여부 확인
SELECT
  proname as function_name,
  pg_get_functiondef(oid) as definition
FROM pg_proc
WHERE proname IN (
  'sync_kiwoom_account_balance',
  'sync_kiwoom_portfolio',
  'update_account_totals'
);
```

**결과가 비어있다면** → 함수가 생성되지 않은 것입니다. 다음 파일을 실행하세요:
- [sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql](sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql)

### 3. 키움 API 키 설정 확인

```sql
-- 현재 사용자의 키움 API 키 확인
SELECT
  key_type,
  is_test_mode,
  is_active,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom';
```

**예상 결과**:
- `app_key` 1개
- `app_secret` 1개
- `is_active = true`
- `is_test_mode = true` (모의투자) 또는 `false` (실전투자)

**결과가 없거나 is_active=false라면** → API 키를 다시 등록해야 합니다.

### 4. 프로필에 계좌번호 확인

```sql
-- 현재 사용자의 키움 계좌번호 확인
SELECT
  id,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();
```

**kiwoom_account가 NULL이거나 잘못되었다면** → 프로필을 업데이트하세요:

```sql
UPDATE profiles
SET kiwoom_account = '8112-5100'  -- 본인 계좌번호로 변경
WHERE id = auth.uid();
```

### 5. Edge Function 로그 확인

Supabase 대시보드에서:
1. Functions 메뉴 클릭
2. `sync-kiwoom-balance` 함수 클릭
3. Logs 탭에서 최근 실행 로그 확인

**에러 로그 예시**:
- `인증되지 않은 사용자입니다` → 로그인 필요
- `키움 계좌 정보가 없습니다` → profiles.kiwoom_account 설정 필요
- `키움 API 키가 설정되지 않았습니다` → user_api_keys 테이블에 키 등록 필요
- `토큰 발급 실패` → API 키가 잘못되었거나 키움 서버 문제

### 6. 수동으로 키움 API 테스트

브라우저 콘솔에서 직접 Edge Function 호출:

```javascript
const { data, error } = await supabase.functions.invoke('sync-kiwoom-balance', {
  method: 'POST',
});

console.log('Response:', data, error);
```

### 7. 테이블 데이터 확인

```sql
-- 현재 계좌 잔고 데이터 확인
SELECT * FROM kw_account_balance
WHERE user_id = auth.uid();

-- 현재 포트폴리오 데이터 확인
SELECT * FROM kw_portfolio
WHERE user_id = auth.uid();
```

## 가능한 원인과 해결 방법

### 원인 1: 데이터베이스 함수가 생성되지 않음

**증상**: Edge Function 로그에 "function sync_kiwoom_account_balance does not exist" 에러

**해결**:
```bash
# Supabase SQL Editor에서 실행
cd d:\Dev\auto_stock
# sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql 파일 내용을 복사하여 실행
```

### 원인 2: 키움 API 키가 없거나 잘못됨

**증상**: "키움 API 키가 설정되지 않았습니다" 또는 "토큰 발급 실패"

**해결**:
1. 키움증권 OpenAPI 사이트에서 API 키 발급
2. Supabase에서 다음 SQL 실행:

```sql
-- 기존 키 삭제 (있다면)
DELETE FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 새 키 등록
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_test_mode, is_active)
VALUES
  (auth.uid(), 'kiwoom', 'app_key', encode('YOUR_APP_KEY'::bytea, 'base64'), true, true),
  (auth.uid(), 'kiwoom', 'app_secret', encode('YOUR_APP_SECRET'::bytea, 'base64'), true, true);
```

### 원인 3: RLS (Row Level Security) 정책 문제

**증상**: 함수는 실행되지만 데이터가 업데이트되지 않음

**해결**:
```sql
-- RLS 정책 확인
SELECT tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('kw_account_balance', 'kw_portfolio');

-- 임시로 RLS 비활성화 (테스트용)
ALTER TABLE kw_account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio DISABLE ROW LEVEL SECURITY;

-- 테스트 후 다시 활성화
ALTER TABLE kw_account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio ENABLE ROW LEVEL SECURITY;
```

### 원인 4: 키움 API 서버 문제 (모의투자)

**증상**: "토큰 발급 실패" 또는 타임아웃

**해결**:
- 키움 모의투자 서버가 점검 중일 수 있음
- 장 마감 후에는 API가 작동하지 않을 수 있음
- 실전투자 API 사용 또는 나중에 다시 시도

### 원인 5: Edge Function이 배포되지 않음

**증상**: "Function not found" 에러

**해결**:
```bash
# Supabase CLI로 Edge Function 배포
cd d:\Dev\auto_stock
supabase functions deploy sync-kiwoom-balance
```

## 빠른 테스트 방법

### 테스트 1: 샘플 데이터로 함수 테스트

```sql
-- 샘플 데이터로 함수가 작동하는지 테스트
SELECT sync_kiwoom_account_balance(
  auth.uid(),
  '8112-5100',
  '{"dnca_tot_amt": "50000000", "nxdy_excc_amt": "45000000", "ord_psbl_cash": "45000000", "prvs_rcdl_excc_amt": "50000000", "pchs_amt_smtl_amt": "0"}'::jsonb
);

-- 결과 확인
SELECT * FROM kw_account_balance WHERE user_id = auth.uid();
```

**작동하면** → Edge Function 문제
**작동 안 하면** → 데이터베이스 함수 문제

### 테스트 2: 직접 데이터 삽입

```sql
-- 직접 데이터 삽입 테스트
INSERT INTO kw_account_balance (
  user_id,
  account_number,
  total_cash,
  available_cash,
  order_cash,
  total_asset,
  stock_value,
  profit_loss,
  profit_loss_rate,
  updated_at
) VALUES (
  auth.uid(),
  '8112-5100',
  50000000,
  45000000,
  45000000,
  50000000,
  0,
  0,
  0,
  now()
)
ON CONFLICT (user_id, account_number)
DO UPDATE SET
  total_cash = EXCLUDED.total_cash,
  updated_at = now();

-- 결과 확인
SELECT * FROM kw_account_balance WHERE user_id = auth.uid();
```

**작동하면** → RLS 문제는 아님
**작동 안 하면** → RLS 또는 권한 문제

## 다음 단계

위 체크리스트를 확인한 후, 발견한 에러 메시지나 문제를 알려주세요:

1. 브라우저 콘솔 로그
2. Supabase Edge Function 로그
3. SQL 쿼리 결과

이 정보를 바탕으로 정확한 원인을 찾아 해결하겠습니다.
