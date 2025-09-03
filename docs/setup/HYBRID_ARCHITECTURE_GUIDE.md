# 🚀 REST API + OpenAPI+ 하이브리드 자동매매 시스템

## ✅ **결론: 두 API 모두 사용하는 것이 최적입니다!**

문제점이 없을 뿐만 아니라, 오히려 **각 API의 장점을 최대한 활용**할 수 있는 완벽한 솔루션입니다.

---

## 📊 하이브리드 아키텍처의 장점

### 1. **역할 분담으로 최적 성능**
```
OpenAPI+ (로컬 PC)          REST API (클라우드/N8N)
├─ 실시간 시세 수신         ├─ 전략 실행 스케줄링
├─ 빠른 주문 체결           ├─ 백테스트 실행
├─ 호가창 모니터링          ├─ 포트폴리오 관리
└─ 긴급 주문 처리           └─ 리포트 생성
```

### 2. **장애 대응 능력 (Failover)**
- REST API 장애 시 → OpenAPI+로 백업
- 로컬 PC 다운 시 → 클라우드에서 계속 모니터링
- 이중화로 안정성 극대화

### 3. **유연한 배포**
- 개발: 로컬에서 OpenAPI+ 테스트
- 운영: 클라우드에서 REST API 실행
- 긴급상황: 둘 다 동시 운영

---

## 🏗️ 하이브리드 시스템 구조

```
┌─────────────────────────────────────────────────┐
│                   웹 인터페이스                   │
│              (React + Supabase)                  │
└─────────────┬───────────────────────┬───────────┘
              │                       │
              ▼                       ▼
     ┌────────────────┐      ┌────────────────┐
     │   Supabase     │◀────▶│     N8N        │
     │   Database     │      │  (Workflow)    │
     └────────────────┘      └────────────────┘
              │                       │
              ├───────────────────────┤
              ▼                       ▼
     ┌────────────────┐      ┌────────────────┐
     │  OpenAPI+      │      │   REST API     │
     │  (로컬 PC)     │      │  (클라우드)     │
     └────────────────┘      └────────────────┘
              │                       │
              └───────────┬───────────┘
                          ▼
                   ┌──────────────┐
                   │  키움증권 서버  │
                   └──────────────┘
```

---

## 💻 구현 방법

### 1. **통합 API 래퍼 클래스**

```python
# kiwoom_hybrid_api.py
import os
from enum import Enum
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

class APIMode(Enum):
    OPENAPI_PLUS = "openapi+"
    REST_API = "rest"
    AUTO = "auto"  # 자동 선택

class KiwoomHybridAPI:
    """OpenAPI+와 REST API를 통합 관리하는 하이브리드 API"""
    
    def __init__(self, mode: APIMode = APIMode.AUTO):
        self.mode = mode
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.rest_url = os.getenv('KIWOOM_API_URL')
        
        # OpenAPI+ 초기화 (Windows만)
        self.openapi = None
        if self._is_windows() and self._check_openapi_installed():
            try:
                import win32com.client
                self.openapi = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
            except:
                pass
        
        # REST API 토큰
        self.rest_token = None
    
    def get_current_price(self, stock_code: str):
        """현재가 조회 - 가능한 API 자동 선택"""
        
        # 1. OpenAPI+ 우선 (더 빠름)
        if self.openapi and self.mode != APIMode.REST_API:
            try:
                return self._get_price_openapi(stock_code)
            except:
                pass
        
        # 2. REST API 폴백
        if self.mode != APIMode.OPENAPI_PLUS:
            return self._get_price_rest(stock_code)
        
        raise Exception("No available API")
    
    def send_order(self, order_params: dict):
        """주문 실행 - 상황에 따라 최적 API 선택"""
        
        # 긴급 주문: OpenAPI+ (더 빠름)
        if order_params.get('urgent') and self.openapi:
            return self._send_order_openapi(order_params)
        
        # 일반 주문: REST API (안정적)
        return self._send_order_rest(order_params)
    
    def get_realtime_data(self, stock_codes: list):
        """실시간 데이터 - OpenAPI+ 전용"""
        if not self.openapi:
            raise Exception("OpenAPI+ required for realtime data")
        
        return self._subscribe_realtime_openapi(stock_codes)
    
    def run_backtest(self, strategy: dict):
        """백테스트 - REST API 전용 (클라우드 실행)"""
        return self._run_backtest_rest(strategy)
    
    # ... 구현 메서드들
```

### 2. **스마트 라우팅 시스템**

```python
# smart_router.py
class SmartRouter:
    """요청을 최적의 API로 라우팅"""
    
    def __init__(self):
        self.openapi_available = self._check_openapi_status()
        self.rest_available = self._check_rest_status()
        
    def route_request(self, request_type: str, params: dict):
        """요청 타입에 따라 최적 API 선택"""
        
        routing_rules = {
            # 실시간 데이터: OpenAPI+ 우선
            'realtime_price': {
                'primary': 'openapi+',
                'fallback': 'websocket'
            },
            
            # 주문 실행: 상황별 선택
            'order': {
                'primary': 'rest',  # 안정성
                'urgent': 'openapi+',  # 속도
                'fallback': 'rest'
            },
            
            # 잔고 조회: REST API 우선
            'balance': {
                'primary': 'rest',
                'fallback': 'openapi+'
            },
            
            # 백테스트: REST API 전용
            'backtest': {
                'primary': 'rest',
                'fallback': None
            }
        }
        
        rule = routing_rules.get(request_type)
        
        # 긴급 요청 체크
        if params.get('urgent') and rule.get('urgent'):
            return self._execute_with_api(rule['urgent'], params)
        
        # 일반 라우팅
        try:
            return self._execute_with_api(rule['primary'], params)
        except:
            if rule.get('fallback'):
                return self._execute_with_api(rule['fallback'], params)
            raise
```

### 3. **N8N 워크플로우 통합**

```yaml
# n8n-hybrid-workflow.yml
name: "하이브리드 자동매매"
nodes:
  - id: "schedule"
    type: "cron"
    schedule: "*/1 * * * *"  # 1분마다
    
  - id: "check_market_hours"
    type: "if"
    condition: "09:00 < now < 15:30"
    
  - id: "select_api"
    type: "function"
    code: |
      // 시간대별 API 선택
      const hour = new Date().getHours();
      
      if (hour === 9) {
        // 장 시작: OpenAPI+ (빠른 체결)
        return { api: "openapi+" };
      } else if (hour >= 10 && hour < 15) {
        // 장중: REST API (안정적)
        return { api: "rest" };
      } else {
        // 장 마감: OpenAPI+ (정확한 체결)
        return { api: "openapi+" };
      }
    
  - id: "execute_strategy"
    type: "http"
    url: "{{api_endpoint}}/execute"
    headers:
      X-API-Mode: "{{select_api.api}}"
```

---

## 📋 기능별 최적 API 매핑

| 기능 | OpenAPI+ | REST API | 추천 |
|------|----------|----------|------|
| **실시간 시세** | ⭐⭐⭐ 최고 | ⭐ WebSocket | OpenAPI+ |
| **주문 체결** | ⭐⭐⭐ 즉시 | ⭐⭐ 양호 | 상황별 |
| **잔고 조회** | ⭐⭐ 양호 | ⭐⭐⭐ 편리 | REST API |
| **과거 데이터** | ⭐⭐ 양호 | ⭐⭐⭐ 편리 | REST API |
| **백테스트** | ⭐ 로컬만 | ⭐⭐⭐ 클라우드 | REST API |
| **전략 실행** | ⭐⭐ 수동 | ⭐⭐⭐ 자동화 | REST API |
| **모니터링** | ⭐⭐ 로컬 | ⭐⭐⭐ 원격 | REST API |

---

## 🔧 환경 설정

### `.env` 파일 (통합)
```env
# 공통 인증
KIWOOM_APP_KEY=YOUR_APP_KEY
KIWOOM_APP_SECRET=YOUR_APP_SECRET
KIWOOM_ACCOUNT_NO=12345678-01

# REST API
KIWOOM_REST_URL=https://openapi.kiwoom.com:9443
KIWOOM_WS_URL=ws://openapi.kiwoom.com:9443

# OpenAPI+
KIWOOM_OPENAPI_PATH=C:\OpenAPI
KIWOOM_LOGIN_TYPE=0  # 0:로그인창, 1:자동

# 운영 모드
API_MODE=hybrid  # openapi, rest, hybrid
PRIMARY_API=rest  # 기본 API
FAILOVER_ENABLED=true  # 장애 전환

# 성능 설정
REALTIME_USE_OPENAPI=true  # 실시간은 OpenAPI+
ORDER_USE_REST=true  # 주문은 REST
PARALLEL_EXECUTION=true  # 병렬 실행
```

---

## 📊 운영 시나리오

### 1. **평일 장중 (09:00 ~ 15:30)**
```
09:00 ~ 09:30: OpenAPI+ (장 초반 빠른 체결)
09:30 ~ 15:00: REST API (안정적 운영)
15:00 ~ 15:30: OpenAPI+ (장 마감 정확한 체결)
야간: REST API (포트폴리오 분석, 백테스트)
```

### 2. **장애 대응**
```
REST API 장애 → OpenAPI+ 자동 전환
로컬 PC 다운 → 클라우드 REST API 계속 운영
키움 서버 점검 → 양쪽 모두 대기
```

### 3. **성능 최적화**
```
실시간 호가: OpenAPI+ (지연 최소)
대량 조회: REST API (병렬 처리)
긴급 주문: OpenAPI+ (즉시 체결)
예약 주문: REST API (스케줄링)
```

---

## ✅ 결론

**REST API + OpenAPI+ 하이브리드는:**
1. ✅ **문제없음** - 같은 계정, 같은 Key 사용
2. ✅ **성능 최적** - 각 API 장점 활용
3. ✅ **안정성 향상** - 이중화 구조
4. ✅ **유연한 운영** - 상황별 최적 선택

**추천 구성:**
- 로컬 PC: OpenAPI+ (실시간, 긴급주문)
- 클라우드: REST API + N8N (자동화, 모니터링)
- Supabase: 통합 데이터 저장

이렇게 구성하면 **24/7 안정적인 자동매매 시스템**을 구축할 수 있습니다!