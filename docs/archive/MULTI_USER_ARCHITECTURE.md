# 🏢 10명 이내 다중 사용자 자동매매 시스템 아키텍처

## ✅ 시스템 요구사항
- **동시 사용자**: 최대 10명
- **사용자별 독립 계좌**: 각자의 키움/한투 계좌
- **개별 전략 실행**: 사용자당 1-5개 전략
- **실시간 시세 공유**: 모든 사용자 동일 데이터

## 🎯 10명 규모에 최적화된 구조

### 1️⃣ 단일 Windows 서버 + 세션 관리 방식 (권장)

```yaml
장점:
  - 비용 효율적 (Windows 서버 1대)
  - 관리 단순
  - 10명 규모에 충분한 성능
  
구현 방식:
  - 사용자 요청 큐잉 시스템
  - 30초 단위 세션 로테이션
  - 우선순위 기반 처리
```

### 📐 시스템 아키텍처

```
┌────────────────────────────────────────────────┐
│              10명의 사용자                       │
│   User1  User2  User3 ... User9  User10        │
│     ↓      ↓      ↓        ↓      ↓           │
└────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────┐
│         Vercel + Supabase (Cloud)              │
│                                                │
│  ✅ 사용자 인증 (Supabase Auth)                 │
│  ✅ 전략 저장 (strategies 테이블)               │
│  ✅ 주문 기록 (orders 테이블)                   │
│  ✅ 포트폴리오 (portfolio 테이블)               │
│  ✅ API 키 관리 (user_api_credentials)         │
│                                                │
│  [RLS로 사용자별 데이터 완전 격리]               │
└────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────┐
│         NAS Docker Container                   │
│         (세션 매니저 & 큐 시스템)                │
│                                                │
│  class SessionManager:                         │
│    - 10개 사용자 세션 풀 관리                    │
│    - 30초 단위 로테이션                         │
│    - 우선순위 큐 (VIP > 일반)                   │
│    - 긴급 주문 우선 처리                        │
│                                                │
│  class OrderQueue:                             │
│    - FIFO 주문 처리                            │
│    - 사용자별 일일 한도 체크                     │
│    - 동시 주문 수 제한 (10건/초)                │
└────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────┐
│      Windows Server (키움 API 실행)             │
│                                                │
│  KiwoomAPIPool:                                │
│    - 동적 로그인/로그아웃                       │
│    - 계정 전환 (3초 소요)                       │
│    - 실시간 시세는 공유                         │
│    - 주문은 순차 처리                           │
│                                                │
│  처리 능력:                                     │
│    - 분당 20개 주문 처리                        │
│    - 10명 기준 사용자당 2개 주문/분              │
│    - 실시간 시세 100종목 동시 구독              │
└────────────────────────────────────────────────┘
```

## 💻 구현 코드

### 1. 세션 매니저 (Python)

```python
# nas_server/session_manager.py
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import queue
from dataclasses import dataclass

@dataclass
class UserSession:
    user_id: str
    api_key: str
    api_secret: str
    account_no: str
    priority: int  # 0=일반, 1=VIP
    last_active: datetime
    daily_trades: int
    daily_limit: int = 100

class MultiUserSessionManager:
    def __init__(self, max_users=10):
        self.max_users = max_users
        self.sessions: Dict[str, UserSession] = {}
        self.active_session: Optional[str] = None
        self.order_queue = queue.PriorityQueue()
        self.kiwoom_api = None
        self.rotation_interval = 30  # 30초마다 세션 교체
        
    async def add_user(self, user_id: str, credentials: dict, priority=0):
        """사용자 세션 추가"""
        if len(self.sessions) >= self.max_users:
            raise Exception(f"최대 사용자 수({self.max_users}명) 초과")
        
        self.sessions[user_id] = UserSession(
            user_id=user_id,
            api_key=credentials['api_key'],
            api_secret=credentials['api_secret'],
            account_no=credentials['account_no'],
            priority=priority,
            last_active=datetime.now(),
            daily_trades=0
        )
        
    async def get_next_session(self) -> Optional[UserSession]:
        """우선순위 기반 다음 세션 선택"""
        # VIP 사용자 우선
        vip_users = [s for s in self.sessions.values() 
                     if s.priority == 1 and s.daily_trades < s.daily_limit]
        if vip_users:
            return min(vip_users, key=lambda x: x.last_active)
        
        # 일반 사용자
        normal_users = [s for s in self.sessions.values() 
                        if s.priority == 0 and s.daily_trades < s.daily_limit]
        if normal_users:
            return min(normal_users, key=lambda x: x.last_active)
        
        return None
    
    async def switch_session(self, user_id: str):
        """키움 API 세션 전환"""
        if self.active_session == user_id:
            return True
        
        session = self.sessions.get(user_id)
        if not session:
            return False
        
        # 현재 세션 로그아웃
        if self.active_session:
            await self.kiwoom_logout()
        
        # 새 세션 로그인 (3초 소요)
        success = await self.kiwoom_login(
            session.api_key,
            session.api_secret,
            session.account_no
        )
        
        if success:
            self.active_session = user_id
            session.last_active = datetime.now()
        
        return success
    
    async def process_order_queue(self):
        """주문 큐 처리 (무한 루프)"""
        while True:
            try:
                # 큐에서 주문 가져오기
                priority, timestamp, order = await asyncio.get_event_loop().run_in_executor(
                    None, self.order_queue.get, True, 1
                )
                
                # 세션 전환
                await self.switch_session(order['user_id'])
                
                # 주문 실행
                result = await self.execute_order(order)
                
                # 일일 거래 카운트 증가
                session = self.sessions[order['user_id']]
                session.daily_trades += 1
                
                # 결과 저장
                await self.save_order_result(order['user_id'], result)
                
            except queue.Empty:
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"주문 처리 오류: {e}")
    
    async def add_order(self, user_id: str, order: dict):
        """주문 큐에 추가"""
        session = self.sessions.get(user_id)
        if not session:
            raise Exception("등록되지 않은 사용자")
        
        if session.daily_trades >= session.daily_limit:
            raise Exception("일일 거래 한도 초과")
        
        # 우선순위 큐에 추가 (VIP 우선)
        priority = 0 if session.priority == 1 else 1
        self.order_queue.put((priority, datetime.now(), {
            'user_id': user_id,
            **order
        }))
    
    async def get_shared_market_data(self):
        """모든 사용자가 공유하는 실시간 시세"""
        # 한 번의 API 호출로 모든 사용자에게 브로드캐스트
        return self.kiwoom_api.get_realtime_prices()
```

### 2. FastAPI 서버 엔드포인트

```python
# nas_server/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()
session_manager = MultiUserSessionManager(max_users=10)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """서버 시작시 세션 매니저 초기화"""
    # 주문 큐 처리 시작
    asyncio.create_task(session_manager.process_order_queue())
    
    # Supabase에서 활성 사용자 로드
    users = await load_active_users()
    for user in users[:10]:  # 최대 10명
        await session_manager.add_user(
            user['id'],
            user['credentials'],
            user['priority']
        )

@app.post("/api/orders")
async def create_order(order_data: dict, user_id: str = Depends(get_current_user)):
    """주문 생성 API"""
    try:
        # 주문 검증
        if not validate_order(order_data):
            raise HTTPException(400, "잘못된 주문")
        
        # 큐에 추가
        await session_manager.add_order(user_id, order_data)
        
        return {"status": "queued", "message": "주문이 대기열에 추가되었습니다"}
        
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/api/queue-status")
async def get_queue_status(user_id: str = Depends(get_current_user)):
    """사용자별 큐 상태 조회"""
    session = session_manager.sessions.get(user_id)
    if not session:
        raise HTTPException(404, "세션을 찾을 수 없습니다")
    
    return {
        "daily_trades": session.daily_trades,
        "daily_limit": session.daily_limit,
        "remaining": session.daily_limit - session.daily_trades,
        "queue_size": session_manager.order_queue.qsize(),
        "is_active": session_manager.active_session == user_id
    }

@app.websocket("/ws/market-data")
async def market_data_websocket(websocket: WebSocket):
    """실시간 시세 WebSocket (모든 사용자 공유)"""
    await websocket.accept()
    
    try:
        while True:
            # 모든 사용자가 동일한 시세 데이터 수신
            market_data = await session_manager.get_shared_market_data()
            await websocket.send_json(market_data)
            await asyncio.sleep(1)  # 1초마다 업데이트
            
    except Exception as e:
        print(f"WebSocket 오류: {e}")
    finally:
        await websocket.close()
```

### 3. 사용자별 제한 설정

```python
# config/user_limits.py

USER_LIMITS = {
    "free": {
        "daily_trades": 10,
        "max_strategies": 1,
        "max_positions": 5,
        "priority": 0
    },
    "basic": {
        "daily_trades": 50,
        "max_strategies": 3,
        "max_positions": 10,
        "priority": 0
    },
    "premium": {
        "daily_trades": 100,
        "max_strategies": 5,
        "max_positions": 20,
        "priority": 1  # VIP 우선순위
    }
}

# 동시성 제어
CONCURRENCY_LIMITS = {
    "max_concurrent_users": 10,
    "orders_per_second": 10,
    "api_calls_per_minute": 600,
    "session_timeout_seconds": 300,
    "rotation_interval_seconds": 30
}
```

## 📊 10명 사용자 처리 능력

### 예상 처리량
```yaml
실시간 시세:
  - 100종목 동시 구독
  - 1초 단위 업데이트
  - 모든 사용자 공유

주문 처리:
  - 분당 20개 주문
  - 사용자당 2개/분
  - 일일 최대 1,000개

세션 관리:
  - 30초 로테이션
  - 3초 전환 시간
  - 27초 활성 시간

일일 한도:
  - Free: 10 거래
  - Basic: 50 거래  
  - Premium: 100 거래
```

### 성능 최적화
```python
# 1. 실시간 시세는 공유
market_data = cache.get_shared_data()

# 2. 주문은 배치 처리
batch_orders = queue.get_batch(max=5)

# 3. 세션 사전 로드
preload_next_session()

# 4. 캐싱 활용
redis_cache.set(key, value, ttl=60)
```

## 🔒 보안 및 격리

```yaml
데이터 격리:
  - Supabase RLS 정책
  - user_id 기반 필터링
  - API 키 암호화

리소스 격리:
  - 일일 거래 한도
  - API 호출 제한
  - 동시 전략 수 제한

세션 보안:
  - JWT 토큰 인증
  - IP 화이트리스트
  - 2FA (선택)
```

## 💰 예상 비용 (10명 기준)

```yaml
인프라:
  - Windows Server: 월 10만원
  - NAS/Docker: 보유
  - Supabase Pro: 월 $25
  - Vercel Pro: 월 $20

총 월 비용: 약 15만원
사용자당: 월 1.5만원
```

## ✅ 결론

**10명 규모에서는 단일 Windows 서버 + 세션 관리 방식이 최적**
- 비용 효율적 (월 15만원)
- 충분한 성능 (사용자당 2주문/분)
- 간단한 관리
- 확장 가능 (20명까지 동일 구조)

이 구조로 10명의 사용자가 각자의 계좌로 동시에 자동매매를 수행할 수 있습니다.