# 워크플로우 B v6 - 5분 사이클 전략

## 📋 개요

v6는 사용자가 요청한 **5분 사이클 특정가 주문 전략**을 구현합니다.

### 핵심 전략

> "5분마다 주문을 특정가로 계속 넣는것이고 체결된 경우에는 더이상 주문을 넣지 않고... 체결이 되지 않으면 다시 계산된 매수가로 주문을 넣는 방식"

## 🎯 주요 특징

### 1. 체결 여부 확인 (Position Check)
- 매 사이클마다 `positions` 테이블을 조회하여 이미 보유중인 종목 확인
- 체결된 종목(포지션 존재)은 **주문 스킵**
- 미체결 종목만 다음 단계로 진행

### 2. 이전 대기 주문 취소
- 미체결 종목에 대해 `PENDING` 상태의 기존 주문 조회
- 기존 대기 주문이 있으면 **자동 취소** (`CANCELLED` 상태로 변경)
- 취소 후 새로운 가격으로 재주문

### 3. 가격 재계산 및 재주문
- 매 사이클마다 최신 현재가를 기준으로 주문 가격 재계산
- 주문 전략(offset)을 적용한 새로운 특정가로 주문
- `LIMIT` 주문으로 실행

## 🔄 워크플로우 흐름

```
1. [5분마다 실행] 트리거
   ↓
2. [환경변수 설정]
   ↓
3. [활성 전략 조회]
   ↓
4. [유니버스 종목 추출]
   ↓
5. [포지션 확인] + [현재가 조회] (병렬)
   ↓
6. [데이터 병합 및 필터링] ⭐ 이미 보유 종목 제외
   ↓
7. [매수매도 신호 생성]
   ↓
8. [기존 대기 주문 확인]
   ↓
9. [취소 데이터 준비]
   ↓
10. [이전 주문 있는지 확인] (IF 분기)
    ├─ YES → [취소할 주문 분리] → [주문 취소] ⭐
    └─ NO  → (스킵)
   ↓
11. [주문 가격 계산] ⭐ 최신 가격으로 재계산
   ↓
12. [신호 저장]
   ↓
13. [키움 토큰 발급]
   ↓
14. [데이터 병합 (주문용)]
   ↓
15. [주문 실행] ⭐ 새 특정가 주문
   ↓
16. [주문 데이터 준비]
   ↓
17. [주문 결과 저장]
```

## 🆕 추가된 노드들

### 1. 포지션 확인 (Check Positions)

**목적**: 이미 체결된 종목 필터링

```http
GET /positions?stock_code=in.(005930,000660,...)
```

**응답 예시**:
```json
[
  {
    "stock_code": "005930",
    "quantity": 10,
    "avg_price": 71200
  }
]
```

### 2. 데이터 병합 및 필터링

**핵심 로직**:
```javascript
// 포지션 맵 생성
const positionMap = {};
for (const item of positionData) {
  // ... 포지션 데이터를 맵으로 변환
}

for (const strategy of strategyData) {
  const existingPosition = positionMap[strategy.stock_code];

  // ✅ 이미 보유중이면 스킵
  if (existingPosition && existingPosition.quantity > 0) {
    console.log(`⏭️ ${strategy.stock_code}: 이미 보유중 - 주문 스킵`);
    continue;
  }

  // 포지션 없으면 주문 진행
  results.push({ json: { ...strategy, ... } });
}
```

### 3. 기존 대기 주문 확인

**목적**: 이전 사이클에서 넣은 미체결 주문 찾기

```http
GET /orders?stock_code=eq.005930&order_status=eq.PENDING
```

**응답 예시**:
```json
[
  {
    "id": 123,
    "stock_code": "005930",
    "order_status": "PENDING",
    "order_price": 71210
  }
]
```

### 4. 취소 데이터 준비

**로직**:
```javascript
const pendingOrders = Array.isArray(pendingOrdersResponse)
  ? pendingOrdersResponse
  : [];

console.log(`📋 ${signalData.stock_code}: 대기중인 주문 ${pendingOrders.length}개 발견`);

return [{
  json: {
    ...signalData,
    pending_orders: pendingOrders,
    has_pending_orders: pendingOrders.length > 0
  }
}];
```

### 5. 이전 주문 있는지 확인 (IF)

**조건**:
```javascript
$json.has_pending_orders === true
```

- **TRUE**: "취소할 주문 분리" 노드로 진행
- **FALSE**: 바로 "주문 가격 계산" 노드로 진행

### 6. 취소할 주문 분리

**목적**: 여러 개의 대기 주문을 개별적으로 취소하기 위해 분리

```javascript
const pendingOrders = data.pending_orders || [];
const results = [];

for (const order of pendingOrders) {
  results.push({
    json: {
      ...data,
      cancel_order_id: order.id
    }
  });
}
```

### 7. 주문 취소

**API 호출**:
```http
PATCH /orders?id=eq.123
Content-Type: application/json

{
  "order_status": "CANCELLED",
  "cancelled_at": "2025-01-13T10:30:00.000Z"
}
```

**Batching**: 1개씩, 1초 간격 (초당 1건 취소)

## 📊 사이클별 시나리오

### 시나리오 1: 첫 주문 (포지션 없음, 대기 주문 없음)

```
10:00 사이클 1
├─ 포지션 확인: 없음
├─ 대기 주문 확인: 없음
├─ 현재가 조회: 71,150원
├─ 주문 가격 계산: 71,150 + 10 = 71,160원
└─ 주문 실행: 71,160원에 10주 매수 주문 → orders 테이블에 PENDING 저장
```

### 시나리오 2: 미체결 재주문 (포지션 없음, 대기 주문 있음)

```
10:05 사이클 2
├─ 포지션 확인: 없음 (아직 미체결)
├─ 대기 주문 확인: 1건 발견 (71,160원)
├─ 이전 주문 취소: order_id=123을 CANCELLED로 변경
├─ 현재가 조회: 71,100원 (가격 하락)
├─ 주문 가격 계산: 71,100 + 10 = 71,110원 (가격 조정)
└─ 주문 실행: 71,110원에 10주 매수 주문 → 새 PENDING 주문 생성
```

### 시나리오 3: 체결 완료 (포지션 있음)

```
10:10 사이클 3
├─ 포지션 확인: 발견 (10주 보유)
└─ 주문 스킵 ⏭️ (이미 체결됨, 더 이상 주문하지 않음)
```

### 시나리오 4: 일부 체결 후 재주문

```
10:15 사이클 4
├─ 포지션 확인: 없음 (5주만 체결, 포지션은 생성되지 않음)
├─ 대기 주문 확인: 1건 발견 (PARTIAL 상태)
├─ 이전 주문 취소: PARTIAL 주문을 CANCELLED로 변경
├─ 현재가 조회: 71,200원
├─ 주문 가격 계산: 71,200 + 10 = 71,210원
└─ 주문 실행: 71,210원에 5주 매수 주문 (잔여 수량)
```

## 🔧 주요 개선 사항

### v5 대비 v6의 변화

| 항목 | v5 | v6 |
|------|----|----|
| 포지션 확인 | ❌ 없음 | ✅ 매 사이클마다 확인 |
| 중복 주문 방지 | ❌ 없음 | ✅ 포지션 있으면 스킵 |
| 기존 주문 취소 | ❌ 없음 | ✅ 자동 취소 후 재주문 |
| 가격 업데이트 | ⚠️ 한 번만 | ✅ 매 사이클마다 재계산 |
| 전략 | 한 번 주문 후 종료 | 5분마다 반복, 체결까지 |

## 💡 동작 원리

### 1. 체결 감지 메커니즘

**positions 테이블 사용**:
- 키움 API에서 주문 체결 시 → `positions` 테이블에 포지션 생성
- 워크플로우는 `positions.quantity > 0` 확인
- 포지션 있으면 = 체결됨 = 주문 스킵

### 2. 주문 갱신 메커니즘

**orders 테이블 사용**:
- 각 사이클마다 `orders` 테이블에서 `PENDING` 주문 조회
- 기존 주문을 `CANCELLED`로 변경
- 최신 가격으로 새 `PENDING` 주문 생성

### 3. 가격 재계산

**매 사이클마다**:
```javascript
현재가 조회 → 최신 가격 획득
  ↓
주문 가격 계산 → offset 적용
  ↓
새 주문 실행 → 갱신된 가격으로 주문
```

## 🎯 사용 예시

### 종목: 005930 (삼성전자)

```
10:00 - 현재가 71,150 → 주문 71,160 (PENDING)
10:05 - 현재가 71,100 → 이전 주문 취소 → 새 주문 71,110 (PENDING)
10:10 - 현재가 71,050 → 이전 주문 취소 → 새 주문 71,060 (PENDING)
10:15 - 현재가 71,080 → 71,060 주문 체결! → 포지션 생성
10:20 - 포지션 확인 → 10주 보유 → 주문 스킵 ✅
10:25 - 포지션 확인 → 10주 보유 → 주문 스킵 ✅
...
```

## ⚙️ 설정 가능한 파라미터

### 1. 사이클 간격

**Schedule Trigger**:
```json
{
  "interval": [
    {
      "field": "minutes",
      "minutesInterval": 5  // ← 변경 가능 (예: 1분, 3분, 10분)
    }
  ]
}
```

### 2. 주문 가격 오프셋

**전략 설정**:
```json
{
  "order_price_strategy": {
    "buy": {
      "type": "best_ask",
      "offset": 10  // ← +10원 (현재가보다 높게)
    },
    "sell": {
      "type": "best_bid",
      "offset": -10  // ← -10원 (현재가보다 낮게)
    }
  }
}
```

### 3. 주문 수량

**주문 실행 노드**:
```json
{
  "ord_qty": "10"  // ← 변경 가능 (1주, 5주, 100주 등)
}
```

### 4. Batching 간격

**주문 취소 노드**:
```json
{
  "batching": {
    "batchSize": 1,
    "batchInterval": 1000  // ← 1초 (변경 가능)
  }
}
```

**주문 실행 노드**:
```json
{
  "batching": {
    "batchSize": 1,
    "batchInterval": 2000  // ← 2초 (변경 가능)
  }
}
```

## 🐛 디버깅 로그

### 포지션 필터링 로그

```javascript
⏭️ 005930: 이미 보유중 (수량: 10) - 주문 스킵
✅ 000660: 포지션 없음 - 주문 진행
```

### 주문 취소 로그

```javascript
📋 005930: 대기중인 주문 1개 발견
🗑️ 이전 주문 취소 필요: 123
```

### 가격 계산 로그

```javascript
[buy] 005930: 기준=71100, offset=10, 주문가=71110
```

## 📈 예상 효과

### 장점

1. **체결 확률 증가**
   - 매 사이클마다 가격 조정으로 시장가에 근접
   - 5분마다 새로운 기회 포착

2. **중복 주문 방지**
   - 포지션 확인으로 이미 체결된 종목 제외
   - 불필요한 추가 매수 방지

3. **유연한 가격 대응**
   - 시장 가격 변동에 실시간 대응
   - 하락 시 낮은 가격으로 재주문
   - 상승 시 높은 가격으로 재주문

4. **깔끔한 주문 관리**
   - 이전 미체결 주문 자동 취소
   - `PENDING` 주문이 쌓이지 않음

### 단점 및 리스크

1. **API 호출량 증가**
   - 5분마다 포지션 조회, 주문 조회, 주문 취소, 주문 생성
   - 키움 API Rate Limit 주의 필요

2. **Slippage 가능성**
   - 주문 취소 후 재주문 사이에 가격 변동 가능
   - 체결 기회를 놓칠 수 있음

3. **거래 수수료**
   - 매번 새 주문 생성 (취소는 무료, 체결 시 수수료)

## 🔮 향후 개선 방안

### 1. 포지션 목표 수량 설정

현재는 1주라도 보유하면 스킵하지만, 목표 수량까지 분할 매수 가능:

```javascript
const targetQuantity = 50;  // 목표: 50주
const currentQuantity = existingPosition?.quantity || 0;

if (currentQuantity >= targetQuantity) {
  console.log(`목표 달성: ${currentQuantity}/${targetQuantity}`);
  continue;  // 스킵
}

// 잔여 수량 계산
const remainingQuantity = targetQuantity - currentQuantity;
```

### 2. 주문 가격 범위 제한

너무 높거나 낮은 가격으로 주문되지 않도록 제한:

```javascript
const maxPrice = currentPrice * 1.03;  // 현재가 +3%까지만
const minPrice = currentPrice * 0.97;  // 현재가 -3%까지만

const orderPrice = Math.min(Math.max(calculatedPrice, minPrice), maxPrice);
```

### 3. 체결률 기반 전략 조정

체결이 계속 안 되면 offset을 늘려서 체결 확률 증가:

```javascript
const failedAttempts = countFailedAttempts(stockCode);

if (failedAttempts > 3) {
  offset += 20;  // 3번 실패하면 offset을 20원으로 증가
  console.log(`⚠️ 체결 실패 ${failedAttempts}회 - offset 증가: ${offset}`);
}
```

### 4. 시장 시간 확인

장 마감 시간에는 주문 중단:

```javascript
const now = new Date();
const hour = now.getHours();
const minute = now.getMinutes();

// 장 운영시간: 09:00 ~ 15:30
if (hour < 9 || hour >= 15 && minute >= 30) {
  console.log('⏸️ 장 마감 - 주문 중단');
  return [];
}
```

## 📝 체크리스트

사용 전 확인 사항:

- [ ] `positions` 테이블이 존재하고 키움 API 체결 시 자동 업데이트되는지 확인
- [ ] `orders` 테이블에 `order_status`, `cancelled_at` 필드가 있는지 확인
- [ ] 키움 API Rate Limit 확인 (5분마다 여러 API 호출)
- [ ] 주문 수량 및 가격 오프셋이 전략에 맞게 설정되었는지 확인
- [ ] 환경변수 (KIWOOM_APP_KEY, KIWOOM_APP_SECRET) 설정 확인
- [ ] 테스트 환경에서 먼저 실행하여 동작 확인

## 🚀 배포 방법

1. **n8n UI에서 워크플로우 Import**
   - Workflows → Import from File
   - `auto-trading-workflow-b-v6.json` 선택

2. **활성화**
   - 워크플로우 상세 화면 → Active 토글 ON

3. **테스트 실행**
   - "Execute Workflow" 버튼 클릭
   - 각 노드의 출력 확인
   - 콘솔 로그 확인

4. **모니터링**
   - `PendingOrdersPanel` UI에서 대기 주문 확인
   - `orders` 테이블에서 취소/생성 내역 확인
   - `positions` 테이블에서 체결 여부 확인

---

## 🎉 결론

v6는 사용자가 요청한 **"5분마다 특정가로 주문을 넣고, 체결되면 중단, 미체결되면 가격 재계산 후 재주문"** 전략을 완벽하게 구현합니다.

핵심은:
1. **포지션 확인**: 체결되면 더 이상 주문 안 함
2. **주문 취소**: 이전 미체결 주문을 자동 취소
3. **가격 갱신**: 매 사이클마다 최신 가격으로 재계산
4. **반복 실행**: 5분마다 자동 실행

이를 통해 **시장 변동에 유연하게 대응하면서도 중복 주문 없이 깔끔하게 자동매매를 수행**할 수 있습니다! 🚀
