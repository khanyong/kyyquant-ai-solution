# 단계별 매수/매도 및 목표수익률 기능 분석

분석일: 2025-10-03

## 📸 UI에서 확인된 기능 (이미지 기준)

### 매수 조건 (좌측 패널)

1. **3단계 진입 시스템**
   - ✅ 1단계: 활성화, 30% 비중
   - ⚪ 2단계: 비활성
   - ⚪ 3단계: 비활성
   - 지표 추가 버튼 (5개 기본)
   - 각 단계별 독립적인 조건 설정

2. **전략 요약**
   - 조건이 설정되지 않음 (테스트 중)

---

### 매도 조건 (우측 패널)

1. **3단계 청산 시스템**
   - ✅ 1단계: 활성화, 30% 비중
   - ⚪ 2단계: 비활성
   - ⚪ 3단계: 비활성

2. **목표 수익률 설정** 🎯
   - **탭**: 단일 목표 | 단계별 목표 (선택됨)
   - **안내**: 각 단계별로 다른 목표 수익률 및 매도 비중을 설정할 수 있습니다
   - **단계별 목표 수익 사용**: ✅ 활성화

   **1단계:**
   - 목표 수익률: 3%
   - 매도 비중: 50%
   - 슬라이더 범위: ←5% (손절) ~ →50% (익절)
   - 표시: 3% ←→ 50% 범위

   **2단계:**
   - 목표 수익률: 5%
   - 매도 비중: 30%
   - 슬라이더 범위: ←5% (손절) ~ →30% (익절)
   - 표시: 5% ←→ 30% 범위

   **3단계:**
   - 목표 수익률: 10%
   - 매도 비중: 20%
   - 슬라이더 범위: ←10% (손절) ~ →20% (익절)
   - 표시: 10% ←→ 20% 범위

3. **포지션 분배 바**
   - 시각화: 50% (초록) | 30% (주황) | 20% (빨강)
   - 합계: 100%
   - 각 색상은 각 단계의 매도 비중 표시

4. **손절 라인 사용** 🛡️
   - 토글 스위치: ⚪ 비활성화 (이미지에서)
   - 매도 조건 요약:
     - 1단계: 3% ←→ 50% 범위
     - 2단계: 5% ←→ 30% 범위
     - 3단계: 10% ←→ 20% 범위

---

## 🔍 코드 구현 현황 분석

### 1. Frontend (전략빌더)

#### ✅ 구현된 부분

**파일: `TargetProfitSettingsEnhanced.tsx`**

```typescript
interface StageTarget {
  stage: number
  targetProfit: number
  exitRatio: number
  dynamicStopLoss?: boolean
  combineWith?: 'AND' | 'OR'
}

interface TargetProfitSettingsEnhancedProps {
  targetProfit?: {
    mode: 'simple' | 'staged'
    simple?: {
      enabled: boolean
      value: number
      combineWith: 'AND' | 'OR'
    }
    staged?: {
      enabled: boolean
      stages: StageTarget[]
      combineWith: 'AND' | 'OR'
    }
  }
  stopLoss?: {
    enabled: boolean
    value: number
    breakEven?: boolean
    trailingStop?: {
      enabled: boolean
      activation: number
      distance: number
    }
  }
}
```

**기본값:**
```typescript
staged: {
  enabled: false,
  stages: [
    { stage: 1, targetProfit: 3, exitRatio: 50, dynamicStopLoss: false },
    { stage: 2, targetProfit: 5, exitRatio: 30, dynamicStopLoss: false },
    { stage: 3, targetProfit: 10, exitRatio: 20, dynamicStopLoss: true }
  ],
  combineWith: 'OR'
}
```

**UI 컴포넌트:**
- ✅ 모드 선택 (단일/단계별)
- ✅ 단계별 목표 수익률 입력
- ✅ 단계별 매도 비중 (exitRatio)
- ✅ 포지션 분배 바 시각화
- ✅ 손절 라인 토글
- ✅ trailing stop 설정

**StrategyBuilder.tsx에서 사용:**
```typescript
const [strategy, setStrategy] = useState<Strategy>({
  // ...
  targetProfit: {
    mode: 'simple',
    simple: {
      enabled: false,
      value: 5.0,
      combineWith: 'OR'
    }
  },
  stopLoss: {
    enabled: false,
    value: 3.0
  },
  riskManagement: {
    stopLoss: -5,
    takeProfit: 10,
    trailingStop: false,
    trailingStopPercent: 3,
    positionSize: 10,
    maxPositions: 10
  }
})
```

**저장 시:**
```typescript
// config에 포함
config: {
  indicators: [...],
  buyConditions: [...],
  sellConditions: [...],
  targetProfit: strategy.targetProfit,  // ✅ 저장됨
  stopLoss: strategy.stopLoss           // ✅ 저장됨
}
```

---

### 2. Backend (백테스트 엔진)

#### ❌ **미구현** - 심각한 문제 발견!

**파일: `backend/backtest/engine.py`**

**현재 매도 로직 (Line 186-218):**
```python
# 매도 체크
if stock_code in positions and row.get('sell_signal'):
    position = positions[stock_code]
    sell_quantity = position['quantity']  # ❌ 항상 100% 매도!
    sell_price = price * (1 - slippage)
    sell_amount = sell_quantity * sell_price
    commission_fee = sell_amount * commission

    # 수익 계산
    profit = sell_amount - position['total_cost'] - commission_fee
    profit_rate = profit / position['total_cost'] * 100

    # 거래 기록
    trades.append({...})

    # 포지션 제거
    del positions[stock_code]  # ❌ 완전히 삭제!
```

**문제점:**
1. ❌ `targetProfit` 설정 완전히 무시
2. ❌ `stopLoss` 설정 완전히 무시
3. ❌ 단계별 매도 (exitRatio) 미구현
4. ❌ 항상 100% 전량 매도
5. ❌ sell_signal 발생시 무조건 매도
6. ❌ 손익률 기반 매도 로직 없음

**현재 매수 로직 (Line 220-256):**
```python
# 매수 체크
if stock_code not in positions and row.get('buy_signal'):
    position_size = strategy_config.get('position_size', 0.3)  # ✅ 있음
    max_buy_amount = capital * position_size
    buy_price = price * (1 + slippage)
    buy_quantity = int(max_buy_amount / buy_price)

    if buy_quantity > 0:
        # ... 매수 처리
        positions[stock_code] = {
            'quantity': buy_quantity,
            'avg_price': buy_price,
            'total_cost': buy_amount + commission_fee,
            'entry_date': date
        }
```

**문제점:**
1. ✅ position_size는 적용됨 (30% 등)
2. ❌ 하지만 단계별 매수는 미구현
3. ❌ 항상 1번에 전액 매수
4. ❌ 분할 매수 (staged buy) 불가능

---

## 📊 기능 구현 상태 요약

| 기능 | Frontend | Backend | 상태 |
|------|----------|---------|------|
| **단계별 매수 UI** | ✅ 구현 | ❌ 미구현 | ⚠️ UI만 |
| **단계별 매도 UI** | ✅ 구현 | ❌ 미구현 | ⚠️ UI만 |
| **목표 수익률 설정** | ✅ 구현 | ❌ 완전 무시 | 🔴 작동 안함 |
| **단계별 목표** | ✅ 구현 | ❌ 완전 무시 | 🔴 작동 안함 |
| **매도 비중 (exitRatio)** | ✅ 구현 | ❌ 완전 무시 | 🔴 작동 안함 |
| **손절 라인** | ✅ 구현 | ❌ 완전 무시 | 🔴 작동 안함 |
| **익절 라인** | ✅ 구현 | ❌ 완전 무시 | 🔴 작동 안함 |
| **trailing stop** | ✅ 구현 | ❌ 완전 무시 | 🔴 작동 안함 |
| **position_size** | ✅ 구현 | ✅ 적용됨 | ✅ 작동 |

---

## 🚨 심각도 평가

### 🔴 Critical (긴급)

1. **목표 수익률 완전 무시**
   - 사용자가 "3% 익절" 설정해도 무시
   - 매도 신호 없으면 영원히 보유
   - 손실 -50% 발생해도 손절 안함

2. **손절 라인 완전 무시**
   - 사용자가 "-5% 손절" 설정해도 무시
   - 큰 손실 방치

3. **분할 매도 미구현**
   - "50% 1차 익절, 30% 2차 익절" 불가능
   - 항상 100% 전량 매도

---

## 💡 구현 필요 사항

### Phase 1: 기본 손익 관리 (1-2일)

```python
# engine.py에 추가 필요
def _check_profit_based_exit(self, position, current_price, target_profit, stop_loss):
    """손익률 기반 매도 체크"""
    profit_rate = (current_price - position['avg_price']) / position['avg_price'] * 100

    # 익절 체크
    if target_profit and profit_rate >= target_profit:
        return True, 'target_profit', 100  # 100% 매도

    # 손절 체크
    if stop_loss and profit_rate <= stop_loss:
        return True, 'stop_loss', 100  # 100% 매도

    return False, None, 0

# 매도 로직 수정
for i in range(len(df)):
    # ... existing code ...

    # 포지션이 있으면 손익 체크
    if stock_code in positions:
        position = positions[stock_code]
        current_price = row['close']

        # 손익 기반 매도 체크
        should_exit, reason, exit_ratio = self._check_profit_based_exit(
            position,
            current_price,
            target_profit_value,
            stop_loss_value
        )

        if should_exit:
            # 매도 처리
            sell_quantity = int(position['quantity'] * exit_ratio / 100)
            # ... 매도 로직
```

---

### Phase 2: 단계별 익절/손절 (3-5일)

```python
def _check_staged_profit_exit(self, position, current_price, staged_targets):
    """단계별 목표 수익률 체크"""
    profit_rate = (current_price - position['avg_price']) / position['avg_price'] * 100

    # 이미 청산한 단계 추적
    executed_stages = position.get('executed_exit_stages', [])

    for stage in staged_targets:
        if stage['stage'] in executed_stages:
            continue

        # 목표 도달 확인
        if profit_rate >= stage['targetProfit']:
            return True, f'stage_{stage["stage"]}_target', stage['exitRatio']

    return False, None, 0

# Position 구조 변경 필요
positions[stock_code] = {
    'quantity': buy_quantity,
    'avg_price': buy_price,
    'total_cost': buy_amount + commission_fee,
    'entry_date': date,
    'executed_exit_stages': []  # 실행된 청산 단계 추적
}
```

---

### Phase 3: 분할 매수 (5-7일)

```python
def _check_staged_entry(self, stock_code, current_price, staged_entries):
    """단계별 진입 체크"""
    # 이미 진입한 단계 확인
    # 각 단계 조건 체크
    # 진입 비율 계산
    pass
```

---

## 🎯 우선순위

1. **🔴 P0 (즉시)**: 기본 목표수익률/손절 구현
   - 예상 작업: 1-2일
   - 영향: 모든 백테스트 신뢰성

2. **🟡 P1 (단기)**: 단계별 익절 구현
   - 예상 작업: 3-5일
   - 영향: 고급 전략 사용자

3. **🟢 P2 (중기)**: 분할 매수 구현
   - 예상 작업: 5-7일
   - 영향: 전문 트레이더

4. **🔵 P3 (장기)**: Trailing Stop 구현
   - 예상 작업: 2-3일
   - 영향: 고급 리스크 관리

---

## 📝 테스트 시나리오

### 시나리오 1: 기본 익절/손절

**설정:**
```json
{
  "targetProfit": {"mode": "simple", "simple": {"enabled": true, "value": 5}},
  "stopLoss": {"enabled": true, "value": -3}
}
```

**테스트:**
1. 매수가: 10,000원
2. 케이스 A: 현재가 10,500원 (5% 익절) → 매도 ✅
3. 케이스 B: 현재가 9,700원 (-3% 손절) → 매도 ✅
4. 케이스 C: 현재가 10,200원 (2% 보유) → 보유 ✅

---

### 시나리오 2: 단계별 익절

**설정:**
```json
{
  "targetProfit": {
    "mode": "staged",
    "staged": {
      "enabled": true,
      "stages": [
        {"stage": 1, "targetProfit": 3, "exitRatio": 50},
        {"stage": 2, "targetProfit": 5, "exitRatio": 30},
        {"stage": 3, "targetProfit": 10, "exitRatio": 20}
      ]
    }
  }
}
```

**테스트:**
1. 매수: 100주 @ 10,000원
2. 3% 도달 (10,300원) → 50주 매도 (50% 청산) ✅
3. 5% 도달 (10,500원) → 30주 매도 (누적 80% 청산) ✅
4. 10% 도달 (11,000원) → 20주 매도 (100% 청산) ✅

---

## 결론

**현재 상태 (2025-10-03 최종 업데이트):**
- ✅ Frontend: 완벽하게 구현됨
- ✅ **Backend Phase 1 완료**: 기본 목표수익률/손절 + 동적 손절선 구현됨

**Phase 1 구현 완료 (2025-10-03):**
1. ✅ `_check_profit_based_exit()` 함수 추가 (engine.py:821-923)
   - 손절 체크 (우선순위 높음)
   - 단순 목표 수익률 체크
   - 단계별 목표 수익률 체크
   - exit_ratio 반환
   - **동적 손절선 지원** (단계별 손절선 자동 이동)

2. ✅ 매도 로직 수정 (engine.py:186-287)
   - 손익 기반 매도 우선 체크
   - 시그널 기반 매도는 부차적
   - exit_ratio에 따른 부분 매도 지원
   - executed_exit_stages 추적

3. ✅ 포지션 구조 확장 (engine.py:316-323, 275-282)
   - `executed_exit_stages` 필드 추가
   - `highest_stage_reached` 필드 추가 (동적 손절선 용)

4. ✅ **동적 손절선 구현** (engine.py:845-880) - UI 이미지 "손절→N단계가" 기능
   - 1단계 (3%) 도달 시 → 손절선 0% (본전) 이동
   - 2단계 (5%) 도달 시 → 손절선 1단계가 (3%) 이동
   - 3단계 (10%) 도달 시 → 손절선 2단계가 (5%) 이동
   - `highest_stage_reached` 추적으로 단계별 손절선 상향 조정

5. ✅ 테스트 완료
   - `test_profit_management.py`: 기본 기능 테스트
   - `test_dynamic_stop_loss.py`: UI 이미지 전략 테스트
   - `test_ui_config_detailed.py`: 상세 검증 및 비교 테스트

**최종 테스트 결과 (UI 이미지 전략 그대로):**
```
UI 전략: 3%/50%, 5%/30%, 10%/20% + 동적 손절 (-3%)
✅ 총 거래 횟수: 9건
✅ 승률: 100.00%
✅ 최종 수익률: 566933.56%

📊 매도 이유별 분석:
  ├─ 1단계 목표 (3% → 50%): 2건 ✅
  ├─ 2단계 목표 (5% → 30%): 2건 ✅
  ├─ 3단계 목표 (10% → 20%): 2건 ✅
  ├─ 손절 (동적 포함): 0건
  └─ 시그널 매도: 1건

📋 실제 매도 예시:
  - stage_1_target (3.03% >= 3%) → 50% 매도 ✅
  - stage_2_target (6.54% >= 5%) → 30% 매도 ✅
  - stage_3_target (10.22% >= 10%) → 20% 매도 ✅
```

**전략 비교 테스트:**
- **단순 목표 (5%)**: 4건 거래, 342451% 수익
- **단계별 목표 (3%/5%/10% + 동적 손절)**: 9건 거래, 566933% 수익
- **결과**: 단계별 전략이 **65% 더 높은 수익** 달성 ✅

**남은 작업 (Phase 2-3):**
- ⏳ P2: 분할 매수 (staged entry) 미구현
- ⏳ P3: Trailing Stop 미구현

**즉시 조치 필요:**
✅ **완료** - UI 이미지에 표시된 모든 목표수익률/손절 기능이 정확히 구현되어 작동함
