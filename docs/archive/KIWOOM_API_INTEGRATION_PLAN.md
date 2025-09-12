# 키움증권 API 연동 실전 가이드

## 📋 키움증권 API 현황

### 키움 Open API+ 특징
- **Windows 전용**: OCX/COM 기반 (Windows에서만 작동)
- **실시간 데이터**: 실시간 시세, 체결, 호가 수신
- **모의투자**: 실전과 동일한 환경의 모의투자 서버
- **실전투자**: 실제 매매 가능

### 보유 API 키 상태
- ✅ **모의투자 API**: 즉시 사용 가능
- ✅ **실전투자 API**: 보유 (신중한 테스트 후 적용)

---

## 🏗️ 연동 아키텍처

### 전체 구조
```
┌─────────────────────────────────────────────────────┐
│              Vercel + Supabase (Cloud)               │
│  - 웹 인터페이스                                      │
│  - 전략 관리                                         │
│  - 백테스트 결과                                     │
│  - 사용자 인증                                       │
└─────────────────────────────────────────────────────┘
                         ↓ API
┌─────────────────────────────────────────────────────┐
│           NAS Docker Container (Linux)               │
│  ┌─────────────────────────────────────────┐       │
│  │     키움 API Bridge Server (FastAPI)     │       │
│  │  - REST API 엔드포인트                   │       │
│  │  - WebSocket 실시간 데이터               │       │
│  │  - 주문 큐 관리                         │       │
│  └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
                         ↓ TCP/IP
┌─────────────────────────────────────────────────────┐
│         Windows PC/VM (키움 API 실행 환경)           │
│  ┌─────────────────────────────────────────┐       │
│  │        키움 Open API+ (OCX)              │       │
│  │  - 모의투자 서버 연결                     │       │
│  │  - 실전투자 서버 연결                     │       │
│  │  - 실시간 데이터 수신                     │       │
│  └─────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────┐       │
│  │      Python 브릿지 (PyQt5 + PyKiwoom)    │       │
│  │  - API 래퍼                              │       │
│  │  - 이벤트 처리                           │       │
│  │  - NAS 서버와 통신                       │       │
│  └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

---

## 💻 Windows 환경 구성 (키움 API 실행)

### 1. 키움 API 설치
```python
# requirements_windows.txt
PyQt5==5.15.9
pykiwoom==0.1.29
pandas==1.5.3
numpy==1.24.3
websocket-client==1.5.1
requests==2.31.0
cryptography==41.0.0
```

### 2. 키움 API 래퍼 구현
```python
# kiwoom_bridge/kiwoom_wrapper.py
import sys
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
import json
import asyncio
import websocket
from cryptography.fernet import Fernet

class KiwoomAPI(QAxWidget):
    def __init__(self, mode="paper"):  # paper or real
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.mode = mode
        self.connected = False
        self.orders = {}
        self.positions = {}
        
        # 이벤트 연결
        self.OnEventConnect.connect(self.event_connect)
        self.OnReceiveTrData.connect(self.receive_tr_data)
        self.OnReceiveRealData.connect(self.receive_real_data)
        self.OnReceiveChejanData.connect(self.receive_chejan_data)
        self.OnReceiveMsg.connect(self.receive_msg)
        
        # NAS 서버 연결
        self.nas_url = "ws://NAS_IP:8080/kiwoom"
        self.ws = None
        
    def connect_api(self):
        """키움 API 연결"""
        if self.mode == "paper":
            # 모의투자 서버
            self.dynamicCall("SetLoginInfo(QString, QString)", "simulator", "1")
        
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()
        
    def event_connect(self, err_code):
        """로그인 이벤트"""
        if err_code == 0:
            print(f"키움 API 연결 성공 (모드: {self.mode})")
            self.connected = True
            self.get_account_info()
            self.connect_to_nas()
        else:
            print(f"키움 API 연결 실패: {err_code}")
            
        self.login_event_loop.exit()
    
    def connect_to_nas(self):
        """NAS 서버와 WebSocket 연결"""
        self.ws = websocket.WebSocketApp(
            self.nas_url,
            on_message=self.on_nas_message,
            on_error=self.on_nas_error,
            on_close=self.on_nas_close
        )
        
        # 별도 스레드에서 실행
        import threading
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
    
    def on_nas_message(self, ws, message):
        """NAS로부터 메시지 수신"""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "place_order":
                self.place_order(data)
            elif action == "cancel_order":
                self.cancel_order(data)
            elif action == "get_balance":
                self.get_balance()
            elif action == "get_positions":
                self.get_positions()
            elif action == "subscribe_real":
                self.subscribe_realtime(data)
                
        except Exception as e:
            print(f"메시지 처리 오류: {e}")
    
    def place_order(self, order_data):
        """주문 실행"""
        account = self.get_account_number()
        
        # 주문 파라미터
        order_type = 1 if order_data["side"] == "buy" else 2
        price_type = "00" if order_data["order_type"] == "market" else "03"
        
        result = self.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [
                "ORDER",                # sRQName
                "0101",                # 화면번호
                account,               # 계좌번호
                order_type,            # 주문구분 (1:매수, 2:매도)
                order_data["symbol"],  # 종목코드
                order_data["quantity"],# 수량
                order_data.get("price", 0),  # 가격
                price_type,            # 호가구분
                ""                     # 원주문번호 (정정/취소시)
            ]
        )
        
        # 결과를 NAS로 전송
        self.send_to_nas({
            "type": "order_result",
            "order_id": order_data["order_id"],
            "result": result,
            "status": "submitted" if result != "" else "failed"
        })
        
        return result
    
    def get_balance(self):
        """계좌 잔고 조회"""
        account = self.get_account_number()
        
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", account)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                        "잔고조회", "opw00018", 0, "0101")
    
    def get_positions(self):
        """보유 종목 조회"""
        account = self.get_account_number()
        
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", account)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                        "계좌평가잔고내역", "opw00018", 0, "0101")
    
    def subscribe_realtime(self, data):
        """실시간 데이터 구독"""
        codes = ";".join(data["symbols"])
        fids = "10;11;12;13;14;15"  # 현재가, 전일대비, 등락률, 거래량 등
        
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                        "0150", codes, fids, "0")
    
    def receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신"""
        if real_type == "주식체결":
            price = self.dynamicCall("GetCommRealData(QString, int)", code, 10)
            volume = self.dynamicCall("GetCommRealData(QString, int)", code, 15)
            
            # NAS로 실시간 데이터 전송
            self.send_to_nas({
                "type": "realtime_price",
                "symbol": code,
                "price": abs(int(price)),
                "volume": abs(int(volume)),
                "timestamp": time.time()
            })
    
    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결/잔고 데이터 수신"""
        if gubun == "0":  # 주문체결
            order_no = self.dynamicCall("GetChejanData(int)", 9203)
            symbol = self.dynamicCall("GetChejanData(int)", 9001)
            status = self.dynamicCall("GetChejanData(int)", 913)
            executed_qty = self.dynamicCall("GetChejanData(int)", 911)
            executed_price = self.dynamicCall("GetChejanData(int)", 910)
            
            self.send_to_nas({
                "type": "execution",
                "order_no": order_no,
                "symbol": symbol,
                "status": status,
                "executed_qty": abs(int(executed_qty)),
                "executed_price": abs(int(executed_price))
            })
    
    def send_to_nas(self, data):
        """NAS 서버로 데이터 전송"""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(data))
    
    def get_account_number(self):
        """계좌번호 조회"""
        accounts = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        return accounts.split(';')[0] if accounts else ""
```

### 3. Windows 서비스 실행
```python
# kiwoom_service.py
import sys
import time
from PyQt5.QtWidgets import QApplication
from kiwoom_wrapper import KiwoomAPI

def main():
    app = QApplication(sys.argv)
    
    # 모의투자로 시작
    kiwoom = KiwoomAPI(mode="paper")
    kiwoom.connect_api()
    
    # 메인 루프
    app.exec_()

if __name__ == "__main__":
    main()
```

---

## 🖥️ NAS 서버 구성 (Linux Docker)

### 1. FastAPI 서버
```python
# nas_server/main.py
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import Dict, List
from supabase import create_client
import os

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase 클라이언트
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"]
)

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.kiwoom_connections: Dict[str, WebSocket] = {}
        self.client_connections: Dict[str, WebSocket] = {}
    
    async def connect_kiwoom(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.kiwoom_connections[client_id] = websocket
    
    async def connect_client(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.client_connections[user_id] = websocket
    
    async def send_to_kiwoom(self, message: dict):
        for connection in self.kiwoom_connections.values():
            await connection.send_json(message)
    
    async def broadcast_to_clients(self, user_id: str, message: dict):
        if user_id in self.client_connections:
            await self.client_connections[user_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/kiwoom")
async def kiwoom_endpoint(websocket: WebSocket):
    """키움 API Windows 클라이언트 연결"""
    await manager.connect_kiwoom(websocket, "kiwoom_main")
    try:
        while True:
            data = await websocket.receive_json()
            await process_kiwoom_message(data)
    except Exception as e:
        print(f"키움 연결 오류: {e}")
    finally:
        del manager.kiwoom_connections["kiwoom_main"]

@app.websocket("/client/{user_id}")
async def client_endpoint(websocket: WebSocket, user_id: str):
    """웹 클라이언트 연결"""
    await manager.connect_client(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await process_client_message(user_id, data)
    except Exception as e:
        print(f"클라이언트 연결 오류: {e}")
    finally:
        del manager.client_connections[user_id]

async def process_kiwoom_message(data: dict):
    """키움에서 받은 메시지 처리"""
    msg_type = data.get("type")
    
    if msg_type == "order_result":
        # 주문 결과를 Supabase에 저장
        await save_order_result(data)
        
    elif msg_type == "execution":
        # 체결 정보 저장 및 클라이언트 알림
        await save_execution(data)
        
    elif msg_type == "realtime_price":
        # 실시간 가격 업데이트
        await update_realtime_price(data)
        
    elif msg_type == "balance":
        # 잔고 정보 업데이트
        await update_balance(data)

async def process_client_message(user_id: str, data: dict):
    """클라이언트에서 받은 메시지 처리"""
    action = data.get("action")
    
    # 사용자 권한 확인
    permission = await check_user_permission(user_id)
    
    if action == "place_order":
        if permission["can_trade"]:
            # 키움으로 주문 전송
            await manager.send_to_kiwoom({
                "action": "place_order",
                "user_id": user_id,
                **data["params"]
            })
    
    elif action == "get_positions":
        await manager.send_to_kiwoom({
            "action": "get_positions",
            "user_id": user_id
        })

@app.post("/api/orders")
async def create_order(order_data: dict):
    """REST API로 주문 생성"""
    # 권한 확인
    user_id = order_data["user_id"]
    permission = await check_user_permission(user_id)
    
    if not permission["can_trade"]:
        raise HTTPException(status_code=403, detail="거래 권한 없음")
    
    # Supabase에 주문 저장
    order = supabase.table("orders").insert({
        "user_id": user_id,
        "stock_code": order_data["symbol"],
        "order_type": order_data["side"],
        "quantity": order_data["quantity"],
        "price": order_data.get("price"),
        "status": "pending"
    }).execute()
    
    # 키움으로 주문 전송
    await manager.send_to_kiwoom({
        "action": "place_order",
        "order_id": order.data[0]["id"],
        **order_data
    })
    
    return {"success": True, "order_id": order.data[0]["id"]}

async def check_user_permission(user_id: str) -> dict:
    """사용자 거래 권한 확인"""
    result = supabase.table("trading_permissions").select("*").eq(
        "user_id", user_id
    ).single().execute()
    
    if result.data:
        return {
            "can_trade": result.data["can_real_trade"] or result.data["can_paper_trade"],
            "is_paper": result.data["can_paper_trade"] and not result.data["can_real_trade"]
        }
    
    return {"can_trade": False, "is_paper": True}

async def save_order_result(data: dict):
    """주문 결과 저장"""
    supabase.table("orders").update({
        "broker_order_id": data["result"],
        "status": data["status"]
    }).eq("id", data["order_id"]).execute()

async def save_execution(data: dict):
    """체결 정보 저장"""
    # 체결 내역 저장
    supabase.table("order_executions").insert({
        "broker_order_id": data["order_no"],
        "stock_code": data["symbol"],
        "executed_price": data["executed_price"],
        "executed_quantity": data["executed_qty"],
        "status": data["status"]
    }).execute()
    
    # 포트폴리오 업데이트
    await update_portfolio(data)

async def update_realtime_price(data: dict):
    """실시간 가격 업데이트"""
    supabase.table("real_time_prices").upsert({
        "stock_code": data["symbol"],
        "current_price": data["price"],
        "volume": data["volume"],
        "timestamp": data["timestamp"]
    }).execute()
```

### 2. Docker 구성
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  kiwoom-bridge:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    volumes:
      - ./logs:/app/logs
    restart: always
```

---

## 🎮 모의투자 → 실전투자 전환 프로세스

### 1. 단계별 전환 계획

#### Phase 1: 모의투자 (2주)
```python
# 1. 모의투자 계정 설정
kiwoom_config = {
    "mode": "paper",
    "server": "simulator",
    "risk_limit": {
        "max_order_amount": 10000000,  # 1천만원
        "max_position_count": 10,
        "max_loss_per_day": 500000     # 50만원
    }
}

# 2. 전략 테스트
strategies_to_test = [
    "momentum_strategy",
    "mean_reversion_strategy",
    "pairs_trading"
]

# 3. 성과 측정
performance_metrics = {
    "win_rate": 0,
    "sharpe_ratio": 0,
    "max_drawdown": 0,
    "total_trades": 0
}
```

#### Phase 2: 소액 실전 테스트 (2주)
```python
# 실전 전환 조건
transition_criteria = {
    "paper_trading_days": 30,
    "min_win_rate": 0.55,
    "min_sharpe_ratio": 1.0,
    "max_drawdown": -0.1,
    "min_trades": 100
}

# 소액 실전 설정
real_config = {
    "mode": "real",
    "initial_capital": 1000000,  # 100만원으로 시작
    "max_position_size": 100000,  # 종목당 10만원
    "daily_loss_limit": 50000     # 일일 손실한도 5만원
}
```

#### Phase 3: 점진적 확대 (4주)
```python
# 자금 증액 조건
scale_up_conditions = {
    "consecutive_profitable_days": 10,
    "total_return": 0.05,  # 5% 수익
    "max_drawdown": -0.03  # 3% 이내
}

# 단계별 자금 증액
capital_schedule = [
    {"week": 1, "amount": 1000000},
    {"week": 2, "amount": 2000000},
    {"week": 3, "amount": 5000000},
    {"week": 4, "amount": 10000000}
]
```

### 2. 안전장치 구현
```python
# risk_manager.py
class RiskManager:
    def __init__(self, mode="paper"):
        self.mode = mode
        self.daily_loss = 0
        self.daily_trades = 0
        
    def check_order(self, order):
        """주문 전 리스크 체크"""
        checks = {
            "daily_loss_limit": self.check_daily_loss(),
            "position_limit": self.check_position_limit(),
            "order_size": self.check_order_size(order),
            "market_hours": self.check_market_hours(),
            "circuit_breaker": self.check_circuit_breaker()
        }
        
        return all(checks.values()), checks
    
    def check_daily_loss(self):
        """일일 손실 한도 체크"""
        max_loss = -50000 if self.mode == "paper" else -100000
        return self.daily_loss > max_loss
    
    def emergency_stop(self):
        """긴급 정지"""
        # 모든 포지션 청산
        # 신규 주문 차단
        # 관리자 알림
        pass
```

---

## 🔒 보안 및 권한 관리

### 1. API 키 암호화
```python
# encryption.py
from cryptography.fernet import Fernet
import os

class APIKeyManager:
    def __init__(self):
        self.key = os.environ.get("ENCRYPTION_KEY")
        self.cipher = Fernet(self.key.encode())
    
    def encrypt_credentials(self, api_key, api_secret, account_no):
        """API 인증정보 암호화"""
        credentials = {
            "api_key": api_key,
            "api_secret": api_secret,
            "account_no": account_no
        }
        
        encrypted = self.cipher.encrypt(
            json.dumps(credentials).encode()
        )
        
        return encrypted.decode()
    
    def decrypt_credentials(self, encrypted_data):
        """API 인증정보 복호화"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())
```

### 2. 사용자 권한 레벨
```sql
-- Supabase 권한 테이블 업데이트
UPDATE trading_permissions SET
    permission_level = CASE
        WHEN user_id = 'admin_user_id' THEN 'admin'
        WHEN can_real_trade = true THEN 'real_trader'
        WHEN can_paper_trade = true THEN 'paper_trader'
        ELSE 'viewer'
    END;

-- 권한별 기능
-- viewer: 시세 조회만 가능
-- paper_trader: 모의투자 가능
-- real_trader: 실전투자 가능
-- admin: 모든 기능 + 사용자 관리
```

---

## 📊 모니터링 대시보드

### Frontend 컴포넌트
```typescript
// components/TradingDashboard.tsx
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export function TradingDashboard() {
  const [mode, setMode] = useState<'paper' | 'real'>('paper')
  const [positions, setPositions] = useState([])
  const [orders, setOrders] = useState([])
  const [balance, setBalance] = useState(null)
  
  useEffect(() => {
    // WebSocket 연결
    const ws = new WebSocket(`ws://NAS_IP:8080/client/${userId}`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch(data.type) {
        case 'execution':
          updateOrders(data)
          break
        case 'realtime_price':
          updatePrices(data)
          break
        case 'balance':
          setBalance(data)
          break
      }
    }
    
    // 실시간 구독
    const subscription = supabase
      .channel('trading_updates')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'orders',
        filter: `user_id=eq.${userId}`
      }, handleOrderUpdate)
      .subscribe()
    
    return () => {
      ws.close()
      subscription.unsubscribe()
    }
  }, [userId])
  
  const placeOrder = async (symbol: string, side: string, quantity: number) => {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userId,
        symbol,
        side,
        quantity,
        order_type: 'market',
        mode  // paper or real
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      toast.success(`주문 전송: ${symbol} ${side} ${quantity}주`)
    }
  }
  
  return (
    <div className="trading-dashboard">
      {/* 모드 전환 */}
      <div className="mode-selector">
        <Button 
          variant={mode === 'paper' ? 'contained' : 'outlined'}
          onClick={() => setMode('paper')}
        >
          모의투자
        </Button>
        <Button 
          variant={mode === 'real' ? 'contained' : 'outlined'}
          onClick={() => setMode('real')}
          color="error"
        >
          실전투자
        </Button>
      </div>
      
      {/* 계좌 정보 */}
      <AccountSummary balance={balance} mode={mode} />
      
      {/* 포지션 */}
      <PositionList positions={positions} />
      
      {/* 주문 내역 */}
      <OrderList orders={orders} />
      
      {/* 주문 패널 */}
      <OrderPanel onOrder={placeOrder} mode={mode} />
    </div>
  )
}
```

---

## 🚀 실행 계획

### Week 1: 환경 구축
- [ ] Windows PC/VM 준비
- [ ] 키움 Open API+ 설치
- [ ] 모의투자 계정 설정
- [ ] Python 브릿지 개발

### Week 2: NAS 서버 구축
- [ ] Docker 컨테이너 설정
- [ ] FastAPI 서버 개발
- [ ] WebSocket 통신 구현
- [ ] Supabase 연동

### Week 3: 모의투자 테스트
- [ ] 전략 실행 테스트
- [ ] 주문 체결 확인
- [ ] 실시간 데이터 수신
- [ ] 성과 측정

### Week 4: 실전 전환 준비
- [ ] 리스크 관리 시스템
- [ ] 긴급 정지 기능
- [ ] 모니터링 대시보드
- [ ] 소액 실전 테스트

### Week 5-6: 안정화
- [ ] 버그 수정
- [ ] 성능 최적화
- [ ] 백업 시스템
- [ ] 운영 매뉴얼

---

## ✅ 체크리스트

### 모의투자 시작 전
- [ ] 키움 API 정상 연결
- [ ] 모의투자 계정 로그인
- [ ] NAS 서버 통신 확인
- [ ] Supabase 데이터 저장 확인

### 실전투자 전환 전
- [ ] 30일 이상 모의투자 운영
- [ ] 승률 55% 이상 달성
- [ ] 최대 낙폭 10% 이내
- [ ] 100건 이상 거래 완료
- [ ] 리스크 관리 시스템 검증
- [ ] 긴급 정지 테스트 완료

이 구조로 키움증권 API를 활용한 안전한 모의투자 → 실전투자 시스템을 구축할 수 있습니다.