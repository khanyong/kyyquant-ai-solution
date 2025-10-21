# n8n 워크플로우 최적화 가이드

## 문제: 워크플로우 실행 시간이 1분 초과

### 현재 구조의 문제점

1. **종목별 순차 API 호출** (가장 큰 병목)
   - 종목 100개 × 3초 = 300초 (5분!)
   - batching 설정: `batchSize: 1, batchInterval: 3000`

2. **불필요한 중복 처리**
   - 매 분마다 모든 종목 재조회
   - 캐싱 없음

3. **동기식 데이터 저장**
   - 각 신호마다 개별 INSERT

## 해결 방안

### 1. 즉시 적용 가능한 방법

#### A. 스케줄 간격 조정
```json
{
  "field": "minutes",
  "minutesInterval": 5  // 1분 → 5분
}
```

#### B. 병렬 실행 방지
**Workflow Settings → Executions:**
- Max Concurrent Executions: **1**
- Execution Timeout: **300** (5분)

### 2. 워크플로우 구조 변경 (권장)

#### 분리 전략: 2개 워크플로우로 분할

**워크플로우 1: 시장 데이터 수집 (1분 주기)**
```
1분마다 실행
  ↓
KOSPI/KOSDAQ 지수 조회
  ↓
시장 데이터 저장
```
- 실행 시간: **5초 미만**
- 가벼운 작업만 수행

**워크플로우 2: 자동매매 신호 생성 (5분 주기)**
```
5분마다 실행
  ↓
전략 조회
  ↓
종목별 시세 조회 (병렬 처리)
  ↓
신호 생성 및 저장
  ↓
자금 검증 → 주문
```
- 실행 시간: **3-5분**
- 무거운 작업 수행

### 3. API 호출 최적화

#### 현재:
```json
{
  "options": {
    "batching": {
      "batch": {
        "batchSize": 1,
        "batchInterval": 3000  // 3초 대기
      }
    }
  }
}
```

#### 개선안:
```json
{
  "options": {
    "batching": {
      "batch": {
        "batchSize": 5,        // 5개씩 묶음
        "batchInterval": 1000  // 1초로 단축
      }
    }
  }
}
```

### 4. 캐싱 전략

#### Supabase에 캐시 테이블 활용

**kw_price_current 테이블 활용:**
- 최근 1분 이내 데이터가 있으면 API 호출 생략
- timestamp 체크하여 fresh data 판단

```sql
-- 1분 이내 데이터 확인
SELECT * FROM kw_price_current
WHERE stock_code = '005930'
  AND updated_at > NOW() - INTERVAL '1 minute';
```

### 5. 권장 설정

#### 개발 환경:
- 스케줄: **5분**
- 타임아웃: **300초**
- 동시 실행: **1개**

#### 운영 환경:
- 스케줄: **3분**
- 타임아웃: **180초**
- 동시 실행: **1개**
- 종목 제한: **상위 50개만**

## 실행 시간 측정

### n8n 실행 이력에서 확인:
1. Workflow → Executions 탭
2. 각 실행의 Duration 확인
3. 평균 실행 시간 파악

### 병목 노드 찾기:
- 각 노드의 실행 시간 확인
- 가장 오래 걸리는 노드 최적화

## 모니터링

### 주의해야 할 지표:
- ⚠️ 실행 시간 > 스케줄 간격
- ⚠️ 큐에 쌓인 실행 건수
- ⚠️ 실패한 실행 비율
- ⚠️ 데이터베이스 응답 시간

### 알림 설정:
n8n에서 워크플로우 실패 시 알림 받기:
- Workflow Settings → Error Workflow
- 실패 시 Slack/Discord 알림
