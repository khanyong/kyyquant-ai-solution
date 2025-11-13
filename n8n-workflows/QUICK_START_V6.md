# 워크플로우 B v6 빠른 시작 가이드

## 🚀 5분 안에 배포하기

### 1단계: 필수 테이블 확인 (1분)

Supabase SQL Editor에서 실행:

```sql
-- positions 테이블 확인
SELECT * FROM positions LIMIT 1;

-- orders 테이블에 cancelled_at 컬럼 확인
SELECT cancelled_at FROM orders LIMIT 1;
```

**컬럼이 없다면**:
```sql
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;
```

### 2단계: 워크플로우 Import (2분)

1. n8n UI 접속
2. **Workflows** → **Import from File**
3. `auto-trading-workflow-b-v6.json` 선택
4. Import 완료

### 3단계: 기존 워크플로우 비활성화 (30초)

1. 기존 "워크플로우 B" 찾기 (v4, v5, v5-simplified)
2. **Active** 토글 OFF
3. v6만 활성 상태로 유지

### 4단계: 테스트 실행 (1분)

1. v6 워크플로우 열기
2. **Execute Workflow** 버튼 클릭
3. 각 노드의 녹색 체크마크 확인

### 5단계: 활성화 (30초)

1. 우측 상단 **Active** 토글 ON
2. 완료! 🎉

---

## 📋 동작 확인 체크리스트

### 첫 실행 후 확인 사항

#### 1. 로그 확인
```
✅ "데이터 병합 및 필터링" 노드 출력:
   📊 포지션: 0개, 현재가: 10개
   ✅ 005930: 포지션 없음 - 주문 진행
   ✅ 3개 종목 병합 완료 (포지션 필터링 후)

✅ "기존 대기 주문 확인" 노드 출력:
   📋 005930: 대기중인 주문 0개 발견

✅ "주문 가격 계산" 노드 출력:
   [buy] 005930: 기준=71150, offset=10, 주문가=71160
```

#### 2. 데이터베이스 확인

**orders 테이블**:
```sql
SELECT
  stock_code,
  order_price,
  order_status,
  created_at
FROM orders
WHERE created_at > NOW() - INTERVAL '10 minutes'
ORDER BY created_at DESC;
```

**예상 결과**:
```
stock_code | order_price | order_status | created_at
-----------+-------------+--------------+------------------
005930     |       71160 | PENDING      | 2025-01-13 10:00
000660     |       89510 | PENDING      | 2025-01-13 10:00
```

✅ **order_price가 0이 아닌 정상 값**이어야 합니다!

#### 3. UI 확인

**자동매매 탭 → 대기중인 주문** 패널:
- ✅ 방금 생성된 주문들이 표시됨
- ✅ 주문 가격이 정상 표시됨
- ✅ 상태가 "PENDING"

---

## 🔄 5분 후 (두 번째 사이클) 확인

### 시나리오 A: 체결되지 않음

**예상 동작**:
1. 포지션 확인 → 없음 (아직 미체결)
2. 기존 대기 주문 확인 → 1건 발견
3. **주문 취소** → order_status = 'CANCELLED'
4. 가격 재계산 → 새로운 현재가 기준
5. **새 주문 생성** → 갱신된 가격으로

**확인 방법**:
```sql
-- 취소된 주문
SELECT * FROM orders
WHERE stock_code = '005930'
  AND order_status = 'CANCELLED'
ORDER BY created_at DESC
LIMIT 1;

-- 새로 생성된 주문
SELECT * FROM orders
WHERE stock_code = '005930'
  AND order_status = 'PENDING'
ORDER BY created_at DESC
LIMIT 1;
```

**예상 결과**:
```
-- 10:00 주문 (취소됨)
order_price: 71160, order_status: CANCELLED, cancelled_at: 2025-01-13 10:05

-- 10:05 주문 (새로 생성)
order_price: 71110, order_status: PENDING, created_at: 2025-01-13 10:05
```

### 시나리오 B: 체결됨

**예상 동작**:
1. 포지션 확인 → **발견 (10주 보유)**
2. **주문 스킵** → 더 이상 주문하지 않음

**확인 방법**:
```sql
-- 포지션 생성 확인
SELECT * FROM positions
WHERE stock_code = '005930';
```

**예상 결과**:
```
stock_code | quantity | avg_price
-----------+----------+-----------
005930     |       10 |     71160
```

**n8n 로그**:
```
⏭️ 005930: 이미 보유중 (수량: 10) - 주문 스킵
```

---

## ⚙️ 맞춤 설정

### 1. 사이클 간격 변경

**기본**: 5분마다

**변경 방법**:
1. "5분마다 실행" 노드 클릭
2. `minutesInterval` 값 변경
   - 1 = 1분마다
   - 3 = 3분마다
   - 10 = 10분마다

### 2. 주문 가격 오프셋 변경

**기본**: +10원

**변경 방법**:

전략 설정 테이블에서:
```sql
UPDATE strategies
SET order_price_strategy = jsonb_set(
  order_price_strategy,
  '{buy,offset}',
  '20'  -- 10원 → 20원으로 변경
)
WHERE id = 1;
```

### 3. 주문 수량 변경

**기본**: 10주

**변경 방법**:
1. "주문 실행" 노드 클릭
2. Body Parameters → `ord_qty` 값 변경
   - "10" → "5" (5주)
   - "10" → "1" (1주)

---

## 🐛 문제 해결

### 문제: order_price가 여전히 0

**원인**: v6가 아닌 이전 버전 실행중

**해결**:
```
1. 워크플로우 목록에서 v6인지 확인
2. 이름: "워크플로우 B: 자동 매매 실행 v6 (5분 사이클 전략)"
3. 다른 버전은 모두 비활성화
```

### 문제: 포지션이 있는데도 계속 주문됨

**원인**: positions 테이블에 데이터가 없음

**확인**:
```sql
SELECT * FROM positions WHERE stock_code = '005930';
-- 결과가 없으면 키움 API 체결 시 positions 테이블 업데이트가 안 되는 것
```

**해결**:
- 키움 API 체결 시 positions 테이블을 업데이트하는 로직 추가 필요
- 또는 orders 테이블의 order_status를 확인하도록 로직 변경

### 문제: 이전 주문이 취소되지 않음

**원인**: cancelled_at 컬럼 없음

**확인**:
```sql
\d orders
-- cancelled_at 컬럼이 있는지 확인
```

**해결**:
```sql
ALTER TABLE orders
ADD COLUMN cancelled_at TIMESTAMPTZ;
```

### 문제: API Rate Limit 초과

**증상**:
```
Error: Rate limit exceeded
```

**해결**:
1. Batching 간격 증가
   - "주문 실행" 노드 → Options → Batching
   - Batch Interval: 2000 → 5000 (5초)
2. 또는 사이클 간격 증가
   - 5분 → 10분

---

## 📊 모니터링 대시보드

### 실시간 확인할 내용

#### 1. 대기중인 주문 (PendingOrdersPanel)

**위치**: 자동매매 탭 → 최상단

**확인 사항**:
- ✅ 주문 개수가 적정한지 (종목 수만큼)
- ✅ order_price가 시장가와 비슷한지
- ✅ 5분마다 갱신되는지 (취소 → 재생성)

#### 2. 포지션 현황

```sql
SELECT
  stock_code,
  quantity,
  avg_price,
  current_price,
  (current_price - avg_price) * quantity as profit
FROM positions
ORDER BY created_at DESC;
```

#### 3. 주문 히스토리

```sql
SELECT
  stock_code,
  order_price,
  order_status,
  created_at,
  cancelled_at
FROM orders
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

**패턴 확인**:
```
10:00 - 005930, 71160, PENDING
10:05 - 005930, 71160, CANCELLED (이전 주문)
10:05 - 005930, 71110, PENDING   (새 주문)
10:10 - 005930, 71110, CANCELLED
10:10 - 005930, 71050, PENDING
```

→ 5분마다 취소/재생성 패턴이 보여야 정상

---

## 🎯 첫 주문 체결까지 예상 시나리오

### 예시: 삼성전자 (005930) 매수

```
10:00 (사이클 1)
├─ 현재가: 71,150원
├─ 주문가: 71,160원 (현재가 + 10원)
└─ 주문 생성: PENDING

10:05 (사이클 2)
├─ 포지션: 없음 (미체결)
├─ 이전 주문: 71,160원
├─ 현재가: 71,100원 (하락)
├─ 주문 취소: 71,160원 주문
└─ 새 주문: 71,110원 (조정된 가격)

10:10 (사이클 3)
├─ 포지션: 없음 (미체결)
├─ 이전 주문: 71,110원
├─ 현재가: 71,080원
├─ 주문 취소: 71,110원 주문
└─ 새 주문: 71,090원

10:15 (사이클 4)
├─ 포지션: **10주 보유!** ✅ (71,090원에 체결됨)
└─ 주문 스킵 (더 이상 주문하지 않음)

10:20 (사이클 5)
├─ 포지션: 10주 보유
└─ 주문 스킵

...계속 스킵...
```

**핵심**:
- ✅ 체결될 때까지 5분마다 가격 조정
- ✅ 체결되면 자동으로 주문 중단
- ✅ 시장 가격에 유연하게 대응

---

## ✅ 성공 확인

다음 모든 항목이 확인되면 성공:

- [x] v6 워크플로우가 활성화됨
- [x] 5분마다 자동 실행됨
- [x] order_price가 0이 아닌 정상 값
- [x] 대기중인 주문이 UI에 표시됨
- [x] 5분마다 주문이 취소/재생성됨
- [x] 포지션이 생기면 주문 중단됨

---

## 🎉 완료!

축하합니다! 5분 사이클 자동매매 시스템이 가동되었습니다.

**다음 단계**:
1. 실전 투자 전 **충분한 테스트** (모의투자)
2. **리스크 관리** 설정 (손절/익절 전략)
3. **모니터링** 시스템 구축

**참고 문서**:
- [WORKFLOW_B_V6_CYCLE_STRATEGY.md](./WORKFLOW_B_V6_CYCLE_STRATEGY.md) - 상세 가이드
- [WORKFLOW_VERSIONS_SUMMARY.md](./WORKFLOW_VERSIONS_SUMMARY.md) - 버전 비교

**문제 발생 시**:
- n8n 실행 로그 확인
- Supabase 데이터베이스 확인
- [문제 해결](#-문제-해결) 섹션 참고

Happy Trading! 🚀📈
