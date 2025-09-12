# 시놀로지 NAS 기반 다중 사용자 투자 플랫폼 마이그레이션 로드맵

## 📋 프로젝트 개요

### 현재 상태
- **환경**: Windows 로컬 환경
- **사용자**: 단일 사용자
- **기능**: 백테스트 전용
- **API**: Kiwoom OpenAPI (Windows COM 기반)

### 목표 상태
- **환경**: Synology NAS + Docker
- **사용자**: 다중 사용자 (Multi-tenant)
- **기능**: 모의투자 + 실전투자
- **API**: REST API 기반

---

## 🏗️ 시스템 아키텍처

### 1. 전체 아키텍처
```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │   Web    │  │  Mobile  │  │   API    │          │
│  │  (React) │  │   App    │  │  Client  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              API Gateway (Kong/Nginx)                │
│         - Rate Limiting                              │
│         - Authentication                             │
│         - Load Balancing                             │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│           Microservices Layer (Docker)               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Auth API   │  │  Trading API │  │ Market    │ │
│  │  (FastAPI)   │  │   (FastAPI)  │  │ Data API  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Backtest API │  │ Strategy API │  │ Alert API │ │
│  │  (FastAPI)   │  │   (FastAPI)  │  │(FastAPI)  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Message Queue (Redis/RabbitMQ)          │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│           Background Workers (Celery)                │
│  - Order Execution                                   │
│  - Market Data Collection                            │
│  - Strategy Execution                                │
│  - Notification Service                              │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ PostgreSQL   │  │   TimescaleDB │  │   Redis   │ │
│  │ (User Data)  │  │ (Market Data) │  │  (Cache)  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│          External Services Integration               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ KIS API      │  │  eBEST API   │  │ Telegram  │ │
│  │ (한투증권)    │  │   (이베스트)   │  │   Bot     │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
```

### 2. NAS 환경 구성
```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Gateway
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - auth-api
      - trading-api
      - backtest-api

  # Authentication Service
  auth-api:
    build: ./services/auth
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/auth
      - JWT_SECRET=${JWT_SECRET}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Trading Service
  trading-api:
    build: ./services/trading
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/trading
      - REDIS_URL=redis://redis:6379
      - KIS_APP_KEY=${KIS_APP_KEY}
      - KIS_APP_SECRET=${KIS_APP_SECRET}
    volumes:
      - trading-data:/app/data
    depends_on:
      - postgres
      - redis
      - rabbitmq

  # Backtest Service
  backtest-api:
    build: ./services/backtest
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/backtest
      - TIMESCALE_URL=postgresql://user:pass@timescale:5432/market
    depends_on:
      - postgres
      - timescaledb

  # Database Services
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  timescaledb:
    image: timescale/timescaledb:latest-pg14
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - timescale-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

volumes:
  postgres-data:
  timescale-data:
  redis-data:
  rabbitmq-data:
  trading-data:
```

---

## 📂 프로젝트 구조

```
auto_stock_nas/
├── docker-compose.yml
├── .env
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── services/
│   ├── auth/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── utils/
│   │   └── tests/
│   ├── trading/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   ├── services/
│   │   │   └── brokers/
│   │   └── tests/
│   ├── backtest/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── engine/
│   │   │   ├── strategies/
│   │   │   └── indicators/
│   │   └── tests/
│   ├── market/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── collectors/
│   │   │   └── processors/
│   │   └── tests/
│   └── notification/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
├── frontend/
│   ├── package.json
│   ├── src/
│   └── public/
├── mobile/
│   └── react-native/
├── database/
│   ├── migrations/
│   └── seeds/
└── docs/
    ├── api/
    └── deployment/
```

---

## 🔐 다중 사용자 시스템 설계

### 1. 사용자 인증/인가
```python
# services/auth/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # 권한 관리
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # 투자 권한
    can_paper_trade = Column(Boolean, default=True)
    can_real_trade = Column(Boolean, default=False)
    daily_trade_limit = Column(Integer, default=10)
    
    # API 권한
    api_calls_limit = Column(Integer, default=1000)
    api_calls_used = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

### 2. 계정별 API 키 관리
```python
# services/trading/app/models/broker_account.py
class BrokerAccount(Base):
    __tablename__ = "broker_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    
    broker_type = Column(String)  # 'kis', 'ebest', 'kiwoom'
    account_number = Column(String, nullable=False)
    
    # 암호화된 API 인증 정보
    encrypted_api_key = Column(String)
    encrypted_api_secret = Column(String)
    encrypted_account_password = Column(String)
    
    # 계정 상태
    is_paper_account = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    last_connected = Column(DateTime)
    
    # 거래 제한
    max_position_size = Column(Float, default=1000000)
    max_daily_trades = Column(Integer, default=50)
    allowed_products = Column(JSON)  # ['stock', 'etf', 'futures']
```

### 3. 세션 관리
```python
# services/auth/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login")
async def login(credentials: LoginSchema):
    user = await authenticate_user(credentials)
    if not user:
        raise HTTPException(status_code=401)
    
    # JWT 토큰 생성
    access_token = create_access_token(
        data={"sub": user.id, "scopes": user.get_scopes()}
    )
    refresh_token = create_refresh_token(user.id)
    
    # Redis에 세션 저장
    await redis.setex(
        f"session:{user.id}",
        3600,
        json.dumps({
            "user_id": str(user.id),
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        })
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    
    # Redis에서 세션 삭제
    await redis.delete(f"session:{user_id}")
    
    # 토큰 블랙리스트 추가
    await redis.setex(f"blacklist:{token}", 3600, "1")
    
    return {"message": "Successfully logged out"}
```

---

## 🚀 개발 단계별 로드맵

### Phase 1: 기반 구축 (2-3주)
- [ ] NAS Docker 환경 설정
- [ ] PostgreSQL + TimescaleDB 설치
- [ ] Redis 캐시 서버 구성
- [ ] Nginx 리버스 프록시 설정
- [ ] SSL 인증서 설정

### Phase 2: 인증 시스템 (2주)
- [ ] JWT 기반 인증 구현
- [ ] OAuth2 소셜 로그인
- [ ] 2FA 구현
- [ ] 권한 관리 시스템
- [ ] API Rate Limiting

### Phase 3: 데이터 마이그레이션 (1-2주)
- [ ] 기존 데이터베이스 스키마 분석
- [ ] 다중 사용자 스키마로 변환
- [ ] 데이터 마이그레이션 스크립트
- [ ] 데이터 검증

### Phase 4: API 서비스 개발 (4-5주)
```python
# 주요 API 엔드포인트
/api/v1/
├── auth/
│   ├── login
│   ├── logout
│   ├── register
│   └── refresh
├── users/
│   ├── profile
│   ├── settings
│   └── api-keys
├── trading/
│   ├── accounts
│   ├── orders
│   ├── positions
│   └── history
├── market/
│   ├── stocks
│   ├── quotes
│   ├── charts
│   └── indicators
├── backtest/
│   ├── strategies
│   ├── run
│   ├── results
│   └── optimize
└── portfolio/
    ├── summary
    ├── performance
    └── analytics
```

### Phase 5: 브로커 통합 (3-4주)
```python
# services/trading/app/brokers/base.py
from abc import ABC, abstractmethod

class BaseBroker(ABC):
    @abstractmethod
    async def connect(self, credentials: dict):
        pass
    
    @abstractmethod
    async def get_account_info(self):
        pass
    
    @abstractmethod
    async def place_order(self, order: OrderSchema):
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str):
        pass
    
    @abstractmethod
    async def get_positions(self):
        pass
    
    @abstractmethod
    async def get_balance(self):
        pass

# services/trading/app/brokers/kis.py
class KISBroker(BaseBroker):
    """한국투자증권 API"""
    
    async def connect(self, credentials: dict):
        self.session = aiohttp.ClientSession()
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.app_key = credentials['app_key']
        self.app_secret = credentials['app_secret']
        await self._get_access_token()
    
    async def place_order(self, order: OrderSchema):
        endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
        headers = self._get_headers("TTTC0802U")
        
        body = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "PDNO": order.symbol,
            "ORD_DVSN": order.order_type,
            "ORD_QTY": str(order.quantity),
            "ORD_UNPR": str(order.price)
        }
        
        async with self.session.post(
            f"{self.base_url}{endpoint}",
            headers=headers,
            json=body
        ) as response:
            return await response.json()
```

### Phase 6: 실시간 데이터 처리 (2-3주)
```python
# services/market/app/collectors/realtime.py
import asyncio
import websockets

class RealtimeDataCollector:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.subscribers = {}
    
    async def connect_websocket(self):
        async with websockets.connect("wss://api.broker.com/stream") as ws:
            await self.authenticate(ws)
            
            # 실시간 데이터 수신
            async for message in ws:
                data = json.loads(message)
                await self.process_message(data)
    
    async def process_message(self, data):
        symbol = data['symbol']
        
        # Redis에 실시간 데이터 저장
        await self.redis.hset(
            f"realtime:{symbol}",
            mapping={
                "price": data['price'],
                "volume": data['volume'],
                "timestamp": data['timestamp']
            }
        )
        
        # Redis Pub/Sub으로 구독자에게 전송
        await self.redis.publish(
            f"market:{symbol}",
            json.dumps(data)
        )
        
        # TimescaleDB에 저장 (1분 단위)
        if self.should_save_to_db(data['timestamp']):
            await self.save_to_timescale(data)
```

### Phase 7: 프론트엔드 연동 (2-3주)
```typescript
// frontend/src/services/api.ts
import axios from 'axios';

class TradingAPI {
  private baseURL = process.env.REACT_APP_API_URL;
  private token: string | null = null;
  
  constructor() {
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor
    axios.interceptors.request.use(
      config => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      error => Promise.reject(error)
    );
    
    // Response interceptor
    axios.interceptors.response.use(
      response => response,
      async error => {
        if (error.response?.status === 401) {
          // Token refresh logic
          const newToken = await this.refreshToken();
          if (newToken) {
            error.config.headers.Authorization = `Bearer ${newToken}`;
            return axios(error.config);
          }
        }
        return Promise.reject(error);
      }
    );
  }
  
  async placeOrder(order: Order): Promise<OrderResponse> {
    const response = await axios.post(
      `${this.baseURL}/api/v1/trading/orders`,
      order
    );
    return response.data;
  }
  
  // WebSocket 연결
  connectMarketStream(symbols: string[]) {
    const ws = new WebSocket(`${this.baseURL}/ws/market`);
    
    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'subscribe',
        symbols: symbols
      }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.updateMarketData(data);
    };
    
    return ws;
  }
}
```

### Phase 8: 모니터링 & 로깅 (1-2주)
```yaml
# monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki

  promtail:
    image: grafana/promtail
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
```

---

## 🔒 보안 고려사항

### 1. API 보안
```python
# services/auth/app/middleware/security.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import hmac

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # IP 화이트리스트 체크
        client_ip = request.client.host
        if not await self.is_ip_allowed(client_ip):
            return JSONResponse(
                status_code=403,
                content={"detail": "IP not allowed"}
            )
        
        # Rate limiting
        if await self.is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
        
        # HMAC 서명 검증 (중요 API)
        if request.url.path.startswith("/api/v1/trading"):
            if not self.verify_signature(request):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid signature"}
                )
        
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
```

### 2. 데이터 암호화
```python
# services/trading/app/utils/encryption.py
from cryptography.fernet import Fernet
import os

class EncryptionService:
    def __init__(self):
        self.key = os.environ.get("ENCRYPTION_KEY").encode()
        self.cipher = Fernet(self.key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def encrypt_sensitive_data(self, data: dict) -> dict:
        encrypted_data = {}
        for key, value in data.items():
            if key in ['api_key', 'api_secret', 'password']:
                encrypted_data[key] = self.encrypt_api_key(value)
            else:
                encrypted_data[key] = value
        return encrypted_data
```

---

## 📊 성능 최적화

### 1. 데이터베이스 최적화
```sql
-- TimescaleDB 하이퍼테이블 생성
CREATE TABLE market_data (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    price       DOUBLE PRECISION,
    volume      BIGINT,
    PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('market_data', 'time');

-- 압축 정책 설정
ALTER TABLE market_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol'
);

SELECT add_compression_policy('market_data', INTERVAL '7 days');

-- 인덱스 생성
CREATE INDEX idx_market_data_symbol_time 
ON market_data (symbol, time DESC);

-- 파티셔닝
CREATE TABLE orders (
    id SERIAL,
    user_id UUID,
    created_at TIMESTAMPTZ,
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2025_01 PARTITION OF orders
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 2. 캐싱 전략
```python
# services/market/app/utils/cache.py
from functools import wraps
import hashlib

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{hashlib.md5(
                f'{args}{kwargs}'.encode()
            ).hexdigest()}"
            
            # 캐시 확인
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 캐시 저장
            await redis.setex(
                cache_key,
                expire_time,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# 사용 예시
@cache_result(expire_time=60)
async def get_stock_info(symbol: str):
    return await db.fetch_one(
        "SELECT * FROM stocks WHERE symbol = $1",
        symbol
    )
```

---

## 🧪 테스트 전략

### 1. 단위 테스트
```python
# services/trading/tests/test_order.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_place_order():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/trading/orders",
            json={
                "symbol": "005930",
                "quantity": 10,
                "price": 70000,
                "order_type": "limit"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
```

### 2. 부하 테스트
```python
# tests/load_test.py
from locust import HttpUser, task, between

class TradingUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 로그인
        response = self.client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def view_portfolio(self):
        self.client.get(
            "/api/v1/portfolio/summary",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def get_market_data(self):
        self.client.get("/api/v1/market/stocks/005930")
    
    @task(1)
    def place_order(self):
        self.client.post(
            "/api/v1/trading/orders",
            json={
                "symbol": "005930",
                "quantity": 1,
                "order_type": "market"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

---

## 📝 마이그레이션 체크리스트

### 준비 단계
- [ ] NAS 사양 확인 (최소 RAM 8GB, CPU 4코어)
- [ ] 도메인 및 SSL 인증서 준비
- [ ] 백업 전략 수립
- [ ] 재해 복구 계획

### 개발 환경
- [ ] Docker & Docker Compose 설치
- [ ] Git 저장소 설정
- [ ] CI/CD 파이프라인 구축
- [ ] 개발/스테이징/프로덕션 환경 분리

### 데이터베이스
- [ ] PostgreSQL 마이그레이션
- [ ] TimescaleDB 설정
- [ ] Redis 캐시 구성
- [ ] 백업 자동화

### API 개발
- [ ] RESTful API 설계
- [ ] WebSocket 실시간 통신
- [ ] 인증/인가 시스템
- [ ] Rate Limiting

### 브로커 연동
- [ ] 한국투자증권 API
- [ ] 이베스트투자증권 API
- [ ] 키움증권 Open API 대체

### 테스트
- [ ] 단위 테스트 (>80% coverage)
- [ ] 통합 테스트
- [ ] 부하 테스트
- [ ] 보안 테스트

### 배포
- [ ] Blue-Green 배포 전략
- [ ] 롤백 계획
- [ ] 모니터링 설정
- [ ] 로그 수집 시스템

### 문서화
- [ ] API 문서 (OpenAPI/Swagger)
- [ ] 사용자 가이드
- [ ] 관리자 매뉴얼
- [ ] 트러블슈팅 가이드

---

## 🎯 성공 지표

### 기술적 지표
- API 응답 시간 < 200ms (p95)
- 시스템 가용성 > 99.9%
- 동시 접속자 1,000명 처리
- 초당 거래 처리량 > 100 TPS

### 비즈니스 지표
- 사용자 가입 전환율 > 30%
- 일일 활성 사용자(DAU) > 100명
- 월간 거래량 > 10억원
- 고객 만족도(NPS) > 50

---

## 📚 참고 자료

### 기술 문서
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Redis Documentation](https://redis.io/documentation)

### 증권사 API
- [한국투자증권 OpenAPI](https://apiportal.koreainvestment.com/)
- [이베스트투자증권 API](https://www.ebestsec.co.kr/)
- [LS증권 OpenAPI](https://www.ls-sec.co.kr/)

### 보안 가이드
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

이 로드맵을 기반으로 단계적으로 개발을 진행하시면 됩니다. 우선순위와 리소스에 따라 일정을 조정하실 수 있습니다.