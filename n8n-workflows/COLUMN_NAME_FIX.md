# 컬럼명 수정 안내

## 🐛 문제

v6 워크플로우 실행 시 다음 에러 발생:

```
column orders.order_status does not exist
```

## ✅ 원인

`orders` 테이블의 실제 컬럼명과 워크플로우/UI에서 사용하는 컬럼명이 불일치했습니다.

### 실제 테이블 스키마 (supabase/add_orders_columns.sql)

```sql
-- 컬럼 이름이 변경됨:
ALTER TABLE orders RENAME COLUMN order_status TO status;
ALTER TABLE orders RENAME COLUMN order_quantity TO quantity;
```

**실제 컬럼명**:
- ✅ `status` (NOT `order_status`)
- ✅ `quantity` (NOT `order_quantity`)

## 🔧 수정된 파일

### 1. auto-trading-workflow-b-v6.json

#### 기존 대기 주문 확인 노드
```json
// ❌ 수정 전
"url": "...orders?stock_code=eq.{{...}}&order_status=eq.PENDING&select=id,stock_code,order_status"

// ✅ 수정 후
"url": "...orders?stock_code=eq.{{...}}&status=eq.PENDING&select=id,stock_code,status"
```

#### 주문 취소 노드
```json
// ❌ 수정 전
"jsonBody": "{\"order_status\": \"CANCELLED\", \"cancelled_at\": ...}"

// ✅ 수정 후
"jsonBody": "{\"status\": \"CANCELLED\", \"cancelled_at\": ...}"
```

### 2. PendingOrdersPanel.tsx

#### Interface 수정
```typescript
// ❌ 수정 전
interface Order {
  order_status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'PARTIAL'
  order_quantity: number
}

// ✅ 수정 후
interface Order {
  status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'PARTIAL'
  quantity: number
}
```

#### 데이터 조회 수정
```typescript
// ❌ 수정 전
.in('order_status', ['PENDING', 'PARTIAL'])

// ✅ 수정 후
.in('status', ['PENDING', 'PARTIAL'])
```

#### 주문 취소 수정
```typescript
// ❌ 수정 전
.update({ order_status: 'CANCELLED', ... })

// ✅ 수정 후
.update({ status: 'CANCELLED', ... })
```

#### 렌더링 수정
```tsx
// ❌ 수정 전
{order.order_quantity.toLocaleString()}주
{getStatusChip(order.order_status)}
{order.order_status === 'PENDING' && (...)}

// ✅ 수정 후
{order.quantity.toLocaleString()}주
{getStatusChip(order.status)}
{order.status === 'PENDING' && (...)}
```

## 📊 컬럼명 매핑표

| 용도 | 잘못된 이름 | 올바른 이름 |
|------|-------------|-------------|
| 주문 상태 | ❌ `order_status` | ✅ `status` |
| 주문 수량 | ❌ `order_quantity` | ✅ `quantity` |
| 주문 가격 | ✅ `order_price` | ✅ `order_price` (변경 없음) |
| 주문 타입 | ✅ `order_type` | ✅ `order_type` (변경 없음) |

## 🎯 확인 방법

### 1. Supabase에서 확인

```sql
-- 테이블 스키마 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'orders'
  AND column_name IN ('status', 'quantity', 'order_status', 'order_quantity')
ORDER BY column_name;

-- 예상 결과:
-- status   | character varying
-- quantity | integer
-- (order_status, order_quantity는 없어야 함)
```

### 2. n8n 워크플로우에서 확인

1. v6 워크플로우 Import
2. "기존 대기 주문 확인" 노드 실행
3. 에러 없이 정상 실행되는지 확인

### 3. UI에서 확인

1. 자동매매 탭 열기
2. "대기중인 주문" 패널 확인
3. 주문이 정상 표시되는지 확인

## ✅ 해결 완료

모든 파일이 올바른 컬럼명(`status`, `quantity`)을 사용하도록 수정되었습니다!

---

## 📝 참고사항

### 다른 컴포넌트도 확인 필요

만약 다른 파일에서도 `orders` 테이블을 사용한다면:

```bash
# 프로젝트 전체에서 order_status 검색
grep -r "order_status" src/

# 프로젝트 전체에서 order_quantity 검색
grep -r "order_quantity" src/
```

발견되면 모두 `status`, `quantity`로 변경해야 합니다.

### 데이터베이스 마이그레이션 이미 완료

`supabase/add_orders_columns.sql` 파일에서 이미 다음 작업이 완료되었습니다:

```sql
-- 컬럼 이름 변경 (이미 실행됨)
ALTER TABLE orders RENAME COLUMN order_status TO status;
ALTER TABLE orders RENAME COLUMN order_quantity TO quantity;
```

**재실행 불필요**: 이미 Supabase에 적용되었으므로 워크플로우와 UI 코드만 수정하면 됩니다.
