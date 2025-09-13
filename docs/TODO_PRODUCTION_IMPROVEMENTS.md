# 🔧 프로덕션 환경 개선 사항

## 📅 작성일: 2025-09-14
## 📌 현재 상태: 임시 해결책으로 운영 중

---

## 1. 🔒 HTTPS 보안 연결 구성 (우선순위: 높음)

### 현재 문제점
- **HTTP 사용 중** (보안 취약): `http://khanyong.asuscomm.com:8080`
- 브라우저 보안 경고 발생 가능
- Mixed Content 문제 (HTTPS 사이트에서 HTTP API 호출)
- 중간자 공격(MITM) 위험 존재

### 해결 방법: Synology 리버스 프록시 설정

#### Step 1: DSM 리버스 프록시 구성
```
1. Synology DSM 로그인
2. 제어판 → 응용 프로그램 포털 → 역방향 프록시
3. "생성" 클릭하여 새 규칙 추가

설정값:
- 설명: Kiwoom API Bridge
- 소스:
  - 프로토콜: HTTPS
  - 호스트명: khanyong.asuscomm.com
  - 포트: 8443 (또는 원하는 포트)

- 대상:
  - 프로토콜: HTTP
  - 호스트명: localhost (또는 192.168.50.150)
  - 포트: 8080

4. 사용자 지정 헤더 추가 (선택사항):
  - X-Real-IP: $remote_addr
  - X-Forwarded-For: $proxy_add_x_forwarded_for
  - X-Forwarded-Proto: $scheme
```

#### Step 2: 방화벽 규칙 추가
```
1. 제어판 → 보안 → 방화벽
2. 포트 8443 허용 규칙 추가
3. 소스 IP: 모두 (또는 특정 IP 범위)
```

#### Step 3: 환경변수 수정
```javascript
// .env.production
VITE_API_URL=https://khanyong.asuscomm.com:8443
VITE_WS_URL=wss://khanyong.asuscomm.com:8443/ws

// Vercel Dashboard에서도 동일하게 수정
```

#### Step 4: Docker 컨테이너 헤더 처리
```python
# backend/kiwoom_bridge/main.py 수정 필요
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 또는 특정 도메인
)
```

---

## 2. 📊 키움 REST API 직접 연동 (우선순위: 중간)

### 현재 문제점
- **pykrx 임시 사용 중**: 한국거래소 데이터 (15분 지연)
- 키움 REST API 시세 조회 500 에러
- 실시간 데이터 불가능
- API 제한 우회용 솔루션

### 진짜 문제의 원인
```python
# 현재 코드 (backend/kiwoom_bridge/main.py)
# 키움 API 시세 조회가 500 에러 반환
price_url = "https://mockapi.kiwoom.com/uapi/domestic-stock/v1/quotations/inquire-price"
# → 500 Internal Server Error
```

### 해결 방법: 키움 API 정상화 대기 및 재구현

#### Option 1: 키움 REST API 디버깅
```python
# backend/kiwoom_bridge/main.py 수정

async def get_current_price(request: CurrentPriceRequest):
    """키움 REST API 직접 사용"""

    # 1. 토큰 발급 (현재 정상 작동)
    token = await get_kiwoom_token()

    # 2. 시세 조회 재시도
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": os.getenv('KIWOOM_APP_KEY'),
        "appsecret": os.getenv('KIWOOM_APP_SECRET'),
        "tr_id": "FHKST01010100"  # 주식 현재가 조회
    }

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": request.stock_code
    }

    # 3. 에러 핸들링 강화
    try:
        response = requests.get(
            "https://mockapi.kiwoom.com/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code == 500:
            # 키움 서버 이슈 - pykrx fallback
            return await get_price_from_pykrx(request.stock_code)

        return response.json()

    except Exception as e:
        logger.error(f"Kiwoom API error: {e}")
        # Fallback to pykrx
        return await get_price_from_pykrx(request.stock_code)
```

#### Option 2: 키움 OpenAPI+ 사용 (32-bit Python)
```python
# 별도 Windows 서버에서 실행
# backend/kiwoom_openapi_server.py

from pykiwoom import Kiwoom
import asyncio
from fastapi import FastAPI

app = FastAPI()
kiwoom = Kiwoom()

@app.get("/api/realtime-price/{stock_code}")
async def get_realtime_price(stock_code: str):
    """실시간 시세 조회"""
    kiwoom.login()

    # 실시간 데이터 구독
    kiwoom.subscribe_stock_conclusion(stock_code)

    # 현재가 조회
    price = kiwoom.get_price(stock_code)
    volume = kiwoom.get_volume(stock_code)

    return {
        "stock_code": stock_code,
        "current_price": price,
        "volume": volume,
        "timestamp": datetime.now().isoformat()
    }
```

### 임시 해결책 (현재 사용 중)
```python
# pykrx 사용 - 안정적이지만 15분 지연
from pykrx import stock

df = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
```

---

## 3. 📈 추가 개선 사항

### 3.1 WebSocket 실시간 데이터
- 현재: HTTP 폴링 방식
- 개선: WebSocket으로 실시간 시세 스트리밍
```python
# backend/kiwoom_bridge/websocket_handler.py
@app.websocket("/ws/realtime/{stock_code}")
async def websocket_endpoint(websocket: WebSocket, stock_code: str):
    await websocket.accept()
    while True:
        price = await get_current_price(stock_code)
        await websocket.send_json(price)
        await asyncio.sleep(1)  # 1초마다 업데이트
```

### 3.2 Redis 캐싱 도입
- 동일 종목 반복 조회 시 캐싱
- API 호출 횟수 감소
```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_price(stock_code: str):
    cached = redis_client.get(f"price:{stock_code}")
    if cached:
        return json.loads(cached)

    # 캐시 미스 - API 호출
    price = fetch_from_api(stock_code)
    redis_client.setex(
        f"price:{stock_code}",
        60,  # 60초 TTL
        json.dumps(price)
    )
    return price
```

### 3.3 로드 밸런싱
- 여러 API 서버 운영
- 장애 대응 (Failover)
```yaml
# docker-compose.yml
services:
  kiwoom-bridge-1:
    build: .
    ports:
      - "8081:8001"

  kiwoom-bridge-2:
    build: .
    ports:
      - "8082:8001"

  nginx:
    image: nginx
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

## 4. 📝 작업 우선순위

1. **즉시 (1주일 내)**
   - [ ] Synology 리버스 프록시 설정
   - [ ] HTTPS 전환
   - [ ] Mixed Content 문제 해결

2. **단기 (1개월 내)**
   - [ ] 키움 REST API 500 에러 원인 파악
   - [ ] 에러 핸들링 개선
   - [ ] Fallback 로직 정교화

3. **중기 (3개월 내)**
   - [ ] WebSocket 실시간 데이터 구현
   - [ ] Redis 캐싱 시스템
   - [ ] 모니터링 시스템 구축

4. **장기 (6개월 내)**
   - [ ] 키움 OpenAPI+ 서버 구축
   - [ ] 로드 밸런싱
   - [ ] 고가용성(HA) 구성

---

## 5. 🚨 주의사항

### 보안 관련
- HTTP 사용 시 민감한 데이터 전송 금지
- API 키는 환경변수로 관리
- CORS 설정 제한적으로 운영

### 성능 관련
- pykrx는 대량 호출 시 제한 있음
- 15분 지연 데이터임을 사용자에게 명시
- 캐싱 적극 활용

### 안정성 관련
- 키움 API 장애 시 자동 Fallback
- 에러 로깅 및 모니터링
- 정기적인 헬스체크

---

## 6. 📞 문의 및 지원

- 키움증권 OpenAPI 지원: 1544-9000
- Synology 기술지원: [synology.com/support](https://www.synology.com/support)
- 프로젝트 이슈: [GitHub Issues](https://github.com/khanyong/kyyquant-ai-solution/issues)

---

*마지막 업데이트: 2025-09-14*
*작성자: KyyQuant Development Team*