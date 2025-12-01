# 🚀 빠른 수정 가이드: 키움 계좌 동기화

## 현재 상황
- ✅ `kw_account_balance` 테이블 존재함
- ✅ `kw_portfolio` 테이블 존재함 (추정)
- ❓ 데이터베이스 함수들이 존재하는지 미확인
- ❓ UNIQUE 제약 조건 확인 필요

## 🔍 1단계: 현재 상태 확인

Supabase SQL Editor에서 다음 파일을 실행하세요:

**[supabase/check_sync_setup.sql](supabase/check_sync_setup.sql)**

이 쿼리는 다음을 확인합니다:
- 테이블 제약 조건
- 인덱스
- 데이터베이스 함수 (가장 중요!)
- RLS 정책
- 현재 사용자 데이터
- 프로필 및 API 키

### 예상 결과

#### ✅ 정상인 경우:
```
Functions 섹션에서 3개의 함수가 보여야 함:
- sync_kiwoom_account_balance
- sync_kiwoom_portfolio
- update_account_totals
```

#### ❌ 문제가 있는 경우:
```
Functions 섹션이 비어있거나 함수 개수가 3개 미만
→ 2단계로 이동
```

## 🔧 2단계: 문제별 해결

### 문제 A: 데이터베이스 함수가 없음

**증상**: check_sync_setup.sql 실행 시 Functions 섹션이 비어있음

**해결**: Supabase SQL Editor에서 다음 파일 실행

**[supabase/migrations/07_create_kiwoom_sync_functions.sql](supabase/migrations/07_create_kiwoom_sync_functions.sql)**

또는 기존 파일이 있다면:

**[sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql](sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql)**

### 문제 B: UNIQUE 제약 조건 없음

**증상**: Constraints 섹션에 `uq_kw_account_balance_user_account`가 없음

**해결**: Supabase SQL Editor에서 다음 파일 실행

**[supabase/fix_kw_account_balance_constraints.sql](supabase/fix_kw_account_balance_constraints.sql)**

### 문제 C: RLS 정책 문제

**증상**: 데이터가 삽입되지만 조회되지 않음

**해결**:
```sql
-- 임시로 RLS 비활성화 (테스트용)
ALTER TABLE kw_account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio DISABLE ROW LEVEL SECURITY;
```

**테스트 후 다시 활성화**:
```sql
ALTER TABLE kw_account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio ENABLE ROW LEVEL SECURITY;
```

### 문제 D: 프로필에 계좌번호 없음

**증상**: Profile 섹션에서 kiwoom_account가 NULL

**해결**:
```sql
UPDATE profiles
SET kiwoom_account = '8112-5100'  -- 본인의 계좌번호로 변경
WHERE id = auth.uid();
```

### 문제 E: API 키 없음

**증상**: API Keys 섹션이 비어있거나 is_active=false

**해결**:
```sql
-- 기존 키 삭제
DELETE FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 새 키 등록 (실제 키로 교체)
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_test_mode, is_active)
VALUES
  (auth.uid(), 'kiwoom', 'app_key', encode('YOUR_APP_KEY'::bytea, 'base64'), true, true),
  (auth.uid(), 'kiwoom', 'app_secret', encode('YOUR_APP_SECRET'::bytea, 'base64'), true, true);
```

## 🧪 3단계: 테스트

### A. 함수 직접 테스트

```sql
-- 샘플 데이터로 함수 테스트
SELECT sync_kiwoom_account_balance(
  auth.uid(),
  '8112-5100',
  '{"dnca_tot_amt": "50000000", "nxdy_excc_amt": "45000000", "ord_psbl_cash": "45000000", "prvs_rcdl_excc_amt": "50000000", "pchs_amt_smtl_amt": "0"}'::jsonb
);

-- 결과 확인
SELECT * FROM kw_account_balance WHERE user_id = auth.uid();
```

**예상 결과**: total_cash = 50000000인 행이 삽입됨

### B. Edge Function 테스트

브라우저 개발자 도구(F12) → Console에서:

```javascript
const { data, error } = await supabase.functions.invoke('sync-kiwoom-balance', {
  method: 'POST',
});

console.log('Response:', data);
console.log('Error:', error);
```

**예상 결과**:
```json
{
  "success": true,
  "message": "계좌 정보 동기화 완료",
  "data": {
    "balance": { ... },
    "portfolio_count": 0,
    "account_number": "8112-5100",
    "is_test_mode": true
  }
}
```

### C. 프론트엔드 버튼 테스트

1. 포트폴리오 패널 접속
2. F12 열기 → Console 탭
3. "키움 계좌 동기화" 버튼 클릭
4. 로그 확인:
   ```
   🔑 키움 API 연동 시작
   ✅ 토큰 발급 성공
   ✅ 잔고 정보 조회 성공
   ✅ 키움 계좌 동기화 완료
   ```

## 🎯 4단계: 최종 확인

모든 설정이 완료되었는지 확인:

```sql
-- 종합 상태 확인
SELECT
  'Tables' as category,
  COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('kw_account_balance', 'kw_portfolio')

UNION ALL

SELECT
  'Functions',
  COUNT(*)
FROM pg_proc
WHERE proname IN (
  'sync_kiwoom_account_balance',
  'sync_kiwoom_portfolio',
  'update_account_totals'
)

UNION ALL

SELECT
  'Profile with Account',
  COUNT(*)
FROM profiles
WHERE id = auth.uid() AND kiwoom_account IS NOT NULL

UNION ALL

SELECT
  'Active API Keys',
  COUNT(*)
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
  AND is_active = true;
```

**예상 결과**:
```
category              | count
----------------------+-------
Tables                | 2
Functions             | 3
Profile with Account  | 1
Active API Keys       | 2
```

## ✅ 완료 체크리스트

- [ ] `check_sync_setup.sql` 실행 완료
- [ ] 3개의 데이터베이스 함수 확인
- [ ] UNIQUE 제약 조건 확인/추가
- [ ] 프로필에 계좌번호 설정
- [ ] API 키 2개 (app_key, app_secret) 활성화
- [ ] 샘플 데이터로 함수 테스트 성공
- [ ] Edge Function 테스트 성공
- [ ] 프론트엔드 버튼 테스트 성공

## 🐛 여전히 안 되는 경우

### 브라우저 콘솔에서 정확한 에러 확인

1. F12 → Console 탭
2. "키움 계좌 동기화" 버튼 클릭
3. **빨간색 에러 메시지 전체를 복사**하여 알려주세요

### Supabase Edge Function 로그 확인

1. Supabase 대시보드
2. Functions 메뉴
3. `sync-kiwoom-balance` 클릭
4. Logs 탭
5. **최근 에러 로그를 복사**하여 알려주세요

## 📂 관련 파일

- [supabase/check_sync_setup.sql](supabase/check_sync_setup.sql) - 현재 상태 확인
- [supabase/fix_kw_account_balance_constraints.sql](supabase/fix_kw_account_balance_constraints.sql) - 제약 조건 추가
- [supabase/migrations/07_create_kiwoom_sync_functions.sql](supabase/migrations/07_create_kiwoom_sync_functions.sql) - 함수 생성
- [sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql](sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql) - 함수 생성 (대체)
