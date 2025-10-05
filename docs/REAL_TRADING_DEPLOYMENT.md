# 실전투자 시스템 배포 가이드

자동매매 실전투자 시스템의 배포 및 운영 가이드입니다.

## 📋 목차

1. [시스템 구성](#시스템-구성)
2. [사전 준비](#사전-준비)
3. [Backend API 배포](#backend-api-배포)
4. [n8n 워크플로우 설정](#n8n-워크플로우-설정)
5. [환경변수 설정](#환경변수-설정)
6. [실행 및 테스트](#실행-및-테스트)
7. [모니터링](#모니터링)
8. [트러블슈팅](#트러블슈팅)

---

## 시스템 구성

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     실전투자 시스템                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   n8n        │─────>│  Backend API │─────>│ Supabase  │ │
│  │  워크플로우   │      │  (FastAPI)   │      │    DB     │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                             │
│         │                      │                             │
│         ▼                      ▼                             │
│  ┌──────────────────────────────────────┐                   │
│  │         키움증권 REST API              │                   │
│  │    (모의투자 / 실전투자)               │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 구성 요소

1. **n8n (워크플로우 엔진)**
   - 메인 자동매매 워크플로우 (1분 주기)
   - 포지션 모니터링 워크플로우 (30초 주기)
   - 위치: `\\eiNNNieSysNAS\docker\n8n`

2. **Backend API (FastAPI)**
   - 전략 신호 생성 (`/api/strategy/check-signal`)
   - 포지션 청산 확인 (`/api/strategy/check-position-exit`)
   - 시장 데이터 조회 (`/api/market/*`)
   - 포트: `8001`

3. **Supabase (데이터베이스)**
   - 전략 정의 (`strategies`)
   - 지표 정의 (`indicators`)
   - 매매 신호 (`trading_signals`)
   - 주문/포지션 (`orders`, `positions`)

4. **키움증권 REST API**
   - 모의투자: `https://mockapi.kiwoom.com`
   - 실전투자: `https://openapi.kiwoom.com`

---

## 사전 준비

### 1. 키움증권 API 신청

1. 키움증권 계좌 개설
2. OpenAPI 신청: https://www.kiwoom.com/h/customer/download/VOpenApiInfoView
3. App Key, App Secret 발급받기
4. 모의투자 계좌 신청 (테스트용)

### 2. Supabase 설정 확인

```sql
-- 필수 테이블 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('strategies', 'indicators', 'trading_signals', 'orders', 'positions');
```

### 3. 시스템 요구사항

- **OS**: Windows Server 2019+ / Linux (Docker)
- **Python**: 3.9+
- **n8n**: v1.0+
- **Network**: 키움 API 접근 가능한 네트워크

---

## Backend API 배포

### 1. 환경변수 설정

`backend/.env` 파일 생성:

```bash
# Supabase
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# 지표 계산 모드
ENFORCE_DB_INDICATORS=true

# 서버 설정
HOST=0.0.0.0
PORT=8001
```

### 2. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 3. 서버 실행

**개발 모드:**
```bash
cd backend
python main.py
```

**프로덕션 모드 (systemd):**

`/etc/systemd/system/auto-stock-backend.service`:

```ini
[Unit]
Description=Auto Stock Trading Backend API
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/home/trading/auto_stock/backend
Environment="PATH=/home/trading/.virtualenvs/auto-stock/bin"
ExecStart=/home/trading/.virtualenvs/auto-stock/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

실행:
```bash
sudo systemctl enable auto-stock-backend
sudo systemctl start auto-stock-backend
sudo systemctl status auto-stock-backend
```

### 4. 헬스체크

```bash
curl http://localhost:8001/health
# {"status":"healthy","timestamp":"2024-10-05T..."}

curl http://localhost:8001/
# {"status":"running","version":"3.0.0",...}
```

---

## n8n 워크플로우 설정

### 1. n8n 환경변수 설정

n8n UI > Settings > Environment Variables:

```bash
# Backend API
BACKEND_URL=http://192.168.50.xxx:8001

# Supabase
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# 키움 API
KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
KIWOOM_ACCOUNT=81101350-01

# 거래 모드
TRADING_MODE=mock  # mock(모의투자) 또는 real(실전투자)
```

### 2. 워크플로우 임포트

n8n UI에서 다음 파일들을 임포트:

1. **메인 자동매매**: `n8n-workflows/auto-trading-with-backend-api.json`
   - 1분마다 실행
   - 장시간(09:00-15:30) 체크
   - Backend API로 신호 생성
   - 매수 신호 시 주문 실행

2. **포지션 모니터링**: `n8n-workflows/position-monitoring-with-backend-api.json`
   - 30초마다 실행
   - 활성 포지션 손절/익절 체크
   - 단계별 매도 실행

### 3. Supabase Credential 설정

n8n UI > Credentials > New Credential > Supabase:

- **Name**: Supabase Account
- **Host**: `hznkyaomtrpzcayayayh.supabase.co`
- **Service Role Secret**: `your_service_role_key`

### 4. 워크플로우 활성화

각 워크플로우를 열어서 우측 상단 **Active** 토글 ON

---

## 환경변수 설정

### Backend API 필수 환경변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `SUPABASE_URL` | Supabase 프로젝트 URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon Key | `eyJhbGci...` |
| `ENFORCE_DB_INDICATORS` | DB 전용 모드 | `true` |

### n8n 필수 환경변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `BACKEND_URL` | Backend API 주소 | `http://localhost:8001` |
| `KIWOOM_APP_KEY` | 키움 App Key | `iQ4uqUvL...` |
| `KIWOOM_APP_SECRET` | 키움 App Secret | `9uBOq4tE...` |
| `KIWOOM_ACCOUNT` | 키움 계좌번호 | `81101350-01` |
| `TRADING_MODE` | 거래 모드 | `mock` 또는 `real` |

---

## 실행 및 테스트

### 1. 모의투자 테스트

**TRADING_MODE=mock 설정 확인**

```bash
# n8n 환경변수 확인
echo $TRADING_MODE  # mock
```

**테스트 전략 생성:**

Supabase > strategies 테이블:

```json
{
  "id": "uuid-here",
  "name": "RSI 과매도 테스트",
  "is_active": true,
  "target_stocks": ["005930"],
  "conditions": {
    "entry": {
      "rsi": {
        "operator": "<",
        "value": 30,
        "period": 14
      }
    },
    "exit": {
      "stop_loss": {
        "enabled": true,
        "rate": -0.05
      },
      "profit_target": {
        "enabled": true,
        "targets": [
          {"rate": 0.03, "percentage": 0.3},
          {"rate": 0.05, "percentage": 0.5},
          {"rate": 0.10, "percentage": 1.0}
        ]
      }
    }
  }
}
```

**수동 신호 확인:**

```bash
curl -X POST http://localhost:8001/api/strategy/check-signal \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "uuid-here",
    "stock_code": "005930"
  }'
```

**워크플로우 실행 확인:**

n8n UI > Executions에서 실행 로그 확인

### 2. 실전투자 전환

**⚠️ 주의: 실제 자금이 투입됩니다!**

1. **모의투자 충분한 테스트 완료 후**
2. **소액으로 먼저 테스트**
3. `TRADING_MODE=real` 변경
4. n8n 워크플로우 재시작

```bash
# n8n 환경변수 변경
TRADING_MODE=real

# n8n 재시작
docker restart n8n
```

### 3. 모니터링 확인

**실시간 로그:**

```bash
# Backend API 로그
tail -f backend/logs/trading.log

# n8n 로그
docker logs -f n8n
```

**Supabase 데이터:**

- `trading_signals`: 신호 생성 확인
- `orders`: 주문 체결 확인
- `positions`: 포지션 상태 확인

---

## 모니터링

### 1. Backend API 모니터링

**엔드포인트 상태:**

```bash
# 헬스체크
curl http://localhost:8001/health

# API 버전
curl http://localhost:8001/
```

**로그 모니터링:**

```bash
# 실시간 로그
tail -f backend/logs/trading.log

# 에러만 필터링
grep ERROR backend/logs/trading.log
```

### 2. n8n 워크플로우 모니터링

**n8n UI > Executions:**

- 성공/실패 실행 확인
- 실행 시간 체크
- 에러 메시지 확인

**주요 메트릭:**

- 워크플로우 성공률
- 평균 실행 시간
- 에러 발생 빈도

### 3. 거래 성과 모니터링

**Supabase SQL:**

```sql
-- 오늘 매매 신호
SELECT * FROM trading_signals
WHERE created_at::date = CURRENT_DATE
ORDER BY created_at DESC;

-- 오늘 체결 주문
SELECT * FROM orders
WHERE status = 'EXECUTED'
AND created_at::date = CURRENT_DATE;

-- 활성 포지션
SELECT * FROM positions
WHERE status = 'active';

-- 전략별 승률
SELECT
  strategy_id,
  COUNT(*) as total_trades,
  SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
  ROUND(AVG(profit_loss_rate) * 100, 2) as avg_return_pct
FROM positions
WHERE status = 'closed'
GROUP BY strategy_id;
```

### 4. 알림 설정

**Slack 알림 (선택사항):**

n8n에 Slack 노드 추가하여:
- 매수/매도 체결 알림
- 손절 발생 알림
- 일일 성과 리포트

---

## 트러블슈팅

### 문제 1: Backend API 연결 실패

**증상:**
```
n8n: Failed to connect to http://localhost:8001/api/strategy/check-signal
```

**해결:**

1. Backend 서버 실행 확인:
```bash
curl http://localhost:8001/health
```

2. 방화벽 확인:
```bash
sudo ufw allow 8001/tcp
```

3. n8n 환경변수 확인:
```bash
echo $BACKEND_URL  # http://localhost:8001 또는 실제 IP
```

### 문제 2: Supabase 연결 실패

**증상:**
```
RuntimeError: FATAL: DB-only mode requires Supabase connection
```

**해결:**

1. 환경변수 확인:
```bash
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

2. Supabase 프로젝트 상태 확인 (https://supabase.com)

3. `.env` 파일에 환경변수 추가:
```bash
cd backend
cat .env
```

### 문제 3: 지표 계산 실패

**증상:**
```
Failed to calculate rsi: Unknown indicator
```

**해결:**

1. Supabase `indicators` 테이블 확인:
```sql
SELECT name, is_active FROM indicators WHERE name = 'rsi';
```

2. 지표가 없으면 생성:
```sql
INSERT INTO indicators (name, calculation_type, is_active)
VALUES ('rsi', 'builtin', true);
```

### 문제 4: 키움 API 인증 실패

**증상:**
```
OAuth token has expired
```

**해결:**

1. App Key/Secret 확인:
```bash
echo $KIWOOM_APP_KEY
echo $KIWOOM_APP_SECRET
```

2. 키움 API 상태 확인: https://apiportal.kiwoom.com

3. 토큰 재발급:
```bash
curl -X POST https://mockapi.kiwoom.com/oauth2/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "appkey": "your_key",
    "secretkey": "your_secret"
  }'
```

### 문제 5: 주문 실패

**증상:**
```
Order failed: rt_cd != 0
```

**해결:**

1. 계좌번호 형식 확인:
```bash
# 올바른 형식: 계좌번호-상품코드
KIWOOM_ACCOUNT=81101350-01
```

2. 거래 모드 확인:
```bash
# 모의투자: VTTC0802U (매수), VTTC0801U (매도)
# 실전투자: TTTC0802U (매수), TTTC0801U (매도)
echo $TRADING_MODE
```

3. 주문 수량 확인 (최소 1주)

---

## 배포 체크리스트

### 모의투자 배포

- [ ] Supabase 연결 확인
- [ ] Backend API 실행 확인
- [ ] n8n 워크플로우 임포트
- [ ] 환경변수 설정 (`TRADING_MODE=mock`)
- [ ] 테스트 전략 생성
- [ ] 수동 신호 확인
- [ ] 워크플로우 활성화
- [ ] 1일 이상 모니터링

### 실전투자 배포

- [ ] 모의투자 충분한 테스트 완료
- [ ] 실전 App Key/Secret 발급
- [ ] 실전 계좌번호 등록
- [ ] 소액 투자로 테스트
- [ ] `TRADING_MODE=real` 변경
- [ ] 손절 설정 확인
- [ ] 알림 설정 완료
- [ ] 백업 플랜 준비

---

## 참고 문서

- [MASTER_ROADMAP.md](../MASTER_ROADMAP.md) - 프로젝트 전체 로드맵
- [TRADING_TABLES_USAGE_PLAN.md](TRADING_TABLES_USAGE_PLAN.md) - 테이블 구조
- [n8n-workflows/SETUP_GUIDE.md](../n8n-workflows/SETUP_GUIDE.md) - n8n 설정
- 키움 OpenAPI 가이드: https://apiportal.kiwoom.com

---

## 라이선스

이 프로젝트는 개인 투자용으로만 사용하세요. 자동매매 투자는 원금 손실 위험이 있습니다.
