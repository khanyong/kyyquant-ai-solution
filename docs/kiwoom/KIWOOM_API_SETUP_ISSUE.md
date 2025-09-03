# 키움 OpenAPI 연동 이슈 및 해결 방안

## 현재 상황

### ✅ 완료된 사항
1. **키움 OpenAPI 설치 확인** - C:\OpenAPI 폴더에 정상 설치됨
2. **Python 환경 확인** - Python 3.10.6 설치됨
3. **필수 패키지 설치** - PyQt5, pykiwoom, websockets 등 설치 완료

### ❌ 발생한 문제
**Python 아키텍처 불일치**
- 현재: Python 3.10.6 **64비트** 사용 중
- 요구사항: 키움 OpenAPI는 **32비트** Python 필요

### 🔍 문제 증상
```
AttributeError: 'QAxWidget' object has no attribute 'OnEventConnect'
AttributeError: 'QAxWidget' object has no attribute 'OnReceiveTrData'
```

## 해결 방안

### 방법 1: 32비트 Python 설치 (권장)

1. **32비트 Python 다운로드 및 설치**
   ```bash
   # Python 3.10.x Windows 32-bit 다운로드
   # https://www.python.org/downloads/windows/
   # "Windows installer (32-bit)" 선택
   ```

2. **가상환경 생성 (32비트)**
   ```bash
   # 32비트 Python으로 가상환경 생성
   C:\Python310-32\python.exe -m venv backend\venv32
   
   # 가상환경 활성화
   backend\venv32\Scripts\activate
   
   # 필수 패키지 설치
   pip install PyQt5==5.15.10 pykiwoom websockets python-dotenv supabase
   ```

3. **테스트 실행**
   ```bash
   cd backend
   python test_kiwoom_simple.py
   ```

### 방법 2: 키움 REST API 사용 (대안)

키움증권에서 제공하는 REST API를 사용하여 32비트 제약을 우회:

1. **키움 REST API 서버 구축**
   - 별도의 32비트 Python 서버에서 키움 OpenAPI 실행
   - FastAPI로 REST API 엔드포인트 제공
   - 메인 애플리케이션은 64비트 Python 사용 가능

2. **구조**
   ```
   [React 앱] <-> [FastAPI 서버 (64bit)] <-> [키움 Bridge 서버 (32bit)] <-> [키움 OpenAPI]
   ```

### 방법 3: Docker 컨테이너 활용

1. **32비트 Python Docker 이미지 생성**
2. **컨테이너에서 키움 API 서버 실행**
3. **호스트와 WebSocket/REST 통신**

## 즉시 실행 가능한 단계

### Step 1: 32비트 Python 설치
```powershell
# PowerShell 관리자 권한으로 실행
# Chocolatey를 사용한 설치 (선택사항)
choco install python310 --x86 -y
```

### Step 2: 환경 변수 설정
```powershell
# 32비트 Python 경로 추가
$env:PATH = "C:\Python310-32;C:\Python310-32\Scripts;" + $env:PATH
```

### Step 3: 테스트 스크립트 실행
```bash
# 32비트 Python 확인
python -c "import platform; print(platform.architecture())"

# 키움 API 테스트
cd backend
python test_kiwoom_simple.py
```

## 추가 고려사항

1. **프로세스 분리**
   - 키움 API 전용 32비트 프로세스
   - 메인 애플리케이션은 64비트 유지
   - IPC(Inter-Process Communication) 활용

2. **성능 최적화**
   - WebSocket을 통한 실시간 데이터 스트리밍
   - Redis를 활용한 데이터 캐싱
   - 비동기 처리로 응답성 향상

3. **안정성 확보**
   - 프로세스 모니터링 및 자동 재시작
   - 에러 핸들링 강화
   - 로깅 시스템 구축

## 결론

**단기 해결책**: 32비트 Python 설치 후 테스트
**장기 해결책**: REST API 서버 구축으로 아키텍처 분리

이를 통해 키움 OpenAPI의 32비트 제약을 극복하고 안정적인 트레이딩 시스템을 구축할 수 있습니다.