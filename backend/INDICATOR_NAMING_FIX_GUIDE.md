# 백테스트 거래 0회 문제 해결 가이드

## 문제 요약

백테스트 실행 시 지표 컬럼명 불일치로 인해 거래 횟수가 0회가 나오는 문제

### 원인

1. **전략 조건에서 접미사 포함 컬럼명 사용**: `macd_12_26`, `rsi_14`, `ma_20` 등
2. **실제 계산되는 표준 컬럼명**: `macd`, `rsi`, `ma` 등
3. **숫자 문자열 처리 문제**: `"0"` vs `0`

## 해결 방법

### 1단계: SQL 패치 적용 (즉시 효과)

```bash
# Supabase SQL 에디터에서 실행
cd backend
cat fix_all_strategy_conditions.sql
```

**또는 Python으로 직접 적용:**

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('../.env')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# MACD 템플릿 수정
supabase.table('strategies').update({
    'config': {
        'buyConditions': [
            {'indicator': 'macd', 'compareTo': 'macd_signal', 'operator': 'cross_above'},
            {'indicator': 'macd', 'value': 0, 'operator': '>'}
        ],
        'sellConditions': [
            {'indicator': 'macd', 'compareTo': 'macd_signal', 'operator': 'cross_below'}
        ]
    }
}).eq('id', '82b9e26e-e115-4d43-a81b-1fa1f444acd0').execute()
```

### 2단계: 엔진 개선 (방어 로직)

✅ 이미 적용됨 - `backend/backtest/engine.py`

**추가된 기능:**

1. **지표 이름 자동 해석** (`_resolve_indicator_name`)
   - `macd_12_26` → `macd`
   - `rsi_14` → `rsi`
   - `bb_upper_20_2` → `bb_upper`
   - `sma_20` → `sma_20` (정확한 이름 우선)

2. **피연산자 자동 해석** (`_resolve_operand`)
   - 숫자 문자열 `"0"` → 숫자 `0`
   - 컬럼명 자동 매핑

3. **Preflight 검증** (`_validate_strategy_conditions`)
   - 백테스트 시작 전 모든 조건의 지표 존재 여부 검증
   - 실패 시 명확한 에러 메시지 제공

### 3단계: 테스트

```bash
# 백엔드 서버 재시작
cd backend
python main.py

# 프론트엔드에서 백테스트 실행
# - [템플릿] MACD 시그널 전략 선택
# - 종목: 005930 (삼성전자)
# - 기간: 2024-01-01 ~ 2024-12-31
# - 실행
```

**기대 결과:**
```
[Engine] ✅ Strategy validation PASSED
[Engine] Signal evaluation complete: X buy signals, Y sell signals
[Engine] Results: Total trades: Z
```

## 표준 지표 컬럼명 매핑표

| 조건에서 사용 가능한 이름 | 실제 컬럼명 | 비고 |
|---|---|---|
| `macd`, `macd_12_26`, `macd_line` | `macd` | MACD Line |
| `macd_signal`, `macd_signal_12_26_9` | `macd_signal` | Signal Line |
| `macd_hist`, `macd_hist_12_26_9` | `macd_hist` | Histogram |
| `rsi`, `rsi_14`, `rsi_9` | `rsi` | RSI |
| `sma_20`, `sma_60`, `sma_5` | `sma_20`, `sma_60`, `sma_5` | 각각 별도 컬럼 |
| `ema_20`, `ema_60` | `ema_20`, `ema_60` | 각각 별도 컬럼 |
| `bb_upper`, `bb_upper_20_2` | `bb_upper` | 볼린저밴드 상단 |
| `bb_middle`, `bb_middle_20_2` | `bb_middle` | 볼린저밴드 중간 |
| `bb_lower`, `bb_lower_20_2` | `bb_lower` | 볼린저밴드 하단 |
| `stochastic`, `stoch_k` | `stoch_k` | Stochastic %K |
| `stoch_d` | `stoch_d` | Stochastic %D |

## 권장 조건 작성 방법

### ✅ 좋은 예

```json
{
  "buyConditions": [
    {"indicator": "macd", "compareTo": "macd_signal", "operator": "cross_above"},
    {"indicator": "macd", "value": 0, "operator": ">"},
    {"indicator": "rsi", "value": 30, "operator": "<"}
  ],
  "sellConditions": [
    {"indicator": "macd", "compareTo": "macd_signal", "operator": "cross_below"},
    {"indicator": "rsi", "value": 70, "operator": ">"}
  ]
}
```

### ❌ 나쁜 예

```json
{
  "buyConditions": [
    {"indicator": "macd_12_26", "compareTo": "macd_signal_12_26_9", "operator": "cross_above"},
    {"indicator": "macd_12_26", "value": "0", "operator": ">"},  // 문자열 "0"
    {"indicator": "rsi_14", "value": "30", "operator": "<"}  // 문자열 "30"
  ]
}
```

## 디버깅 방법

### 1. 로그 확인

백테스트 실행 시 터미널에서 다음 로그를 확인:

```
[Engine] Final columns: ['open', 'high', 'low', 'close', 'volume', 'macd', 'macd_signal', 'macd_hist', 'rsi']
[Engine] Buy conditions: [{'indicator': 'macd_12_26', ...}]
[Engine] ❌ Strategy validation FAILED:
  - BUY condition #1: Indicator 'macd_12_26' not found. Available: open, high, low, close, volume, macd, macd_signal, macd_hist, rsi
```

### 2. 수동 검증

```python
# Python 스크립트
from indicators.calculator import IndicatorCalculator
import pandas as pd

calculator = IndicatorCalculator()

# 샘플 데이터
df = pd.DataFrame({...})

# 지표 계산
result = calculator.calculate(df, {
    'name': 'macd',
    'params': {'period': 12}
})

print("Generated columns:", list(result.columns.keys()))
# 출력: ['macd', 'macd_signal', 'macd_hist']
```

## Q&A

### Q1: 기존 전략들은 모두 수정해야 하나요?

**A:** 엔진의 자동 매핑 기능으로 대부분 동작하지만, **표준 컬럼명 사용을 강력히 권장**합니다.

### Q2: 새로운 지표를 추가하려면?

**A:**
1. Supabase `indicators` 테이블에 지표 정의 추가
2. `output_columns` 필드에 생성될 컬럼명 명시
3. 전략 조건에서 해당 컬럼명 사용

### Q3: 여러 기간의 같은 지표를 동시에 사용하려면?

**A:**
```json
{
  "indicators": [
    {"name": "sma", "params": {"period": 20}, "output_name": "sma_20"},
    {"name": "sma", "params": {"period": 60}, "output_name": "sma_60"}
  ],
  "buyConditions": [
    {"indicator": "sma_20", "compareTo": "sma_60", "operator": "cross_above"}
  ]
}
```

### Q4: 프론트엔드에서 드롭다운으로 강제할까요?

**A:** **YES - 강력히 권장**합니다. 다음 단계로 진행:

1. 전략 편집기에서 지표 선택을 드롭다운으로 제한
2. Supabase에서 사용 가능한 지표 목록을 가져와 표시
3. 수동 입력 불가
4. 숫자 입력은 number input으로 강제

## 향후 개선 사항

- [ ] 프론트엔드 지표 선택 드롭다운 구현
- [ ] 전략 마이그레이션 자동화 도구
- [ ] 지표 컬럼명 표준화 가이드라인 문서
- [ ] 백테스트 API에서 조건 자동 정규화
- [ ] 실시간 검증 UI 추가

## 관련 파일

- `backend/fix_all_strategy_conditions.sql` - 전략 일괄 수정 SQL
- `backend/backtest/engine.py` - 백테스트 엔진 (지표 매핑 로직)
- `backend/indicators/calculator.py` - 지표 계산기
- `src/components/BacktestRunner.tsx` - 백테스트 UI

## 지원

문제가 계속되면 다음을 확인:

1. 백엔드 로그 (`[Engine]` 태그)
2. Supabase `indicators` 테이블의 `output_columns` 필드
3. 전략 `config.indicators` 배열

---

**최종 업데이트**: 2025-09-30
**작성자**: Claude Code Assistant