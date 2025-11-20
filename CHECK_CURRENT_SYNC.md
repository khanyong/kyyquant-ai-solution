# 현재 동기화 문제 진단

## 🔍 즉시 확인할 사항

### 1️⃣ 브라우저 콘솔 로그 확인

F12 → Console 탭에서 다음을 확인하세요:

1. "키움 계좌 동기화" 버튼 클릭 후 로그
2. 빨간색 에러 메시지
3. `Edge Function response:` 의 전체 내용

**특히 이 부분을 복사해주세요:**
```javascript
Edge Function response: { ... }
```

### 2️⃣ Supabase Edge Function 로그 확인

1. Supabase 대시보드 → Functions → sync-kiwoom-balance → Logs
2. **가장 최근 로그** (방금 클릭한 시간)
3. 다음 로그를 찾아주세요:
   - `📡 토큰 응답 상태`
   - `📈 보유종목 조회 응답 상태`
   - `✅ 잔고 정보 조회 성공` 또는 `❌ 에러`

### 3️⃣ 데이터베이스 실제 데이터 확인

Supabase SQL Editor에서 실행:

```sql
-- 계좌 잔고 확인
SELECT
  user_id,
  account_number,
  total_cash,
  available_cash,
  total_asset,
  stock_value,
  updated_at,
  NOW() as current_time,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) as seconds_since_update
FROM kw_account_balance
WHERE user_id = auth.uid()
ORDER BY updated_at DESC
LIMIT 1;

-- 포트폴리오 확인
SELECT
  stock_code,
  stock_name,
  quantity,
  avg_price,
  current_price,
  evaluated_amount,
  profit_loss,
  updated_at
FROM kw_portfolio
WHERE user_id = auth.uid()
ORDER BY updated_at DESC;
```

**확인할 점:**
- `updated_at`이 방금 전(몇 초 전)인가?
- 아니면 오래된 시간인가?

## 🎯 가능한 원인들

### 원인 A: Edge Function이 배포되지 않음

수정한 코드가 아직 배포 안 됨

**확인:**
```bash
supabase functions deploy sync-kiwoom-balance
```

### 원인 B: 키움 API가 여전히 500 에러 반환

장 시작했지만 여전히 서버 오류

**확인:** Edge Function 로그에서 `📈 보유종목 조회 응답 상태: 500` 확인

### 원인 C: 데이터는 업데이트되었지만 UI가 새로고침 안 됨

DB에는 저장됐지만 프론트엔드가 반영 안 함

**확인:** 위 SQL 실행 후 `updated_at`이 최근이면 이 경우

**해결:**
1. 포트폴리오 패널의 "새로고침" 버튼 클릭
2. 페이지 전체 새로고침 (F5)

### 원인 D: Realtime 구독 문제

DB는 업데이트되었지만 Realtime이 작동 안 함

**확인:** 브라우저 콘솔에서 Realtime 로그 확인
```javascript
📦 Order status changed: ...
💰 Account balance changed: ...
📊 Portfolio changed: ...
```

### 원인 E: RLS 정책 문제

DB 함수가 데이터를 삽입했지만 SELECT 권한 없음

**확인:**
```sql
-- RLS 정책 확인
SELECT tablename, policyname, cmd
FROM pg_policies
WHERE tablename IN ('kw_account_balance', 'kw_portfolio')
  AND schemaname = 'public';

-- 임시로 RLS 비활성화 (테스트)
ALTER TABLE kw_account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio DISABLE ROW LEVEL SECURITY;
```

## 📋 빠른 진단 순서

1. **브라우저 콘솔** 확인 → 에러 메시지?
2. **Edge Function 로그** 확인 → 500 에러?
3. **SQL 쿼리** 실행 → `updated_at`이 최근?
4. **페이지 새로고침** (F5) → UI 업데이트?

## 🚀 제게 알려주실 정보

다음 정보를 복사해서 알려주세요:

1. **브라우저 콘솔 로그** (Edge Function response 부분)
2. **Edge Function 최신 로그** (JSON 전체)
3. **SQL 쿼리 결과** (updated_at 시간)

이 정보로 정확한 원인을 바로 찾을 수 있습니다!
