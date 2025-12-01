# 키움 API 500 에러 해결 가이드

## 🚨 현재 상황

장중 시간(10:52)인데도 키움 모의투자 API가 500 에러를 반환하고 있습니다.

```
📡 토큰 응답 상태: 200 OK ✅
📈 보유종목 조회 상태: 500 ❌
⚠️ 보유 종목 조회 실패: INTERNAL_SERVER_ERROR
```

## 🔍 원인 분석

### 원인 1: 키움 모의투자 서버 문제 (가능성 높음)

**증상:**
- 토큰 발급은 성공
- 계좌 조회만 500 에러

**확인 방법:**
1. 키움증권 HTS 또는 웹 접속
2. 모의투자 계좌 조회 가능한지 확인
3. 키움 OpenAPI 공지사항 확인: https://apiportal.kiwoom.com

**해결:**
- 키움 서버가 정상화될 때까지 대기
- 1~2시간 후 재시도

### 원인 2: 모의투자 계좌 만료/비활성화

**증상:**
- 토큰은 받지만 계좌 조회 실패
- 모의투자 계좌가 비활성화됨

**확인 방법:**
```sql
-- Supabase SQL Editor에서 실행
SELECT kiwoom_account FROM profiles WHERE id = auth.uid();
```

**해결:**
1. 키움증권 HTS 접속
2. 모의투자 메뉴 확인
3. 모의투자 계좌 재신청 (만료된 경우)
4. 새 계좌번호로 프로필 업데이트:
   ```sql
   UPDATE profiles
   SET kiwoom_account = '새계좌번호'
   WHERE id = auth.uid();
   ```

### 원인 3: API 호출 파라미터 오류

**증상:**
- 계좌번호 형식이 잘못됨
- API 요청 파라미터 오류

**확인 방법:**
Supabase SQL Editor에서 [supabase/test_kiwoom_api_direct.sql](supabase/test_kiwoom_api_direct.sql) 실행

**예상 결과:**
```
계좌번호: 8112-5100
prefix: 8112 (4자리)
suffix: 5100 (4자리)
```

**문제가 있는 경우:**
- 계좌번호에 `-`가 없음
- prefix 또는 suffix 길이가 4자리가 아님

**해결:**
```sql
UPDATE profiles
SET kiwoom_account = '8112-5100'  -- 올바른 형식
WHERE id = auth.uid();
```

### 원인 4: Edge Function 코드 문제

**증상:**
- API 요청 방식이 잘못됨
- 헤더 또는 파라미터 오류

**확인:** Edge Function 코드 검토 필요

## 🎯 즉시 시도할 해결 방법

### 1단계: 계좌번호 확인 및 수정

Supabase SQL Editor에서:

```sql
-- 현재 계좌번호 확인
SELECT kiwoom_account FROM profiles WHERE id = auth.uid();

-- 만약 형식이 잘못되었다면 수정
UPDATE profiles
SET kiwoom_account = '8112-5100'  -- 본인의 정확한 계좌번호
WHERE id = auth.uid();
```

### 2단계: 키움 HTS에서 모의투자 확인

1. 키움증권 HTS 실행
2. 모의투자 메뉴 접속
3. 계좌 조회 시도
4. 계좌가 정상적으로 조회되는지 확인

### 3단계: 다른 시간대에 재시도

- 오후 1시경 재시도
- 오후 2시경 재시도
- 장 마감 전(오후 3시) 재시도

### 4단계: 실전투자 API로 전환 (최후의 수단)

모의투자 API가 계속 작동하지 않으면:

```sql
-- API 키를 실전투자 모드로 변경
UPDATE user_api_keys
SET is_test_mode = false
WHERE user_id = auth.uid()
  AND provider = 'kiwoom';
```

**⚠️ 주의:** 실전투자로 전환하면 **실제 계좌**를 사용합니다!

## 🔧 임시 해결책: 수동 데이터 입력

키움 API가 작동하지 않는 동안 임시로 데이터를 수동으로 입력할 수 있습니다:

```sql
-- 임시: 수동으로 계좌 잔고 입력
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
  45000000,  -- 실제 현금 잔고
  45000000,
  45000000,
  50000000,  -- 실제 총 자산
  5000000,   -- 실제 주식 평가액
  500000,    -- 실제 평가손익
  1.0,       -- 실제 수익률
  NOW()
)
ON CONFLICT (user_id, account_number)
DO UPDATE SET
  total_cash = EXCLUDED.total_cash,
  available_cash = EXCLUDED.available_cash,
  total_asset = EXCLUDED.total_asset,
  stock_value = EXCLUDED.stock_value,
  profit_loss = EXCLUDED.profit_loss,
  profit_loss_rate = EXCLUDED.profit_loss_rate,
  updated_at = NOW();

-- 임시: 수동으로 보유 종목 입력
DELETE FROM kw_portfolio WHERE user_id = auth.uid();

INSERT INTO kw_portfolio (
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  available_quantity,
  avg_price,
  current_price,
  purchase_amount,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at
) VALUES (
  auth.uid(),
  '8112-5100',
  '005930',      -- 종목코드
  '삼성전자',     -- 종목명
  10,            -- 보유수량
  10,
  70000,         -- 평균단가
  71000,         -- 현재가
  700000,
  710000,
  10000,
  1.43,
  NOW()
);
```

## 📞 추가 지원

### 키움증권 고객센터
- 전화: 1544-9000
- 문의 사항: "모의투자 API 계좌 조회 500 에러"

### 키움 OpenAPI 포털
- URL: https://apiportal.kiwoom.com
- 공지사항 및 FAQ 확인

## 📊 다음 단계

1. **[supabase/test_kiwoom_api_direct.sql](supabase/test_kiwoom_api_direct.sql)** 실행하여 계좌번호 확인
2. **키움 HTS**에서 모의투자 계좌 확인
3. **1~2시간 후** 다시 "키움 계좌 동기화" 버튼 클릭
4. **여전히 실패하면** 키움 고객센터에 문의

## 🔍 제게 알려주실 정보

다음 정보를 알려주시면 더 정확한 해결책을 드릴 수 있습니다:

1. **test_kiwoom_api_direct.sql** 실행 결과 (계좌번호 형식)
2. **키움 HTS**에서 모의투자 계좌 조회 가능 여부
3. **키움 OpenAPI 공지사항**에 점검 안내 있는지 여부
