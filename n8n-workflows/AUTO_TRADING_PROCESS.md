# 자동매매 프로세스 구현 계획

## 현재 상태 (v38)
```
1시간마다 실행
  ↓
종목 현재가 조회
  ↓
DB 저장 (kw_price_current)
  ↓
**여기서 종료** ❌
```

## 필요한 추가 구현 (v39)

### 1단계: 전략 조건 확인 ✅
```javascript
// 노드: 전략 조건 확인 준비
// 현재가 데이터를 다음 단계로 전달
```

### 2단계: 매수/매도 신호 생성 ✅
```javascript
// 노드: 매수/매도 신호 생성
// 입력: 현재가 + 전략 조건
// 출력: trading_signals

매수 조건 예시:
- RSI < 30 (과매도)
- 거래량 > 평균 * 2
- 가격 < MA20

매도 조건 예시:
- 수익률 > 5% (목표 수익)
- 손실률 < -3% (손절)
- RSI > 70 (과매수)
```

### 3단계: 신호 저장 ✅
```sql
INSERT INTO trading_signals (
  stock_code,
  stock_name,
  signal_type,  -- 'buy' or 'sell'
  strategy_id,
  current_price,
  confidence,
  status  -- 'pending'
)
```

### 4단계: 주문 실행 ✅
```javascript
// Kiwoom API 주문
POST https://mockapi.kiwoom.com/api/dostk/order
{
  "stk_cd": "005930",
  "ord_qty": "10",
  "ord_prc": "72000",
  "ord_type": "1",  // 1=매수, 2=매도
  "ord_condition": "0"  // 0=지정가
}
```

### 5단계: 주문 결과 저장 ✅
```sql
INSERT INTO orders (
  signal_id,
  strategy_id,
  stock_code,
  order_type,  -- 'BUY' or 'SELL'
  order_method,  -- 'LIMIT'
  quantity,
  order_price,
  status,  -- 'PENDING'
  api_response
)
```

### 6단계: 체결 확인 (추가 워크플로우 필요)
```
별도 워크플로우 (5분마다 실행):
  ↓
orders 테이블에서 PENDING 조회
  ↓
Kiwoom API 체결 조회
  ↓
체결 완료 시:
  - orders.status = 'EXECUTED'
  - positions 테이블 업데이트
```

## 추가 필요 노드 목록

1. **전략 조건 확인 준비** (Code 노드)
2. **전략 조건 조회** (HTTP Request)
3. **매수/매도 신호 생성** (Code 노드)
4. **신호 저장** (HTTP Request → trading_signals)
5. **주문 실행** (HTTP Request → Kiwoom API)
6. **주문 결과 저장** (HTTP Request → orders)

## 주의사항

### 매수 조건 체크
- 보유 종목 수 확인 (max_positions)
- 사용 가능 자금 확인 (allocated_capital)
- 중복 매수 방지

### 매도 조건 체크
- 실제 보유 여부 확인 (positions 테이블)
- 매도 수량 확인

### API Rate Limit
- Kiwoom API 호출 간격 준수
- 초당 최대 요청 수 제한

## 실제 구현 시 고려사항

1. **지표 계산**
   - RSI, MACD 등은 별도 계산 필요
   - kw_price_daily 테이블에서 과거 데이터 조회
   - 실시간 계산 vs 미리 계산 (성능 고려)

2. **자금 관리**
   - 전략별 할당 자금 추적
   - 포지션 크기 계산 (position_size %)
   - 최대 보유 종목 수 제한

3. **리스크 관리**
   - 손절 라인 설정
   - 목표 수익률 설정
   - 일일 최대 손실 제한

4. **에러 처리**
   - API 호출 실패 시 재시도
   - 주문 실패 시 알림
   - 로그 저장

## 다음 단계

1. v39 워크플로우에 위 노드들 추가
2. 실제 전략 조건 로직 구현
3. 테스트 (Mock 데이터)
4. 실전 배포
