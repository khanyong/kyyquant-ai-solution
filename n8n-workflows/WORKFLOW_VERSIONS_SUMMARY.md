# 워크플로우 B 버전별 요약

## 📊 버전 비교표

| 기능 | v4 | v5 | v5-simplified | v6 (최신) |
|------|----|----|---------------|-----------|
| **호가 조회** | ❌ 잘못된 필드 사용 | ✅ orderbook 테이블 | ❌ 스킵 | ❌ 스킵 |
| **order_price** | ❌ 0으로 저장됨 | ✅ 정상 | ✅ 정상 | ✅ 정상 |
| **가격 기준** | ❌ 52주 최고/최저가 | ✅ 실제 호가 | ✅ 현재가 | ✅ 현재가 |
| **포지션 확인** | ❌ | ❌ | ❌ | ✅ |
| **중복 주문 방지** | ❌ | ❌ | ❌ | ✅ |
| **기존 주문 취소** | ❌ | ❌ | ❌ | ✅ |
| **5분 사이클** | ✅ | ✅ | ✅ | ✅ |
| **가격 재계산** | ⚠️ 한번만 | ⚠️ 한번만 | ⚠️ 한번만 | ✅ 매 사이클 |
| **실전 사용** | ❌ | ⚠️ 호가 데이터 필요 | ✅ | ✅ 권장 |

## 📁 파일 목록

### 워크플로우 JSON

1. **auto-trading-workflow-b-v4.json** (구버전)
   - 문제: order_price = 0 버그
   - 원인: high_52w/low_52w를 호가로 잘못 사용

2. **auto-trading-workflow-b-v5.json**
   - 해결: orderbook 테이블 조회 추가
   - 문제: orderbook 테이블에 데이터 없음

3. **auto-trading-workflow-b-v5-simplified.json**
   - 해결: 호가 없이 현재가만 사용
   - 장점: 안정적으로 동작
   - 단점: 포지션 확인 없음

4. **auto-trading-workflow-b-v6.json** ⭐ **권장**
   - 해결: 모든 문제 해결
   - 추가: 포지션 확인, 주문 취소, 가격 재계산
   - 전략: 5분 사이클 특정가 주문

### 문서 파일

1. **WORKFLOW_B_V3_UI_FIX.md**
   - n8n UI에서 직접 수정하는 방법
   - JSON 파싱 에러 해결

2. **WORKFLOW_B_V4_CHANGES.md**
   - v4의 변경 사항 및 문제점

3. **WORKFLOW_B_V5_ORDER_PRICE_FIX.md**
   - order_price = 0 문제 분석
   - orderbook 테이블 조회 추가 방법

4. **WORKFLOW_B_V5_SIMPLIFIED.md**
   - 호가 없이 현재가만 사용하는 간소화 방법
   - 향후 개선 방안

5. **WORKFLOW_B_V6_CYCLE_STRATEGY.md** ⭐ **필독**
   - 5분 사이클 전략 상세 설명
   - 시나리오별 동작 방식
   - 설정 가능한 파라미터

6. **WORKFLOW_VERSIONS_SUMMARY.md** (이 파일)
   - 전체 버전 요약 및 비교

## 🎯 어떤 버전을 사용해야 할까?

### ✅ v6 사용 조건 (권장)

다음 요구사항이 있다면 **v6**를 사용하세요:

- ✅ 5분마다 주문을 갱신하고 싶음
- ✅ 체결되면 더 이상 주문하지 않음
- ✅ 미체결 시 가격을 재계산하여 재주문
- ✅ 이전 대기 주문을 자동 취소

**필요한 테이블**:
- `positions` (포지션 확인용)
- `orders` (주문 관리용)
- `kw_price_current` (현재가 조회용)

### ⚠️ v5-simplified 사용 조건

다음과 같은 경우 **v5-simplified**를 사용하세요:

- ⚠️ positions 테이블이 아직 없음
- ⚠️ 한 번만 주문하고 끝내고 싶음
- ⚠️ 간단한 테스트만 하고 싶음

**장점**:
- 설정이 간단함
- 호가 데이터 불필요
- order_price는 정상 작동

**단점**:
- 중복 주문 가능
- 가격 갱신 안 됨
- 체결 여부와 관계없이 계속 주문

### ❌ v4, v5 사용 금지

- **v4**: order_price = 0 버그, 사용 금지
- **v5**: orderbook 데이터 없으면 실패, 비추천

## 🔄 v5-simplified → v6 마이그레이션

### 1. positions 테이블 준비

```sql
-- positions 테이블이 없다면 생성
CREATE TABLE IF NOT EXISTS positions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users,
  stock_code TEXT NOT NULL,
  stock_name TEXT,
  quantity INTEGER NOT NULL DEFAULT 0,
  avg_price NUMERIC(12, 2),
  current_price NUMERIC(12, 2),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. orders 테이블 확인

```sql
-- cancelled_at 컬럼 추가 (없는 경우)
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;
```

### 3. v6 워크플로우 Import

1. n8n UI → Workflows
2. Import from File
3. `auto-trading-workflow-b-v6.json` 선택
4. 기존 v5-simplified 비활성화
5. v6 활성화

### 4. 테스트

```
1. "5분마다 실행" 노드 수동 실행
2. "포지션 확인" 노드 출력 확인 → 빈 배열 []
3. "데이터 병합 및 필터링" 노드 → 모든 종목 통과
4. "기존 대기 주문 확인" 노드 → 빈 배열 []
5. "이전 주문 있는지 확인" → FALSE 경로
6. "주문 가격 계산" → 정상 가격 확인
7. 전체 워크플로우 실행 → 주문 생성 확인
```

## 🐛 문제 해결 히스토리

### 문제 1: order_price = 0

**증상**:
```sql
SELECT * FROM orders;
-- order_price가 0으로 저장됨
```

**원인** (v4):
```javascript
sell_price: priceInfo.high_52w,  // ❌ 52주 최고가
buy_price: priceInfo.low_52w,    // ❌ 52주 최저가
```

**해결** (v5, v5-simplified, v6):
```javascript
sell_price: priceInfo.current_price,  // ✅ 현재가
buy_price: priceInfo.current_price,   // ✅ 현재가
```

### 문제 2: 호가 데이터 없음

**증상**:
```
[error] Node '호가 조회' hasn't been executed
```

**원인** (v5):
- `kw_price_orderbook` 테이블에 데이터 없음
- 노드 연결 순서 오류

**해결** (v5-simplified, v6):
- 호가 조회 노드 제거
- 현재가만 사용

### 문제 3: 중복 주문

**증상**:
```
매 5분마다 계속 주문이 들어감
이미 체결된 종목도 계속 주문됨
```

**원인** (v5-simplified):
- 포지션 확인 로직 없음

**해결** (v6):
```javascript
// 포지션 확인 노드 추가
if (existingPosition && existingPosition.quantity > 0) {
  console.log(`이미 보유중 - 주문 스킵`);
  continue;
}
```

### 문제 4: 이전 주문 누적

**증상**:
```sql
SELECT * FROM orders WHERE order_status = 'PENDING';
-- 같은 종목에 PENDING 주문이 여러 개
```

**원인** (v5-simplified):
- 이전 주문 취소 로직 없음

**해결** (v6):
```javascript
// 기존 대기 주문 확인 및 취소
PATCH /orders?id=eq.123
{
  "order_status": "CANCELLED",
  "cancelled_at": "2025-01-13T10:30:00.000Z"
}
```

## 📈 성능 비교

### API 호출 횟수 (1사이클 당, 종목 10개 기준)

| 작업 | v5-simplified | v6 |
|------|---------------|-----|
| 전략 조회 | 1 | 1 |
| 현재가 조회 | 10 | 10 |
| **포지션 조회** | - | **1** |
| **대기 주문 조회** | - | **10** |
| **주문 취소** | - | **0~10** |
| 주문 생성 | 10 | 0~10 |
| **합계** | **21** | **22~42** |

**분석**:
- v6는 API 호출이 약 2배 증가
- 하지만 불필요한 중복 주문 방지로 실제 비용은 더 적을 수 있음
- Rate Limit 주의 필요

### 메모리 사용량

- v5-simplified: 낮음 (노드 13개)
- v6: 약간 높음 (노드 19개, +6개)

### 실행 시간

- v5-simplified: 약 10~15초
- v6: 약 15~25초 (포지션/주문 조회 추가)

## 🎓 학습 포인트

### 1. 데이터베이스 스키마 설계

**교훈**: 초기에 필요한 필드를 모두 설계해야 함

```sql
-- orders 테이블에 필요한 필드
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  stock_code TEXT NOT NULL,
  order_price NUMERIC(12, 2),     -- ⭐ 주문 가격
  order_status TEXT,                -- ⭐ 주문 상태
  cancelled_at TIMESTAMPTZ,        -- ⭐ 취소 시간 (v6에서 추가)
  ...
);
```

### 2. n8n 노드 연결 순서

**교훈**: 노드 연결 index가 중요함

```javascript
// 잘못된 연결 (v5 초기)
현재가 조회 → 데이터 병합 (index 0)
호가 조회   → 데이터 병합 (index 0)  // ❌ 같은 index

// 올바른 연결
현재가 조회 → 데이터 병합 (index 0)
호가 조회   → 데이터 병합 (index 1)  // ✅ 다른 index
```

### 3. Fallback 로직의 중요성

**교훈**: 외부 데이터에 의존하지 말고 fallback 제공

```javascript
// 호가가 없어도 현재가로 대체
const askPrice = orderbookInfo?.ask_price1 || priceInfo.current_price;
const bidPrice = orderbookInfo?.bid_price1 || priceInfo.current_price;
```

### 4. 비즈니스 로직 명확화

**교훈**: 사용자 요구사항을 코드로 정확히 구현

**요구사항**:
> "5분마다 주문을 넣되, 체결되면 중단, 미체결되면 재주문"

**구현**:
1. ✅ 5분 트리거
2. ✅ 포지션 확인 (체결 여부)
3. ✅ 이전 주문 취소
4. ✅ 가격 재계산
5. ✅ 새 주문 생성

## 🚀 다음 단계

### 즉시 적용 가능

1. **v6 배포**
   - Import 및 활성화
   - 모니터링 설정

2. **UI 연동**
   - PendingOrdersPanel 확인
   - 취소된 주문도 UI에 표시

3. **로그 모니터링**
   - n8n 실행 로그 확인
   - 포지션 확인 로그 확인

### 향후 개선 사항

1. **분할 매수 전략**
   - 목표 수량 설정
   - 수량 미달 시 추가 매수

2. **동적 오프셋 조정**
   - 체결률 기반 오프셋 증가/감소
   - 변동성 기반 오프셋 조정

3. **시장 시간 체크**
   - 장 운영 시간에만 주문
   - 장 마감 30분 전 주문 중단

4. **성과 분석**
   - 체결률 통계
   - 평균 체결 시간
   - 가격 슬리피지 분석

## 📚 참고 문서

1. [WORKFLOW_B_V6_CYCLE_STRATEGY.md](./WORKFLOW_B_V6_CYCLE_STRATEGY.md) - v6 상세 가이드
2. [WORKFLOW_B_V5_SIMPLIFIED.md](./WORKFLOW_B_V5_SIMPLIFIED.md) - v5-simplified 설명
3. [WORKFLOW_B_V5_ORDER_PRICE_FIX.md](./WORKFLOW_B_V5_ORDER_PRICE_FIX.md) - 문제 해결 과정

## 💬 FAQ

### Q1: v6를 사용하려면 positions 테이블이 필수인가요?

**A**: 예, 필수입니다. 포지션 확인 없이는 중복 주문을 막을 수 없습니다. 대안으로 v5-simplified를 사용하되, 수동으로 주문을 관리해야 합니다.

### Q2: 호가 데이터는 언제 사용하나요?

**A**: 현재 v6는 호가 데이터를 사용하지 않고 현재가만 사용합니다. 향후 `kw_price_orderbook` 테이블에 데이터가 쌓이면 더 정확한 가격으로 주문할 수 있습니다.

### Q3: 5분마다 실행되는데 Rate Limit은 괜찮나요?

**A**: 키움 API의 Rate Limit을 확인해야 합니다. 보통 초당 2~5회 정도 허용되므로, Batching 설정(2~3초 간격)으로 조절하면 안전합니다.

### Q4: 주문이 부분 체결되면 어떻게 되나요?

**A**: 현재 v6는 `positions.quantity > 0`만 확인하므로 부분 체결되어도 주문을 중단합니다. 목표 수량까지 매수하려면 코드 수정이 필요합니다.

### Q5: 여러 전략에서 같은 종목을 주문하면?

**A**: 각 전략별로 별도의 주문이 생성됩니다. 전략 간 충돌을 방지하려면 포지션 확인 시 전략 ID도 함께 확인해야 합니다.

---

## 🎉 결론

**권장 사항**: **v6 (auto-trading-workflow-b-v6.json)** 사용

**이유**:
1. ✅ order_price = 0 문제 해결
2. ✅ 5분 사이클 특정가 주문 전략 구현
3. ✅ 포지션 확인으로 중복 주문 방지
4. ✅ 이전 주문 자동 취소 및 가격 재계산
5. ✅ 실전 사용 가능

**다음 단계**: [WORKFLOW_B_V6_CYCLE_STRATEGY.md](./WORKFLOW_B_V6_CYCLE_STRATEGY.md)를 읽고 배포하세요! 🚀
