# 🚀 키움 계좌 연동 빠른 설정 가이드

## ⚠️ 중요: 실행 순서

다음 순서대로 **정확히** 실행하세요:

---

## 📝 Step 1: 테이블 확인 및 생성

**Supabase SQL Editor에서 실행**:

```sql
-- 파일: sql/CHECK_TABLES_AND_CREATE_API_KEYS.sql
-- 전체 내용 복사하여 실행
```

**확인사항**:
- ✅ `user_api_keys 테이블: ✅ 존재`
- ✅ `profiles.kiwoom_account 컬럼: ✅ 존재`

두 항목 모두 "✅ 존재"가 나와야 합니다!

---

## 📝 Step 2: 계좌 잔고 테이블 생성

**Supabase SQL Editor에서 실행**:

```sql
-- 파일: sql/CREATE_ACCOUNT_BALANCE_TABLES.sql
-- 전체 내용 복사하여 실행
```

**생성되는 테이블**:
- `kw_account_balance` - 계좌 잔고
- `kw_portfolio` - 보유 주식
- `kw_transaction_history` - 거래 내역

---

## 📝 Step 3: 동기화 함수 생성

**Supabase SQL Editor에서 실행**:

```sql
-- 파일: sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql
-- 전체 내용 복사하여 실행
```

**생성되는 함수**:
- `sync_kiwoom_account_balance()`
- `sync_kiwoom_portfolio()`
- `update_account_totals()`

---

## 📝 Step 4: 키움 API 키 저장

**Supabase SQL Editor에서 실행**:

```sql
-- 파일: sql/INSERT_MY_KIWOOM_KEYS.sql
-- 전체 내용 복사하여 실행
```

**확인**: 마지막 쿼리 결과
```
type            | count
----------------+-------
API Keys        | 2      ← 반드시 2여야 함!
Account Number  | 0 또는 1
```

`API Keys`가 **2**가 나와야 정상입니다!

---

## 📝 Step 5: 계좌번호 설정

**sql/INSERT_MY_KIWOOM_KEYS.sql 파일의 7번 섹션 수정**:

```sql
-- 주석 해제하고 본인 계좌번호로 수정!
UPDATE profiles
SET kiwoom_account = '81126100-01'  -- ← 본인 계좌번호로 변경!
WHERE id = auth.uid();
```

**계좌번호 형식**:
- `8자리숫자-01`
- 예: `81126100-01`
- 키움증권 앱 → 계좌 메뉴에서 확인

**실행 후 확인**:
```sql
SELECT kiwoom_account FROM profiles WHERE id = auth.uid();
```

---

## 📝 Step 6: Edge Function 배포

**터미널에서 실행**:

```bash
# 1. 프로젝트 디렉토리로 이동
cd d:\Dev\auto_stock

# 2. Supabase 로그인 (처음만)
supabase login

# 3. 프로젝트 연결 (처음만)
# Supabase Dashboard → Settings → General → Project ID 복사
supabase link --project-ref YOUR_PROJECT_ID

# 4. Edge Function 배포
supabase functions deploy sync-kiwoom-balance
```

**성공 메시지**:
```
Deployed Function sync-kiwoom-balance on project YOUR_PROJECT_ID
```

---

## 📝 Step 7: 프론트엔드 테스트

```bash
# 개발 서버 실행
npm run dev
```

**브라우저에서**:
1. http://localhost:5173 접속
2. 로그인
3. **"자동매매"** 탭 클릭
4. 하단으로 스크롤
5. **"키움 계좌 동기화"** 버튼 클릭
6. 계좌 정보 표시 확인! 🎉

---

## ✅ 최종 확인 체크리스트

### Supabase 테이블
- [ ] `user_api_keys` 테이블 존재
- [ ] `profiles` 테이블에 `kiwoom_account` 컬럼 존재
- [ ] `kw_account_balance` 테이블 존재
- [ ] `kw_portfolio` 테이블 존재
- [ ] `kw_transaction_history` 테이블 존재

### Supabase 함수
- [ ] `sync_kiwoom_account_balance()` 함수 존재
- [ ] `sync_kiwoom_portfolio()` 함수 존재
- [ ] `update_account_totals()` 함수 존재

### API 키 설정
- [ ] App Key 저장됨 (count = 1)
- [ ] Secret Key 저장됨 (count = 1)
- [ ] 총 API Keys = 2
- [ ] 계좌번호 저장됨

### Edge Function
- [ ] `sync-kiwoom-balance` 배포됨
- [ ] Supabase Dashboard에서 확인 가능

### 프론트엔드
- [ ] "키움 계좌 동기화" 버튼 동작
- [ ] 계좌 잔고 카드에 데이터 표시
- [ ] 보유 종목 테이블에 데이터 표시

---

## 🐛 트러블슈팅

### 문제 1: API Keys count = 0

**원인**: `user_api_keys` 테이블이 없거나 키 저장 실패

**해결**:
1. Step 1 실행: `CHECK_TABLES_AND_CREATE_API_KEYS.sql`
2. 테이블 생성 확인
3. Step 4 다시 실행: `INSERT_MY_KIWOOM_KEYS.sql`

---

### 문제 2: "relation 'user_api_keys' does not exist"

**해결**:
```sql
-- 파일: sql/CHECK_TABLES_AND_CREATE_API_KEYS.sql
-- 전체 실행하면 자동으로 테이블 생성됨
```

---

### 문제 3: "column 'kiwoom_account' does not exist"

**해결**:
```sql
-- profiles 테이블에 컬럼 추가
ALTER TABLE profiles ADD COLUMN kiwoom_account varchar(50);
```

또는 Step 1의 `CHECK_TABLES_AND_CREATE_API_KEYS.sql` 실행

---

### 문제 4: Edge Function 배포 실패

**확인사항**:
```bash
# Supabase CLI 설치 확인
supabase --version

# 로그인 상태 확인
supabase projects list

# 프로젝트 연결 확인
cat .git/config | grep supabase  # 또는
ls -la .supabase/
```

**재시도**:
```bash
supabase link --project-ref YOUR_PROJECT_ID
supabase functions deploy sync-kiwoom-balance --no-verify-jwt
```

---

### 문제 5: "키움 계좌 정보가 없습니다"

**확인**:
```sql
SELECT id, kiwoom_account FROM profiles WHERE id = auth.uid();
```

**계좌번호가 NULL이면**:
```sql
UPDATE profiles
SET kiwoom_account = '본인계좌번호-01'
WHERE id = auth.uid();
```

---

## 📊 데이터 확인 쿼리

**모든 설정 한 번에 확인**:

```sql
-- 1. 내 사용자 ID
SELECT auth.uid() as my_user_id;

-- 2. API 키 확인
SELECT key_type, is_test_mode, is_active, created_at
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 3. 계좌번호 확인
SELECT kiwoom_account FROM profiles WHERE id = auth.uid();

-- 4. 계좌 잔고 확인
SELECT * FROM kw_account_balance WHERE user_id = auth.uid();

-- 5. 보유 종목 확인
SELECT stock_code, stock_name, quantity, current_price, profit_loss
FROM kw_portfolio
WHERE user_id = auth.uid();
```

---

## 🎯 성공 기준

### Supabase 쿼리 결과
```sql
SELECT
  'API Keys' as type,
  COUNT(*) as count
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom' AND is_active = true
UNION ALL
SELECT
  'Account Number' as type,
  CASE WHEN kiwoom_account IS NOT NULL THEN 1 ELSE 0 END as count
FROM profiles
WHERE id = auth.uid();
```

**성공 결과**:
```
type            | count
----------------+-------
API Keys        | 2      ← ✅ 2여야 함!
Account Number  | 1      ← ✅ 1이어야 함!
```

### 프론트엔드 결과
- "키움 계좌 동기화" 버튼 클릭 시
- 계좌 잔고 카드 표시
- 보유 종목 테이블 표시

**모두 성공하면 설정 완료! 🎉**

---

## 📚 참고 문서

- [상세 설정 가이드](./KIWOOM_BALANCE_SETUP.md)
- [체크리스트](./SETUP_CHECKLIST.md)
- [키움 Open API](https://openapi.kiwoom.com/document)
