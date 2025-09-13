# Backend 폴더 구조

## 📁 디렉토리 구조

```
backend/
│
├── api/                    # API 엔드포인트 및 서버 관련
│   ├── api_server.py       # 메인 API 서버
│   ├── api_strategy_routes.py  # 전략 관련 API 라우트
│   ├── backend_api.py      # 백엔드 API 핵심 로직
│   ├── main.py            # FastAPI 메인 애플리케이션
│   └── main_dev.py        # 개발용 메인 애플리케이션
│
├── core/                   # 핵심 비즈니스 로직
│   ├── strategy_manager.py     # 전략 관리
│   ├── strategy_config_manager.py  # 전략 설정 관리
│   ├── strategy_config_schema.py   # 전략 설정 스키마
│   ├── strategy_execution_manager.py  # 전략 실행 관리
│   ├── risk_manager.py         # 리스크 관리
│   ├── trading_engine.py       # 트레이딩 엔진
│   ├── dynamic_indicator_system.py  # 동적 지표 시스템
│   ├── data_pipeline.py        # 데이터 파이프라인
│   └── cloud_executor.py       # 클라우드 실행 관리
│
├── database/               # 데이터베이스 관련
│   ├── database.py         # 데이터베이스 연결 관리
│   ├── database_supabase.py    # Supabase 연결 관리
│   └── models.py           # 데이터베이스 모델
│
├── scripts/                # 실행 스크립트
│   ├── kiwoom/            # 키움 관련 스크립트
│   │   ├── kiwoom_api.py           # 키움 API 핵심
│   │   ├── kiwoom_bridge_server.py # 키움 브리지 서버
│   │   ├── kiwoom_hybrid_api.py    # 키움 하이브리드 API
│   │   ├── kiwoom_data_saver.py    # 키움 데이터 저장
│   │   ├── kiwoom_supabase_bridge.py  # 키움-Supabase 브리지
│   │   ├── kiwoom_trading_api.py   # 키움 트레이딩 API
│   │   └── *.bat                   # 각종 실행 배치 파일
│   │
│   └── setup/             # 설치 및 설정 스크립트
│       ├── setup_*.py     # 각종 설정 파이썬 스크립트
│       ├── setup_*.bat    # 설정 배치 파일
│       └── *.md           # 설정 가이드 문서
│
├── sql/                    # SQL 스크립트
│   ├── create_*.sql       # 테이블 생성 SQL
│   ├── alter_*.sql        # 테이블 수정 SQL
│   ├── update_*.sql       # 데이터 업데이트 SQL
│   ├── fix_*.sql          # 버그 수정 SQL
│   └── check_*.sql        # 데이터 확인 SQL
│
├── tests/                  # 테스트 파일
│   ├── test_*.py          # 각종 테스트 스크립트
│   ├── check_*.py         # 검증 스크립트
│   └── inspect_*.py       # 검사 스크립트
│
├── strategies/             # 전략 모듈
│   ├── base_strategy.py   # 기본 전략 클래스
│   └── momentum_strategy.py  # 모멘텀 전략
│
├── config/                 # 설정 파일
│   ├── config.py          # 메인 설정
│   └── save_complex_indicators.py  # 복잡한 지표 저장 설정
│
├── docs/                   # 문서
│   ├── *.md               # 마크다운 문서
│   └── *.json             # JSON 예제 파일
│
├── venv32/                # 32비트 파이썬 가상환경
├── requirements.txt       # 파이썬 패키지 요구사항
├── Procfile              # Heroku 배포 설정
└── run_servers.sh        # 서버 실행 스크립트

```

## 🚀 주요 모듈 설명

### API 모듈
- FastAPI 기반 REST API 서버
- 전략 관리, 주문 실행, 데이터 조회 엔드포인트 제공

### Core 모듈
- 트레이딩 전략 실행 및 관리
- 리스크 관리 및 포지션 관리
- 기술적 지표 계산 및 신호 생성

### Database 모듈
- Supabase 연결 및 데이터 저장
- PostgreSQL 데이터베이스 관리

### Scripts 모듈
- 키움 OpenAPI 연동 스크립트
- 시스템 설정 및 초기화 스크립트

## 📝 실행 방법

1. **API 서버 실행**
   ```bash
   cd backend
   python api/main.py
   ```

2. **키움 브리지 서버 실행**
   ```bash
   cd backend/scripts/kiwoom
   python kiwoom_bridge_server.py
   ```

3. **테스트 실행**
   ```bash
   cd backend
   python tests/test_kiwoom_data_flow.py
   ```