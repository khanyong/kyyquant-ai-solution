# 키움 계좌 잔고 연동 설정 가이드

## 📋 개요
프론트엔드에서 키움증권 API를 통해 실제 계좌 잔고와 보유 주식을 조회하여 표시하는 기능입니다.

---

## 🚀 설정 순서

### Step 1: Supabase 테이블 생성

Supabase SQL Editor에서 다음 파일들을 순서대로 실행하세요:

#### 1-1. 계좌 테이블 생성
```sql
-- 파일: sql/CREATE_ACCOUNT_BALANCE_TABLES.sql
-- 실행: Supabase SQL Editor에 전체 내용 복사 후 실행
```

이 스크립트는 다음 테이블을 생성합니다:
- `kw_account_balance` - 계좌 잔고 (현금, 총자산, 평가손익)
- `kw_portfolio` - 보유 주식
- `kw_transaction_history` - 거래 내역

#### 1-2. 동기화 함수 생성
```sql
-- 파일: sql/CREATE_KIWOOM_BALANCE_SYNC_FUNCTION.sql
-- 실행: Supabase SQL Editor에 전체 내용 복사 후 실행
```

이 스크립트는 다음 함수를 생성합니다:
- `sync_kiwoom_account_balance()` - 계좌 잔고 동기화
- `sync_kiwoom_portfolio()` - 보유 주식 동기화
- `update_account_totals()` - 총 자산 계산

---

### Step 2: Supabase Edge Function 배포

#### 2-1. Supabase CLI 설치 (아직 안했다면)
```bash
npm install -g supabase
```

#### 2-2. Supabase 로그인
```bash
supabase login
```

#### 2-3. 프로젝트 연결
```bash
supabase link --project-ref YOUR_PROJECT_REF
```

프로젝트 REF는 Supabase Dashboard → Settings → General → Project ID에서 확인

#### 2-4. Edge Function 배포
```bash
supabase functions deploy sync-kiwoom-balance
```

#### 2-5. 환경변수 설정
Edge Function이 Supabase에 접근할 수 있도록 자동으로 설정됩니다.

---

### Step 3: 키움 API 키 설정

#### 3-1. 키움 API 키 발급
1. 키움증권 Open API 사이트 접속: https://openapi.kiwoom.com
2. 로그인 후 "API 관리" → "모의투자 APP KEY 관리"
3. App Key와 Secret Key 발급 (모의투자용)

#### 3-2. Supabase에 API 키 저장

Supabase SQL Editor에서 실행:

```sql
-- 파일: sql/INSERT_KIWOOM_API_KEYS.sql 수정하여 실행

-- App Key 저장
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  key_name,
  encrypted_value,
  is_test_mode,
  is_active
) VALUES (
  auth.uid(),
  'kiwoom',
  'app_key',
  'Kiwoom App Key',
  encode('YOUR_APP_KEY_HERE'::bytea, 'base64'),  -- 발급받은 App Key
  true,  -- 모의투자 = true, 실전 = false
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('YOUR_APP_KEY_HERE'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();

-- Secret Key 저장
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  key_name,
  encrypted_value,
  is_test_mode,
  is_active
) VALUES (
  auth.uid(),
  'kiwoom',
  'app_secret',
  'Kiwoom App Secret',
  encode('YOUR_SECRET_KEY_HERE'::bytea, 'base64'),  -- 발급받은 Secret Key
  true,
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('YOUR_SECRET_KEY_HERE'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();
```

#### 3-3. user_profiles에 계좌번호 저장

```sql
UPDATE user_profiles
SET kiwoom_account = '본인계좌번호'  -- 예: '81126100-01'
WHERE user_id = auth.uid();
```

---

### Step 4: 프론트엔드에서 확인

#### 4-1. 로그인
웹 애플리케이션에 로그인

#### 4-2. 자동매매 탭 접속
상단 탭에서 "자동매매" 클릭

#### 4-3. 키움 계좌 동기화 버튼 클릭
하단 "계좌 잔고 및 보유 자산" 섹션에서 **"키움 계좌 동기화"** 버튼 클릭

#### 4-4. 결과 확인
- 계좌 잔고 카드에 실제 키움 계좌 정보 표시
- 보유 종목 테이블에 실제 보유 주식 표시

---

## 🔍 동작 원리

```
[사용자] → [프론트엔드: "키움 계좌 동기화" 클릭]
   ↓
[Supabase Edge Function 호출]
   ↓
[키움 API]
   ├─ OAuth 토큰 발급
   ├─ 예수금 조회 (잔고)
   └─ 보유 종목 조회 (포트폴리오)
   ↓
[Supabase Functions 실행]
   ├─ sync_kiwoom_account_balance() - 잔고 저장
   ├─ sync_kiwoom_portfolio() - 보유 주식 저장
   └─ update_account_totals() - 총자산 계산
   ↓
[Supabase DB 업데이트]
   ├─ kw_account_balance 테이블
   └─ kw_portfolio 테이블
   ↓
[프론트엔드: 새로고침]
   └─ 실시간 데이터 표시
```

---

## 📊 키움 API 엔드포인트

### 1. OAuth 토큰 발급
- **URL**: `POST /oauth2/token`
- **용도**: API 호출에 필요한 액세스 토큰 발급

### 2. 예수금 조회 (계좌 잔고)
- **URL**: `GET /uapi/domestic-stock/v1/trading/inquire-psbl-order`
- **TR_ID**: `VTTC8908R` (모의), `TTTC8908R` (실전)
- **응답 필드**:
  - `dnca_tot_amt`: 예수금 총액
  - `nxdy_excc_amt`: 출금가능금액
  - `ord_psbl_cash`: 주문가능현금

### 3. 보유 종목 조회
- **URL**: `GET /uapi/domestic-stock/v1/trading/inquire-balance`
- **TR_ID**: `VTTC8434R` (모의), `TTTC8434R` (실전)
- **응답 필드**:
  - `pdno`: 종목코드
  - `prdt_name`: 종목명
  - `hldg_qty`: 보유수량
  - `pchs_avg_pric`: 매입평균가격
  - `prpr`: 현재가
  - `evlu_amt`: 평가금액
  - `evlu_pfls_amt`: 평가손익

---

## 🧪 테스트 방법

### 샘플 데이터로 테스트

키움 API 연동 전에 샘플 데이터로 UI를 먼저 확인:

```sql
SELECT insert_sample_account_data(auth.uid(), '본인계좌번호');
```

이 함수는 다음 샘플 데이터를 생성합니다:
- 총 자산: ₩80,000,000
- 현금: ₩50,000,000
- 주식: 삼성전자, SK하이닉스, 카카오

---

## ⚠️ 주의사항

1. **모의투자 vs 실전투자**
   - 처음에는 반드시 모의투자로 테스트
   - `is_test_mode = true`로 설정
   - 모의투자 API 키와 실전 API 키는 다름

2. **API 호출 제한**
   - 키움 API는 초당 호출 횟수 제한 있음
   - "키움 계좌 동기화" 버튼은 필요할 때만 클릭

3. **보안**
   - API 키는 Base64 인코딩되어 저장
   - RLS (Row Level Security)로 사용자별 데이터 격리
   - 프론트엔드에서 직접 API 호출하지 않고 Edge Function 사용

4. **장 운영시간**
   - 실시간 데이터는 장 운영시간에만 정확
   - 장 마감 후에는 종가 데이터 표시

---

## 🐛 트러블슈팅

### 1. "키움 API 키가 설정되지 않았습니다"
→ Step 3-2 확인: `user_api_keys` 테이블에 키 저장 확인
```sql
SELECT * FROM user_api_keys WHERE user_id = auth.uid() AND provider = 'kiwoom';
```

### 2. "키움 계좌 정보가 없습니다"
→ Step 3-3 확인: `user_profiles`에 계좌번호 저장 확인
```sql
SELECT kiwoom_account FROM user_profiles WHERE user_id = auth.uid();
```

### 3. "토큰 발급 실패"
→ App Key와 Secret Key가 정확한지 확인
→ 모의투자 키는 모의투자 URL(`mockapi.kiwoom.com`)에서만 동작

### 4. Edge Function 오류
→ Supabase Dashboard → Edge Functions → Logs에서 로그 확인

### 5. "인증되지 않은 사용자입니다"
→ 로그인 상태 확인
→ Supabase 세션 만료 시 재로그인

---

## 📝 추가 기능 제안

1. **자동 동기화**
   - 5분마다 자동으로 키움 계좌 동기화
   - useEffect + setInterval 사용

2. **거래 내역 조회**
   - 키움 API로 당일 거래 내역 조회
   - `kw_transaction_history` 테이블에 저장

3. **알림 기능**
   - 특정 종목 손익률 도달 시 브라우저 알림
   - Supabase Realtime으로 실시간 업데이트

4. **차트 표시**
   - 보유 종목별 비중 파이 차트
   - 일별 자산 증감 라인 차트

---

## 📚 참고 문서

- [키움 Open API 가이드](https://openapi.kiwoom.com/document)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Supabase RLS](https://supabase.com/docs/guides/auth/row-level-security)
