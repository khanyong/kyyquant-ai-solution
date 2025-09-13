# 📦 시놀로지 NAS 배포 가이드

## 🚀 키움 REST API Bridge 서버를 시놀로지 NAS에 배포하기

### 사전 준비사항
1. 시놀로지 NAS에 Docker (Container Manager) 설치
2. N8N이 이미 설치되어 실행 중
3. SSH 접속 가능

---

## 📋 Step 1: 파일 전송

### 1.1 필요한 파일들을 NAS로 복사

```bash
# 로컬 PC에서 실행
# backend/kiwoom_bridge 폴더 전체를 NAS로 복사

# 방법 1: File Station 사용
# 1. File Station 열기
# 2. docker 폴더로 이동
# 3. kiwoom_bridge 폴더 생성
# 4. 파일 업로드:
#    - main.py
#    - requirements.txt
#    - Dockerfile
#    - docker-compose.yml
#    - .env (수정 필요)

# 방법 2: SCP 명령어 사용
scp -r backend/kiwoom_bridge/ your_nas_user@nas_ip:/volume1/docker/
```

### 1.2 NAS에 폴더 구조 생성

```
/volume1/docker/kiwoom_bridge/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── logs/
└── n8n_workflows/
    └── auto_trading_workflow.json
```

---

## 📋 Step 2: 환경 변수 설정

### 2.1 SSH로 NAS 접속

```bash
ssh your_username@your_nas_ip
```

### 2.2 .env 파일 생성 및 수정

```bash
cd /volume1/docker/kiwoom_bridge
nano .env
```

`.env` 파일 내용:
```env
# Supabase Configuration
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # 실제 키 입력

# Frontend URL (for CORS)
FRONTEND_URL=https://your-app.vercel.app  # 또는 http://localhost:3000

# NAS IP
NAS_IP=192.168.1.100  # 실제 NAS IP

# N8N (이미 설치된 경우)
N8N_URL=http://localhost:5678

# 로깅
LOG_LEVEL=INFO
```

---

## 📋 Step 3: Docker 이미지 빌드 및 실행

### 3.1 Container Manager GUI 사용 방법

1. **Container Manager 열기**
2. **프로젝트** 탭 클릭
3. **생성** 버튼 클릭
4. 프로젝트 이름: `kiwoom-bridge`
5. 경로: `/docker/kiwoom_bridge`
6. **docker-compose.yml** 선택
7. **웹 포털** 설정:
   - 포트 매핑 확인: 8001:8001
8. **다음** → **적용**

### 3.2 SSH 명령어 사용 방법

```bash
cd /volume1/docker/kiwoom_bridge

# Docker 이미지 빌드
sudo docker build -t kiwoom-bridge:latest .

# Docker 컨테이너 실행
sudo docker-compose up -d

# 로그 확인
sudo docker-compose logs -f

# 상태 확인
sudo docker ps
```

---

## 📋 Step 4: N8N 워크플로우 설정

### 4.1 N8N 접속
```
http://your_nas_ip:5678
```

### 4.2 워크플로우 임포트

1. N8N 대시보드에서 **Workflows** → **Import from File**
2. `auto_trading_workflow.json` 파일 선택
3. 워크플로우 수정:
   - **환경 변수 설정**:
     - Settings → Variables
     - `USER_ID`: Supabase 사용자 ID
     - `DISCORD_WEBHOOK_URL`: 디스코드 웹훅 (선택)

### 4.3 워크플로우 커스터마이징

```javascript
// 매매 신호 생성 로직 수정 예시
// "매매 신호 생성" 노드의 코드 수정

const currentPrice = $input.item.json.data.output.stck_prpr;
const ma5 = calculateMA(5);  // 5일 이동평균
const ma20 = calculateMA(20); // 20일 이동평균

// 골든크로스/데드크로스 전략
if (ma5 > ma20 && previousMA5 <= previousMA20) {
  return {
    signal: 'buy',
    stock_code: '005930',
    quantity: 10,
    reason: '골든크로스 발생'
  };
} else if (ma5 < ma20 && previousMA5 >= previousMA20) {
  return {
    signal: 'sell',
    stock_code: '005930',
    quantity: 10,
    reason: '데드크로스 발생'
  };
}
```

---

## 📋 Step 5: 테스트

### 5.1 API 서버 테스트

```bash
# NAS IP를 실제 IP로 변경
curl http://192.168.1.100:8001/

# 현재가 조회 테스트
curl -X POST http://192.168.1.100:8001/api/market/current-price \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "005930"}'
```

### 5.2 브라우저에서 테스트

1. **Frontend 수정** (src/services/kiwoomApiService.ts)
```typescript
// baseUrl을 NAS IP로 변경
const baseUrl = 'http://192.168.1.100:8001'
```

2. **MyPage에서 API 키 확인**
   - 모의투자 API 키가 저장되어 있는지 확인
   - 계좌번호가 등록되어 있는지 확인

3. **자동매매 탭에서 테스트**
   - 현재가 조회
   - 모의 주문 실행

---

## 📋 Step 6: 실전 운영

### 6.1 자동 시작 설정

Container Manager에서:
1. 컨테이너 선택
2. **설정** → **자동 재시작** 활성화

### 6.2 모니터링

```bash
# 로그 모니터링
sudo docker logs -f kiwoom-bridge

# 리소스 사용량 확인
sudo docker stats kiwoom-bridge

# 헬스체크
curl http://localhost:8001/
```

### 6.3 백업

```bash
# 설정 백업
cp -r /volume1/docker/kiwoom_bridge /volume1/backup/

# Docker 이미지 백업
sudo docker save kiwoom-bridge:latest > kiwoom-bridge-backup.tar
```

---

## 🔧 트러블슈팅

### 문제: 포트 충돌
```bash
# 사용 중인 포트 확인
sudo netstat -tulpn | grep 8001

# docker-compose.yml에서 포트 변경
ports:
  - "8002:8001"  # 8002로 변경
```

### 문제: 권한 오류
```bash
# 폴더 권한 설정
sudo chown -R docker:docker /volume1/docker/kiwoom_bridge
sudo chmod -R 755 /volume1/docker/kiwoom_bridge
```

### 문제: 메모리 부족
Container Manager에서:
1. 컨테이너 설정
2. 리소스 제한 조정
3. 메모리: 최소 512MB 권장

---

## 🔒 보안 설정

### 방화벽 규칙
1. **Control Panel** → **Security** → **Firewall**
2. 규칙 추가:
   - 포트 8001 (키움 API Bridge)
   - 소스 IP: 로컬 네트워크만 허용

### HTTPS 설정 (선택사항)
```nginx
# Nginx 리버스 프록시 설정
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 N8N 고급 워크플로우 예시

### 복잡한 전략 구현
```javascript
// Bollinger Bands + RSI 전략
const price = $input.item.json.price;
const bb_upper = $input.item.json.bb_upper;
const bb_lower = $input.item.json.bb_lower;
const rsi = $input.item.json.rsi;

// 매수 조건: 가격이 볼린저 밴드 하단 터치 & RSI < 30
if (price <= bb_lower && rsi < 30) {
  return { signal: 'buy', confidence: 'high' };
}

// 매도 조건: 가격이 볼린저 밴드 상단 터치 & RSI > 70
if (price >= bb_upper && rsi > 70) {
  return { signal: 'sell', confidence: 'high' };
}
```

### 포트폴리오 관리
```javascript
// 여러 종목 동시 관리
const portfolio = [
  { code: '005930', weight: 0.3 },  // 삼성전자 30%
  { code: '000660', weight: 0.2 },  // SK하이닉스 20%
  { code: '035720', weight: 0.2 },  // 카카오 20%
  // ...
];

for (const stock of portfolio) {
  // 각 종목별 신호 생성
  const signal = generateSignal(stock.code);
  if (signal) {
    await executeOrder(stock, signal);
  }
}
```

---

## 📞 지원

문제가 발생하면:
1. Docker 로그 확인: `sudo docker logs kiwoom-bridge`
2. N8N 실행 로그 확인
3. Supabase 대시보드에서 API 키 확인
4. 네트워크 연결 상태 확인

---

## ✅ 체크리스트

- [ ] 시놀로지 NAS에 Docker 설치
- [ ] 파일 업로드 완료
- [ ] .env 파일 설정
- [ ] Docker 컨테이너 실행
- [ ] API 서버 테스트
- [ ] N8N 워크플로우 설정
- [ ] Frontend 연결 설정
- [ ] 모의투자 테스트
- [ ] 자동 시작 설정
- [ ] 백업 설정