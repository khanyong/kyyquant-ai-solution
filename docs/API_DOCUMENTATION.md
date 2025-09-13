# KYY Quant AI Solution - API Documentation

## Base URL
```
Production: https://api.kyyquant.com
Development: http://localhost:8000
```

## Authentication
모든 API 요청은 Bearer Token 인증이 필요합니다.

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 1. 전략 관리 API

### 1.1 전략 목록 조회
```http
GET /api/strategies
```

**Response:**
```json
{
  "strategies": [
    {
      "id": "uuid",
      "name": "RSI + MACD Strategy",
      "created_at": "2024-01-01T00:00:00Z",
      "performance": {
        "total_return": 15.5,
        "win_rate": 65.2
      }
    }
  ]
}
```

### 1.2 전략 생성
```http
POST /api/strategies
```

**Request Body:**
```json
{
  "name": "My Strategy",
  "config": {
    "indicators": ["RSI", "MACD"],
    "buy_conditions": [
      {
        "indicator": "RSI",
        "operator": "<",
        "value": 30
      }
    ],
    "sell_conditions": [
      {
        "indicator": "RSI",
        "operator": ">",
        "value": 70
      }
    ]
  }
}
```

### 1.3 전략 분석
```http
POST /api/strategies/{strategy_id}/analyze
```

**Response:**
```json
{
  "analysis": {
    "description": "이 전략은 RSI 과매도 구간에서 매수하고...",
    "optimization_suggestions": [
      "손절 라인 추가를 고려하세요",
      "거래량 필터를 추가하면 승률이 향상될 수 있습니다"
    ],
    "risk_assessment": {
      "risk_level": "medium",
      "max_drawdown": 15.2
    }
  }
}
```

---

## 2. 백테스팅 API

### 2.1 백테스트 실행
```http
POST /api/backtest/run
```

**Request Body:**
```json
{
  "strategy_id": "uuid",
  "symbols": ["005930", "000660"],
  "period": {
    "start": "2023-01-01",
    "end": "2023-12-31"
  },
  "initial_capital": 10000000,
  "commission": 0.00015,
  "slippage": 0.001
}
```

**Response:**
```json
{
  "backtest_id": "uuid",
  "status": "completed",
  "results": {
    "total_return": 25.5,
    "sharpe_ratio": 1.8,
    "max_drawdown": -12.3,
    "win_rate": 68.5,
    "total_trades": 42,
    "winning_trades": 29,
    "losing_trades": 13
  },
  "trades": [
    {
      "date": "2023-03-15",
      "symbol": "005930",
      "action": "buy",
      "price": 65000,
      "quantity": 10,
      "profit": null
    }
  ]
}
```

### 2.2 백테스트 결과 조회
```http
GET /api/backtest/{backtest_id}
```

### 2.3 백테스트 비교
```http
POST /api/backtest/compare
```

**Request Body:**
```json
{
  "backtest_ids": ["uuid1", "uuid2", "uuid3"]
}
```

---

## 3. 실시간 데이터 API

### 3.1 실시간 가격 조회
```http
GET /api/market/price/{symbol}
```

**Response:**
```json
{
  "symbol": "005930",
  "name": "삼성전자",
  "current_price": 71500,
  "change": 500,
  "change_rate": 0.7,
  "volume": 15234567,
  "timestamp": "2024-01-01T10:30:00Z"
}
```

### 3.2 과거 데이터 조회
```http
GET /api/market/history/{symbol}?period=1y&interval=1d
```

**Response:**
```json
{
  "symbol": "005930",
  "data": [
    {
      "date": "2023-01-02",
      "open": 60000,
      "high": 61000,
      "low": 59500,
      "close": 60500,
      "volume": 20000000
    }
  ]
}
```

---

## 4. 매매 신호 API

### 4.1 신호 생성
```http
POST /api/signals/generate
```

**Request Body:**
```json
{
  "strategy_id": "uuid",
  "symbols": ["005930", "000660"],
  "mode": "realtime"
}
```

**Response:**
```json
{
  "signals": [
    {
      "symbol": "005930",
      "action": "buy",
      "strength": "strong",
      "confidence": 0.85,
      "reasons": [
        "RSI가 30 이하로 과매도 구간",
        "MACD 골든크로스 발생"
      ],
      "suggested_size": 0.1,
      "stop_loss": 69000,
      "take_profit": 75000
    }
  ]
}
```

### 4.2 신호 검증
```http
POST /api/signals/validate
```

**Request Body:**
```json
{
  "signals": [...],
  "risk_parameters": {
    "max_position_size": 0.2,
    "max_daily_trades": 5,
    "min_confidence": 0.7
  }
}
```

---

## 5. 포트폴리오 API

### 5.1 포트폴리오 조회
```http
GET /api/portfolio
```

**Response:**
```json
{
  "total_value": 15000000,
  "cash": 5000000,
  "positions": [
    {
      "symbol": "005930",
      "quantity": 100,
      "avg_price": 70000,
      "current_price": 71500,
      "profit": 150000,
      "profit_rate": 2.14
    }
  ],
  "performance": {
    "daily_return": 1.5,
    "total_return": 15.0,
    "realized_pnl": 500000,
    "unrealized_pnl": 150000
  }
}
```

### 5.2 포트폴리오 리밸런싱
```http
POST /api/portfolio/rebalance
```

**Request Body:**
```json
{
  "target_allocation": {
    "005930": 0.3,
    "000660": 0.3,
    "035720": 0.2,
    "cash": 0.2
  },
  "threshold": 0.05
}
```

---

## 6. 사용자 설정 API

### 6.1 API 키 등록
```http
POST /api/settings/api-keys
```

**Request Body:**
```json
{
  "provider": "kiwoom",
  "api_key": "encrypted_key",
  "api_secret": "encrypted_secret"
}
```

### 6.2 알림 설정
```http
PUT /api/settings/notifications
```

**Request Body:**
```json
{
  "email": true,
  "slack": true,
  "webhook_url": "https://hooks.slack.com/...",
  "triggers": {
    "trade_executed": true,
    "daily_report": true,
    "error_alert": true
  }
}
```

---

## 7. WebSocket API

### 7.1 실시간 가격 스트리밍
```javascript
const ws = new WebSocket('wss://api.kyyquant.com/ws/price');

ws.send(JSON.stringify({
  action: 'subscribe',
  symbols: ['005930', '000660']
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {
  //   "symbol": "005930",
  //   "price": 71500,
  //   "change": 500,
  //   "volume": 15234567,
  //   "timestamp": "2024-01-01T10:30:00Z"
  // }
};
```

### 7.2 매매 신호 스트리밍
```javascript
const ws = new WebSocket('wss://api.kyyquant.com/ws/signals');

ws.send(JSON.stringify({
  action: 'subscribe',
  strategy_id: 'uuid'
}));
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - 잘못된 요청 |
| 401 | Unauthorized - 인증 실패 |
| 403 | Forbidden - 권한 없음 |
| 404 | Not Found - 리소스 없음 |
| 429 | Too Many Requests - 요청 제한 초과 |
| 500 | Internal Server Error - 서버 오류 |

**Error Response Format:**
```json
{
  "error": {
    "code": "INVALID_STRATEGY",
    "message": "전략 설정이 올바르지 않습니다",
    "details": {
      "field": "buy_conditions",
      "reason": "최소 하나 이상의 매수 조건이 필요합니다"
    }
  }
}
```

---

## Rate Limiting

- 일반 API: 분당 60 요청
- 백테스팅 API: 분당 10 요청
- WebSocket: 초당 10 메시지

헤더에서 제한 정보 확인:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704067200
```

---

## Webhook Events

### 매매 실행 알림
```json
{
  "event": "trade_executed",
  "data": {
    "symbol": "005930",
    "action": "buy",
    "price": 71000,
    "quantity": 10,
    "timestamp": "2024-01-01T10:30:00Z"
  }
}
```

### 일일 리포트
```json
{
  "event": "daily_report",
  "data": {
    "date": "2024-01-01",
    "total_trades": 5,
    "profit": 150000,
    "return_rate": 1.5
  }
}
```

---

## SDK Examples

### Python
```python
from kyyquant import Client

client = Client(api_key="your_api_key")

# 전략 생성
strategy = client.strategies.create(
    name="My Strategy",
    indicators=["RSI", "MACD"],
    buy_conditions=[...],
    sell_conditions=[...]
)

# 백테스트 실행
backtest = client.backtest.run(
    strategy_id=strategy.id,
    symbols=["005930"],
    period=("2023-01-01", "2023-12-31")
)

print(f"Total Return: {backtest.total_return}%")
```

### JavaScript/TypeScript
```typescript
import { KYYQuantClient } from '@kyyquant/sdk';

const client = new KYYQuantClient({
  apiKey: 'your_api_key'
});

// 실시간 가격 구독
client.market.subscribe(['005930'], (data) => {
  console.log(`${data.symbol}: ${data.price}`);
});

// 신호 생성
const signals = await client.signals.generate({
  strategyId: 'uuid',
  symbols: ['005930']
});
```

---

## 문의 및 지원

- API 문의: api@kyyquant.com
- 기술 지원: support@kyyquant.com
- Discord: https://discord.gg/kyyquant
- GitHub Issues: https://github.com/khanyong/kyyquant-ai-solution/issues