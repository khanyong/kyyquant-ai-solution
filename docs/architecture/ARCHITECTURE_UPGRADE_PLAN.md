# 백테스트 시스템 아키텍처 업그레이드 플랜

## 개요

"거래 0회" 문제를 근본적으로 해결하고, 실전 매매까지 안전하게 확장 가능한 아키텍처로 개편.

---

## ✅ Phase 1: Supabase 스키마 강화 (완료)

### 목표
- 지표/전략의 **버전 관리** 및 **재현성 보장**
- 백테스트 실행 기록의 **완전한 감사 추적**

### 구현 내용

#### 1.1 indicators 테이블 강화
```sql
-- 추가된 컬럼
version TEXT DEFAULT '1.0.0'           -- SemVer 버전
checksum TEXT                          -- MD5 해시 (재현성)
is_active BOOLEAN DEFAULT true         -- 활성 상태
metadata JSONB                         -- 추가 메타데이터
created_at, updated_at TIMESTAMPTZ     -- 타임스탬프
```

**자동 체크섬 트리거**:
- `formula->>'code'` + `output_columns` + `default_params`의 MD5 해시
- INSERT/UPDATE 시 자동 계산
- 동일한 내용 = 동일한 체크섬 = 재현 가능

**제약 조건**:
- `calculation_type='python_code'`일 때 `formula->>'code'` 필수
- `output_columns` 비어있지 않음
- `UNIQUE(LOWER(name), version)` - 대소문자 무관 유니크

#### 1.2 strategies 테이블 강화
```sql
version TEXT DEFAULT '1.0.0'
checksum TEXT                          -- config 전체의 MD5
is_active BOOLEAN DEFAULT true
tags TEXT[]                            -- ['momentum', 'long'] 등
metadata JSONB
```

**제약 조건**:
- `config`에 `indicators`, `buyConditions`, `sellConditions` 필수

#### 1.3 백테스트 기록 테이블 (신규)

**backtest_runs**: 실행 기록
```sql
id UUID PRIMARY KEY
strategy_id UUID
strategy_version TEXT                  -- 실행 시점 버전
strategy_checksum TEXT                 -- 실행 시점 체크섬
indicators_versions JSONB              -- 사용된 지표 버전 스냅샷
                                       -- [{"name":"macd","version":"1.0.0","checksum":"abc"}]
code_commit_hash TEXT                  -- Git 커밋 해시 (옵션)
engine_version TEXT                    -- 백테스트 엔진 버전

stock_codes TEXT[]
start_date, end_date DATE
initial_capital, commission, slippage

status TEXT                            -- pending/running/completed/failed
error_message TEXT

-- 결과 요약
total_trades, win_rate, total_return, sharpe_ratio, max_drawdown
result_summary JSONB

created_at, started_at, completed_at
created_by UUID
```

**backtest_trades**: 개별 거래
```sql
run_id UUID
stock_code, side, quantity, price
trade_date, trade_time
pnl, pnl_percent
commission_paid, slippage_cost
signal_reason TEXT                     -- 매매 이유
conditions_met JSONB                   -- 만족한 조건
```

**backtest_equity**: 자산 곡선
```sql
run_id UUID
date, timestamp
equity, cash, position_value
daily_return, cumulative_return, drawdown
positions JSONB                        -- 포지션 스냅샷
```

### 적용 방법

```bash
# Supabase SQL Editor에서 실행
# 파일: sql/01_enhance_indicators_strategies.sql
```

**주의사항**:
- 기존 테이블에 컬럼 추가 (데이터 유실 없음)
- 기존 데이터에 자동으로 체크섬 생성
- RLS 정책 활성화 (소유자만 조회 가능)

### 기대 효과
- ✅ 백테스트 결과를 정확히 재현 가능
- ✅ 지표/전략 변경 이력 추적
- ✅ 성과 비교 분석 (같은 전략의 여러 실행)

---

## ✅ Phase 2: 프리플라이트 검증 시스템 (완료)

### 목표
**런타임 실패를 사전에 차단** - "거래 0회", "컬럼 없음" 등의 문제를 **실행 전에** 감지

### 구현 내용

#### 2.1 핵심 모듈: `backtest/preflight.py`

**ValidationResult**: 검증 결과 (ERROR/WARNING/INFO)
**PreflightReport**: 종합 보고서 (passed, errors, warnings, info)
**ConditionParser**: 조건 파싱 및 필요 컬럼 추출
**IndicatorColumnMapper**: 지표 → 생성 컬럼 매핑
**PreflightValidator**: 검증 로직 통합

#### 2.2 검증 항목

**구조 검증**:
- `indicators`, `buyConditions`, `sellConditions` 필수
- 리스트 타입 확인
- 비어있는 조건 경고

**지표 검증**:
- Supabase에 지표 존재 확인
- `output_columns` 비어있지 않음
- 활성 상태 (`is_active=true`) 확인

**조건 검증** (핵심):
- 조건 구조 정합성 (operator, left, right)
- **필요한 컬럼이 지표에서 생성되는지 확인**
  - 예: `macd crossover macd_signal` → `macd`, `macd_signal` 필요
  - 지표 `config.indicators`에서 생성 가능한지 검증
- 누락 컬럼 즉시 보고

**데이터 기간 검증**:
- 백테스트 기간 vs 최대 지표 period
- 최소 3배 이상 권장 (워밍업 데이터)

#### 2.3 API 통합

**신규 엔드포인트**: `POST /api/backtest/preflight`
```json
{
  "strategy_id": "uuid",
  "stock_codes": ["005930"],
  "date_range": ["2023-01-01", "2023-12-31"]
}
```

**응답**:
```json
{
  "passed": false,
  "errors": [
    {
      "level": "error",
      "message": "buyConditions[0]: Missing columns: ['macd_signal']",
      "details": {
        "condition": {...},
        "required": ["macd", "macd_signal"],
        "available": ["macd", "close", "sma_20"],
        "missing": ["macd_signal"]
      }
    }
  ],
  "warnings": [...],
  "info": [...]
}
```

**백테스트 실행 시 자동 검증**:
```python
# api/backtest.py
@router.post("/run")
async def run_backtest(request):
    # 1. 전략 로드
    # 2. 프리플라이트 검증 ← 여기서 실패 시 422 반환
    # 3. 백테스트 실행
```

### 사용 예제

**프론트엔드에서 저장 전 검증**:
```javascript
// 전략 저장 전
const result = await fetch('/api/backtest/preflight', {
  method: 'POST',
  body: JSON.stringify({
    strategy_config: strategyConfig,
    date_range: ['2023-01-01', '2023-12-31']
  })
});

if (!result.passed) {
  showErrors(result.errors); // 사용자에게 즉시 피드백
  return;
}

// 검증 통과 후 저장
await saveStrategy(strategyConfig);
```

**백엔드에서 실행 전 자동 검증**:
```python
from backtest.preflight import preflight_check

# 백테스트 실행 전
report = await preflight_check(
    strategy_config=config,
    calculator=calculator,
    raise_on_error=True  # 실패 시 ValueError
)

# 통과하면 실행
result = await engine.run(...)
```

### 기대 효과
- ✅ **"거래 0회" 문제 사전 차단** (컬럼 불일치 즉시 감지)
- ✅ 명확한 에러 메시지 (어떤 컬럼이 누락되었는지)
- ✅ 사용자 경험 개선 (실행 전 피드백)
- ✅ 개발 시간 절약 (디버깅 불필요)

---

## 🔄 Phase 3: API/워커 분리 (다음 단계)

### 목표
- API 게이트웨이와 백테스트 실행 분리
- **무거운 연산이 API를 블로킹하지 않도록**

### 설계

```
[Frontend] → [FastAPI Gateway] → [Redis Queue] → [Worker Process(es)]
                    ↓                                      ↓
              Job ID 즉시 반환                    비동기 백테스트 실행
                    ↑                                      ↓
              WebSocket으로                         결과 Supabase 저장
              진행상황 푸시                               ↓
                                                   WebSocket으로 알림
```

### 구현 계획

#### 3.1 Redis 추가
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - ./redis:/data
```

#### 3.2 작업 큐 (Arq/RQ/Celery 중 택1)

**Arq 추천 이유**:
- FastAPI 네이티브 (async/await)
- Redis 기반 (추가 인프라 불필요)
- 간단한 설정

```python
# workers/backtest_worker.py
from arq import create_pool
from arq.connections import RedisSettings

async def run_backtest_job(ctx, strategy_id, stock_codes, start_date, end_date):
    """백테스트 워커 잡"""
    engine = BacktestEngine()
    result = await engine.run(strategy_id, stock_codes, start_date, end_date)

    # 결과 저장
    await save_to_supabase(result)

    # WebSocket으로 완료 알림
    await notify_completion(ctx['user_id'], result)

    return result

class WorkerSettings:
    functions = [run_backtest_job]
    redis_settings = RedisSettings(host='redis', port=6379)
```

#### 3.3 API 수정
```python
# api/backtest.py
from arq import create_pool

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    # 프리플라이트 검증
    report = await preflight_check(...)
    if not report.passed:
        raise HTTPException(422, str(report))

    # 작업 큐에 투입
    redis = await create_pool(RedisSettings())
    job = await redis.enqueue_job(
        'run_backtest_job',
        request.strategy_id,
        request.stock_codes,
        request.start_date,
        request.end_date
    )

    # 즉시 Job ID 반환 (백테스트는 백그라운드에서 실행)
    return {
        "job_id": job.job_id,
        "status": "queued",
        "message": "Backtest queued. Use /status/{job_id} to check progress."
    }

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """작업 상태 조회"""
    redis = await create_pool(RedisSettings())
    job = Job(job_id, redis=redis)
    info = await job.info()

    return {
        "job_id": job_id,
        "status": info.status,  # queued/in_progress/complete/failed
        "progress": info.result  # 중간 결과
    }
```

#### 3.4 Docker Compose 구성
```yaml
version: "3.8"
services:
  api:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8001
    ports: ["8080:8001"]
    depends_on: [redis]

  backtest-worker:
    build: ./backend
    command: arq workers.backtest_worker.WorkerSettings
    depends_on: [redis]
    deploy:
      replicas: 2  # 동시 2개 백테스트 실행
      resources:
        limits:
          cpus: '2.0'
          memory: 4g

  redis:
    image: redis:7-alpine
    volumes: ["./redis:/data"]
```

### 기대 효과
- ✅ API 응답 속도 향상 (즉시 반환)
- ✅ 동시 여러 백테스트 실행 가능 (워커 스케일링)
- ✅ 리소스 격리 (백테스트 실패가 API에 영향 없음)
- ✅ 진행상황 추적 가능

---

## 🖥️ Phase 4: Windows Execution Agent (실전 매매)

### 목표
- 키움 OpenAPI+를 안전하게 운영
- NAS(Linux)와 Windows 머신 간 안정적 통신

### 설계

```
[NAS Backend]                    [Windows PC]
     ↓                                ↓
Trade Orchestrator ←─gRPC/REST─→ Execution Agent
     ↓                                ↓
 Risk Guards                     Kiwoom OpenAPI+
 Order Management                     ↓
 Position Tracking               실제 매매 체결
```

### 구현 계획

#### 4.1 gRPC 프로토콜 정의
```protobuf
// trade_execution.proto
syntax = "proto3";

service TradeExecution {
  // 주문
  rpc PlaceOrder(OrderRequest) returns (OrderResponse);
  rpc CancelOrder(CancelRequest) returns (CancelResponse);

  // 조회
  rpc GetPositions(PositionsRequest) returns (PositionsResponse);
  rpc GetAccount(AccountRequest) returns (AccountResponse);

  // 헬스체크
  rpc Heartbeat(HeartbeatRequest) returns (HeartbeatResponse);
}

message OrderRequest {
  string account_no = 1;
  string stock_code = 2;
  string side = 3;       // buy/sell
  int32 quantity = 4;
  double price = 5;      // 0 = 시장가
  string order_type = 6; // limit/market/stop
  string idempotency_key = 7;  // 중복 방지
}
```

#### 4.2 Windows Agent 구조
```python
# agent/windows_execution_agent.py
import grpc
from kiwoom import KiwoomAPI

class ExecutionAgent:
    def __init__(self):
        self.kiwoom = KiwoomAPI()
        self.risk_guard = RiskGuard()
        self.order_cache = OrderCache()  # 중복 방지

    async def PlaceOrder(self, request, context):
        # 1. Idempotency 체크
        if self.order_cache.exists(request.idempotency_key):
            return self.order_cache.get(request.idempotency_key)

        # 2. 리스크 가드 (로컬)
        if not self.risk_guard.check(request):
            raise grpc.RpcError("Risk limit exceeded")

        # 3. 키움 주문 실행
        result = self.kiwoom.place_order(
            account=request.account_no,
            code=request.stock_code,
            side=request.side,
            qty=request.quantity,
            price=request.price
        )

        # 4. 캐시 저장
        self.order_cache.set(request.idempotency_key, result)

        return OrderResponse(
            order_id=result.order_id,
            status="accepted"
        )

    async def Heartbeat(self, request, context):
        """2초마다 상태 체크"""
        return HeartbeatResponse(
            status="alive",
            kiwoom_connected=self.kiwoom.is_connected(),
            account_no=self.kiwoom.get_account_no(),
            timestamp=datetime.now().isoformat()
        )
```

#### 4.3 Trade Orchestrator (NAS)
```python
# trade/orchestrator.py
import grpc
from trade_execution_pb2_grpc import TradeExecutionStub

class TradeOrchestrator:
    def __init__(self, agent_host='192.168.50.100:50051'):
        channel = grpc.aio.insecure_channel(agent_host)
        self.agent = TradeExecutionStub(channel)

    async def execute_signal(self, signal):
        """전략 시그널 → 실제 주문"""
        # 1. 리스크 가드 (서버 측)
        if not self.check_risk_limits(signal):
            logger.warning("Risk limit exceeded")
            return

        # 2. 주문 요청
        try:
            response = await self.agent.PlaceOrder(
                OrderRequest(
                    account_no=os.getenv('KIWOOM_ACCOUNT'),
                    stock_code=signal.stock_code,
                    side=signal.side,
                    quantity=signal.quantity,
                    price=signal.price,
                    idempotency_key=f"{signal.id}_{uuid.uuid4()}"
                ),
                timeout=5.0
            )

            logger.info(f"Order placed: {response.order_id}")
            await self.save_to_db(signal, response)

        except grpc.RpcError as e:
            logger.error(f"Order failed: {e}")
            await self.handle_failure(signal, e)

    async def monitor_heartbeat(self):
        """에이전트 상태 모니터링"""
        while True:
            try:
                hb = await self.agent.Heartbeat(HeartbeatRequest())
                if not hb.kiwoom_connected:
                    await self.alert("Kiwoom disconnected!")
            except grpc.RpcError:
                await self.alert("Agent unreachable!")
            await asyncio.sleep(2)
```

### 기대 효과
- ✅ 키움 API와 백엔드 완전 분리
- ✅ 네트워크 단절 시 로컬 킬스위치 작동
- ✅ 중복 주문 방지 (idempotency)
- ✅ 양방향 리스크 가드 (서버+에이전트)

---

## 📋 마이그레이션 체크리스트

### Phase 1 (즉시 적용)
- [ ] Supabase SQL Editor에서 `01_enhance_indicators_strategies.sql` 실행
- [ ] 기존 지표/전략에 체크섬 자동 생성 확인
- [ ] `backtest_runs` 테이블 생성 확인

### Phase 2 (즉시 적용)
- [ ] `backend/backtest/preflight.py` 배포
- [ ] `backend/api/backtest.py` 업데이트 (프리플라이트 통합)
- [ ] 프론트엔드에서 `/api/backtest/preflight` 호출 테스트
- [ ] 실패 케이스 테스트 (누락 지표, 잘못된 조건)

### Phase 3 (선택적)
- [ ] Redis 컨테이너 추가
- [ ] Arq 워커 구현 및 테스트
- [ ] Docker Compose 업데이트 (api + worker + redis)
- [ ] WebSocket 진행상황 알림 구현

### Phase 4 (실전 준비 시)
- [ ] gRPC 프로토콜 정의
- [ ] Windows Agent 구현 (키움 연동)
- [ ] Trade Orchestrator 구현
- [ ] 모의 투자로 E2E 테스트

---

## 🔍 검증 방법

### Phase 1 검증
```sql
-- 체크섬 생성 확인
SELECT name, version, checksum FROM indicators LIMIT 5;

-- 백테스트 기록 테이블 확인
SELECT * FROM backtest_runs LIMIT 1;
```

### Phase 2 검증
```bash
# 프리플라이트 API 테스트
curl -X POST http://192.168.50.150:8080/api/backtest/preflight \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_config": {
      "indicators": [{"name": "macd", "params": {}}],
      "buyConditions": [{"left": "macd", "operator": "crossover", "right": "nonexistent_col"}],
      "sellConditions": []
    }
  }'

# 기대 결과: passed=false, errors에 "Missing columns: ['nonexistent_col']"
```

### Phase 3 검증
```bash
# 워커 로그 확인
docker logs backtest-worker-1 -f

# 작업 큐 상태
docker exec -it redis redis-cli
> KEYS *  # 큐에 쌓인 작업 확인
```

---

## 📊 기대 성과

| 지표 | 현재 | 목표 |
|------|------|------|
| 백테스트 실행 실패율 | ~30% | <5% |
| 에러 진단 시간 | 10-30분 | <1분 |
| 동시 백테스트 처리 | 1개 | 2-4개 |
| API 응답 시간 | 10-60초 | <200ms |
| 재현 가능성 | 불가능 | 100% |

---

## 다음 단계

1. **Phase 1+2 즉시 적용** (리스크 최소, 효과 최대)
2. **1주일 운영 후 평가**
3. **Phase 3 결정** (워커 분리 필요성 확인)
4. **실전 매매 준비 시 Phase 4 착수**

---

## 문의 및 피드백

Phase 1+2는 기존 시스템을 건드리지 않고 추가만 하므로 **안전하게 적용 가능**합니다.
문제 발생 시 해당 파일만 제거하면 롤백 완료됩니다.