# 백테스트 조건 처리 분석 리포트

생성일: 2025-10-03

## 1. 현재 구현 상태

### 1.1 전략빌더 (StrategyBuilder.tsx)

**조건 구조:**
```typescript
interface Condition {
  id: string
  type: 'buy' | 'sell'
  indicator: string
  operator: string
  value: number
  combineWith: 'AND' | 'OR'  // ✅ 지원됨
}
```

**UI 지원:**
- ✅ AND/OR 선택 가능 (line 1652-1657)
- ✅ 각 조건마다 combineWith 설정
- ✅ 조건 추가/제거 가능

**기본 동작:**
- 첫 번째 조건: combineWith는 무시됨
- 두 번째 이후: 이전 조건과 combineWith로 결합
- 예: `[조건1] AND [조건2] OR [조건3]`

---

## 2. 백테스트 엔진 (engine.py) 조건 평가

### 2.1 현재 구현 코드

**매수 조건 평가 (line 478-493):**
```python
# 매수 조건 체크 - AND 조건으로 평가
all_buy_conditions_met = True
buy_reasons = []

if buy_conditions:
    for condition in buy_conditions:
        if not self._check_condition(df.iloc[i], condition):
            all_buy_conditions_met = False
            break
        else:
            buy_reasons.append(self._format_condition_reason(condition))

    if all_buy_conditions_met:
        df.loc[df.index[i], 'buy_signal'] = True
        df.loc[df.index[i], 'buy_reason'] = ' & '.join(buy_reasons)
        buy_signal_count += 1
```

**매도 조건 평가 (line 495-501):**
```python
# 매도 조건 체크 - OR 조건으로 평가 (하나라도 만족하면 매도)
for condition in sell_conditions:
    if self._check_condition(df.iloc[i], condition):
        df.loc[df.index[i], 'sell_signal'] = True
        df.loc[df.index[i], 'sell_reason'] = self._format_condition_reason(condition)
        sell_signal_count += 1
        break
```

---

## 3. 문제점 분석

### ❌ 문제 1: combineWith 필드 무시

**현재 상황:**
- 전략빌더에서 각 조건에 `combineWith: 'AND' | 'OR'` 설정 가능
- **백테스트 엔진에서 이 필드를 완전히 무시함**

**실제 동작:**
- **매수 조건**: 무조건 모든 조건 AND 결합
- **매도 조건**: 무조건 모든 조건 OR 결합

**예시:**
```json
// 사용자가 설정한 조건
{
  "buyConditions": [
    {"left": "rsi", "operator": "<", "right": 30},        // 첫 조건
    {"left": "macd_line", "operator": ">", "right": 0, "combineWith": "OR"},  // OR
    {"left": "volume", "operator": ">", "right": "volume_ma_20", "combineWith": "AND"}  // AND
  ]
}

// 의도: (rsi < 30) OR (macd_line > 0 AND volume > volume_ma_20)
// 실제: (rsi < 30) AND (macd_line > 0) AND (volume > volume_ma_20)  ❌
```

---

### ❌ 문제 2: 복잡한 조건 조합 불가능

**불가능한 케이스:**
1. `(A OR B) AND C`
2. `A OR (B AND C)`
3. `(A AND B) OR (C AND D)`

**현재 제한:**
- 매수: 오직 `A AND B AND C ...`만 가능
- 매도: 오직 `A OR B OR C ...`만 가능

---

### ❌ 문제 3: 분할매수/분할매도 미구현

**검색 결과:**
- "분할매수", "partial buy", "scale in" 키워드 검색
- 58개 파일 매칭되지만 실제 구현 없음
- 대부분 문서, 주석, 계획 파일

**현재 상태:**
- 매수 신호 발생 → 전액 매수 (100% position size)
- 분할 진입/청산 로직 없음

---

## 4. 개선 방안

### 4.1 combineWith 지원 구현

**Option 1: 순차적 평가 (간단)**
```python
def _evaluate_conditions_with_combine(self, row, conditions):
    if not conditions:
        return False

    # 첫 번째 조건 평가
    result = self._check_condition(row, conditions[0])

    # 나머지 조건들을 combineWith에 따라 결합
    for condition in conditions[1:]:
        current_result = self._check_condition(row, condition)
        combine_with = condition.get('combineWith', 'AND')

        if combine_with == 'AND':
            result = result and current_result
        else:  # OR
            result = result or current_result

    return result
```

**장점:**
- 간단한 구현
- `A AND B OR C AND D` 같은 순차 조합 가능

**단점:**
- 괄호 그룹핑 불가 `(A OR B) AND C`
- 연산자 우선순위 없음

---

**Option 2: 표현식 파서 (복잡, 강력)**
```python
def _evaluate_conditions_with_grouping(self, row, conditions):
    # 조건을 AST로 변환
    # AND/OR 우선순위 처리
    # 괄호 그룹핑 지원
    pass
```

**장점:**
- 완전한 논리 표현 가능
- `(A OR B) AND (C OR D)` 지원

**단점:**
- 복잡한 구현
- UI도 복잡해짐 (괄호 입력)

---

### 4.2 분할매수/분할매도 구현

**필요한 필드 추가:**
```json
{
  "buyConditions": [...],
  "buyStages": [
    {
      "conditions": [...],
      "positionSize": 30,  // 30% 매수
      "priority": 1
    },
    {
      "conditions": [...],
      "positionSize": 70,  // 70% 매수
      "priority": 2
    }
  ]
}
```

**구현 방안:**
1. 각 stage마다 별도 조건 평가
2. priority 순서대로 진입
3. positionSize에 따라 분할 매수/매도

---

## 5. 테스트 케이스

### 5.1 AND 조건 테스트

**테스트 케이스:**
```json
{
  "buyConditions": [
    {"left": "rsi", "operator": "<", "right": 30},
    {"left": "macd_line", "operator": ">", "right": "macd_signal", "combineWith": "AND"}
  ]
}
```

**예상 결과:**
- RSI < 30 AND MACD > Signal 모두 만족해야 매수

**현재 동작:** ✅ 정상 (기본이 AND이므로)

---

### 5.2 OR 조건 테스트

**테스트 케이스:**
```json
{
  "buyConditions": [
    {"left": "rsi", "operator": "<", "right": 30},
    {"left": "rsi", "operator": ">", "right": 70, "combineWith": "OR"}
  ]
}
```

**예상 결과:**
- RSI < 30 OR RSI > 70 중 하나만 만족하면 매수

**현재 동작:** ❌ 실패
- 무조건 AND 평가 → RSI < 30 AND RSI > 70 (불가능)
- 거래 0회

---

### 5.3 혼합 조건 테스트

**테스트 케이스:**
```json
{
  "buyConditions": [
    {"left": "rsi", "operator": "<", "right": 40},
    {"left": "macd_line", "operator": ">", "right": 0, "combineWith": "AND"},
    {"left": "volume", "operator": ">", "right": "volume_ma_20", "combineWith": "OR"}
  ]
}
```

**의도:** `(RSI < 40 AND MACD > 0) OR (Volume > VMA)`

**현재 동작:** ❌ 실패
- `RSI < 40 AND MACD > 0 AND Volume > VMA`로 평가
- combineWith 무시됨

---

## 6. 권장 사항

### 단기 (즉시 수정 필요) ⚠️

1. **combineWith 필드 지원 구현**
   - Option 1 (순차 평가) 방식 채택
   - 매수/매도 조건 모두 적용
   - 2-3시간 작업량

2. **문서화 업데이트**
   - 현재 제한사항 명시
   - 사용자 가이드 작성

---

### 중기 (다음 스프린트)

3. **분할매수/분할매도 구현**
   - Stage 기반 접근 방식
   - UI 개선 필요
   - 1-2주 작업량

4. **복잡한 조건 지원**
   - 괄호 그룹핑
   - 조건 그룹 UI
   - 2-3주 작업량

---

## 7. 결론

### 현재 상태 요약

| 기능 | 전략빌더 | 백테스트 엔진 | 상태 |
|------|----------|---------------|------|
| AND 조건 | ✅ 지원 | ✅ 작동 | ✅ 정상 |
| OR 조건 | ✅ UI 지원 | ❌ 무시됨 | ❌ 버그 |
| 혼합 조건 | ✅ UI 지원 | ❌ 무시됨 | ❌ 버그 |
| 분할매수 | ❌ 미지원 | ❌ 미구현 | ⚠️ 계획 중 |
| 분할매도 | ❌ 미지원 | ❌ 미구현 | ⚠️ 계획 중 |

### 우선순위

1. **🔴 긴급**: combineWith 필드 지원 (OR 조건 버그)
2. **🟡 중요**: 분할매수/매도 구현
3. **🟢 일반**: 복잡한 조건 그룹핑

---

**다음 단계:**
1. combineWith 지원 구현 코드 작성
2. 테스트 케이스 실행
3. 복합전략 B 재테스트
