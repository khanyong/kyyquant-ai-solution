# KyyQuant AI Solution

Python Backend (FastAPI) + React Frontend 기반 자동매매 시스템

## 시스템 구조

```
React Frontend (포트 3000)
      ↓ REST API / WebSocket
FastAPI Backend (포트 8000)
      ↓ COM/ActiveX
Kiwoom OpenAPI+
```

## 사전 준비사항

1. **키움증권 계좌 개설**
2. **키움 OpenAPI+ 설치** ([키움증권 홈페이지](https://www.kiwoom.com))
3. **모의투자 신청** (선택사항, 테스트용)
4. **Python 3.10+** 설치
5. **Node.js 18+** 설치

## 설치 방법

### 1. 백엔드 설정

```bash
# Python 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 계좌 정보 입력
```

### 2. 프론트엔드 설정

```bash
# Node 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

## 실행 방법

### 1. 백엔드 서버 실행

```bash
# FastAPI 서버 시작
python main.py
# 또는
uvicorn main:app --reload --port 8000
```

서버가 http://localhost:8000 에서 실행됩니다.

### 2. 프론트엔드 실행

```bash
npm run dev
```

웹 인터페이스가 http://localhost:3000 에서 실행됩니다.

## API 엔드포인트

### REST API

- `GET /` - 서버 상태 확인
- `GET /health` - 헬스체크
- `POST /api/login` - 로그인
- `GET /api/accounts` - 계좌 목록 조회
- `POST /api/balance` - 계좌 잔고 조회
- `POST /api/stock-info` - 주식 정보 조회
- `POST /api/order` - 주문 실행
- `GET /api/markets/{market}/stocks` - 시장별 종목 조회

### WebSocket

- `ws://localhost:8000/ws` - 실시간 데이터 스트리밍

## 주요 파일 설명

```
├── main.py              # FastAPI 메인 서버
├── backend_api.py       # API 엔드포인트 정의
├── kiwoom_api.py        # 키움 OpenAPI+ 래퍼
├── requirements.txt     # Python 의존성
├── package.json         # Node.js 의존성
├── .env.example         # 환경변수 템플릿
└── architecture.md      # 시스템 아키텍처 문서
```

## 주의사항

1. **Windows 환경에서만 실행 가능** (키움 OpenAPI+ 제약)
2. **키움 OpenAPI+ 로그인 필요**
3. **실거래 시 주의** - DEMO_MODE=false 설정 시 실제 주문 실행
4. **API 호출 제한** - 초당 5회 제한 준수

## 개발 로드맵

- [x] Phase 1: 백엔드 기본 구조
- [ ] Phase 2: React 프론트엔드
- [ ] Phase 3: 자동매매 전략
- [ ] Phase 4: 백테스팅 시스템

## 라이선스

Private