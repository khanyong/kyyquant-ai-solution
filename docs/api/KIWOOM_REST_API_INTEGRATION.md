# 🚀 키움증권 REST API 실전 매매 시스템 통합 계획

## 📋 프로젝트 개요

현재 React/TypeScript 백테스트 시스템에 키움증권 REST API를 통한 실전 매매 기능을 추가합니다.

### 현재 시스템 구조
- **Frontend**: React + TypeScript + MUI
- **Backend**: FastAPI (백테스트용)
- **Database**: Supabase
- **배포**: Vercel (Frontend)

### 추가될 기능
- 키움증권 REST API 연동
- 시놀로지 NAS 기반 자동매매
- N8N 워크플로우 자동화
- 실시간 시세/매매 연동

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                   사용자 인터페이스                     │
│            React Frontend (Vercel)                  │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│                    Supabase                        │
│         (Database + Authentication + API)          │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│               시놀로지 NAS (24/7)                    │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐             │
│  │     N8N      │───▶│  Trading API  │             │
│  │  Workflows   │    │   (FastAPI)   │             │
│  └──────────────┘    └──────────────┘             │
│         ↓                    ↓                     │
│  ┌──────────────────────────────────┐             │
│  │    키움 REST API Bridge           │             │
│  └──────────────────────────────────┘             │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│              키움증권 REST API 서버                   │
│          https://api.kiwoom.com                    │
└─────────────────────────────────────────────────────┘
```

## 📁 프로젝트 구조 확장

```
auto_stock/
├── src/                          # 기존 Frontend
│   ├── components/
│   │   ├── trading/             # 🆕 실전 매매 컴포넌트
│   │   │   ├── LiveTrading.tsx
│   │   │   ├── OrderPanel.tsx
│   │   │   ├── PositionMonitor.tsx
│   │   │   └── AccountInfo.tsx
│   │   └── ...
│   ├── services/
│   │   ├── kiwoomApi.ts        # 🆕 키움 API 클라이언트
│   │   └── ...
│   └── types/
│       ├── trading.ts           # 🆕 매매 관련 타입
│       └── ...
│
├── backend/                      # 기존 백테스트 서버
│   └── ...
│
├── trading-server/              # 🆕 실전 매매 서버
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── kiwoom/
│   │   ├── __init__.py
│   │   ├── api_client.py       # 키움 REST API 클라이언트
│   │   ├── auth.py             # OAuth 인증
│   │   └── models.py           # 데이터 모델
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── executor.py         # 전략 실행 엔진
│   └── n8n/
│       ├── webhooks.py         # N8N 웹훅 처리
│       └── workflows.json      # N8N 워크플로우 템플릿
│
└── deployment/                  # 🆕 배포 설정
    ├── docker-compose.yml       # NAS Docker 설정
    ├── n8n/
    │   └── workflows/
    └── nginx/
        └── nginx.conf
```

## 🔧 키움 REST API 통합 구현

### 1. 키움 API 클라이언트 (`trading-server/kiwoom/api_client.py`)

```python
import aiohttp
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime

class KiwoomRestAPI:
    """키움증권 REST API 클라이언트"""
    
    def __init__(self):
        self.base_url = "https://api.kiwoom.com"
        self.mock_url = "https://mockapi.kiwoom.com"  # 모의투자
        self.access_token = None
        self.token_expires = None
        
    async def authenticate(self, app_key: str, secret_key: str) -> str:
        """OAuth 2.0 인증"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/oauth2/token"
            
            # Client credentials grant
            data = {
                "grant_type": "client_credentials",
                "client_id": app_key,
                "client_secret": secret_key
            }
            
            async with session.post(url, data=data) as resp:
                result = await resp.json()
                self.access_token = result["access_token"]
                self.token_expires = datetime.now().timestamp() + result["expires_in"]
                return self.access_token
    
    async def get_current_price(self, stock_code: str) -> Dict[str, Any]:
        """현재가 조회"""
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/stock/price"
            params = {"stock_code": stock_code}
            
            async with session.get(url, headers=headers, params=params) as resp:
                return await resp.json()
    
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 실행"""
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/trading/order"
            
            async with session.post(url, headers=headers, json=order_data) as resp:
                return await resp.json()
    
    async def get_balance(self, account_no: str) -> Dict[str, Any]:
        """계좌 잔고 조회"""
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/account/balance"
            params = {"account_no": account_no}
            
            async with session.get(url, headers=headers, params=params) as resp:
                return await resp.json()
    
    async def get_positions(self, account_no: str) -> Dict[str, Any]:
        """보유 종목 조회"""
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/account/positions"
            params = {"account_no": account_no}
            
            async with session.get(url, headers=headers, params=params) as resp:
                return await resp.json()
    
    async def subscribe_realtime(self, stock_codes: list, callback):
        """실시간 시세 구독 (WebSocket)"""
        ws_url = self.base_url.replace("https", "wss") + "/realtime"
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 인증
                await ws.send_json({
                    "type": "auth",
                    "token": self.access_token
                })
                
                # 종목 구독
                await ws.send_json({
                    "type": "subscribe",
                    "stocks": stock_codes
                })
                
                # 실시간 데이터 수신
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await callback(data)
    
    def _get_headers(self) -> Dict[str, str]:
        """API 헤더 생성"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
```

### 2. FastAPI 매매 서버 (`trading-server/main.py`)

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from kiwoom.api_client import KiwoomRestAPI
from strategies.executor import StrategyExecutor
from supabase import create_client, Client

app = FastAPI(title="키움 실전 매매 서버")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
kiwoom_api = KiwoomRestAPI()
strategy_executor = StrategyExecutor()
supabase: Client = None

class OrderRequest(BaseModel):
    user_id: str
    stock_code: str
    order_type: str  # buy, sell
    quantity: int
    price_type: str  # market, limit
    price: Optional[float] = None

class StrategyStart(BaseModel):
    user_id: str
    strategy_id: str
    account_no: str
    investment_amount: float

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    global supabase
    
    # Supabase 연결
    supabase = create_client(
        "YOUR_SUPABASE_URL",
        "YOUR_SUPABASE_KEY"
    )
    
    # 키움 API 인증
    await kiwoom_api.authenticate(
        app_key="YOUR_APP_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    
    print("✅ 키움 매매 서버 시작")

@app.get("/")
async def root():
    return {"message": "키움증권 실전 매매 서버", "status": "running"}

@app.get("/api/market/price/{stock_code}")
async def get_price(stock_code: str):
    """현재가 조회"""
    try:
        price_data = await kiwoom_api.get_current_price(stock_code)
        return price_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trading/order")
async def place_order(order: OrderRequest):
    """주문 실행"""
    try:
        # 사용자 인증 확인
        user = supabase.table("users").select("*").eq("id", order.user_id).single().execute()
        if not user.data:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # 키움 API로 주문 전송
        order_data = {
            "account_no": user.data["kiwoom_account"],
            "stock_code": order.stock_code,
            "order_type": order.order_type,
            "quantity": order.quantity,
            "price_type": order.price_type,
            "price": order.price
        }
        
        result = await kiwoom_api.place_order(order_data)
        
        # 주문 기록 저장
        supabase.table("orders").insert({
            "user_id": order.user_id,
            "stock_code": order.stock_code,
            "order_type": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "status": "submitted",
            "order_id": result["order_id"],
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account/balance/{user_id}")
async def get_balance(user_id: str):
    """계좌 잔고 조회"""
    try:
        # 사용자 계좌 정보 조회
        user = supabase.table("users").select("kiwoom_account").eq("id", user_id).single().execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        balance = await kiwoom_api.get_balance(user.data["kiwoom_account"])
        return balance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account/positions/{user_id}")
async def get_positions(user_id: str):
    """보유 종목 조회"""
    try:
        user = supabase.table("users").select("kiwoom_account").eq("id", user_id).single().execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        positions = await kiwoom_api.get_positions(user.data["kiwoom_account"])
        return positions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategy/start")
async def start_strategy(strategy: StrategyStart, background_tasks: BackgroundTasks):
    """전략 실행 시작"""
    try:
        # 전략 정보 조회
        strategy_data = supabase.table("strategies").select("*").eq("id", strategy.strategy_id).single().execute()
        if not strategy_data.data:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # 백그라운드에서 전략 실행
        background_tasks.add_task(
            strategy_executor.run_strategy,
            user_id=strategy.user_id,
            strategy_config=strategy_data.data,
            account_no=strategy.account_no,
            investment_amount=strategy.investment_amount
        )
        
        return {"message": "전략 실행 시작", "strategy_id": strategy.strategy_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategy/stop/{strategy_id}")
async def stop_strategy(strategy_id: str):
    """전략 실행 중지"""
    try:
        await strategy_executor.stop_strategy(strategy_id)
        return {"message": "전략 실행 중지", "strategy_id": strategy_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/realtime/{stock_codes}")
async def websocket_endpoint(websocket, stock_codes: str):
    """실시간 시세 WebSocket"""
    await websocket.accept()
    
    stocks = stock_codes.split(",")
    
    async def send_price(data):
        await websocket.send_json(data)
    
    try:
        await kiwoom_api.subscribe_realtime(stocks, send_price)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 3. N8N 워크플로우 설정

```json
{
  "name": "키움 자동매매 워크플로우",
  "nodes": [
    {
      "id": "1",
      "type": "n8n-nodes-base.cron",
      "name": "매일 09:00 시작",
      "parameters": {
        "cronExpression": "0 9 * * 1-5"
      }
    },
    {
      "id": "2",
      "type": "n8n-nodes-base.httpRequest",
      "name": "전략 목록 조회",
      "parameters": {
        "url": "http://trading-api:8001/api/strategies/active",
        "method": "GET"
      }
    },
    {
      "id": "3",
      "type": "n8n-nodes-base.function",
      "name": "전략 필터링",
      "parameters": {
        "code": "return items.filter(item => item.json.enabled === true);"
      }
    },
    {
      "id": "4",
      "type": "n8n-nodes-base.httpRequest",
      "name": "전략 실행",
      "parameters": {
        "url": "http://trading-api:8001/api/strategy/start",
        "method": "POST",
        "body": "={{ $json }}"
      }
    },
    {
      "id": "5",
      "type": "n8n-nodes-base.webhook",
      "name": "거래 신호 수신",
      "parameters": {
        "path": "trading-signal",
        "method": "POST"
      }
    },
    {
      "id": "6",
      "type": "n8n-nodes-base.httpRequest",
      "name": "주문 실행",
      "parameters": {
        "url": "http://trading-api:8001/api/trading/order",
        "method": "POST"
      }
    }
  ]
}
```

### 4. Docker Compose 설정 (`deployment/docker-compose.yml`)

```yaml
version: '3.8'

services:
  # N8N 워크플로우 엔진
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-trading
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://your-nas-ip:5678/
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - ./n8n/data:/home/node/.n8n
      - ./n8n/files:/files
    restart: unless-stopped
    networks:
      - trading-network

  # 키움 매매 API 서버
  trading-api:
    build: ../trading-server
    container_name: trading-api
    ports:
      - "8001:8001"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - KIWOOM_APP_KEY=${KIWOOM_APP_KEY}
      - KIWOOM_SECRET_KEY=${KIWOOM_SECRET_KEY}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - trading-network

  # Redis (캐싱 및 큐)
  redis:
    image: redis:7-alpine
    container_name: trading-redis
    ports:
      - "6379:6379"
    volumes:
      - ./redis/data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - trading-network

  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    container_name: trading-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - trading-api
      - n8n
    restart: unless-stopped
    networks:
      - trading-network

networks:
  trading-network:
    driver: bridge

volumes:
  n8n-data:
  redis-data:
```

### 5. Frontend 통합 (`src/components/trading/LiveTrading.tsx`)

```typescript
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { useTradingApi } from '../../hooks/useTradingApi';
import { Position, Order, Balance } from '../../types/trading';

export const LiveTrading: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [orderForm, setOrderForm] = useState({
    stockCode: '',
    orderType: 'buy',
    quantity: 0,
    priceType: 'market',
    price: 0
  });
  
  const { 
    fetchPositions, 
    fetchBalance, 
    placeOrder,
    subscribeRealtime 
  } = useTradingApi();

  useEffect(() => {
    // 초기 데이터 로드
    loadAccountData();
    
    // 실시간 데이터 구독
    const unsubscribe = subscribeRealtime(['005930', '000660'], (data) => {
      console.log('실시간 데이터:', data);
      // 실시간 가격 업데이트 처리
    });
    
    return () => unsubscribe();
  }, []);

  const loadAccountData = async () => {
    try {
      const [posData, balData] = await Promise.all([
        fetchPositions(),
        fetchBalance()
      ]);
      setPositions(posData);
      setBalance(balData);
    } catch (error) {
      console.error('계좌 데이터 로드 실패:', error);
    }
  };

  const handleOrder = async () => {
    try {
      const result = await placeOrder(orderForm);
      if (result.success) {
        alert('주문이 성공적으로 접수되었습니다.');
        loadAccountData(); // 데이터 새로고침
      }
    } catch (error) {
      alert('주문 실패: ' + error.message);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        실전 매매
      </Typography>

      <Grid container spacing={3}>
        {/* 계좌 정보 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                계좌 정보
              </Typography>
              {balance && (
                <>
                  <Typography>
                    예수금: {balance.cash.toLocaleString()}원
                  </Typography>
                  <Typography>
                    평가금액: {balance.totalValue.toLocaleString()}원
                  </Typography>
                  <Typography>
                    손익: {balance.profit.toLocaleString()}원
                    <Chip 
                      label={`${balance.profitRate}%`}
                      color={balance.profit > 0 ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 주문 패널 */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                주문
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="종목코드"
                    value={orderForm.stockCode}
                    onChange={(e) => setOrderForm({
                      ...orderForm,
                      stockCode: e.target.value
                    })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Select
                    fullWidth
                    value={orderForm.orderType}
                    onChange={(e) => setOrderForm({
                      ...orderForm,
                      orderType: e.target.value
                    })}
                  >
                    <MenuItem value="buy">매수</MenuItem>
                    <MenuItem value="sell">매도</MenuItem>
                  </Select>
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="수량"
                    value={orderForm.quantity}
                    onChange={(e) => setOrderForm({
                      ...orderForm,
                      quantity: parseInt(e.target.value)
                    })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Select
                    fullWidth
                    value={orderForm.priceType}
                    onChange={(e) => setOrderForm({
                      ...orderForm,
                      priceType: e.target.value
                    })}
                  >
                    <MenuItem value="market">시장가</MenuItem>
                    <MenuItem value="limit">지정가</MenuItem>
                  </Select>
                </Grid>
                {orderForm.priceType === 'limit' && (
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="number"
                      label="지정가격"
                      value={orderForm.price}
                      onChange={(e) => setOrderForm({
                        ...orderForm,
                        price: parseFloat(e.target.value)
                      })}
                    />
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color={orderForm.orderType === 'buy' ? 'error' : 'primary'}
                    onClick={handleOrder}
                    fullWidth
                  >
                    {orderForm.orderType === 'buy' ? '매수' : '매도'} 주문
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* 보유 종목 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                보유 종목
              </Typography>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>종목명</TableCell>
                    <TableCell>보유수량</TableCell>
                    <TableCell>평균단가</TableCell>
                    <TableCell>현재가</TableCell>
                    <TableCell>평가금액</TableCell>
                    <TableCell>손익</TableCell>
                    <TableCell>수익률</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {positions.map((position) => (
                    <TableRow key={position.stockCode}>
                      <TableCell>{position.stockName}</TableCell>
                      <TableCell>{position.quantity}</TableCell>
                      <TableCell>{position.avgPrice.toLocaleString()}</TableCell>
                      <TableCell>{position.currentPrice.toLocaleString()}</TableCell>
                      <TableCell>{position.evalAmount.toLocaleString()}</TableCell>
                      <TableCell>
                        <Typography 
                          color={position.profit > 0 ? 'success.main' : 'error.main'}
                        >
                          {position.profit.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${position.profitRate.toFixed(2)}%`}
                          color={position.profitRate > 0 ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
```

## 📝 구현 로드맵

### Phase 1: 기초 설정 (1주)
- [ ] 키움 REST API 앱 등록 및 인증 키 발급
- [ ] 시놀로지 NAS Docker 환경 구성
- [ ] Supabase 테이블 스키마 확장 (users, orders, positions)

### Phase 2: 백엔드 구현 (2주)
- [ ] 키움 REST API 클라이언트 개발
- [ ] FastAPI 매매 서버 구현
- [ ] 전략 실행 엔진 개발
- [ ] WebSocket 실시간 시세 연동

### Phase 3: Frontend 통합 (1주)
- [ ] 실전 매매 컴포넌트 개발
- [ ] 계좌 정보 표시 UI
- [ ] 주문 인터페이스 구현
- [ ] 실시간 시세 업데이트

### Phase 4: N8N 워크플로우 (1주)
- [ ] 자동매매 워크플로우 설계
- [ ] 조건부 매매 로직 구현
- [ ] 알림 시스템 연동
- [ ] 백테스트-실전 연계

### Phase 5: 테스트 및 최적화 (1주)
- [ ] 모의투자 환경 테스트
- [ ] 성능 최적화
- [ ] 에러 처리 강화
- [ ] 보안 점검

## 🔒 보안 고려사항

1. **API 키 관리**
   - 환경 변수로 관리
   - Supabase Vault 활용
   - 키 로테이션 정책

2. **접근 제어**
   - JWT 기반 인증
   - IP 화이트리스트
   - Rate limiting

3. **데이터 보호**
   - HTTPS 통신
   - 민감 정보 암호화
   - 로그 마스킹

## 📊 모니터링

1. **시스템 모니터링**
   - Prometheus + Grafana
   - 서버 상태 체크
   - API 응답 시간

2. **거래 모니터링**
   - 실시간 손익 추적
   - 이상 거래 감지
   - 일일 리포트

## 🚀 배포 프로세스

```bash
# 1. NAS에 Docker 설치 (Container Manager)

# 2. Git 클론
git clone https://github.com/your-repo/auto_stock.git
cd auto_stock

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 4. Docker Compose 실행
cd deployment
docker-compose up -d

# 5. N8N 워크플로우 임포트
# N8N UI에서 워크플로우 JSON 임포트

# 6. 시스템 확인
docker-compose ps
curl http://localhost:8001/
```

## 📚 참고 자료

- [키움 REST API 문서](https://openapi.kiwoom.com/guide/apiguide)
- [N8N 문서](https://docs.n8n.io/)
- [시놀로지 Docker 가이드](https://www.synology.com/ko-kr/dsm/packages/Docker)
- [Supabase 문서](https://supabase.com/docs)

## ⚠️ 주의사항

1. **실전 거래 전 충분한 테스트**
   - 모의투자로 최소 1개월 테스트
   - 소액으로 시작
   - 손절 로직 필수

2. **시스템 안정성**
   - UPS 전원 보호
   - 자동 재시작 설정
   - 백업 시스템 구축

3. **법적 준수사항**
   - 알고리즘 거래 신고
   - 시장 조작 금지
   - 개인정보 보호