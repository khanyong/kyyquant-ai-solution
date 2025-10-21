# 전략별 자금 관리 시스템 설계

## 🎯 현재 상황 분석

### ✅ 이미 구현된 것
1. **할당 자금 설정** - `strategies` 테이블에 `allocated_capital`, `allocated_percent` 저장
2. **포지션 추적** - `positions` 테이블에 `strategy_id` 연결

### ❌ 아직 구현되지 않은 것
1. **전략별 사용 중인 자금 실시간 추적**
2. **전략별 가용 자금 계산**
3. **매수 시 할당 자금 초과 방지**
4. **전략별 잔고 독립 관리**

---

## 📊 문제 시나리오

### 시나리오: 10,000,000원 계좌

**초기 할당:**
```
전략 A (RSI):    3,000,000원 (30%)
전략 B (골든크로스): 5,000,000원 (50%)
전략 C (볼린저):  2,000,000원 (20%)
합계:            10,000,000원 (100%)
```

**매수/매도 후:**
```
전략 A:
  - 삼성전자 매수: 1,000,000원 사용
  - SK하이닉스 매수: 800,000원 사용
  → 사용 중: 1,800,000원
  → 가용 자금: 1,200,000원

전략 B:
  - NAVER 매수: 2,000,000원 사용
  → 사용 중: 2,000,000원
  → 가용 자금: 3,000,000원

전략 C:
  - 카카오 매수: 1,500,000원 사용
  → 사용 중: 1,500,000원
  → 가용 자금: 500,000원
```

**문제점:**
1. 전략 A가 1,500,000원짜리 종목 매수 시도 → 가용 자금(1,200,000원) 부족 → 실패해야 함
2. 전략 간 자금 격리가 안 되면 전략 A가 전략 B의 자금 사용 가능 → ❌ 잘못됨

---

## 🏗️ 필요한 구현

### 1. 전략별 자금 현황 뷰 생성

```sql
-- 전략별 실시간 자금 현황
CREATE OR REPLACE VIEW strategy_capital_status AS
SELECT
  s.id as strategy_id,
  s.name as strategy_name,
  s.allocated_capital,
  s.allocated_percent,
  s.user_id,

  -- 활성 포지션에 사용 중인 자금
  COALESCE(SUM(p.quantity * p.avg_price), 0) as capital_in_use,

  -- 할당 자금 (고정 금액 우선, 없으면 비율로 계산)
  CASE
    WHEN s.allocated_capital > 0 THEN s.allocated_capital
    WHEN s.allocated_percent > 0 THEN
      -- 계좌 잔고는 별도로 조회 필요 (여기서는 0으로 처리)
      s.allocated_percent * 0 / 100
    ELSE 0
  END as total_allocated,

  -- 가용 자금
  CASE
    WHEN s.allocated_capital > 0 THEN
      s.allocated_capital - COALESCE(SUM(p.quantity * p.avg_price), 0)
    WHEN s.allocated_percent > 0 THEN
      (s.allocated_percent * 0 / 100) - COALESCE(SUM(p.quantity * p.avg_price), 0)
    ELSE 0
  END as available_capital,

  -- 포지션 개수
  COUNT(p.id) FILTER (WHERE p.is_active = true) as active_positions,

  -- 총 평가 손익
  COALESCE(SUM(p.unrealized_pnl), 0) as total_pnl

FROM strategies s
LEFT JOIN positions p ON s.id = p.strategy_id AND p.is_active = true
WHERE s.is_active = true
GROUP BY s.id, s.name, s.allocated_capital, s.allocated_percent, s.user_id;
```

### 2. 매수 전 자금 검증 함수

```sql
-- 전략별 매수 가능 여부 체크
CREATE OR REPLACE FUNCTION check_strategy_capital(
  p_strategy_id UUID,
  p_order_amount DECIMAL,
  p_account_balance DECIMAL DEFAULT 0
) RETURNS JSONB AS $$
DECLARE
  v_allocated_capital DECIMAL;
  v_allocated_percent DECIMAL;
  v_capital_in_use DECIMAL;
  v_available_capital DECIMAL;
  v_result JSONB;
BEGIN
  -- 전략 정보 조회
  SELECT
    allocated_capital,
    allocated_percent
  INTO v_allocated_capital, v_allocated_percent
  FROM strategies
  WHERE id = p_strategy_id AND is_active = true;

  -- 전략이 없거나 비활성
  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'allowed', false,
      'reason', '전략이 존재하지 않거나 비활성 상태입니다',
      'available_capital', 0
    );
  END IF;

  -- 사용 중인 자금 계산
  SELECT COALESCE(SUM(quantity * avg_price), 0)
  INTO v_capital_in_use
  FROM positions
  WHERE strategy_id = p_strategy_id AND is_active = true;

  -- 할당된 총 자금 계산
  IF v_allocated_capital > 0 THEN
    -- 고정 금액 모드
    v_available_capital := v_allocated_capital - v_capital_in_use;
  ELSIF v_allocated_percent > 0 THEN
    -- 비율 모드
    v_available_capital := (p_account_balance * v_allocated_percent / 100) - v_capital_in_use;
  ELSE
    -- 할당 없음 - 무제한
    v_available_capital := p_account_balance;
  END IF;

  -- 결과 반환
  IF p_order_amount <= v_available_capital THEN
    RETURN jsonb_build_object(
      'allowed', true,
      'available_capital', v_available_capital,
      'order_amount', p_order_amount,
      'remaining', v_available_capital - p_order_amount
    );
  ELSE
    RETURN jsonb_build_object(
      'allowed', false,
      'reason', '할당 자금 부족',
      'available_capital', v_available_capital,
      'order_amount', p_order_amount,
      'shortfall', p_order_amount - v_available_capital
    );
  END IF;
END;
$$ LANGUAGE plpgsql;
```

### 3. n8n 워크플로우에서 자금 검증

```javascript
// n8n Function 노드: 매수 전 자금 체크
const strategyId = $input.item.json.strategy_id
const stockPrice = $input.item.json.current_price
const quantity = 10  // 매수할 수량
const orderAmount = stockPrice * quantity

// Supabase에서 자금 검증
const { data: checkResult } = await $supabase
  .rpc('check_strategy_capital', {
    p_strategy_id: strategyId,
    p_order_amount: orderAmount,
    p_account_balance: 10000000  // 실제 계좌 잔고
  })

if (!checkResult.allowed) {
  console.log('❌ 매수 불가:', checkResult.reason)
  console.log('가용 자금:', checkResult.available_capital)
  console.log('필요 자금:', checkResult.order_amount)
  console.log('부족 금액:', checkResult.shortfall)

  return {
    json: {
      error: checkResult.reason,
      skipped: true
    }
  }
}

console.log('✅ 매수 가능')
console.log('가용 자금:', checkResult.available_capital)
console.log('주문 금액:', checkResult.order_amount)
console.log('주문 후 잔액:', checkResult.remaining)

// 매수 진행
return {
  json: {
    ...checkResult,
    proceed: true
  }
}
```

### 4. UI에서 실시간 자금 현황 표시

```typescript
// React Component
const StrategyCapitalStatus: React.FC = () => {
  const [capitalStatus, setCapitalStatus] = useState<any[]>([])

  useEffect(() => {
    const fetchCapitalStatus = async () => {
      const { data } = await supabase
        .from('strategy_capital_status')
        .select('*')

      setCapitalStatus(data || [])
    }

    fetchCapitalStatus()
    const interval = setInterval(fetchCapitalStatus, 5000) // 5초마다

    return () => clearInterval(interval)
  }, [])

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>전략</TableCell>
          <TableCell>할당 자금</TableCell>
          <TableCell>사용 중</TableCell>
          <TableCell>가용 자금</TableCell>
          <TableCell>활성 포지션</TableCell>
          <TableCell>평가 손익</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {capitalStatus.map(item => (
          <TableRow key={item.strategy_id}>
            <TableCell>{item.strategy_name}</TableCell>
            <TableCell>
              {item.total_allocated.toLocaleString()}원
            </TableCell>
            <TableCell>
              <Chip
                label={`${item.capital_in_use.toLocaleString()}원`}
                color="warning"
              />
            </TableCell>
            <TableCell>
              <Chip
                label={`${item.available_capital.toLocaleString()}원`}
                color={item.available_capital > 0 ? 'success' : 'error'}
              />
            </TableCell>
            <TableCell>{item.active_positions}개</TableCell>
            <TableCell>
              <Typography color={item.total_pnl >= 0 ? 'success.main' : 'error.main'}>
                {item.total_pnl >= 0 ? '+' : ''}
                {item.total_pnl.toLocaleString()}원
              </Typography>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

---

## 🎬 동작 흐름

### 매수 프로세스

```
1. n8n 워크플로우에서 매수 신호 발생
   ↓
2. 전략 ID와 주문 금액 확인
   ↓
3. check_strategy_capital() 함수 호출
   ↓
4. 가용 자금 체크
   ├─ ✅ 충분 → 매수 진행
   └─ ❌ 부족 → 주문 스킵 (로그 기록)
   ↓
5. 매수 체결 시 positions 테이블에 기록
   ↓
6. 전략별 사용 중 자금 자동 증가
```

### 매도 프로세스

```
1. 매도 신호 발생 또는 조건 만족
   ↓
2. positions 테이블에서 해당 포지션 조회
   ↓
3. 매도 체결
   ↓
4. positions.is_active = false 업데이트
   ↓
5. 전략별 사용 중 자금 자동 감소
   ↓
6. 가용 자금 자동 증가
```

---

## 📈 예시 시나리오

### 초기 상태
```
전략 A: 할당 3,000,000원
  - 사용 중: 0원
  - 가용: 3,000,000원
  - 포지션: 0개
```

### 삼성전자 매수 (1,000,000원)
```
✅ 체크: 1,000,000 <= 3,000,000 (OK)
→ 매수 진행

전략 A: 할당 3,000,000원
  - 사용 중: 1,000,000원
  - 가용: 2,000,000원
  - 포지션: 1개 (삼성전자)
```

### SK하이닉스 매수 시도 (2,500,000원)
```
❌ 체크: 2,500,000 > 2,000,000 (부족)
→ 매수 스킵

로그: "전략 A - SK하이닉스 매수 불가: 가용 자금 2,000,000원 < 필요 자금 2,500,000원"

전략 A: 할당 3,000,000원
  - 사용 중: 1,000,000원 (변화 없음)
  - 가용: 2,000,000원
  - 포지션: 1개
```

### 삼성전자 매도 (1,200,000원에 체결)
```
매도 완료

전략 A: 할당 3,000,000원
  - 사용 중: 0원
  - 가용: 3,000,000원
  - 포지션: 0개
  - 실현 수익: +200,000원
```

---

## ⚠️ 주의사항

### 1. 계좌 잔고 vs 전략 할당
- **계좌 잔고**: 키움증권 예수금 (실제 현금)
- **전략 할당**: 논리적 배분 (가상 분할)

**중요:** 모든 전략의 할당 합계가 계좌 잔고를 초과하면 안 됨!

### 2. 비율 모드에서 계좌 잔고 변동
```
초기: 계좌 잔고 10,000,000원, 전략 A 30% → 3,000,000원

매도로 잔고 증가: 12,000,000원
→ 전략 A 할당: 12,000,000 × 30% = 3,600,000원 (자동 증가)

손실로 잔고 감소: 8,000,000원
→ 전략 A 할당: 8,000,000 × 30% = 2,400,000원 (자동 감소)
```

### 3. 고정 금액 모드
```
계좌 잔고 변동 무관
전략 A: 항상 3,000,000원 고정
```

---

## 🚀 구현 우선순위

### Phase 1 (필수)
1. ✅ `strategy_capital_status` 뷰 생성
2. ✅ `check_strategy_capital()` 함수 생성
3. ✅ n8n 워크플로우에 자금 검증 추가

### Phase 2 (권장)
4. ⬜ UI에 전략별 자금 현황 표시
5. ⬜ 매수 실패 로그 수집 및 알림
6. ⬜ 전략별 자금 이력 추적 테이블

### Phase 3 (선택)
7. ⬜ 자동 리밸런싱 (비율 유지)
8. ⬜ 전략 간 자금 재배분 기능
9. ⬜ 전략별 수익률 대시보드

---

지금 바로 구현하시겠습니까?
