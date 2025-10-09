# 전략 A1 검증 보고서

## 📋 개요

- **검증 대상**: 전략 A1
- **검증 일시**: 2025-10-08
- **검증자**: Auto Trading System
- **데이터**: 전략 A1 검증 요청.csv

---

## 🎯 전략 A1 설정 요약

### Stop Loss 설정
- **손절 기준**: -10.6%
- **활성화**: True
- **Trailing Stop**: False

### Target Profit 설정 (Staged Mode)
- **Stage 1**: 10% 수익 시 50% 청산
- **Stage 2**: 20% 수익 시 30% 청산
- **Stage 3**: 30% 수익 시 20% 청산

### Dynamic Stop Loss 설정
```json
{
  "stage": 1,
  "dynamicStopLoss": false  // ⚠️ 비활성화
}
```

---

## 📊 백테스트 거래 내역 분석

### 총 거래 현황
- **총 거래 수**: 25건
- **Buy 거래**: 16건
- **Sell 거래**: 9건

### Sell 거래 상세 분류

| 이유 | 건수 | 수익률 범위 |
|------|------|-------------|
| **Stop Loss** | 5건 | -13.31% ~ -0.23% |
| **Stage 1 Target** | 4건 | +11.80% ~ +12.98% |
| **Stage 2 Target** | 0건 | - |
| **Stage 3 Target** | 0건 | - |

### Stop Loss 거래 상세

| 순번 | 날짜 | 수익률 | 손절 조건 | 정상 여부 |
|------|------|--------|-----------|----------|
| 1 | 2024-11-13 | -13.31% | -13.20% <= -10.60% | ✅ 정상 |
| 2 | 2024-11-20 | -1.30% | -1.17% <= 0.00% | ❌ **비정상** |
| 3 | 2025-03-31 | -1.89% | -1.77% <= 0.00% | ❌ **비정상** |
| 4 | 2025-07-09 | -0.60% | -0.47% <= 0.00% | ❌ **비정상** |
| 5 | 2025-09-01 | -0.23% | -0.10% <= 0.00% | ❌ **비정상** |

### Stage 1 Target 거래 상세

| 순번 | 날짜 | 수익률 | 목표 조건 | 정상 여부 |
|------|------|--------|-----------|----------|
| 1 | 2024-11-18 | +11.80% | 11.94% >= 10% | ✅ 정상 |
| 2 | 2025-03-21 | +11.87% | 12.02% >= 10% | ✅ 정상 |
| 3 | 2025-07-03 | +12.98% | 13.13% >= 10% | ✅ 정상 |
| 4 | 2025-07-28 | +12.20% | 12.35% >= 10% | ✅ 정상 |

---

## 🚨 발견된 문제점

### 1. Stop Loss 로직 불일치

#### Config 설정값
```json
{
  "stopLoss": {
    "value": 10.6,
    "enabled": true
  }
}
```

#### 실제 거래 결과
- **첫 번째 거래**: -13.20% ✅ (설정값 -10.6% 초과하여 정상)
- **나머지 4건**: -1.17%, -1.77%, -0.47%, -0.10% ❌

**문제**: 나머지 4건이 -10.6% 설정값보다 훨씬 작은 손실에서 청산됨

### 2. Dynamic Stop Loss 강제 활성화

#### Config 설정값
```json
{
  "stage": 1,
  "dynamicStopLoss": false  // 비활성화
}
```

#### 실제 동작
- Stage 1 도달 후 **무조건** 손절선이 0% (본전)으로 변경됨
- Config의 `dynamicStopLoss: false` 설정이 **무시**됨

### 3. 거래 패턴 분석

전형적인 패턴:
1. Stage 1 목표 (10%) 도달
2. 50% 청산 (정상)
3. 가격 하락
4. 나머지 50%가 0% 근처에서 손절 (비정상)

---

## 🔍 근본 원인 분석

### 코드 위치
**파일**: `backend/backtest/engine.py`
**함수**: `_check_profit_based_exit`
**라인**: 1144-1160

### 문제 코드

```python
# Line 1144-1147
# 최고 도달 단계에 따라 손절선 조정
if highest_stage > 0 and stop_loss and stop_loss.get('enabled', False):
    # 손절→본전: 1단계 도달 시
    if highest_stage == 1:
        dynamic_stop_loss = 0  # ⚠️ 무조건 0%로 설정
```

### 문제점
1. **Line 1144**: `dynamicStopLoss` 설정값을 확인하지 않음
2. **Line 1147**: Stage 1 도달 시 **무조건** `dynamic_stop_loss = 0` 설정
3. **Line 1136**: `dynamic_stop_enabled` 변수를 읽기만 하고 **사용하지 않음**

```python
# Line 1136 - 사용되지 않는 변수
dynamic_stop_enabled = stage_config.get('dynamicStopLoss', False)
# ⚠️ 선언만 하고 조건문에 사용하지 않음!
```

### 로직 흐름

```
1. 가격 상승 → Stage 1 목표 (10%) 도달
   ↓
2. 50% 청산 (정상)
   ↓
3. highest_stage_reached = 1 기록
   ↓
4. ⚠️ Line 1144-1147 실행
   → dynamic_stop_loss = 0 (무조건 설정)
   ↓
5. 가격 하락
   ↓
6. profit_rate가 0% 이하로 하락
   ↓
7. Line 1173: 손절 발동
   → stop_loss (-1.17% <= 0.00%)
```

---

## ✅ 수정 방안

### 1. 즉시 수정 사항

**파일**: `backend/backtest/engine.py`
**라인**: 1144-1160

#### 수정 전
```python
# 최고 도달 단계에 따라 손절선 조정
if highest_stage > 0 and stop_loss and stop_loss.get('enabled', False):
    # 손절→본전: 1단계 도달 시
    if highest_stage == 1:
        dynamic_stop_loss = 0
    # 손절→1단계가: 2단계 도달 시
    elif highest_stage == 2:
        stage_1 = next((s for s in stages if s.get('stage') == 1), None)
        if stage_1 and stage_1.get('dynamicStopLoss', False):
            dynamic_stop_loss = stage_1.get('targetProfit', 0)
    # ...
```

#### 수정 후
```python
# 최고 도달 단계에 따라 손절선 조정
if highest_stage > 0 and stop_loss and stop_loss.get('enabled', False):
    # 현재 도달한 단계의 dynamicStopLoss 설정 확인
    current_stage_config = next((s for s in stages if s.get('stage') == highest_stage), None)

    # ✅ dynamicStopLoss가 true일 때만 손절선 조정
    if current_stage_config and current_stage_config.get('dynamicStopLoss', False):
        # 손절→본전: 1단계 도달 시
        if highest_stage == 1:
            dynamic_stop_loss = 0
        # 손절→1단계가: 2단계 도달 시
        elif highest_stage == 2:
            stage_1 = next((s for s in stages if s.get('stage') == 1), None)
            if stage_1:
                dynamic_stop_loss = stage_1.get('targetProfit', 0)
        # 손절→2단계가: 3단계 도달 시
        elif highest_stage >= 3:
            stage_2 = next((s for s in stages if s.get('stage') == 2), None)
            if stage_2:
                dynamic_stop_loss = stage_2.get('targetProfit', 0)
```

### 2. 수정 핵심 포인트

✅ **Before**: 무조건 동적 손절 활성화
✅ **After**: `dynamicStopLoss: true`일 때만 활성화

### 3. 기대 효과

수정 후 동작:
- `dynamicStopLoss: false` → 항상 -10.6%에서 손절
- `dynamicStopLoss: true` → Stage 1 도달 시 0%로 손절선 조정

---

## 🧪 테스트 계획

### 1. 단위 테스트

**테스트 케이스 1**: dynamicStopLoss = false
```python
# Given
config = {
    "stopLoss": {"value": 10.6, "enabled": true},
    "targetProfit": {
        "mode": "staged",
        "staged": {
            "stages": [
                {"stage": 1, "targetProfit": 10, "exitRatio": 50, "dynamicStopLoss": false}
            ]
        }
    }
}

# When
- Stage 1 도달 (10% 수익)
- 50% 청산
- 가격 -5% 하락

# Then
- 손절 발동 안 됨 (아직 -10.6%에 도달하지 않음)
```

**테스트 케이스 2**: dynamicStopLoss = true
```python
# Given
config = {
    "stopLoss": {"value": 10.6, "enabled": true},
    "targetProfit": {
        "mode": "staged",
        "staged": {
            "stages": [
                {"stage": 1, "targetProfit": 10, "exitRatio": 50, "dynamicStopLoss": true}
            ]
        }
    }
}

# When
- Stage 1 도달 (10% 수익)
- 50% 청산
- 가격 -1% 하락

# Then
- 손절 발동 (0% 이하로 하락)
```

### 2. 통합 테스트

전략 A1 Config로 재실행:
```bash
# 백테스트 재실행
python backend/test_strategy_a1_validation.py
```

**예상 결과**:
- Stop Loss 5건 → 모두 -10.6% 이하에서만 발동
- Stage 1 Target 4건 → 동일 (정상)

---

## 📝 수정 체크리스트

- [ ] `backend/backtest/engine.py` Line 1144-1160 수정
- [ ] 단위 테스트 작성 및 실행
- [ ] 통합 테스트 (전략 A1 재실행)
- [ ] 백엔드 서버 재시작
- [ ] 프론트엔드에서 백테스트 재실행 및 결과 확인

---

## 🔄 배포 절차

### 1. 코드 수정 완료 후

```bash
# 1. 백엔드 서버 재시작 (NAS 서버)
cd /path/to/auto_stock/backend
pkill -f "python.*api"  # 기존 프로세스 종료
python -m uvicorn api.main:app --reload
```

### 2. 검증 절차

```bash
# 1. 백엔드 API 상태 확인
curl http://localhost:8000/health

# 2. 백테스트 API 테스트
curl -X POST http://localhost:8000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d @strategy_a1_config.json
```

### 3. 프론트엔드 재테스트

1. 브라우저에서 전략 A1 선택
2. 백테스트 실행
3. 결과 CSV 다운로드
4. Stop Loss 조건 재확인

---

## 📌 결론

### 불일치 원인
`backend/backtest/engine.py:1144-1147`에서 Config의 `dynamicStopLoss: false` 설정을 무시하고 Stage 1 도달 시 무조건 손절선을 0%로 변경

### 영향 범위
- Staged Exit 전략을 사용하는 모든 전략
- `dynamicStopLoss: false` 설정을 사용하는 경우

### 수정 방법
각 단계의 `dynamicStopLoss` 설정값을 확인하여 `true`일 때만 동적 손절 활성화

### 재배포 필요 여부
**✅ 예** - 백엔드 코드 수정 후 서버 재시작 필요

---

## 📎 참고 자료

- **Config 파일**: 전략 A1 Config (본문 참조)
- **검증 데이터**: `C:\Users\khanyong\OneDrive\Documents\KakaoTalk Downloads\전략 A1 검증 요청.csv`
- **문제 코드**: `backend/backtest/engine.py:1144-1160`
- **관련 문서**:
  - `backend/STAGED_BUY_SELL_IMPLEMENTATION.md`
  - `backend/STAGE_BASED_TRADING_ANALYSIS.md`

---

**작성일**: 2025-10-08
**버전**: 1.0
**상태**: 수정 대기 중
