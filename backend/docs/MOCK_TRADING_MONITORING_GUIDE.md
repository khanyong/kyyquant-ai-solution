# 📈 모의투자 실시간 주가 모니터링 가이드

## 🔄 시스템 구조

```
실시간 주가 → N8N 스케줄러 → 키움 Bridge API → 매매 신호 → 주문 실행
     ↑                                                        ↓
  키움 REST API                                         Supabase 저장
```

## 🚀 모의투자 모니터링 프로세스

### 1. **N8N 스케줄러 설정**
N8N이 주기적으로 실시간 주가를 확인하고 매매 신호를 생성합니다.

```json
{
  "schedule": {
    "interval": "1분",  // 1분마다 실행
    "tradingHours": "09:00-15:30"  // 장중 시간만
  }
}
```

### 2. **실시간 주가 수집 방법**

#### 방법 A: REST API 폴링 (현재 구현)
```python
# backend/kiwoom_bridge/main.py 에서 실행
@router.get("/api/market/current-price/{stock_code}")
async def get_current_price(stock_code: str):
    """실시간 현재가 조회"""
    # 키움 REST API로 현재가 조회
    price = await kiwoom_api.get_current_price(stock_code)

    # Supabase에 저장
    supabase.table('kw_price_current').upsert({
        'stock_code': stock_code,
        'current_price': price.price,
        'change_rate': price.change_rate,
        'volume': price.volume,
        'timestamp': datetime.now()
    }).execute()

    return price
```

#### 방법 B: WebSocket 실시간 구독 (향후 구현)
```python
# 실시간 체결 데이터 구독
async def subscribe_realtime(stock_codes: List[str]):
    """WebSocket으로 실시간 데이터 구독"""
    ws_url = "ws://openapi.kiwoom.com:9443/realtime"

    async with websockets.connect(ws_url) as ws:
        # 종목 구독
        await ws.send(json.dumps({
            "tr_type": "1",  # 실시간 등록
            "tr_key": stock_codes
        }))

        # 실시간 데이터 수신
        async for message in ws:
            data = json.loads(message)
            await process_realtime_data(data)
```

### 3. **N8N 워크플로우 구성**

#### 3.1 주가 모니터링 워크플로우
```javascript
// N8N 워크플로우 노드 구성
1. Schedule Trigger (1분마다)
   ↓
2. HTTP Request - 현재가 조회
   POST http://kiwoom-bridge:8001/api/market/current-price
   Body: { "stock_codes": ["005930", "000660", "035720"] }
   ↓
3. Code Node - 매매 신호 생성
   - 전략 조건 확인
   - RSI, MACD 등 지표 계산
   - Buy/Sell/Hold 신호 생성
   ↓
4. IF Node - 신호 확인
   ↓
5. HTTP Request - 주문 실행
   POST http://kiwoom-bridge:8001/api/trading/order
```

#### 3.2 매매 신호 생성 로직
```javascript
// N8N Code Node 예시
const currentPrice = $input.item.json.current_price;
const indicators = $input.item.json.indicators;

// 전략 조건 확인
if (indicators.rsi < 30 && indicators.macd_signal > 0) {
    return {
        signal: 'BUY',
        stock_code: $input.item.json.stock_code,
        quantity: calculateQuantity(currentPrice),
        reason: 'RSI 과매도 + MACD 골든크로스'
    };
}

if (indicators.rsi > 70) {
    return {
        signal: 'SELL',
        stock_code: $input.item.json.stock_code,
        quantity: 'ALL',
        reason: 'RSI 과매수'
    };
}

return { signal: 'HOLD' };
```

### 4. **모의투자 주문 실행**

```python
# backend/kiwoom_bridge/trading_executor.py
async def execute_mock_order(order: OrderRequest):
    """모의투자 주문 실행"""

    # 1. 현재가 조회
    current_price = await get_current_price(order.stock_code)

    # 2. 모의 계좌 잔고 확인
    balance = await get_mock_balance(order.user_id)

    # 3. 주문 가능 여부 확인
    if order.order_type == 'BUY':
        required_amount = current_price * order.quantity
        if balance.cash < required_amount:
            return {"error": "잔고 부족"}

    # 4. 모의 주문 체결
    mock_order = {
        'user_id': order.user_id,
        'stock_code': order.stock_code,
        'order_type': order.order_type,
        'quantity': order.quantity,
        'price': current_price,
        'status': 'EXECUTED',  # 모의투자는 즉시 체결
        'executed_at': datetime.now()
    }

    # 5. Supabase에 기록
    supabase.table('mock_orders').insert(mock_order).execute()

    # 6. 모의 잔고 업데이트
    await update_mock_balance(order.user_id, mock_order)

    return mock_order
```

### 5. **모니터링 대시보드**

```python
# backend/api/monitoring.py
@router.get("/api/monitoring/dashboard")
async def get_monitoring_dashboard(user_id: str):
    """모니터링 대시보드 데이터"""

    # 실시간 포트폴리오 현황
    portfolio = await get_portfolio_status(user_id)

    # 오늘의 거래 내역
    todays_trades = await get_todays_trades(user_id)

    # 실시간 손익
    realtime_pnl = await calculate_realtime_pnl(user_id)

    # 주요 지표
    market_indicators = await get_market_indicators()

    return {
        'portfolio': portfolio,
        'trades': todays_trades,
        'pnl': realtime_pnl,
        'indicators': market_indicators,
        'timestamp': datetime.now()
    }
```

## 📊 데이터 흐름

### 1. **실시간 데이터 수집**
```
키움 REST API (1분마다)
    ↓
현재가, 호가, 체결 데이터
    ↓
Supabase 저장 (kw_price_current)
    ↓
N8N 워크플로우 트리거
```

### 2. **매매 신호 생성**
```
현재가 + 기술적 지표
    ↓
전략 조건 확인
    ↓
Buy/Sell/Hold 신호
    ↓
주문 실행 요청
```

### 3. **모의 체결 처리**
```
주문 요청
    ↓
잔고 확인
    ↓
즉시 체결 (모의)
    ↓
포트폴리오 업데이트
    ↓
성과 기록
```

## 🛠️ 설정 방법

### 1. N8N 워크플로우 임포트
```bash
# N8N 관리자 페이지 접속
http://NAS_IP:5678

# 워크플로우 임포트
Settings → Import → auto_trading_workflow.json
```

### 2. 환경변수 설정
```env
# .env 파일
KIWOOM_MODE=MOCK  # 모의투자 모드
N8N_WEBHOOK_URL=http://nas_ip:5678
MONITORING_INTERVAL=60  # 초 단위
```

### 3. 모니터링 시작
```bash
# Docker 컨테이너 실행
docker-compose up -d

# N8N 워크플로우 활성화
# N8N UI에서 워크플로우 활성화 버튼 클릭

# 로그 확인
docker logs -f kiwoom-bridge
```

## 📈 성과 추적

### 일일 성과 리포트
```sql
-- 오늘의 거래 성과
SELECT
    COUNT(*) as total_trades,
    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(profit) as total_profit,
    AVG(profit_rate) as avg_profit_rate
FROM mock_orders
WHERE DATE(executed_at) = CURRENT_DATE
  AND user_id = 'user123';
```

### 실시간 포트폴리오 가치
```sql
-- 현재 보유 종목 시가 평가
SELECT
    p.stock_code,
    p.quantity,
    p.avg_price,
    c.current_price,
    (c.current_price - p.avg_price) * p.quantity as unrealized_pnl
FROM mock_positions p
JOIN kw_price_current c ON p.stock_code = c.stock_code
WHERE p.user_id = 'user123';
```

## ⚠️ 주의사항

1. **API 호출 제한**
   - 키움 API: 초당 5회 제한
   - 종목 수에 따라 조회 간격 조정 필요

2. **장 운영시간**
   - 정규장: 09:00 ~ 15:30
   - 장 시작/종료 시간 자동 체크

3. **모의투자 한계**
   - 실제 호가/체결과 차이 있음
   - 슬리피지 고려 필요

4. **리스크 관리**
   - 최대 투자금액 제한
   - 손절 기준 설정
   - 분산 투자 강제

## 🔍 트러블슈팅

### 실시간 데이터 수신 안됨
```bash
# API 연결 상태 확인
curl http://localhost:8001/api/health

# N8N 워크플로우 로그 확인
docker logs n8n-trading

# 키움 API 키 확인
SELECT * FROM user_api_keys WHERE provider = 'kiwoom';
```

### 주문 실행 실패
```bash
# 잔고 확인
curl http://localhost:8001/api/account/balance

# 주문 이력 확인
SELECT * FROM mock_orders ORDER BY created_at DESC LIMIT 10;
```