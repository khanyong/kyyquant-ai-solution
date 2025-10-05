# 환경변수 설정 가이드

실전투자 시스템의 모의투자/실전투자 전환을 위한 환경변수 설정 가이드입니다.

## 📋 목차

1. [n8n 환경변수](#n8n-환경변수)
2. [Backend API 환경변수](#backend-api-환경변수)
3. [모의투자 설정](#모의투자-설정)
4. [실전투자 설정](#실전투자-설정)
5. [환경변수 전환 프로세스](#환경변수-전환-프로세스)

---

## n8n 환경변수

### 설정 위치

**방법 1: n8n UI (권장)**
1. n8n UI 접속: http://192.168.50.150:5678
2. Settings > Environment Variables
3. 아래 변수들 추가

**방법 2: Docker Compose**
```yaml
# docker-compose.yml
environment:
  - BACKEND_URL=http://192.168.50.xxx:8001
  - KIWOOM_APP_KEY=your_key
  ...
```

### 필수 환경변수

```bash
# ============================================
# Backend API
# ============================================
BACKEND_URL=http://192.168.50.150:8001

# ============================================
# Supabase
# ============================================
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ============================================
# 키움증권 API (모의투자용)
# ============================================
KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
KIWOOM_ACCOUNT=81101350-01

# ============================================
# 거래 모드 (중요!)
# ============================================
TRADING_MODE=mock
# mock: 모의투자 (https://mockapi.kiwoom.com)
# real: 실전투자 (https://openapi.kiwoom.com)
```

---

## Backend API 환경변수

### 설정 위치

`backend/.env` 파일:

```bash
# ============================================
# Supabase 연결
# ============================================
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ============================================
# 지표 계산 모드
# ============================================
ENFORCE_DB_INDICATORS=true
# true: Supabase 지표만 사용 (권장)
# false: 빌트인 지표 허용 (개발용)

# ============================================
# 서버 설정
# ============================================
HOST=0.0.0.0
PORT=8001

# ============================================
# 로깅 레벨
# ============================================
LOG_LEVEL=INFO
# DEBUG, INFO, WARNING, ERROR
```

---

## 모의투자 설정

### 1. n8n 환경변수

```bash
# 거래 모드
TRADING_MODE=mock

# 키움 모의투자 계정
KIWOOM_APP_KEY=모의투자_앱키
KIWOOM_APP_SECRET=모의투자_시크릿
KIWOOM_ACCOUNT=모의투자_계좌번호
```

### 2. 사용되는 엔드포인트

- **API Base URL**: `https://mockapi.kiwoom.com`
- **OAuth**: `https://mockapi.kiwoom.com/oauth2/token`
- **주문**: `https://mockapi.kiwoom.com/uapi/domestic-stock/v1/trading/order-cash`
- **TR ID**:
  - 매수: `VTTC0802U`
  - 매도: `VTTC0801U`

### 3. 확인 방법

n8n 워크플로우 실행 시 로그 확인:

```json
{
  "url": "https://mockapi.kiwoom.com/oauth2/token",
  "tr_id": "VTTC0802U"
}
```

---

## 실전투자 설정

### ⚠️ 주의사항

**실전투자는 실제 자금이 투입됩니다!**

1. 모의투자 충분한 테스트 필수 (최소 1주일)
2. 소액으로 먼저 시작 (100만원 이하 권장)
3. 손절 설정 반드시 확인
4. 백업 플랜 준비

### 1. n8n 환경변수

```bash
# 거래 모드
TRADING_MODE=real  # ⚠️ mock → real 변경

# 키움 실전투자 계정
KIWOOM_APP_KEY=실전투자_앱키
KIWOOM_APP_SECRET=실전투자_시크릿
KIWOOM_ACCOUNT=실전투자_계좌번호
```

### 2. 사용되는 엔드포인트

- **API Base URL**: `https://openapi.kiwoom.com`
- **OAuth**: `https://openapi.kiwoom.com/oauth2/token`
- **주문**: `https://openapi.kiwoom.com/uapi/domestic-stock/v1/trading/order-cash`
- **TR ID**:
  - 매수: `TTTC0802U`
  - 매도: `TTTC0801U`

### 3. 확인 방법

n8n 워크플로우 실행 시 로그 확인:

```json
{
  "url": "https://openapi.kiwoom.com/oauth2/token",
  "tr_id": "TTTC0802U"
}
```

---

## 환경변수 전환 프로세스

### 모의투자 → 실전투자 전환

#### 1단계: 모의투자 검증

```bash
# n8n 환경변수 확인
TRADING_MODE=mock
```

**체크리스트:**
- [ ] 1주일 이상 모의투자 운영
- [ ] 매수/매도 신호 정상 동작
- [ ] 손절/익절 정상 동작
- [ ] 포지션 모니터링 정상 동작
- [ ] 전략 수익률 확인

#### 2단계: 실전투자 계정 준비

1. **키움증권 실전 계좌 개설**
2. **OpenAPI 실전 App Key/Secret 발급**
   - 키움 API 포털: https://apiportal.kiwoom.com
   - 신청 → 승인 (1~2일 소요)
3. **계좌번호 확인**
   ```
   형식: 12345678-01
   ```

#### 3단계: n8n 환경변수 변경

**n8n UI > Settings > Environment Variables:**

```bash
# 변경 전
TRADING_MODE=mock
KIWOOM_APP_KEY=모의투자_앱키
KIWOOM_APP_SECRET=모의투자_시크릿
KIWOOM_ACCOUNT=81101350-01

# 변경 후
TRADING_MODE=real  # ⚠️
KIWOOM_APP_KEY=실전투자_앱키
KIWOOM_APP_SECRET=실전투자_시크릿
KIWOOM_ACCOUNT=실제계좌번호-01
```

#### 4단계: n8n 재시작

**Docker 환경:**
```bash
cd /path/to/n8n
docker-compose restart
```

**systemd 환경:**
```bash
sudo systemctl restart n8n
```

#### 5단계: 동작 확인

1. **워크플로우 로그 확인**
   ```json
   {
     "url": "https://openapi.kiwoom.com/...",
     "tr_id": "TTTC0802U"
   }
   ```

2. **첫 주문 테스트 (소액)**
   - 수동으로 워크플로우 실행
   - 주문 체결 확인
   - Supabase orders 테이블 확인

3. **자동 실행 활성화**
   - 워크플로우 Active ON

---

## 환경변수별 동작 비교

| 설정 | TRADING_MODE=mock | TRADING_MODE=real |
|------|-------------------|-------------------|
| **API URL** | `https://mockapi.kiwoom.com` | `https://openapi.kiwoom.com` |
| **매수 TR_ID** | `VTTC0802U` | `TTTC0802U` |
| **매도 TR_ID** | `VTTC0801U` | `TTTC0801U` |
| **자금** | 가상 자금 | **실제 자금** ⚠️ |
| **리스크** | 없음 | **원금 손실 가능** ⚠️ |

---

## 자동 전환 로직

n8n 워크플로우는 `TRADING_MODE` 환경변수 하나만 변경하면 자동으로 전환됩니다.

### 키움 인증 노드

```json
{
  "url": "={{($env.TRADING_MODE === 'real' ? 'https://openapi.kiwoom.com' : 'https://mockapi.kiwoom.com') + '/oauth2/token'}}"
}
```

### 주문 실행 노드

```json
{
  "url": "={{($env.TRADING_MODE === 'real' ? 'https://openapi.kiwoom.com' : 'https://mockapi.kiwoom.com') + '/uapi/domestic-stock/v1/trading/order-cash'}}",
  "headers": {
    "tr_id": "={{$env.TRADING_MODE === 'real' ? 'TTTC0802U' : 'VTTC0802U'}}"
  }
}
```

---

## 트러블슈팅

### 문제 1: 환경변수 적용 안됨

**증상:**
```
TRADING_MODE=real인데도 mockapi.kiwoom.com 호출
```

**해결:**
1. n8n 재시작
   ```bash
   docker-compose restart
   ```
2. 워크플로우 재활성화
   - Active OFF → ON

### 문제 2: 실전투자 인증 실패

**증상:**
```
OAuth token error: Invalid credentials
```

**해결:**
1. App Key/Secret 확인
   - 키움 API 포털에서 재확인
   - 복사 시 공백/줄바꿈 제거
2. 계좌번호 형식 확인
   ```bash
   # 올바른 형식
   KIWOOM_ACCOUNT=12345678-01
   ```
3. 실전투자 승인 여부 확인
   - 키움 API 포털에서 상태 확인

### 문제 3: TR_ID 에러

**증상:**
```
TR_ID not found: VTTC0802U (실전투자 시)
```

**해결:**
```bash
# 환경변수 확인
echo $TRADING_MODE  # real

# TRADING_MODE=real이면 TTTC0802U 사용해야 함
```

---

## 환경변수 백업

중요한 환경변수는 안전한 곳에 백업하세요.

**백업 파일 예시:** `.env.backup`

```bash
# 모의투자
TRADING_MODE_MOCK=mock
KIWOOM_APP_KEY_MOCK=xxx
KIWOOM_APP_SECRET_MOCK=xxx
KIWOOM_ACCOUNT_MOCK=81101350-01

# 실전투자
TRADING_MODE_REAL=real
KIWOOM_APP_KEY_REAL=xxx
KIWOOM_APP_SECRET_REAL=xxx
KIWOOM_ACCOUNT_REAL=12345678-01
```

---

## 참고 문서

- [REAL_TRADING_DEPLOYMENT.md](REAL_TRADING_DEPLOYMENT.md) - 배포 가이드
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Backend API 명세
- 키움 OpenAPI 가이드: https://apiportal.kiwoom.com
