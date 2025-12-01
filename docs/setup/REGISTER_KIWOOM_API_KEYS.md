# 🔑 키움 API 키 등록 가이드

## 🚨 문제 확인

```sql
SELECT * FROM user_api_keys WHERE user_id = auth.uid() AND provider = 'kiwoom';
-- 결과: No rows returned
```

**키움 API 키가 등록되어 있지 않습니다!** 이것이 동기화가 작동하지 않는 근본 원인입니다.

## 📋 키움 API 키 발급받기

### 1단계: 키움증권 OpenAPI 포털 접속

1. **https://apiportal.kiwoom.com** 접속
2. 로그인 (키움증권 계좌 필요)

### 2단계: 모의투자 API 신청

1. 상단 메뉴에서 **"API 신청"** 클릭
2. **"모의투자 API"** 선택
3. 약관 동의 후 신청
4. 승인 대기 (보통 즉시 또는 1영업일 소요)

### 3단계: API 키 발급

1. 승인 후 **"API 키 관리"** 메뉴 접속
2. **App Key** 와 **App Secret** 확인
3. 복사하여 메모장에 저장

**예시:**
```
App Key:     PS1234567890abcdefghijklmnopqrstuvwxyz12345
App Secret:  AS9876543210zyxwvutsrqponmlkjihgfedcba54321
```

## 🔧 API 키 등록하기

### 방법 1: SQL로 등록 (권장)

1. Supabase SQL Editor 열기
2. [supabase/register_kiwoom_api_keys.sql](supabase/register_kiwoom_api_keys.sql) 파일 열기
3. **YOUR_APP_KEY** 와 **YOUR_APP_SECRET** 을 실제 키로 교체:

```sql
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  encrypted_value,
  is_test_mode,
  is_active,
  created_at,
  updated_at
) VALUES
  -- App Key
  (
    auth.uid(),
    'kiwoom',
    'app_key',
    encode('PS1234567890abcdefghijklmnopqrstuvwxyz12345'::bytea, 'base64'),  -- 🔑 실제 App Key
    true,  -- 모의투자
    true,
    NOW(),
    NOW()
  ),
  -- App Secret
  (
    auth.uid(),
    'kiwoom',
    'app_secret',
    encode('AS9876543210zyxwvutsrqponmlkjihgfedcba54321'::bytea, 'base64'),  -- 🔑 실제 App Secret
    true,  -- 모의투자
    true,
    NOW(),
    NOW()
  );
```

4. **실행** 버튼 클릭

### 방법 2: 프론트엔드에서 등록 (UI가 있다면)

1. 설정 메뉴 → API 키 관리
2. 키움 API 키 입력 폼에 App Key와 App Secret 입력
3. 저장

## ✅ 등록 확인

SQL Editor에서 실행:

```sql
SELECT
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;
```

**예상 결과:**
```
key_type    | is_active | is_test_mode | key_length | created_at
------------|-----------|--------------|------------|------------
app_key     | true      | true         | 60         | 2025-11-17...
app_secret  | true      | true         | 60         | 2025-11-17...
```

- ✅ 2개의 행이 반환되어야 함
- ✅ `is_active = true`
- ✅ `is_test_mode = true` (모의투자)
- ✅ `key_length > 0`

## 🧪 API 키 등록 후 테스트

### 1. "키움 계좌 동기화" 버튼 클릭

1. 포트폴리오 패널 접속
2. F12 (개발자 도구) 열기
3. **"키움 계좌 동기화"** 버튼 클릭
4. 콘솔 로그 확인

**예상 로그:**
```javascript
🔑 키움 API 연동 시작
✅ 토큰 발급 성공
📊 계좌평가잔고내역 조회 시작
✅ 잔고 정보 조회 성공
✅ 보유 종목 조회 성공
✅ 키움 계좌 동기화 완료
```

### 2. Edge Function 로그 확인

Supabase 대시보드 → Functions → sync-kiwoom-balance → Logs

**정상 로그:**
```
🔑 키움 API 연동 시작: { accountNumber: "8112-5100", isTestMode: true }
📡 토큰 응답 상태: 200 OK
✅ 토큰 발급 성공
📊 계좌평가잔고내역 조회 시작
✅ 잔고 정보 조회 성공
✅ 보유 종목 조회 성공 (1개)
```

### 3. 데이터베이스 확인

```sql
-- 계좌 잔고 확인
SELECT * FROM kw_account_balance WHERE user_id = auth.uid();

-- 포트폴리오 확인
SELECT * FROM kw_portfolio WHERE user_id = auth.uid();
```

**정상이면:** 실제 키움 계좌 데이터가 조회되어야 함

## ⚠️ 주의사항

### 보안

- API 키는 **절대 공개하지 마세요**
- GitHub에 커밋하지 마세요
- `.env` 파일에도 넣지 마세요 (Supabase DB에만 저장)

### 모의투자 vs 실전투자

- `is_test_mode = true` → 모의투자 (권장)
- `is_test_mode = false` → **실전투자** (실제 계좌 사용, 주의!)

### API 키 만료

- 키움 API 키는 **1년마다 갱신** 필요
- 만료되면 새로 발급받아 등록

## 🐛 트러블슈팅

### 문제: "키움 API 키가 설정되지 않았습니다" 에러

**원인:** API 키가 등록되지 않음 또는 `is_active = false`

**해결:**
```sql
-- is_active 확인
SELECT key_type, is_active FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 활성화
UPDATE user_api_keys
SET is_active = true
WHERE user_id = auth.uid() AND provider = 'kiwoom';
```

### 문제: "토큰 발급 실패" 에러

**원인:** API 키가 잘못됨

**해결:**
1. 키움 OpenAPI 포털에서 API 키 재확인
2. 올바른 키로 재등록
3. App Key와 App Secret을 바꿔서 입력하지 않았는지 확인

### 문제: "키움 API 키가 완전하지 않습니다" 에러

**원인:** app_key 또는 app_secret 중 하나만 등록됨

**해결:** 2개 모두 등록되었는지 확인
```sql
SELECT key_type, COUNT(*) FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom'
GROUP BY key_type;

-- 예상: app_key = 1, app_secret = 1
```

## 📞 추가 지원

### 키움 OpenAPI 고객센터
- 전화: 1544-9000
- 문의: "OpenAPI App Key 발급 문의"

### 키움 OpenAPI 포털
- URL: https://apiportal.kiwoom.com
- FAQ 및 개발 가이드 확인

## 🎯 다음 단계

1. ✅ 키움 OpenAPI 포털에서 API 키 발급
2. ✅ Supabase SQL Editor에서 API 키 등록
3. ✅ 등록 확인 (2개의 행 반환)
4. ✅ "키움 계좌 동기화" 버튼 클릭
5. ✅ 정상 작동 확인

**API 키만 등록하면 모든 문제가 해결됩니다!** 🚀
