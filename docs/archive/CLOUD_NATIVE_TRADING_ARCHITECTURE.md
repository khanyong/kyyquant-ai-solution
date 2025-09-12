# 🌐 클라우드 네이티브 자동매매 시스템 아키텍처
## Windows 서버 없이 REST API 기반 10명 동시 사용

## 🎯 시스템 목표
- **Windows 서버 제거**: REST API만 사용
- **완전 클라우드**: Synology NAS + n8n + Supabase + Vercel
- **다중 사용자**: 10명 동시 사용 (각자 API 키)
- **백테스트**: 기존 Windows OpenAPI+ 활용 (개발용)
- **실거래**: REST API 전환 (운영용)

---

## 🏗️ 시스템 아키텍처

```
┌────────────────────────────────────────────────┐
│              Vercel (Frontend)                  │
│                                                │
│  User1    User2    User3  ...  User10         │
│    ↓        ↓        ↓           ↓            │
│                                                │
│  - React + TypeScript                          │
│  - 전략 빌더 UI                                │
│  - 실시간 대시보드                              │
│  - 포트폴리오 관리                              │
└────────────────────────────────────────────────┘
                        ↓
                   [HTTPS/WSS]
                        ↓
┌────────────────────────────────────────────────┐
│            Supabase (Backend)                  │
│                                                │
│  Database (PostgreSQL):                        │
│  ├─ strategies (user_id 격리)                  │
│  ├─ user_api_credentials (암호화)              │
│  ├─ orders (주문 내역)                         │
│  ├─ portfolio (포트폴리오)                     │
│  └─ signals (매매 신호)                        │
│                                                │
│  Auth: 사용자 인증                             │
│  Realtime: WebSocket 구독                      │
│  Storage: 파일 저장                            │
└────────────────────────────────────────────────┘
                        ↓
                   [Webhook/API]
                        ↓
┌────────────────────────────────────────────────┐
│         Synology NAS + n8n Server              │
│                                                │
│  n8n Workflows:                                │
│  ├─ 전략 모니터링 (1분 주기)                    │
│  ├─ 신호 생성 워크플로우                       │
│  ├─ 주문 실행 워크플로우                       │
│  └─ 포트폴리오 업데이트                        │
│                                                │
│  Docker Containers:                            │
│  ├─ n8n (워크플로우 엔진)                      │
│  ├─ Redis (캐싱/큐)                           │
│  └─ Python API Server                         │
└────────────────────────────────────────────────┘
                        ↓
                  [REST API Calls]
                        ↓
┌────────────────────────────────────────────────┐
│          증권사 REST API Servers               │
│                                                │
│  한국투자증권 REST API:                        │
│  ├─ OAuth 2.0 인증                            │
│  ├─ 주문/체결 API                             │
│  ├─ 잔고/포지션 조회                          │
│  └─ 실시간 웹소켓 (별도)                       │
│                                                │
│  LS증권 REST API:                              │
│  ├─ API Key 인증                              │
│  └─ RESTful 엔드포인트                        │
│                                                │
│  eBest REST API:                               │
│  ├─ OAuth 인증                                │
│  └─ xingAPI REST                              │
└────────────────────────────────────────────────┘
```

---

## 💻 핵심 구현 - REST API 기반

### 1. 한국투자증권 REST API 연동

```python
# nas_server/brokers/kis_rest_api.py
import asyncio
import aiohttp
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
import jwt

class KISRestAPI:
    """한국투자증권 REST API 클라이언트"""
    
    def __init__(self, user_credentials: dict):
        self.app_key = user_credentials['app_key']
        self.app_secret = user_credentials['app_secret']
        self.account_no = user_credentials['account_no']
        self.is_mock = user_credentials.get('is_mock', True)
        
        # URL 설정 (모의/실전)
        self.base_url = "https://openapivts.koreainvestment.com:29443" if self.is_mock \
                    else "https://openapi.koreainvestment.com:9443"
        
        self.access_token = None
        self.token_expired = None
        self.session = None
        
    async def initialize(self):
        """세션 초기화 및 토큰 발급"""
        self.session = aiohttp.ClientSession()
        await self.get_access_token()
        
    async def get_access_token(self):
        """OAuth 토큰 발급"""
        url = f"{self.base_url}/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        async with self.session.post(url, json=body) as response:
            data = await response.json()
            self.access_token = data['access_token']
            self.token_expired = datetime.now().timestamp() + data['expires_in']
            
    async def create_order(self, order: dict) -> dict:
        """주문 생성 (REST API)"""
        # 토큰 갱신 체크
        if datetime.now().timestamp() > self.token_expired:
            await self.get_access_token()
            
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "TTTC0802U" if order['side'] == 'buy' else "TTTC0801U"
        }
        
        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[8:],
            "PDNO": order['symbol'],
            "ORD_DVSN": "01",  # 시장가
            "ORD_QTY": str(order['quantity']),
            "ORD_UNPR": "0"
        }
        
        async with self.session.post(url, headers=headers, json=body) as response:
            result = await response.json()
            
            if result['rt_cd'] == '0':
                return {
                    'success': True,
                    'order_id': result['ODNO'],
                    'message': result['msg1']
                }
            else:
                return {
                    'success': False,
                    'error': result['msg1']
                }
    
    async def get_balance(self) -> dict:
        """계좌 잔고 조회"""
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "TTTC8908R"
        }
        
        params = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[8:],
            "PDNO": "005930",  # 삼성전자 (임시)
            "ORD_UNPR": "",
            "ORD_DVSN": "01",
            "CMA_EVLU_AMT_ICLD_YN": "N",
            "OVRS_ICLD_YN": "N"
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            
            return {
                'cash': float(data['output']['ord_psbl_cash']),
                'buying_power': float(data['output']['max_buy_amt']),
                'total_value': float(data['output']['nrcvb_buy_amt'])
            }
    
    async def get_positions(self) -> List[dict]:
        """보유 종목 조회"""
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "TTTC8434R"
        }
        
        params = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[8:],
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "N",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            
            positions = []
            for item in data['output1']:
                if int(item['hldg_qty']) > 0:
                    positions.append({
                        'symbol': item['pdno'],
                        'quantity': int(item['hldg_qty']),
                        'avg_price': float(item['pchs_avg_pric']),
                        'current_price': float(item['prpr']),
                        'profit_loss': float(item['evlu_pfls_amt']),
                        'profit_rate': float(item['evlu_pfls_rt'])
                    })
            
            return positions
    
    async def close(self):
        """세션 종료"""
        if self.session:
            await self.session.close()
```

### 2. n8n 워크플로우 설정

```json
{
  "name": "Multi-User Trading Workflow",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{ "field": "seconds", "secondsInterval": 30 }]
        }
      },
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT * FROM strategies WHERE is_active = true AND auto_trade_enabled = true"
      },
      "name": "Get Active Strategies",
      "type": "n8n-nodes-base.supabase",
      "position": [450, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "// 각 사용자별 전략 실행\nconst strategy = $item.json;\nconst userId = strategy.user_id;\n\n// 사용자 API 키 조회\nconst credentials = await $node['Get User Credentials'].json;\n\n// REST API로 주문 실행\nconst apiClient = new KISRestAPI(credentials);\nconst signals = await evaluateStrategy(strategy);\n\nfor (const signal of signals) {\n  if (signal.action === 'buy' || signal.action === 'sell') {\n    const order = {\n      symbol: signal.symbol,\n      side: signal.action,\n      quantity: signal.quantity,\n      user_id: userId\n    };\n    \n    const result = await apiClient.createOrder(order);\n    \n    // 결과 저장\n    await saveOrderResult(result, userId);\n  }\n}\n\nreturn { success: true, processed: signals.length };"
      },
      "name": "Execute Strategy",
      "type": "n8n-nodes-base.code",
      "position": [650, 300]
    },
    {
      "parameters": {
        "operation": "update",
        "table": "strategies",
        "updateKey": "id",
        "columns": "last_signal_at,performance_metrics"
      },
      "name": "Update Strategy Status",
      "type": "n8n-nodes-base.supabase",
      "position": [850, 300]
    }
  ]
}
```

### 3. 다중 사용자 세션 관리 (REST API 버전)

```python
# nas_server/multi_user_manager.py
import asyncio
from typing import Dict, List
from datetime import datetime
import redis
from supabase import create_client

class MultiUserRESTManager:
    """REST API 기반 다중 사용자 관리"""
    
    def __init__(self):
        self.users: Dict[str, KISRestAPI] = {}
        self.redis = redis.Redis(host='localhost', port=6379)
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.max_concurrent = 10
        
    async def initialize_users(self):
        """활성 사용자 초기화 (최대 10명)"""
        # Supabase에서 활성 사용자 조회
        result = self.supabase.table('user_api_credentials') \
            .select('*') \
            .eq('is_active', True) \
            .limit(10) \
            .execute()
        
        for user_cred in result.data:
            user_id = user_cred['user_id']
            
            # REST API 클라이언트 생성
            api_client = KISRestAPI({
                'app_key': decrypt(user_cred['api_key']),
                'app_secret': decrypt(user_cred['api_secret']),
                'account_no': decrypt(user_cred['account_no']),
                'is_mock': user_cred['is_demo']
            })
            
            await api_client.initialize()
            self.users[user_id] = api_client
            
        print(f"초기화 완료: {len(self.users)}명 사용자")
    
    async def execute_user_strategy(self, user_id: str, strategy: dict):
        """사용자별 전략 실행"""
        if user_id not in self.users:
            print(f"사용자 {user_id} 없음")
            return
        
        api_client = self.users[user_id]
        
        try:
            # 1. 현재 잔고 조회
            balance = await api_client.get_balance()
            
            # 2. 보유 종목 조회
            positions = await api_client.get_positions()
            
            # 3. 전략 신호 생성
            signals = await self.generate_signals(strategy, positions, balance)
            
            # 4. 주문 실행
            for signal in signals:
                if signal['strength'] > 0.7:  # 신호 강도 체크
                    order = {
                        'symbol': signal['symbol'],
                        'side': signal['action'],
                        'quantity': self.calculate_position_size(
                            balance['buying_power'],
                            signal['price']
                        )
                    }
                    
                    result = await api_client.create_order(order)
                    
                    # 주문 결과 저장
                    await self.save_order(user_id, order, result)
                    
        except Exception as e:
            print(f"전략 실행 오류 ({user_id}): {e}")
            await self.log_error(user_id, str(e))
    
    async def run_all_users(self):
        """모든 사용자 전략 동시 실행"""
        tasks = []
        
        # 각 사용자의 활성 전략 조회
        for user_id, api_client in self.users.items():
            strategies = await self.get_user_strategies(user_id)
            
            for strategy in strategies:
                # 비동기 태스크 생성
                task = asyncio.create_task(
                    self.execute_user_strategy(user_id, strategy)
                )
                tasks.append(task)
        
        # 모든 태스크 동시 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 로깅
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"실행 완료: {success_count}/{len(tasks)} 성공")
    
    async def get_user_strategies(self, user_id: str) -> List[dict]:
        """사용자의 활성 전략 조회"""
        result = self.supabase.table('strategies') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('is_active', True) \
            .eq('auto_trade_enabled', True) \
            .execute()
        
        return result.data
    
    async def save_order(self, user_id: str, order: dict, result: dict):
        """주문 결과 저장"""
        self.supabase.table('orders').insert({
            'user_id': user_id,
            'stock_code': order['symbol'],
            'order_type': order['side'],
            'quantity': order['quantity'],
            'status': 'executed' if result['success'] else 'failed',
            'broker_order_id': result.get('order_id'),
            'created_at': datetime.now().isoformat()
        }).execute()
    
    def calculate_position_size(self, buying_power: float, price: float) -> int:
        """포지션 크기 계산"""
        # 매수가능금액의 10% 사용
        position_value = buying_power * 0.1
        quantity = int(position_value / price)
        return max(1, quantity)
```

### 4. Docker Compose 설정 (Synology NAS)

```yaml
# docker-compose.yml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - ./n8n_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - trading_network

  redis:
    image: redis:alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - ./redis_data:/data
    restart: unless-stopped
    networks:
      - trading_network

  trading_api:
    build: ./trading_api
    container_name: trading_api
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - REDIS_HOST=redis
      - ENVIRONMENT=production
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - trading_network

networks:
  trading_network:
    driver: bridge
```

---

## 🎯 REST API 장점

### 1. **Windows 서버 불필요**
- 클라우드 네이티브 구조
- Docker 컨테이너로 관리
- 크로스 플랫폼 지원

### 2. **완벽한 다중 사용자 지원**
- 세션 제약 없음
- 동시 10명 처리 가능
- 사용자별 독립 API 클라이언트

### 3. **확장성**
- 수평 확장 가능
- 로드 밸런싱 지원
- 마이크로서비스 구조

### 4. **비용 효율**
```yaml
월 비용:
  - Synology NAS: 보유 (전력비만)
  - Supabase: $25
  - Vercel: $20
  - 총: 약 5만원 (10명 기준 5천원/명)
```

---

## 📊 성능 비교

| 항목 | Windows + OpenAPI | REST API |
|------|------------------|----------|
| 동시 사용자 | 1명 (세션 전환 필요) | 10명+ (제한 없음) |
| 서버 비용 | 월 10만원 | 월 0원 (NAS 활용) |
| 확장성 | 제한적 | 무제한 |
| 관리 복잡도 | 높음 | 낮음 |
| 실시간 시세 | 우수 | 양호 (폴링) |
| 주문 처리 | 즉시 | 즉시 |

---

## 🚀 구현 로드맵

### Phase 1: 기본 구조 (1주)
- [ ] KIS REST API 클라이언트 구현
- [ ] n8n 워크플로우 설정
- [ ] Docker 컨테이너 구성

### Phase 2: 다중 사용자 (1주)
- [ ] 10명 동시 처리 테스트
- [ ] 에러 핸들링
- [ ] 로깅 시스템

### Phase 3: 운영 최적화 (1주)
- [ ] 성능 튜닝
- [ ] 모니터링 대시보드
- [ ] 백업/복구 시스템

---

## ✅ 결론

**REST API 기반으로 Windows 서버 없이 10명 동시 자동매매 완벽 지원**
- Synology NAS + n8n으로 완전 자동화
- 사용자별 독립적인 API 세션
- 월 5만원으로 10명 운영 가능
- 확장 가능한 클라우드 네이티브 구조

이 구조로 Windows 의존성을 완전히 제거하고 효율적인 다중 사용자 자동매매 시스템을 구축할 수 있습니다.