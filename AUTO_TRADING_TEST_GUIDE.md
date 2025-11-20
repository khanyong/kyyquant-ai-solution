# 자동 매매 테스트 가이드

## 📋 개요

이 문서는 **시그널 발생 시 자동으로 주문이 들어가는지** 확인하는 테스트 절차를 설명합니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                   자동매매 파이프라인                            │
└─────────────────────────────────────────────────────────────┘

1. 조건 모니터링 (n8n workflow-v7-1)
   ↓ 매 1분마다 실행
   ├─ strategies 테이블에서 활성 전략 조회
   ├─ investment_universe에서 모니터링 종목 조회
   ├─ 각 종목의 시장 데이터 조회 (Kiwoom API)
   ├─ 조건 충족도 점수 계산 (0-100점)
   └─ strategy_monitoring 테이블 업데이트 (80점 이상만)

2. 매수 주문 생성 (n8n workflow-v7-2)
   ↓ 매 1분마다 실행
   ├─ strategy_monitoring에서 score=100 종목 조회
   ├─ 계좌 잔고 확인 (kw_account_balance)
   ├─ 포지션 사이즈 계산
   ├─ Kiwoom API 주문 전송
   ├─ orders 테이블 INSERT (auto_cancel_at 설정)
   └─ trading_signals 업데이트 (signal_status='ORDERED')

3. 주문 자동 취소 (n8n workflow-v7-3)
   ↓ 매 1분마다 실행
   ├─ auto_cancel_at 경과된 미체결 주문 조회
   ├─ Kiwoom API 취소 요청
   ├─ orders.status='CANCELLED' 업데이트
   └─ trading_signals.signal_status='CANCELLED' 업데이트
```

## 📊 데이터베이스 테이블 구조

### 핵심 테이블

1. **strategies**: 사용자가 만든 자동매매 전략
   - `is_active`: 활성화 여부
   - `entry_conditions`: 매수 조건 (JSON)
   - `position_size_percent`: 포지션 크기 (%)

2. **investment_universe**: 전략별 모니터링 종목
   - `strategy_id` + `stock_code`
   - 전략이 감시할 종목 목록

3. **strategy_monitoring**: 조건 근접도 추적 (NEW in v7)
   - `condition_match_score`: 0-100점
   - `is_near_entry`: 80점 이상 여부
   - `conditions_met`: 각 조건별 충족 상태 (JSONB)

4. **trading_signals**: 매수/매도 시그널
   - `signal_status`: PENDING → ORDERED → EXECUTED/CANCELLED
   - `order_id`: 연결된 주문 ID

5. **orders**: 실제 주문
   - `order_status`: PENDING → SUBMITTED → EXECUTED
   - `auto_cancel_at`: 자동 취소 예정 시간

6. **kw_account_balance**: 계좌 잔고
   - `available_cash`: 주문 가능 현금

## ✅ 테스트 시나리오

### 시나리오 1: 정상 자동매매 플로우

```
[전제 조건]
✓ 활성 전략 존재 (is_active=true)
✓ 투자 유니버스에 종목 등록
✓ 계좌 잔고 충분 (available_cash > 100만원)
✓ n8n 워크플로우 3개 모두 Active

[예상 동작]
1. workflow-v7-1이 1분마다 종목 점수 계산
2. 조건 충족 시 strategy_monitoring에 score=100 저장
3. workflow-v7-2가 감지하여 즉시 주문 생성
4. orders 테이블에 레코드 INSERT
5. trading_signals의 signal_status='ORDERED' 업데이트
6. 30분 후 미체결 시 workflow-v7-3이 자동 취소
```

### 시나리오 2: 잔고 부족

```
[전제 조건]
✓ 활성 전략 존재
✓ available_cash < 필요 금액

[예상 동작]
1. workflow-v7-2가 주문 생성 시도
2. 잔고 부족 감지
3. 주문 생성 건너뛰기 (로그에 기록)
```

### 시나리오 3: 조건 미충족

```
[전제 조건]
✓ 활성 전략 존재
✓ 투자 유니버스 종목 존재
✓ 조건 점수 < 100점 (예: 85점)

[예상 동작]
1. strategy_monitoring에 score=85로 저장
2. "매수 대기 종목"에 표시 (is_near_entry=true)
3. 주문은 생성되지 않음 (score=100 도달 시까지)
```

## 🔍 테스트 실행 방법

### STEP 1: 진단 SQL 실행

Supabase SQL Editor에서 다음 파일 실행:

```bash
d:\Dev\auto_stock\supabase\test_auto_trading_flow.sql
```

이 SQL은 다음을 확인합니다:
1. ✅ 활성 전략 존재 여부
2. ✅ 투자 유니버스 설정 여부
3. ✅ strategy_monitoring 업데이트 상태 (워크플로우 실행 여부)
4. ✅ 최근 시그널 발생 이력
5. ✅ 최근 주문 생성 이력
6. ✅ 계좌 잔고 상태
7. ✅ 자동매매 파이프라인 요약
8. ✅ 문제 진단 및 해결 방법

### STEP 2: n8n 워크플로우 확인

1. n8n 대시보드 접속: http://localhost:5678
2. 다음 워크플로우가 **Active** 상태인지 확인:
   - ✅ workflow-v7-1-condition-monitoring-fixed
   - ✅ workflow-v7-2-buy-order-creation-fixed
   - ✅ workflow-v7-3-auto-cancel-orders

3. 각 워크플로우의 실행 로그 확인:
   - Executions 탭 클릭
   - 최근 1분 내 실행 이력 확인
   - 에러 메시지 확인

### STEP 3: 실시간 모니터링

진단 SQL의 **STEP 7** (실시간 대시보드) 부분을 반복 실행하며 모니터링:

```sql
-- 10초마다 새로고침하여 실행
SELECT
  'Active Strategies: ' || ... as stat1,
  'Monitored Stocks: ' || ... as stat2,
  'Ready to Buy (Score 100): ' || ... as stat3,
  'Signals Today: ' || ... as stat4,
  'Orders Today: ' || ... as stat5,
  'Available Cash: ₩' || ... as stat6;
```

### STEP 4: 테스트 시그널 수동 생성 (선택사항)

⚠️ **주의**: 실제 주문이 발생할 수 있으므로 테스트 환경에서만 사용!

진단 SQL의 **STEP 5** 주석을 해제하여 수동으로 시그널 생성:

```sql
INSERT INTO trading_signals (
  user_id,
  strategy_id,
  stock_code,
  stock_name,
  signal_type,
  signal_strength,
  current_price,
  target_price,
  stop_loss,
  confidence,
  reasons,
  signal_status
)
SELECT
  'f912da32-897f-4dbb-9242-3a438e9733a8',
  s.id,
  '005930',
  '삼성전자',
  'BUY',
  'STRONG',
  72000,
  76000,
  68000,
  0.85,
  ARRAY['RSI < 30 (과매도)', '거래량 급증 (2.5배)', '이동평균선 돌파'],
  'PENDING'
FROM strategies s
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
LIMIT 1
RETURNING id, stock_code, stock_name, signal_type, created_at;
```

시그널 생성 후:
1. 1분 대기
2. workflow-v7-2가 실행되는지 n8n에서 확인
3. orders 테이블에 새 레코드 생성되었는지 확인
4. trading_signals의 signal_status가 'ORDERED'로 변경되었는지 확인

## 🐛 문제 해결

### 문제 1: 워크플로우가 실행되지 않음

**증상**:
```sql
SELECT MAX(updated_at) FROM strategy_monitoring;
-- 결과: 30분 이상 경과
```

**원인**: n8n 워크플로우가 비활성화되었거나 중단됨

**해결**:
1. n8n 대시보드에서 워크플로우 Active 상태 확인
2. n8n 서비스 재시작:
   ```bash
   # Docker 사용 시
   docker restart n8n

   # npm 사용 시
   npm run n8n
   ```

### 문제 2: 조건 충족했지만 주문 미생성

**증상**:
```sql
SELECT * FROM strategy_monitoring WHERE condition_match_score = 100;
-- 결과: 1개 이상 존재
SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '5 minutes';
-- 결과: 0개
```

**원인**: workflow-v7-2의 주문 생성 로직 오류 또는 잔고 부족

**해결**:
1. n8n에서 workflow-v7-2의 실행 로그 확인
2. 계좌 잔고 확인:
   ```sql
   SELECT available_cash FROM kw_account_balance
   WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
   ```
3. Kiwoom API 서버 상태 확인 (localhost:3001)

### 문제 3: 시그널 생성됐지만 status가 PENDING에서 변경 안 됨

**증상**:
```sql
SELECT * FROM trading_signals
WHERE signal_status = 'PENDING'
  AND created_at < NOW() - INTERVAL '5 minutes';
-- 결과: 오래된 PENDING 시그널 존재
```

**원인**: workflow-v7-2가 trading_signals 업데이트 실패

**해결**:
1. workflow-v7-2의 "Update Signal Status" 노드 확인
2. PostgreSQL 연결 credential 확인
3. RLS 정책 확인:
   ```sql
   SELECT * FROM pg_policies
   WHERE schemaname = 'public'
     AND tablename = 'trading_signals';
   ```

### 문제 4: 주문이 즉시 취소됨

**증상**:
```sql
SELECT * FROM orders
WHERE order_status = 'CANCELLED'
  AND EXTRACT(EPOCH FROM (updated_at - created_at)) < 60;
-- 결과: 1분 이내 취소된 주문
```

**원인**: auto_cancel_at이 잘못 설정되었거나 workflow-v7-3이 과도하게 실행됨

**해결**:
1. auto_cancel_at 값 확인:
   ```sql
   SELECT
     id,
     created_at,
     auto_cancel_at,
     EXTRACT(EPOCH FROM (auto_cancel_at - created_at)) / 60 as minutes_until_cancel
   FROM orders
   WHERE order_status = 'CANCELLED';
   ```
2. workflow-v7-3의 조건 로직 확인

## 📈 성공 지표

자동매매가 정상 작동하는지 확인하는 지표:

### ✅ 즉시 확인 (5분 이내)

```sql
-- 1. 워크플로우 실행 여부
SELECT
  EXTRACT(EPOCH FROM (NOW() - MAX(updated_at))) / 60 as minutes_ago
FROM strategy_monitoring;
-- 예상: < 2분

-- 2. 조건 충족 종목 → 주문 생성 시간
SELECT
  ts.created_at as signal_time,
  o.created_at as order_time,
  EXTRACT(EPOCH FROM (o.created_at - ts.created_at)) as delay_seconds
FROM trading_signals ts
JOIN orders o ON o.stock_code = ts.stock_code
  AND o.user_id = ts.user_id
WHERE ts.created_at > NOW() - INTERVAL '1 hour'
ORDER BY ts.created_at DESC;
-- 예상: delay_seconds < 120 (2분 이내)
```

### ✅ 장기 모니터링 (1일 이상)

```sql
-- 1. 일일 시그널 발생 건수
SELECT
  DATE(created_at) as date,
  COUNT(*) as total_signals,
  COUNT(CASE WHEN signal_status = 'ORDERED' THEN 1 END) as ordered,
  COUNT(CASE WHEN signal_status = 'EXECUTED' THEN 1 END) as executed
FROM trading_signals
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 2. 주문 체결률
SELECT
  COUNT(*) as total_orders,
  COUNT(CASE WHEN order_status = 'EXECUTED' THEN 1 END) as executed,
  ROUND(
    COUNT(CASE WHEN order_status = 'EXECUTED' THEN 1 END)::NUMERIC / COUNT(*) * 100,
    2
  ) as execution_rate_percent
FROM orders
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND created_at > NOW() - INTERVAL '7 days';
```

## 🚀 다음 단계

자동매매 테스트가 성공하면:

1. **UI 표시 확인**:
   - [AutoTradingPanelV2.tsx](src/components/trading/AutoTradingPanelV2.tsx)에서 "매수 대기 종목" 표시
   - [OrderPanel.tsx](src/components/trading/OrderPanel.tsx)에서 "대기중인 주문" 표시
   - 자동취소 카운트다운 표시

2. **실제 매매 테스트** (소액):
   - position_size_percent를 1% 이하로 설정
   - 실제 시장 조건에서 테스트
   - 체결 후 포트폴리오 업데이트 확인

3. **모니터링 대시보드 구축**:
   - 일일 시그널 발생 통계
   - 전략별 수익률 추적
   - 주문 체결률 분석

## 📝 체크리스트

테스트 시작 전 확인:

- [ ] Supabase 프로젝트 실행 중
- [ ] Kiwoom API 서버 실행 중 (localhost:3001)
- [ ] n8n 서버 실행 중 (localhost:5678)
- [ ] 계좌 설정 완료 (kiwoom_account, API keys)
- [ ] 활성 전략 존재 (is_active=true)
- [ ] 투자 유니버스 설정됨
- [ ] 계좌 잔고 충분 (>100만원 권장)
- [ ] 3개 워크플로우 모두 Active:
  - [ ] workflow-v7-1-condition-monitoring-fixed
  - [ ] workflow-v7-2-buy-order-creation-fixed
  - [ ] workflow-v7-3-auto-cancel-orders

테스트 완료 후 확인:

- [ ] strategy_monitoring에 종목 등록됨
- [ ] condition_match_score 정확히 계산됨
- [ ] score=100 도달 시 자동 주문 생성됨
- [ ] trading_signals.signal_status 업데이트됨
- [ ] orders 테이블에 레코드 생성됨
- [ ] auto_cancel_at 올바르게 설정됨 (created_at + 30분)
- [ ] UI에 주문이 표시됨
