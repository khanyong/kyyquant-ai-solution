# 자동 매매 시스템 백엔드 v3.0

## 📁 프로젝트 구조

```
backend_new/
├── api/                    # API 엔드포인트
│   ├── backtest.py        # 백테스트 API
│   ├── market.py          # 시장 데이터 API
│   └── strategy.py        # 전략 관리 API
│
├── backtest/              # 백테스트 엔진
│   ├── engine.py          # 핵심 백테스트 로직
│   └── models.py          # 데이터 모델
│
├── strategies/            # 거래 전략
│   ├── base.py           # 기본 전략 클래스
│   ├── manager.py        # 전략 관리자
│   ├── technical/        # 기술적 분석 전략
│   │   ├── golden_cross.py
│   │   ├── rsi_oversold.py
│   │   └── bollinger_band.py
│   ├── stage_based/      # 단계별 전략
│   └── custom/           # 사용자 정의 전략
│
├── indicators/           # 지표 계산
│   └── calculator.py     # 기술적 지표 계산기
│
├── data/                 # 데이터 관리
│   └── provider.py       # 데이터 제공자
│
├── config/               # 설정
├── utils/                # 유틸리티
└── tests/                # 테스트
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 설정
```

### 2. 로컬 실행

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

### 3. Docker 실행

```bash
# Docker 이미지 빌드
docker build -t auto_stock_backend .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env auto_stock_backend

# 또는 docker-compose 사용
docker-compose up
```

## 📡 API 엔드포인트

### 백테스트
- `POST /api/backtest/run` - 백테스트 실행
- `POST /api/backtest/quick` - 빠른 백테스트 (전략 저장 없이)
- `GET /api/backtest/results/{user_id}` - 결과 조회

### 시장 데이터
- `GET /api/market/stocks` - 종목 목록
- `GET /api/market/price/{stock_code}` - 현재가 조회

### 전략 관리
- `GET /api/strategy/list` - 전략 목록
- `POST /api/strategy/save` - 전략 저장
- `GET /api/strategy/{strategy_id}` - 전략 조회

## 🔑 주요 기능

### ✅ 구현 완료
- Clean Architecture 구조
- 모듈화된 전략 시스템
- Stage-based Trading 지원
- Sell Conditions 완벽 지원
- 다양한 기술적 지표
- Supabase 연동
- Docker 지원

### 📋 TODO
- WebSocket 실시간 데이터
- 백테스트 결과 캐싱
- 전략 성능 최적화
- 더 많은 기술적 지표
- 테스트 코드 추가

## 📦 나스 서버 배포

### 나스 정보
- **내부 IP**: 192.168.50.150
- **외부 DDNS**: khanyong.asuscomm.com
- **Cloudflared**: api.bll-pro.com (포트 8080)

### 배포 방법
1. 이 폴더 전체를 나스 서버 `/volume1/docker/auto_stock`에 업로드
2. SSH 접속: `ssh khanyong@192.168.50.150`
3. Docker 빌드 및 실행:
   ```bash
   cd /volume1/docker/auto_stock
   docker-compose build
   docker-compose up -d
   ```

### 접속 URL
- 로컬: http://192.168.50.150:8080
- 외부 (Cloudflared): https://api.bll-pro.com
- API 문서: https://api.bll-pro.com/docs

### Frontend 연동 (Vercel)
Frontend는 Vercel에 배포되어 있으며, 다음 환경 변수로 연결됨:
- `VITE_API_URL=https://api.bll-pro.com`
- `VITE_WS_URL=wss://api.bll-pro.com/ws`
- `VITE_N8N_URL=https://workflow.bll-pro.com`

## 📝 라이센스

Private Project