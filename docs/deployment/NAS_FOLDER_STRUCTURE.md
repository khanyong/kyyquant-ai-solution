# NAS 서버 폴더 및 파일 구조

## 개요
Synology NAS (192.168.50.150)에서 실행되는 자동매매 백테스트 시스템의 폴더 구조 및 각 파일의 역할을 설명합니다.

---

## 📁 전체 구조

```
/volume1/docker/auto-stock/
├── backend/
│   ├── api/
│   │   └── backtest.py              # 백테스트 REST API 엔드포인트
│   ├── backtest/
│   │   └── engine.py                # 백테스트 핵심 엔진
│   ├── indicators/
│   │   ├── __init__.py
│   │   └── calculator.py            # 지표 계산 엔진
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py                  # 전략 베이스 클래스
│   │   ├── manager.py               # 전략 관리자
│   │   └── technical/               # 기술적 지표 기반 전략들
│   ├── .env                         # 환경 변수 (Supabase 키 등)
│   ├── .env.production              # 프로덕션 환경 변수
│   ├── main.py                      # FastAPI 메인 애플리케이션
│   ├── requirements.txt             # Python 의존성 패키지
│   ├── Dockerfile                   # Docker 이미지 빌드 설정
│   └── docker-compose.yml           # Docker Compose 설정
└── logs/                            # 애플리케이션 로그 (선택사항)
```

---

## 📂 주요 디렉토리 설명

### 1. `/volume1/docker/auto-stock/`
- **역할**: 프로젝트 루트 디렉토리
- **용도**: Docker 컨테이너가 마운트하는 베이스 경로

### 2. `backend/`
- **역할**: 백엔드 애플리케이션 소스 코드
- **용도**: Python FastAPI 기반 백테스트 서버

---

## 📄 핵심 파일 상세 설명

### 🔧 설정 파일

#### `backend/.env`
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
```
- **역할**: 환경 변수 설정
- **포함 내용**:
  - Supabase 데이터베이스 연결 정보
  - API 키 및 인증 토큰
- **중요도**: ⭐⭐⭐⭐⭐ (없으면 서버 작동 불가)

#### `backend/docker-compose.yml`
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8080:8001"
    volumes:
      - ./:/app
```
- **역할**: Docker Compose 구성
- **주요 설정**:
  - 포트 매핑: 8080(외부) → 8001(내부)
  - 볼륨 마운트: 로컬 파일을 컨테이너에 실시간 반영
  - 자동 재시작 정책

#### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```
- **역할**: Docker 이미지 빌드 설정
- **주요 작업**:
  - Python 3.11 베이스 이미지 사용
  - 필요한 패키지 설치
  - 애플리케이션 복사 및 실행

#### `backend/requirements.txt`
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.3
numpy==1.26.2
supabase==2.0.3
python-dotenv==1.0.0
```
- **역할**: Python 패키지 의존성 정의
- **주요 패키지**:
  - fastapi: REST API 프레임워크
  - pandas/numpy: 데이터 처리 및 계산
  - supabase: Supabase 클라이언트

---

### 🚀 애플리케이션 파일

#### `backend/main.py`
```python
from fastapi import FastAPI
from api.backtest import router as backtest_router

app = FastAPI(title="Auto Stock Backend", version="3.0.0")
app.include_router(backtest_router, prefix="/api")
```
- **역할**: FastAPI 애플리케이션 진입점
- **주요 기능**:
  - API 라우터 등록
  - CORS 설정
  - 헬스 체크 엔드포인트
- **실행**: `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`
- **URL**: http://192.168.50.150:8080/docs (API 문서)

#### `backend/api/backtest.py`
```python
@router.post("/backtest/run")
async def run_backtest(request: BacktestRequest):
    # 백테스트 실행 로직
    return results
```
- **역할**: 백테스트 REST API 엔드포인트
- **주요 엔드포인트**:
  - `POST /api/backtest/run`: 백테스트 실행
  - `GET /health`: 서버 상태 확인
- **요청 처리**:
  1. 프론트엔드로부터 전략 ID 수신
  2. Supabase에서 전략 설정 로드
  3. BacktestEngine 호출
  4. 결과 반환

---

### 🔬 백테스트 엔진

#### `backend/backtest/engine.py`
```python
class BacktestEngine:
    def run(self, strategy, stocks, start_date, end_date):
        # 1. 데이터 로드
        # 2. 지표 계산
        # 3. 매매 신호 생성
        # 4. 포지션 관리
        # 5. 수익률 계산
        return results
```
- **역할**: 백테스트 핵심 실행 엔진 (762 라인)
- **주요 메서드**:
  - `run()`: 백테스트 전체 실행
  - `_calculate_indicators()`: 지표 계산 (라인 386)
  - `_evaluate_conditions()`: 매매 조건 평가
  - `_resolve_indicator_name()`: 지표 이름 해석 (macd_12_26 → macd)
  - `_resolve_operand()`: 조건 피연산자 해석
- **중요 기능**:
  - 지표명 자동 매칭 (suffixed names 처리)
  - 크로스오버/크로스언더 신호 감지
  - 포지션 및 손익 계산

**주요 처리 흐름**:
```
1. Strategy 로드 (Supabase)
   ↓
2. 주가 데이터 로드 (kw_price_daily 테이블)
   ↓
3. 지표 계산 (IndicatorCalculator.calculate())
   ↓
4. Preflight 검증 (지표 컬럼 존재 확인)
   ↓
5. 매매 신호 평가 (각 행마다 조건 체크)
   ↓
6. 포지션 관리 (매수/매도 실행)
   ↓
7. 결과 집계 및 반환
```

---

### 📊 지표 계산 시스템

#### `backend/indicators/calculator.py`
```python
class IndicatorCalculator:
    def calculate(self, df, indicator, stock_code):
        # Supabase에서 지표 정의 로드
        # Python 코드 실행
        # 결과 컬럼 반환
        return result_columns
```
- **역할**: 기술적 지표 계산 엔진 (967 라인)
- **주요 메서드**:
  - `calculate()`: 지표 계산 진입점 (라인 620)
  - `_calculate_from_definition()`: Supabase 정의 기반 계산
  - `_calculate_python_code()`: Python 코드 실행 (라인 779)
  - `_execute_supabase_code()`: Supabase 형식 코드 실행

**최근 수정 사항** (2025-09-30):
```python
# 라인 781-785: formula에서 code 추출 로직 수정
if 'formula' in config and isinstance(config['formula'], dict):
    code = config['formula'].get('code', '')
else:
    code = config.get('code', '')
```
- **수정 이유**: Supabase의 indicator 테이블 구조가 `{formula: {code: '...'}}` 형태인데, 기존 코드는 `{code: '...'}` 형태로만 처리
- **영향**: MACD 등 모든 python_code 타입 지표가 정상 작동

**지표 계산 흐름**:
```
1. Supabase에서 indicator 정의 로드
   {
     name: 'macd',
     calculation_type: 'python_code',
     formula: {
       code: 'exp1 = df["close"].ewm(...)...'
     },
     output_columns: ['macd', 'macd_signal', 'macd_hist']
   }
   ↓
2. 안전한 네임스페이스 생성
   namespace = {
     'df': DataFrame,
     'params': {'fast': 12, 'slow': 26, 'signal': 9},
     'pd': pandas,
     'np': numpy
   }
   ↓
3. exec(code, namespace) 실행
   ↓
4. result = namespace.get('result')
   {'macd': Series, 'macd_signal': Series, 'macd_hist': Series}
   ↓
5. DataFrame에 컬럼 추가
   df['macd'] = result['macd']
   df['macd_signal'] = result['macd_signal']
   df['macd_hist'] = result['macd_hist']
```

---

### 📈 전략 관리

#### `backend/strategies/base.py`
```python
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signals(self, df):
        pass
```
- **역할**: 전략 베이스 클래스
- **용도**: 모든 전략이 상속받아야 하는 인터페이스 정의

#### `backend/strategies/manager.py`
```python
class StrategyManager:
    def load_from_supabase(self, strategy_id):
        # Supabase에서 전략 로드
        return strategy_config
```
- **역할**: 전략 로드 및 관리
- **주요 기능**:
  - Supabase strategies 테이블 쿼리
  - 전략 설정 파싱
  - 기본값 적용

---

## 🔄 Docker 컨테이너 관리

### 컨테이너 상태 확인
```bash
ssh admin@192.168.50.150
cd /volume1/docker/auto-stock
docker-compose ps
```

### 로그 확인
```bash
docker logs auto-stock-backend-1 --tail 100
docker logs auto-stock-backend-1 -f  # 실시간
```

### 재시작 (파일 수정 후)
```bash
# 파일 업로드
scp D:\Dev\auto_stock\backend\indicators\calculator.py admin@192.168.50.150:/volume1/docker/auto-stock/backend/indicators/

# 자동 재시작 (--reload 모드)
# 또는 수동 재시작:
docker-compose restart
```

### 완전 재빌드 (필요시)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📡 네트워크 및 포트

| 서비스 | 내부 포트 | 외부 포트 | URL |
|--------|----------|----------|-----|
| Backend API | 8001 | 8080 | http://192.168.50.150:8080 |
| API Docs | 8001 | 8080 | http://192.168.50.150:8080/docs |
| Health Check | 8001 | 8080 | http://192.168.50.150:8080/health |

---

## 🗄️ 데이터베이스 연동

### Supabase 테이블

#### `strategies` 테이블
```sql
{
  id: uuid,
  name: text,
  config: jsonb {
    buyConditions: [...],
    sellConditions: [...],
    indicators: [
      {name: 'macd', type: 'MACD', params: {fast: 12, slow: 26, signal: 9}}
    ]
  }
}
```

#### `indicators` 테이블
```sql
{
  id: uuid,
  name: text,
  calculation_type: text,  -- 'python_code', 'builtin', 'custom_formula'
  formula: jsonb {
    code: text  -- Python 실행 코드
  },
  output_columns: text[],
  default_params: jsonb
}
```

#### `kw_price_daily` 테이블
```sql
{
  stock_code: text,
  trade_date: date,
  open: numeric,
  high: numeric,
  low: numeric,
  close: numeric,
  volume: bigint
}
```

---

## 🔍 디버깅 가이드

### 1. 백테스트가 0회 거래인 경우
```bash
# 로그 확인
docker logs auto-stock-backend-1 --tail 100 | grep "ERROR"

# 지표 계산 로그 확인
docker logs auto-stock-backend-1 --tail 100 | grep "DEBUG"
```

**확인 사항**:
- `[DEBUG] Executing code with params` - params가 제대로 전달되는가?
- `[DEBUG] Code to execute` - 코드가 비어있지 않은가?
- `[DEBUG] Execution result type` - result가 None이 아닌가?
- `Final columns` - 지표 컬럼이 추가되었는가?

### 2. 파일 변경이 반영되지 않는 경우
```bash
# 1. 파일이 정확히 업로드되었는지 확인
ssh admin@192.168.50.150 "cat /volume1/docker/auto-stock/backend/indicators/calculator.py | grep -A 5 'formula in config'"

# 2. 컨테이너가 파일을 감지했는지 확인
docker logs auto-stock-backend-1 --tail 20 | grep "Reloading"

# 3. 수동 재시작
docker-compose restart
```

### 3. 컨테이너가 시작되지 않는 경우
```bash
# 빌드 로그 확인
docker-compose logs backend

# 일반적인 원인:
# - requirements.txt 패키지 설치 실패
# - .env 파일 누락
# - 포트 충돌 (8080 이미 사용 중)
```

---

## 📝 파일 업로드 체크리스트

백엔드 파일 수정 후 NAS 업로드 시 체크:

- [ ] `calculator.py` - 지표 계산 로직 수정
- [ ] `engine.py` - 백테스트 엔진 수정
- [ ] `main.py` - API 엔드포인트 추가
- [ ] `requirements.txt` - 패키지 추가 (재빌드 필요)
- [ ] `.env` - 환경 변수 변경
- [ ] `docker-compose.yml` - 컨테이너 설정 변경 (재시작 필요)

**주의**: `requirements.txt` 또는 `Dockerfile` 변경 시 반드시 `docker-compose build` 필요!

---

## 🚨 중요 주의사항

1. **파일 권한**: NAS에 업로드된 파일은 `admin` 사용자 권한 필요
2. **포트 충돌**: 8080 포트가 다른 서비스와 충돌하지 않도록 주의
3. **환경 변수**: `.env` 파일의 Supabase 키는 절대 외부 노출 금지
4. **볼륨 마운트**: `./:/app` 마운트로 인해 로컬 파일 변경이 즉시 반영됨
5. **Python 캐싱**: `.pyc` 파일 캐싱으로 인해 변경이 반영 안 될 수 있음 → 재시작 필요

---

## 📚 관련 문서

- [백테스트 시스템 가이드](./docs/complete_data_flow.md)
- [지표 계산 로직](./backend/indicators/README.md)
- [NAS 배포 가이드](./NAS_DEPLOYMENT.md)
- [Supabase 스키마](./docs/supabase_schema.md)

---

## 버전 정보

- **Current Build**: 2025-09-30T20:52:39
- **Python**: 3.11.13
- **FastAPI**: 0.104.1
- **Docker**: 적용됨
- **Auto-reload**: 활성화됨 (개발 모드)

---

## 문제 해결 히스토리

### 2025-09-30: MACD 지표 계산 실패 이슈
**증상**: 백테스트 실행 시 0회 거래, "Indicator 'macd' not found" 에러

**원인**:
1. `calculator.py`의 `_calculate_python_code()` 메서드가 `config.get('code')`로 코드 추출
2. Supabase 구조는 `config['formula']['code']`에 코드 저장
3. 결과적으로 `code = ''` (빈 문자열)이 되어 아무것도 실행 안 됨

**해결**:
```python
# calculator.py 라인 781-785
if 'formula' in config and isinstance(config['formula'], dict):
    code = config['formula'].get('code', '')
else:
    code = config.get('code', '')
```

**결과**: MACD 지표가 정상적으로 계산되어 백테스트 실행 가능