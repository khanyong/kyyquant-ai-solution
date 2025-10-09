# SQL 비교 분석

## 주요 차이점

### 1. 필드명 차이
| 항목 | 첫 번째 SQL | 두 번째 SQL |
|------|------------|------------|
| 조건 필드 | `indicator`, `compareTo`, `value` | `left`, `right` |
| 트랜잭션 | 없음 | `BEGIN;` / `COMMIT;` |
| indicators 배열 | ❌ 없음 | ✅ 포함 |

### 2. 조건 구조 비교

#### 첫 번째 SQL (현재 버전)
```json
{
  "indicator": "macd",
  "compareTo": "macd_signal",
  "operator": "cross_above"
}
```

#### 두 번째 SQL (제안된 버전)
```json
{
  "left": "macd",
  "right": "macd_signal",
  "operator": "cross_above"
}
```

### 3. 호환성 분석

**백엔드 엔진 코드 (engine.py:489-494):**
```python
def _check_condition(self, row: pd.Series, condition: Dict) -> bool:
    """조건 체크"""
    indicator = condition.get('indicator')  # ← 이 필드를 사용
    operator = condition.get('operator')
    value = condition.get('value')
    compare_to = condition.get('compareTo')  # ← 이 필드를 사용
```

**결론:** 현재 엔진은 **`indicator` / `compareTo` / `value`** 구조를 사용합니다.

### 4. indicators 배열 차이

#### 첫 번째 SQL
- `indicators` 배열을 수정하지 않음
- 전략에 이미 정의된 지표 사용

#### 두 번째 SQL
```json
{
  "indicators": [
    {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
  ]
}
```
- 모든 전략에 `indicators` 배열 명시
- 지표 파라미터 명확히 정의
- 더 명확하고 자기 완결적

### 5. 숫자 처리

#### 첫 번째 SQL
```json
{"indicator": "macd", "value": 0, "operator": ">"}
```

#### 두 번째 SQL
```json
{"left": "macd", "right": 0, "operator": ">"}
```

두 버전 모두 숫자를 정수로 처리 (올바름)

### 6. 트랜잭션

#### 첫 번째 SQL
- 트랜잭션 없음
- 각 UPDATE는 독립적으로 실행
- 실패 시 일부만 적용될 위험

#### 두 번째 SQL
```sql
BEGIN;
-- updates...
COMMIT;
```
- 트랜잭션으로 감쌈
- 전체 성공 또는 전체 롤백
- 더 안전함 ✓

## 권장 사항

### 🚨 중요: 현재 백엔드와의 호환성

현재 백엔드 엔진(`engine.py`)은 다음 필드를 사용합니다:
- `indicator` (not `left`)
- `compareTo` (not `right`)
- `value`

**두 번째 SQL을 사용하려면 백엔드 코드도 수정해야 합니다!**

### 옵션 1: 첫 번째 SQL + indicators 추가 (추천)

```sql
BEGIN;

UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyConditions}',
      '[
        {"indicator": "macd", "compareTo": "macd_signal", "operator": "cross_above"},
        {"indicator": "macd", "value": 0, "operator": ">"}
      ]'::jsonb
    ),
    '{sellConditions}',
    '[
      {"indicator": "macd", "compareTo": "macd_signal", "operator": "cross_below"}
    ]'::jsonb
  ),
  '{indicators}',
  '[
    {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
  ]'::jsonb
)
WHERE id = '82b9e26e-e115-4d43-a81b-1fa1f444acd0';

-- ... 다른 전략들도 동일하게

COMMIT;
```

**장점:**
- ✅ 현재 백엔드와 완전 호환
- ✅ indicators 배열로 명확성 증가
- ✅ 트랜잭션으로 안전성 보장

### 옵션 2: 두 번째 SQL + 백엔드 수정

**백엔드 수정 필요:**
```python
def _check_condition(self, row: pd.Series, condition: Dict) -> bool:
    # 새 필드명 지원
    indicator = condition.get('indicator') or condition.get('left')
    compare_to = condition.get('compareTo') or condition.get('right')
    value = condition.get('value') or condition.get('right')
```

**장점:**
- ✅ 더 직관적인 필드명 (`left`/`right`)
- ✅ indicators 배열 포함
- ✅ 트랜잭션 보장

**단점:**
- ⚠️ 백엔드 코드 수정 필요
- ⚠️ 기존 전략 마이그레이션 필요

## 최종 권장

### 🎯 즉시 적용 가능 (Option 1)

첫 번째 SQL에 다음을 추가:
1. `BEGIN;` / `COMMIT;` 트랜잭션
2. `indicators` 배열

### 📋 개선된 버전

```sql
BEGIN;

-- 1. MACD 시그널
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'macd', 'compareTo', 'macd_signal', 'operator', 'cross_above'),
      jsonb_build_object('indicator', 'macd', 'value', 0, 'operator', '>')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'macd', 'compareTo', 'macd_signal', 'operator', 'cross_below')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object('name', 'macd', 'params', jsonb_build_object('fast', 12, 'slow', 26, 'signal', 9))
    )
  )
WHERE id = '82b9e26e-e115-4d43-a81b-1fa1f444acd0';

-- 2. RSI 과매수/과매도
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'rsi', 'value', 30, 'operator', '<')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'rsi', 'value', 70, 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object('name', 'rsi', 'params', jsonb_build_object('period', 14))
    )
  )
WHERE id = '97d50901-504e-4e53-8e29-0d535dc095f0';

-- ... 나머지 전략들

COMMIT;
```

## 요약

| 기준 | 첫 번째 SQL | 두 번째 SQL | 권장 |
|------|------------|------------|------|
| 백엔드 호환성 | ✅ 즉시 호환 | ❌ 코드 수정 필요 | 첫 번째 |
| 필드명 직관성 | ⚠️ 보통 | ✅ 우수 | 두 번째 |
| indicators 포함 | ❌ 없음 | ✅ 있음 | 두 번째 |
| 트랜잭션 | ❌ 없음 | ✅ 있음 | 두 번째 |
| **즉시 사용 가능** | **✅ YES** | **❌ NO** | **첫 번째** |

**최종 결론:** 첫 번째 SQL을 기반으로 트랜잭션과 indicators를 추가한 버전을 사용하세요.