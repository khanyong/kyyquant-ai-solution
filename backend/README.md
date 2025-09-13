# Backend Server Structure

백엔드 서버의 구조와 주요 컴포넌트 설명

## 📁 디렉토리 구조

```
backend/
├── rest_api/           # REST API 서버 핵심 파일
│   ├── main_rest.py    # REST API 전용 서버
│   ├── main_hybrid.py  # 하이브리드 모드 서버
│   ├── backtest_server.py  # 백테스트 서버
│   └── kiwoom_*.py     # 키움 API 관련 모듈
├── data_collectors/    # 데이터 수집 스크립트
│   ├── collect_*.py    # 데이터 수집
│   ├── download_*.py   # 데이터 다운로드
│   └── update_*.py     # 데이터 업데이트
├── batch_scripts/      # 배치 실행 스크립트
│   └── *.bat          # Windows 배치 파일
├── strategies/         # 백테스트 전략
│   └── backtest_*.py   # 백테스트 구현
├── utils/             # 유틸리티 모듈
│   ├── n8n_*.py       # n8n 연동
│   └── *.py           # 기타 유틸리티
├── tests/             # 테스트 파일
│   └── test_*.py      # 단위 테스트
├── api/               # API 엔드포인트
├── config/            # 설정 파일
├── core/              # 핵심 비즈니스 로직
├── database/          # 데이터베이스 관련
├── indicators/        # 기술지표 계산
├── kiwoom_bridge/     # 키움 브릿지
└── sql/               # SQL 스크립트
```

## 🚀 서버 실행

### REST API 서버 (권장)
```bash
cd backend/rest_api
python main_rest.py
```

### 하이브리드 서버
```bash
cd backend/rest_api
python main_hybrid.py
```

### 백테스트 서버
```bash
cd backend/rest_api
python backtest_server.py
```

## 📊 데이터 수집

```bash
cd backend/data_collectors
python collect_all_data.py
```

## 🧪 테스트

```bash
cd backend/tests
python test_backtest_simple.py
```