# n8n Workflow V7 구현 가이드

## 📋 개요

자동매매 시스템의 "매수 대기 종목" 및 "대기중인 주문" 기능을 위한 n8n 워크플로우 3개입니다.

## 🔄 워크플로우 목록

### 1. workflow-v7-1-condition-monitoring.json
**조건 근접도 모니터링 워크플로우**

- **목적**: 전략의 투자유니버스 종목들을 모니터링하여 매수 조건 근접도 추적
- **실행 주기**: 매 1분마다
- **주요 기능**:
  - 활성화된 전략 조회
  - 각 전략의 투자유니버스 종목별 시장 데이터 조회
  - 조건 충족도 점수 계산 (0-100점)
  - 80점 이상인 종목을 `strategy_monitoring` 테이블에 저장

### 2. workflow-v7-2-buy-order-creation.json
**매수 주문 생성 워크플로우**

- **목적**: 조건 100% 충족 종목에 대해 매수 주문 자동 생성
- **실행 주기**: 매 1분마다
- **주요 기능**:
  - `strategy_monitoring`에서 조건 100% 충족 종목 조회
  - 계좌 잔고 조회 및 포지션 사이즈 계산
  - Kiwoom API를 통한 매수 주문 전송
  - `orders` 테이블에 주문 기록 (auto_cancel_at 자동 설정)
  - `trading_signals` 테이블 업데이트 (signal_status = 'ORDERED')

### 3. workflow-v7-3-auto-cancel-orders.json
**주문 자동 취소 워크플로우**

- **목적**: auto_cancel_at 시간이 지난 미체결/부분체결 주문 자동 취소
- **실행 주기**: 매 1분마다
- **주요 기능**:
  - 자동 취소 대상 주문 조회
  - Kiwoom API를 통한 주문 취소 요청
  - `orders.status` = 'CANCELLED' 업데이트
  - `trading_signals.signal_status` = 'CANCELLED' 업데이트
  - `strategy_monitoring`에서 해당 종목 제거

## 📥 n8n에 워크플로우 가져오기

1. n8n 대시보드 열기
2. 좌측 메뉴에서 "Workflows" 클릭
3. 우측 상단 "Import from File" 클릭
4. 각 JSON 파일을 선택하여 가져오기:
   - `workflow-v7-1-condition-monitoring.json`
   - `workflow-v7-2-buy-order-creation.json`
   - `workflow-v7-3-auto-cancel-orders.json`

## ⚙️ 설정 필요 사항

### 1. Supabase Credentials 설정

각 워크플로우의 PostgreSQL 노드에서 Supabase 연결 정보를 설정해야 합니다:

```
Host: your-project.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: your-supabase-password
SSL: true
```

### 2. Kiwoom API 엔드포인트 확인

다음 API 엔드포인트가 구현되어 있어야 합니다:

- `POST http://localhost:3001/api/kiwoom/market-data`
  - 요청: `{ stock_code: "005930" }`
  - 응답: `{ stock_name, current_price, rsi, volume_ratio, ma20, ... }`

- `POST http://localhost:3001/api/kiwoom/order`
  - 요청: `{ stock_code, order_type: "BUY", price, quantity }`
  - 응답: `{ kiwoom_order_no, success, ... }`

- `POST http://localhost:3001/api/kiwoom/cancel-order`
  - 요청: `{ order_no, stock_code, order_type, quantity }`
  - 응답: `{ success, ... }`

### 3. 조건 충족도 계산 로직 커스터마이징

`workflow-v7-1-condition-monitoring.json`의 "Calculate Condition Score" 노드에서 전략의 `entry_conditions` 구조에 맞게 로직을 수정해야 합니다.

**예시**:
```javascript
// entry_conditions 구조
{
  "rsi_below": 30,
  "volume_multiplier": 2,
  "price_vs_ma": "below"
}
```

## 🚀 워크플로우 활성화

1. 각 워크플로우를 n8n에 가져온 후
2. 우측 상단의 "Active" 토글을 켜서 활성화
3. "Execute Workflow" 버튼으로 테스트 실행 가능

## ⚠️ 주의사항

### 장중 운영시간 체크 추가 필요

현재 워크플로우는 매 1분마다 실행되도록 설정되어 있습니다. 실제 운영 시에는 **장중 시간대만 실행**되도록 조건을 추가하는 것이 좋습니다.

**방법 1**: Schedule Trigger에 시간 조건 추가
```
Cron: */1 9-15 * * 1-5  (월-금, 09:00-15:59)
```

**방법 2**: 워크플로우 시작 부분에 IF 노드 추가
```javascript
// 현재 시간이 장중인지 확인
const now = new Date();
const hour = now.getHours();
const day = now.getDay(); // 0=일요일, 6=토요일

// 월-금, 09:00-15:30
const isMarketHours =
  day >= 1 && day <= 5 &&
  hour >= 9 && hour < 16;

return { json: { isMarketHours } };
```

### 테스트 환경 권장

1. **실제 주문 전 테스트**: Kiwoom API 호출 부분을 주석 처리하고 로그만 출력
2. **소액 테스트**: position_size_percent를 1% 이하로 설정
3. **모니터링**: 워크플로우 실행 로그를 주기적으로 확인

## 📊 데이터 흐름

```
1. Condition Monitoring (매 1분)
   ↓
   strategy_monitoring 테이블 업데이트 (조건 80% 이상 종목)
   ↓
2. Buy Order Creation (매 1분)
   ↓
   조건 100% 종목 발견 → Kiwoom 주문 → orders 테이블 INSERT
   ↓
3. Auto Cancel (매 1분)
   ↓
   30분 경과 미체결 주문 → Kiwoom 취소 → orders/signals 업데이트
```

## 🔍 트러블슈팅

### 워크플로우가 실행되지 않는 경우
- n8n 서비스가 실행 중인지 확인
- "Active" 토글이 켜져 있는지 확인
- Execution 로그에서 에러 메시지 확인

### Supabase 연결 에러
- Credentials 설정 확인
- Supabase 프로젝트의 Database Settings에서 Connection String 확인
- SSL 설정 확인

### Kiwoom API 에러
- Kiwoom OpenAPI가 실행 중인지 확인
- API 서버(localhost:3001)가 실행 중인지 확인
- 로그인 상태 확인

## 📝 다음 단계

Phase 2 완료 후:
- **Phase 3**: 프론트엔드 코드 수정
  - StrategyCard.tsx에서 strategy_monitoring 데이터 표시
  - 조건 충족도 점수 및 진행률 바 추가
  - 대기중인 주문에 auto-cancel 카운트다운 표시
