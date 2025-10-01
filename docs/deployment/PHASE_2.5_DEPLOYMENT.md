# Phase 2.5 배포 가이드 - 재현성·안전성 보강

## 개요

Phase 1 (스키마) + Phase 2 (프리플라이트)를 보강하여:
- ✅ **지표 컬럼 표준화** (`indicator_columns` 테이블)
- ✅ **샌드박스 강화** (타임아웃/메모리/AST 검증)
- 🔄 **데이터 스냅샷** (다음 단계 준비)

---

## 🎯 Phase 2.5a: 표준화 + 샌드박스 (즉시 적용)

### 목표
1. 지표명 → 컬럼 매핑을 **테이블화**하여 명명 충돌 원천 차단
2. DB 코드 실행에 **타임아웃/메모리 제한** 적용

### 적용 순서

#### 1단계: Supabase 스키마 (5분)

```sql
-- Supabase SQL Editor에서 실행
-- 파일: sql/02_indicator_columns_standard.sql
```

**생성되는 것**:
- `indicator_columns` 테이블 (지표-컬럼 매핑)
- 핵심 지표 10개 등록 (macd, rsi, sma, ema, bollinger_bands, atr, stochastic, adx, volume_ma, parabolic_sar)
- 헬퍼 함수:
  - `get_indicator_columns(indicator_name)` - 지표의 컬럼 조회
  - `get_available_columns(indicator_names[])` - 전략에서 사용 가능한 모든 컬럼
  - `validate_indicator_output_columns()` - indicators 테이블과 일치 확인

**검증**:
```sql
-- MACD 컬럼 확인
SELECT * FROM get_indicator_columns('macd');
-- 결과: macd, macd_signal, macd_hist

-- 전략에서 사용 가능한 컬럼 (macd + rsi 사용 시)
SELECT * FROM get_available_columns(ARRAY['macd', 'rsi']);
-- 결과: close, open, high, low, volume, macd, macd_signal, macd_hist, rsi

-- indicators 테이블과 동기화 확인
SELECT * FROM validate_indicator_output_columns();
-- 불일치가 있으면 ❌ Mismatch로 표시
```

---

#### 2단계: 백엔드 파일 업로드 (2분)

```powershell
# PowerShell (Windows)
$NAS = "admin@192.168.50.150"
$PATH = "/volume1/docker/auto-stock/backend"

# 1. 샌드박스 모듈 (신규)
scp backend\indicators\sandbox.py "${NAS}:${PATH}/indicators/"

# 2. 프리플라이트 (업데이트 - indicator_columns 활용)
scp backend\backtest\preflight.py "${NAS}:${PATH}/backtest/"

# 3. 재시작
ssh $NAS "cd /volume1/docker/auto-stock && docker-compose restart backend"
```

```bash
# Bash (Linux/Mac)
NAS="admin@192.168.50.150"
PATH="/volume1/docker/auto-stock/backend"

scp backend/indicators/sandbox.py "${NAS}:${PATH}/indicators/"
scp backend/backtest/preflight.py "${NAS}:${PATH}/backtest/"

ssh $NAS "cd /volume1/docker/auto-stock && docker-compose restart backend"
```

---

#### 3단계: 검증 (2분)

**테스트 1: 프리플라이트가 indicator_columns 테이블 사용 확인**
```bash
curl -X POST http://192.168.50.150:8080/api/backtest/preflight \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_config": {
      "indicators": [{"name": "macd", "params": {}}],
      "buyConditions": [
        {"left": "macd", "operator": "crossover", "right": "macd_signal"}
      ],
      "sellConditions": []
    }
  }'

# 기대 결과:
# {
#   "passed": true,
#   "info": [
#     {"message": "indicators[0]: 'macd' → ['macd', 'macd_signal', 'macd_hist']"},
#     {"message": "buyConditions[0]: ✓ All columns available (['macd', 'macd_signal'])"}
#   ]
# }
```

**테스트 2: 표준표에 없는 컬럼 사용 시 에러**
```bash
curl -X POST http://192.168.50.150:8080/api/backtest/preflight \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_config": {
      "indicators": [{"name": "sma", "params": {"period": 20}}],
      "buyConditions": [
        {"left": "macd", "operator": ">", "right": "0"}
      ],
      "sellConditions": []
    }
  }'

# 기대 결과:
# {
#   "passed": false,
#   "errors": [
#     {
#       "message": "buyConditions[0]: Missing columns: ['macd']",
#       "details": {
#         "available": ["close", "open", "high", "low", "volume", "sma"],
#         "missing": ["macd"]
#       }
#     }
#   ]
# }
```

**테스트 3: 샌드박스 검증 (악성 코드 차단)**

샌드박스는 `indicators.calculator.py`에서 사용되므로, 실제 백테스트 실행 시 자동으로 적용됩니다.
별도 테스트는 불필요하지만, 확인하려면:

```python
# backend/indicators/sandbox.py 직접 실행
python backend/indicators/sandbox.py

# 출력:
# ✓ Good code executed: [nan, nan, 101.0, 102.66..., ...]
# ✓ Bad code (import) blocked: AST validation failed: Import statements are not allowed
# ✓ Bad code (file) blocked: AST validation failed: Blocked function: open
# ✓ Timeout code blocked: (Windows에서는 수동 체크)
```

---

### 기대 효과

**Before** (Phase 1+2):
- 프리플라이트가 indicators 테이블의 `output_columns` 조회
- 지표 정의가 변경되면 불일치 발생 가능
- DB 코드 실행 시 타임아웃/메모리 제한 없음

**After** (Phase 2.5a):
- ✅ `indicator_columns` 표준표로 **명명 계약** 명시화
- ✅ indicators 테이블과 **동기화 검증** 가능
- ✅ 샌드박스 타임아웃 (5초), 메모리 제한 (512MB)
- ✅ AST 검증으로 import/파일 접근 차단

---

## 📊 Phase 2.5b: 데이터 스냅샷 (다음 단계)

### 목표
가격 데이터의 **버전 고정** - 데이터 정정/리비전에도 과거 백테스트 재현 가능

### 설계

```sql
-- dataset_snapshots 테이블
CREATE TABLE dataset_snapshots (
    dataset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 쿼리 정의 (재현성)
    source_table TEXT NOT NULL,            -- 'kw_price_daily'
    query_hash TEXT NOT NULL,              -- SELECT ... WHERE 쿼리의 해시
    stock_codes TEXT[] NOT NULL,
    date_range TSTZRANGE NOT NULL,         -- '[2023-01-01, 2024-01-01)'

    -- 데이터 체크섬
    data_checksum TEXT NOT NULL,           -- 실제 데이터 행들의 해시
    row_count BIGINT NOT NULL,
    checksum_method TEXT DEFAULT 'md5',

    -- 캐시 위치 (Parquet)
    parquet_path TEXT,                     -- '/cache/datasets/{dataset_id}.parquet'
    parquet_size_bytes BIGINT,

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,                -- 캐시 만료 (NULL = 영구)

    UNIQUE(query_hash, data_checksum)
);

-- backtest_runs에 dataset_id 추가
ALTER TABLE backtest_runs
    ADD COLUMN IF NOT EXISTS dataset_id UUID REFERENCES dataset_snapshots(dataset_id);
```

**사용 흐름**:
1. 백테스트 시작 → 데이터 로드 쿼리 생성
2. 쿼리 해시 계산 → `dataset_snapshots` 조회
3. 존재하면 `dataset_id` 재사용, 없으면 신규 생성 + 데이터 체크섬 계산
4. `backtest_runs.dataset_id`에 기록
5. Parquet 캐시 저장 (`/cache/datasets/{dataset_id}.parquet`)

**재현 방법**:
```python
# 과거 백테스트 재현
run = get_backtest_run(run_id)
dataset = load_dataset_snapshot(run.dataset_id)  # Parquet에서 로드

# 동일한 가격 데이터로 재실행
result = backtest_engine.run(
    strategy=run.strategy,
    data=dataset,  # 고정된 데이터
    ...
)
```

---

## 🔒 Phase 2.5c: JSON Schema 검증 (보강)

### 목표
전략 `config` 구조를 **스키마로 강제** - 런타임 에러 사전 차단

### JSON Schema 정의

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Strategy Config",
  "type": "object",
  "required": ["indicators", "buyConditions", "sellConditions"],
  "properties": {
    "indicators": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": {"type": "string"},
          "params": {"type": "object"}
        }
      }
    },
    "buyConditions": {
      "type": "array",
      "items": {"$ref": "#/definitions/condition"}
    },
    "sellConditions": {
      "type": "array",
      "items": {"$ref": "#/definitions/condition"}
    }
  },
  "definitions": {
    "condition": {
      "type": "object",
      "required": ["operator"],
      "properties": {
        "operator": {
          "type": "string",
          "enum": ["crossover", "crossunder", ">", "<", ">=", "<=", "==", "!=", "and", "or", "not"]
        },
        "left": {
          "oneOf": [
            {"type": "string"},
            {"type": "number"},
            {"$ref": "#/definitions/condition"}
          ]
        },
        "right": {
          "oneOf": [
            {"type": "string"},
            {"type": "number"},
            {"$ref": "#/definitions/condition"}
          ]
        },
        "conditions": {
          "type": "array",
          "items": {"$ref": "#/definitions/condition"}
        }
      }
    }
  }
}
```

**적용 위치**:
- 프론트엔드: 전략 저장 전 클라이언트 검증
- 백엔드: `strategies` 테이블 저장 시 트리거 검증
- API: `POST /api/backtest/run` 시 재검증

---

## 📝 체크리스트

### Phase 2.5a (즉시)
- [x] SQL: `sql/02_indicator_columns_standard.sql` 실행
- [x] 코드: `sandbox.py`, `preflight.py` 업로드
- [x] 검증: 프리플라이트 API 테스트
- [ ] 모니터링: 1주일 동안 프리플라이트 실패율 추적

### Phase 2.5b (다음 스프린트)
- [ ] SQL: `dataset_snapshots` 테이블 생성
- [ ] 코드: 데이터 로더에 스냅샷 로직 추가
- [ ] 캐시: Parquet 저장/로드 구현
- [ ] 검증: 동일 dataset_id로 재현성 테스트

### Phase 2.5c (점진적)
- [ ] JSON Schema 정의 완성
- [ ] Supabase 트리거 추가 (저장 시 검증)
- [ ] API 검증 로직 추가
- [ ] 프론트엔드 클라이언트 검증 추가

---

## 🚨 주의사항

### 샌드박스 제한 (Windows)
- Windows에서는 `signal.SIGALRM` 미지원 → 타임아웃 수동 체크
- 메모리 제한도 미지원 → 로그 경고만

**대안**:
- NAS(Linux)에서는 정상 작동
- Windows 개발 환경에서는 `limits=SandboxLimits(timeout_seconds=999)` 로 우회 가능

### indicator_columns 동기화
- 새 지표 추가 시 **반드시** `indicator_columns`에도 등록
- `validate_indicator_output_columns()` 로 불일치 확인

### Parquet 캐시 용량
- `dataset_snapshots`가 늘어나면 디스크 사용량 증가
- `expires_at` 설정 + 주기적 정리 필요

---

## 🔍 트러블슈팅

### Q: "indicator_columns 테이블이 없습니다"
**A**: `02_indicator_columns_standard.sql` 실행 확인. Supabase SQL Editor 로그 확인.

### Q: 프리플라이트가 컬럼을 찾지 못합니다
**A**:
1. `SELECT * FROM indicator_columns WHERE indicator_name = 'your_indicator';` 실행
2. 없으면 수동 등록:
   ```sql
   INSERT INTO indicator_columns (indicator_name, column_name, is_primary, output_order) VALUES
   ('your_indicator', 'your_column', true, 1);
   ```

### Q: 샌드박스 타임아웃이 동작하지 않습니다 (Windows)
**A**: 정상입니다. Windows는 `signal` 미지원. NAS 배포 후 정상 작동.

### Q: 기존 전략이 갑자기 실패합니다
**A**:
1. 프리플라이트 에러 메시지 확인 (`/api/backtest/preflight`)
2. 누락된 지표를 `config.indicators`에 추가
3. 또는 `indicator_columns`에 컬럼 등록

---

## 다음 단계

1. **Phase 2.5a 배포** (지금)
2. **1주일 모니터링** - 프리플라이트 실패 케이스 분석
3. **Phase 2.5b 착수** - 데이터 스냅샷으로 완전한 재현성 확보
4. **Phase 3 평가** - API/워커 분리 필요성 판단

---

## 성과 지표

| 항목 | Before | Target |
|------|--------|--------|
| 프리플라이트 정확도 | ~85% | >95% |
| 명명 충돌 발생률 | ~10% | 0% |
| DB 코드 실행 타임아웃 | 무제한 | 5초 |
| 악성 코드 차단 | AST만 | AST+타임아웃+메모리 |

---

## 참고 문서
- [ARCHITECTURE_UPGRADE_PLAN.md](./ARCHITECTURE_UPGRADE_PLAN.md) - 전체 플랜
- [sql/01_enhance_indicators_strategies.sql](./sql/01_enhance_indicators_strategies.sql) - Phase 1 스키마
- [sql/02_indicator_columns_standard.sql](./sql/02_indicator_columns_standard.sql) - Phase 2.5a 스키마