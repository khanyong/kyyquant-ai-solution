# 🚀 Synology NAS + n8n + 키움증권 REST API 자동매매 시스템

## ⚠️ 중요: 키움증권 API 특성
**키움증권은 REST API를 제공하지 않습니다!**
- OpenAPI+는 Windows COM/OCX 기반 (REST API 없음)
- 해결 방안: 키움 대신 REST API 지원 증권사 사용

## 📌 REST API 지원 증권사 옵션

### 1️⃣ **한국투자증권 (권장)**
```yaml
장점:
  - 완벽한 REST API 지원
  - OAuth 2.0 인증
  - 실시간 웹소켓
  - 모의투자 지원
  
API 엔드포인트:
  - 모의: https://openapivts.koreainvestment.com:29443
  - 실전: https://openapi.koreainvestment.com:9443
```

### 2️⃣ **LS증권**
```yaml
장점:
  - REST API 지원
  - 간단한 인증
  
단점:
  - 기능 제한적
  - 문서 부족
```

### 3️⃣ **eBest투자증권 (이베스트)**
```yaml
장점:
  - xingAPI REST 지원
  - 다양한 기능
  
단점:
  - 복잡한 구조
  - 높은 수수료
```

---

## 🔄 키움증권 연동 대안 솔루션

### 방안 1: Windows Bridge Server (복잡)
```
Synology NAS (n8n)
    ↓ REST API 호출
Windows PC (24시간 구동)
    ↓ 키움 OpenAPI+
키움증권 서버
```

### 방안 2: 증권사 변경 (권장) ✅
```
Synology NAS (n8n)
    ↓ REST API 직접 호출
한국투자증권 REST API
```

---

## 🏗️ 한국투자증권 REST API 시스템 구현

### Docker Compose 설정
```yaml
# /docker/auto-trading/docker-compose.yml
version: '3.8'

services:
  # n8n 워크플로우 엔진
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
      - NODE_ENV=production
      - WEBHOOK_URL=http://nas-ip:5678/
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - ./n8n/data:/home/node/.n8n
      - ./n8n/files:/files
    restart: unless-stopped
    networks:
      - trading-network

  # FastAPI 트레이딩 서버
  api-server:
    build: ./api-server
    container_name: trading-api
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - KIS_APP_KEY=${KIS_APP_KEY}  # 한국투자증권
      - KIS_APP_SECRET=${KIS_APP_SECRET}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - ENVIRONMENT=production
    volumes:
      - ./api-server/logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - trading-network

  # Redis 캐싱/큐잉
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

  # 키움 Bridge (선택사항 - Windows 필요)
  # kiwoom-bridge:
  #   image: windows-bridge:latest  # 별도 구축 필요
  #   container_name: kiwoom-bridge
  #   ports:
  #     - "9000:9000"
  #   environment:
  #     - KIWOOM_ID=${KIWOOM_ID}
  #     - KIWOOM_PW=${KIWOOM_PW}
  #   networks:
  #     - trading-network

networks:
  trading-network:
    driver: bridge
```

---

## 💡 키움증권 데이터 활용 + 한투 실거래

### 하이브리드 전략
```python
# /docker/auto-trading/api-server/hybrid_broker.py
"""
키움: 백테스트, 과거 데이터 (Windows 개발 PC)
한투: 실시간 시세, 실거래 (NAS REST API)
"""

class HybridBrokerAPI:
    def __init__(self):
        self.kis_api = KISRestAPI()  # 한국투자증권 - 실거래
        # self.kiwoom_api = None      # 키움 - 백테스트용
    
    async def get_realtime_price(self, symbol: str):
        """실시간 시세 - 한투 REST API"""
        return await self.kis_api.get_price(symbol)
    
    async def place_order(self, order: dict):
        """실제 주문 - 한투 REST API"""
        return await self.kis_api.create_order(order)
    
    def get_historical_data(self, symbol: str, period: str):
        """과거 데이터 - 키움 (개발 PC에서만)"""
        # 키움 데이터는 Supabase에 미리 저장
        return supabase.table("historical_prices").select("*") \
            .eq("symbol", symbol).execute()
```

---

## 🔧 키움 없이 완전한 REST API 시스템

### FastAPI 서버 (한국투자증권 전용)
```python
# /docker/auto-trading/api-server/main.py
from fastapi import FastAPI, HTTPException
import aiohttp
from datetime import datetime
import os

app = FastAPI(title="KIS Trading API Server")

class KISRestAPI:
    """한국투자증권 REST API 전용 클라이언트"""
    
    def __init__(self):
        # 모의투자 서버
        self.base_url = "https://openapivts.koreainvestment.com:29443"
        self.app_key = os.getenv("KIS_APP_KEY")
        self.app_secret = os.getenv("KIS_APP_SECRET")
        self.access_token = None
        
    async def authenticate(self):
        """OAuth 인증"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/oauth2/tokenP"
            body = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            async with session.post(url, json=body) as resp:
                data = await resp.json()
                self.access_token = data["access_token"]
                return self.access_token
    
    async def get_price(self, symbol: str):
        """현재가 조회"""
        if not self.access_token:
            await self.authenticate()
            
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": symbol
            }
            
            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()
                
                return {
                    "symbol": symbol,
                    "price": float(data["output"]["stck_prpr"]),
                    "change": float(data["output"]["prdy_vrss"]),
                    "volume": int(data["output"]["acml_vol"]),
                    "high": float(data["output"]["stck_hgpr"]),
                    "low": float(data["output"]["stck_lwpr"])
                }
    
    async def place_order(self, user_creds: dict, order: dict):
        """주문 실행"""
        if not self.access_token:
            await self.authenticate()
            
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
            
            # 모의투자 주문 tr_id
            if order["side"] == "buy":
                tr_id = "VTTC0802U"  # 모의투자 매수
            else:
                tr_id = "VTTC0801U"  # 모의투자 매도
                
            headers = {
                "authorization": f"Bearer {self.access_token}",
                "appkey": user_creds["api_key"],
                "appsecret": user_creds["api_secret"],
                "tr_id": tr_id
            }
            
            body = {
                "CANO": user_creds["account_no"][:8],
                "ACNT_PRDT_CD": user_creds["account_no"][8:],
                "PDNO": order["symbol"],
                "ORD_DVSN": "01",  # 시장가
                "ORD_QTY": str(order["quantity"]),
                "ORD_UNPR": "0"
            }
            
            async with session.post(url, headers=headers, json=body) as resp:
                data = await resp.json()
                
                if data["rt_cd"] == "0":
                    return {
                        "success": True,
                        "order_id": data["output"]["ODNO"],
                        "message": "주문 성공"
                    }
                else:
                    return {
                        "success": False,
                        "message": data["msg1"]
                    }

# API 인스턴스
kis_api = KISRestAPI()

@app.get("/")
async def root():
    return {
        "message": "한국투자증권 REST API 서버",
        "note": "키움증권은 REST API를 지원하지 않습니다"
    }

@app.get("/api/price/{symbol}")
async def get_price(symbol: str):
    """시세 조회 (한투)"""
    try:
        return await kis_api.get_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/order")
async def create_order(order_data: dict):
    """주문 실행 (한투)"""
    try:
        # Supabase에서 사용자 API 키 조회
        user_creds = {
            "api_key": order_data["api_key"],
            "api_secret": order_data["api_secret"],
            "account_no": order_data["account_no"]
        }
        
        order = {
            "symbol": order_data["symbol"],
            "side": order_data["side"],
            "quantity": order_data["quantity"]
        }
        
        return await kis_api.place_order(user_creds, order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 키움 vs 한투 비교

| 항목 | 키움증권 | 한국투자증권 |
|------|----------|-------------|
| **REST API** | ❌ 없음 | ✅ 완벽 지원 |
| **운영 환경** | Windows 필수 | OS 무관 |
| **NAS 호환** | ❌ 불가능 | ✅ 완벽 |
| **동시 사용자** | 1명 | 무제한 |
| **수수료** | 낮음 | 보통 |
| **백테스트 데이터** | 우수 | 양호 |

---

## 🎯 권장 솔루션

### 옵션 1: 한국투자증권으로 전환 ✅
```yaml
장점:
  - REST API 완벽 지원
  - NAS에서 직접 실행
  - Windows 불필요
  - 10명 동시 사용
  
단점:
  - 계좌 이전 필요
  - 수수료 약간 높음
```

### 옵션 2: 하이브리드 운영
```yaml
구성:
  - 백테스트: 키움 (Windows PC)
  - 실거래: 한투 (NAS REST API)
  
장점:
  - 키움 데이터 활용
  - REST API 실거래
  
단점:
  - 2개 증권사 관리
```

### 옵션 3: Windows Bridge 구축
```yaml
구성:
  - Windows Server 24시간 운영
  - 키움 API → REST API 변환
  
장점:
  - 키움 계속 사용
  
단점:
  - Windows 서버 비용
  - 복잡한 구조
  - 유지보수 어려움
```

---

## ✅ 결론 및 추천

### 🏆 **한국투자증권 REST API 사용 강력 권장**

**이유:**
1. 키움은 REST API 미지원 (Windows 필수)
2. NAS에서 직접 실행 불가능
3. 한투는 완벽한 REST API 제공
4. 동일한 기능, 더 나은 확장성

### 💡 **마이그레이션 경로**
```
1단계: 한투 계좌 개설
2단계: 모의투자로 테스트
3단계: 소액 실거래 전환
4단계: 완전 이전
```

**키움증권을 고집한다면 Windows 서버가 반드시 필요합니다!**