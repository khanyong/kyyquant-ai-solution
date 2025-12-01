# 키움 계좌 연동 설정 체크리스트 ✅

## 📋 빠른 설정 가이드

### ✅ Step 1: Supabase 테이블 생성

**1-1. 계좌 테이블 생성**
```bash
실행 파일: sql/CREATE_ACCOUNT_BALANCE_TABLES.sql
```
- [ ] Supabase SQL Editor 열기
- [ ] 위 파일 전체 내용 복사하여 붙여넣기
- [ ] "Run" 클릭
- [ ] 성공 메시지 확인

**1-2. 동기화 함수 생성**
```bash
실행 파일: sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql
```
- [ ] Supabase SQL Editor에서 위 파일 전체 내용 실행
- [ ] 3개 함수 생성 확인:
  - `sync_kiwoom_account_balance()`
  - `sync_kiwoom_portfolio()`
  - `update_account_totals()`

---

### ✅ Step 2: 키움 API 키 저장

**2-1. API 키 저장**
```bash
실행 파일: sql/INSERT_MY_KIWOOM_KEYS.sql
```
- [ ] Supabase SQL Editor에서 위 파일 전체 내용 실행
- [ ] "API Keys" 확인 쿼리 결과 = 2 (App Key + Secret Key)

**2-2. 계좌번호 설정**
```sql
-- 본인 키움 계좌번호로 수정!
UPDATE user_profiles
SET kiwoom_account = '본인계좌번호-01'
WHERE user_id = auth.uid();
```
- [ ] 위 쿼리의 `'본인계좌번호-01'`을 실제 계좌번호로 수정
- [ ] 실행
- [ ] 계좌번호 저장 확인:
```sql
SELECT kiwoom_account FROM user_profiles WHERE user_id = auth.uid();
```

**참고**: 키움 모의투자 계좌번호 형식
- 일반적으로 `8자리숫자-01` 형식
- 예: `81126100-01`
- 키움증권 앱에서 확인 가능

---

### ✅ Step 3: Supabase Edge Function 배포

**3-1. Supabase CLI 설치** (이미 설치했다면 건너뛰기)
```bash
npm install -g supabase
```
- [ ] 설치 완료

**3-2. Supabase 로그인**
```bash
supabase login
```
- [ ] 브라우저에서 로그인
- [ ] 터미널에 "Logged in" 메시지 확인

**3-3. 프로젝트 연결**
```bash
supabase link --project-ref YOUR_PROJECT_REF
```
- [ ] Supabase Dashboard → Settings → General → Project ID 복사
- [ ] `YOUR_PROJECT_REF`를 실제 Project ID로 교체
- [ ] 실행
- [ ] "Linked" 메시지 확인

**3-4. Edge Function 배포**
```bash
cd d:\Dev\auto_stock
supabase functions deploy sync-kiwoom-balance
```
- [ ] 배포 성공 메시지 확인
- [ ] Supabase Dashboard → Edge Functions에서 `sync-kiwoom-balance` 확인

---

### ✅ Step 4: 프론트엔드 테스트

**4-1. 프론트엔드 실행**
```bash
npm run dev
```
- [ ] 웹 브라우저에서 `http://localhost:5173` 접속

**4-2. 로그인**
- [ ] 우측 상단 "로그인" 클릭
- [ ] Supabase 계정으로 로그인

**4-3. 키움 계좌 동기화**
- [ ] 상단 탭에서 **"자동매매"** 클릭
- [ ] 하단으로 스크롤하여 "계좌 잔고 및 보유 자산" 섹션 찾기
- [ ] **"키움 계좌 동기화"** 버튼 클릭
- [ ] 로딩 완료 후 계좌 정보 표시 확인

**예상 결과**:
```
✅ 계좌 잔고 카드
   - 총 자산: ₩XX,XXX,XXX
   - 보유 현금: ₩XX,XXX,XXX
   - 주식 평가액: ₩XX,XXX,XXX
   - 평가손익: +₩XXX,XXX (+X.XX%)

✅ 보유 종목 테이블
   - 종목명, 수량, 평균단가, 현재가 등 표시
```

---

## 🐛 문제 해결

### 문제 1: "키움 API 키가 설정되지 않았습니다"

**확인 사항**:
```sql
SELECT * FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
  AND is_active = true;
```
- 결과가 2개 행이어야 함 (app_key, app_secret)
- 0개라면 Step 2-1 다시 실행

---

### 문제 2: "키움 계좌 정보가 없습니다"

**확인 사항**:
```sql
SELECT kiwoom_account FROM user_profiles WHERE user_id = auth.uid();
```
- 결과가 NULL이면 Step 2-2 다시 실행
- 계좌번호 형식 확인: `XXXXXXXX-XX`

---

### 문제 3: "Edge Function이 배포되지 않았습니다"

**확인 사항**:
```bash
supabase functions list
```
- `sync-kiwoom-balance`가 목록에 있어야 함
- 없으면 Step 3-4 다시 실행

---

### 문제 4: "토큰 발급 실패"

**원인**: 키움 API 키가 올바르지 않음

**해결 방법**:
1. 키움 Open API 사이트에서 API 키 재확인
2. `sql/INSERT_MY_KIWOOM_KEYS.sql` 파일의 키 값 확인
3. App Key와 Secret Key가 정확히 입력되었는지 확인

---

### 문제 5: Edge Function 로그 확인

**Supabase Dashboard에서 확인**:
1. Dashboard → Edge Functions → `sync-kiwoom-balance` 클릭
2. "Logs" 탭 클릭
3. 에러 메시지 확인

**자주 나오는 에러**:
- `"인증되지 않은 사용자입니다"` → 로그아웃 후 재로그인
- `"토큰 발급 실패"` → API 키 확인
- `"키움 계좌 정보가 없습니다"` → user_profiles 테이블에 계좌번호 저장 확인

---

## 📊 현재 설정 확인 쿼리

**전체 설정 상태 한 번에 확인**:
```sql
-- 1. API 키 확인
SELECT 'API Keys' as category,
       key_type,
       is_test_mode,
       is_active
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 2. 계좌번호 확인
SELECT 'Account' as category,
       kiwoom_account
FROM user_profiles
WHERE user_id = auth.uid();

-- 3. 계좌 잔고 데이터 확인
SELECT 'Balance' as category,
       total_asset,
       total_cash,
       stock_value,
       profit_loss,
       updated_at
FROM kw_account_balance
WHERE user_id = auth.uid();

-- 4. 보유 종목 확인
SELECT 'Portfolio' as category,
       stock_code,
       stock_name,
       quantity,
       current_price,
       profit_loss
FROM kw_portfolio
WHERE user_id = auth.uid();
```

---

## ✨ 성공 확인

모든 체크박스를 체크했다면:

- ✅ **Step 1**: 테이블 및 함수 생성 완료
- ✅ **Step 2**: API 키 및 계좌번호 저장 완료
- ✅ **Step 3**: Edge Function 배포 완료
- ✅ **Step 4**: 프론트엔드에서 정상 동작 확인

**축하합니다! 🎉 키움 계좌 연동이 완료되었습니다!**

---

## 📝 다음 단계

### 자동 동기화 설정 (선택사항)

5분마다 자동으로 계좌 정보 업데이트:

**PortfolioPanel.tsx에 추가**:
```typescript
useEffect(() => {
  if (user) {
    fetchPortfolio()

    // 5분마다 자동 동기화
    const interval = setInterval(() => {
      syncKiwoomBalance()
    }, 5 * 60 * 1000) // 5분

    return () => clearInterval(interval)
  }
}, [user])
```

---

## 🔒 보안 참고사항

- ✅ API 키는 Base64로 인코딩되어 저장됨
- ✅ 프론트엔드에 API 키 노출 안 됨 (Edge Function 사용)
- ✅ RLS로 사용자별 데이터 격리
- ✅ 모의투자 모드로 안전하게 테스트 가능

---

## 📚 참고 문서

- [전체 설정 가이드](./KIWOOM_BALANCE_SETUP.md)
- [키움 Open API 가이드](https://openapi.kiwoom.com/document)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
