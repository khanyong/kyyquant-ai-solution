# n8n 워크플로우 자금 검증 통합 가이드

## 🎯 목적

전략별로 할당된 자금을 초과하지 않도록 매수 전 자동 검증하는 시스템 구축

---

## 📋 전체 워크플로우 구조

```
1. 매수 신호 발생 (기존)
   ↓
2. 🆕 전략 자금 검증 (새로 추가)
   ↓
3-A. ✅ 자금 충분 → 매수 진행
   ↓
3-B. ❌ 자금 부족 → 주문 스킵 (로그 기록)
```

---

## 🛠️ 구현 단계

### Step 1: Supabase Function 노드 추가

워크플로우에서 매수 신호 다음에 **Supabase** 노드 추가:

**노드 이름:** `자금 검증`

**설정:**
- **Operation:** `Invoke a Postgres function (rpc)`
- **Function:** `check_strategy_capital`
- **Parameters:**

```json
{
  "p_strategy_id": "{{ $json.strategy_id }}",
  "p_order_amount": "{{ $json.order_amount }}",
  "p_account_balance": "{{ $json.account_balance }}"
}
```

**Parameters 설명:**
- `p_strategy_id`: 현재 실행 중인 전략 ID
- `p_order_amount`: 매수하려는 금액 (종목가격 × 수량)
- `p_account_balance`: 현재 계좌 잔고 (키움증권 예수금)

---

### Step 2: Function 노드로 검증 결과 처리

**노드 이름:** `검증 결과 확인`

**Code:**

```javascript
// 이전 노드에서 전달받은 검증 결과
const checkResult = $input.item.json

// 매수 가능 여부 확인
if (!checkResult.allowed) {
  // ❌ 자금 부족 - 주문 스킵
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('❌ 매수 불가 - 자금 부족')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('전략:', checkResult.strategy_name)
  console.log('사유:', checkResult.reason)
  console.log('총 할당:', checkResult.total_allocated?.toLocaleString(), '원')
  console.log('사용 중:', checkResult.capital_in_use?.toLocaleString(), '원')
  console.log('가용 자금:', checkResult.available_capital?.toLocaleString(), '원')
  console.log('주문 금액:', checkResult.order_amount?.toLocaleString(), '원')
  console.log('부족 금액:', checkResult.shortfall?.toLocaleString(), '원')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  // 스킵 처리 (다음 노드로 전달하지 않음)
  return {
    json: {
      skipped: true,
      reason: checkResult.reason,
      strategy_name: checkResult.strategy_name,
      shortfall: checkResult.shortfall
    }
  }
}

// ✅ 자금 충분 - 매수 진행
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('✅ 매수 가능')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('전략:', checkResult.strategy_name)
console.log('총 할당:', checkResult.total_allocated?.toLocaleString(), '원')
console.log('사용 중:', checkResult.capital_in_use?.toLocaleString(), '원')
console.log('가용 자금:', checkResult.available_capital?.toLocaleString(), '원')
console.log('주문 금액:', checkResult.order_amount?.toLocaleString(), '원')
console.log('주문 후 잔액:', checkResult.remaining_after_order?.toLocaleString(), '원')
console.log('활성 포지션:', checkResult.active_positions, '개')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

// 매수 진행 (원래 데이터에 검증 정보 추가)
return {
  json: {
    ...checkResult,
    proceed_to_buy: true,
    original_data: $input.item.json
  }
}
```

---

### Step 3: IF 노드로 분기 처리

**노드 이름:** `매수 진행 여부`

**설정:**
- **Conditions:**
  - `{{ $json.proceed_to_buy }}` **equals** `true`

**연결:**
- **True → 키움 매수 API 노드**
- **False → 스킵 로그 기록 노드**

---

### Step 4: 스킵 로그 기록 (선택)

자금 부족으로 스킵된 경우 로그 저장:

**노드 이름:** `스킵 로그 저장`

**Supabase Insert:**

```json
{
  "table": "trading_logs",
  "records": {
    "strategy_id": "{{ $json.strategy_id }}",
    "event_type": "order_skipped",
    "reason": "insufficient_capital",
    "details": {
      "strategy_name": "{{ $json.strategy_name }}",
      "shortfall": "{{ $json.shortfall }}",
      "available_capital": "{{ $json.available_capital }}",
      "order_amount": "{{ $json.order_amount }}"
    },
    "created_at": "{{ $now }}"
  }
}
```

---

## 🔍 전체 노드 구성 예시

```
┌─────────────────────────────────────────────────────┐
│ 1. 매수 신호 발생                                    │
│    (기존 신호 생성 로직)                              │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ 2. 주문 금액 계산                                    │
│    Function 노드                                     │
│    ─────────────────────────────────────────       │
│    const price = $json.current_price                │
│    const quantity = 10                              │
│    const orderAmount = price * quantity             │
│    return { ...data, order_amount: orderAmount }    │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ 3. 🆕 자금 검증                                      │
│    Supabase RPC 노드                                 │
│    ─────────────────────────────────────────       │
│    Function: check_strategy_capital                 │
│    Params: {                                        │
│      p_strategy_id,                                 │
│      p_order_amount,                                │
│      p_account_balance                              │
│    }                                                │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ 4. 검증 결과 확인                                    │
│    Function 노드                                     │
│    ─────────────────────────────────────────       │
│    if (!checkResult.allowed) {                      │
│      return { skipped: true, ... }                  │
│    }                                                │
│    return { proceed_to_buy: true, ... }             │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ 5. 매수 진행 여부                                    │
│    IF 노드                                           │
│    ─────────────────────────────────────────       │
│    Condition: proceed_to_buy == true                │
└──────┬────────────────────────┬─────────────────────┘
       ↓ True                   ↓ False
┌──────────────────┐   ┌────────────────────────────┐
│ 6-A. 키움 매수    │   │ 6-B. 스킵 로그 저장        │
│      API 호출     │   │      (Supabase Insert)     │
└──────────────────┘   └────────────────────────────┘
```

---

## 💡 실제 사용 예시

### 예시 1: 자금 충분 - 매수 진행

**입력 데이터:**
```json
{
  "strategy_id": "abc-123",
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "current_price": 75000,
  "quantity": 10,
  "order_amount": 750000,
  "account_balance": 10000000
}
```

**검증 결과:**
```json
{
  "allowed": true,
  "strategy_name": "골든크로스",
  "total_allocated": 3000000,
  "capital_in_use": 1500000,
  "available_capital": 1500000,
  "order_amount": 750000,
  "remaining_after_order": 750000,
  "active_positions": 2
}
```

**로그 출력:**
```
✅ 매수 가능
전략: 골든크로스
총 할당: 3,000,000 원
사용 중: 1,500,000 원
가용 자금: 1,500,000 원
주문 금액: 750,000 원
주문 후 잔액: 750,000 원
활성 포지션: 2 개
```

**결과:** 키움 매수 API 호출 → 매수 체결

---

### 예시 2: 자금 부족 - 주문 스킵

**입력 데이터:**
```json
{
  "strategy_id": "abc-123",
  "stock_code": "000660",
  "stock_name": "SK하이닉스",
  "current_price": 150000,
  "quantity": 20,
  "order_amount": 3000000,
  "account_balance": 10000000
}
```

**검증 결과:**
```json
{
  "allowed": false,
  "reason": "할당 자금 부족",
  "strategy_name": "골든크로스",
  "total_allocated": 3000000,
  "capital_in_use": 2500000,
  "available_capital": 500000,
  "order_amount": 3000000,
  "shortfall": 2500000
}
```

**로그 출력:**
```
❌ 매수 불가 - 자금 부족
전략: 골든크로스
사유: 할당 자금 부족
총 할당: 3,000,000 원
사용 중: 2,500,000 원
가용 자금: 500,000 원
주문 금액: 3,000,000 원
부족 금액: 2,500,000 원
```

**결과:** 주문 스킵 → 로그만 기록

---

## 🔧 계좌 잔고 가져오기

n8n에서 키움증권 계좌 잔고를 가져오는 방법:

### 방법 1: Supabase에서 조회

```javascript
// kw_account_balance 테이블에서 최신 잔고 조회
const { data } = await $supabase
  .from('kw_account_balance')
  .select('deposited_amount')
  .order('updated_at', { ascending: false })
  .limit(1)
  .single()

const accountBalance = data?.deposited_amount || 0

return {
  json: {
    ...originalData,
    account_balance: accountBalance
  }
}
```

### 방법 2: 키움 API 직접 호출

```javascript
// 키움 Open API 서버에 HTTP 요청
const response = await fetch('http://localhost:8001/api/kiwoom/balance')
const data = await response.json()

const accountBalance = data.deposited_amount || 0

return {
  json: {
    ...originalData,
    account_balance: accountBalance
  }
}
```

---

## ⚙️ 설정 팁

### 1. 비율 모드 vs 고정 금액 모드

**비율 모드 (권장):**
```javascript
// 계좌 잔고의 30%를 이 전략에 할당
{
  allocated_percent: 30,
  allocated_capital: 0
}
```
→ 계좌 잔고가 변해도 자동으로 비율 유지

**고정 금액 모드:**
```javascript
// 정확히 3,000,000원만 사용
{
  allocated_capital: 3000000,
  allocated_percent: 0
}
```
→ 계좌 잔고 변동 무관, 고정 금액 사용

### 2. 할당 없음 (무제한)

```javascript
{
  allocated_capital: 0,
  allocated_percent: 0
}
```
→ 자금 검증 통과, 계좌 잔고 전체 사용 가능

---

## 📊 모니터링

### UI에서 실시간 확인

앱의 **모니터링** 탭 또는 **자동매매** 탭에 `StrategyCapitalStatus` 컴포넌트 추가:

```tsx
import StrategyCapitalStatus from '@/components/StrategyCapitalStatus'

// 모니터링 페이지에 추가
<StrategyCapitalStatus />
```

**표시 내용:**
- 전략별 총 할당 자금
- 현재 사용 중인 자금
- 가용 자금
- 사용률 (%)
- 활성 포지션 개수
- 총 손익

---

## ⚠️ 주의사항

### 1. 동시 매수 처리

여러 신호가 동시에 발생하면 경쟁 조건(race condition) 발생 가능:

```
시간 T:
  - 신호 A: 가용 자금 1,000,000원 확인 → 통과
  - 신호 B: 가용 자금 1,000,000원 확인 → 통과

시간 T+1:
  - 신호 A 매수 체결 → 가용 자금 0원
  - 신호 B 매수 체결 시도 → 실패! (자금 부족)
```

**해결책:**
- n8n 워크플로우에 **Queue 모드** 설정
- 또는 DB 레벨 락 사용 (고급)

### 2. 계좌 잔고 동기화

계좌 잔고는 최신 상태여야 정확한 검증 가능:

```javascript
// 잔고 캐시 시간 체크 (5분 이내만 사용)
const balanceAge = Date.now() - balanceUpdatedAt
if (balanceAge > 5 * 60 * 1000) {
  // 5분 초과 → 최신 잔고 다시 조회
  await refreshBalance()
}
```

### 3. 슬리피지 고려

실제 체결가는 예상가와 다를 수 있음:

```javascript
// 슬리피지 2% 여유 두기
const bufferRate = 1.02
const safeOrderAmount = orderAmount * bufferRate

const checkResult = await check_strategy_capital(
  strategyId,
  safeOrderAmount,  // 여유있게 검증
  accountBalance
)
```

---

## 🎓 테스트 시나리오

### 시나리오 1: 정상 매수

```
1. 전략 A (30% 할당, 잔고 10,000,000원 → 3,000,000원)
2. 현재 사용 중: 1,000,000원
3. 가용: 2,000,000원
4. 매수 시도: 1,500,000원
5. 결과: ✅ 통과 (1,500,000 < 2,000,000)
```

### 시나리오 2: 자금 부족

```
1. 전략 A (30% 할당 → 3,000,000원)
2. 현재 사용 중: 2,800,000원
3. 가용: 200,000원
4. 매수 시도: 1,500,000원
5. 결과: ❌ 차단 (1,500,000 > 200,000)
```

### 시나리오 3: 매도 후 자금 증가

```
1. 전략 A 가용 자금: 200,000원
2. 포지션 매도 (+1,500,000원 회수)
3. 전략 A 가용 자금: 1,700,000원
4. 새 매수 시도: 1,500,000원
5. 결과: ✅ 통과 (자동 반영됨)
```

---

## 📚 참고 자료

- [전략별 자금 관리 시스템 설계](./STRATEGY_CAPITAL_MANAGEMENT.md)
- [자금 할당 가이드](./CAPITAL_ALLOCATION_GUIDE.md)
- [Supabase RPC Functions](https://supabase.com/docs/guides/database/functions)

---

구현 후 의문사항이 있으면 언제든지 문의하세요!
