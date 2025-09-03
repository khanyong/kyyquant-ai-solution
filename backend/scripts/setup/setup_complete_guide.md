# 📋 키움증권 모의투자 환경 설정 완전 가이드

## 현재 상태 및 필요한 작업

### ✅ 완료된 작업
1. 프로젝트 구조 설정 완료
2. API 테스트 스크립트 작성 완료
3. 설정 가이드 문서 작성 완료

### ❌ 필요한 작업
1. **32비트 Python 설치** (필수)
2. **키움 OpenAPI+ 설치** (필수)
3. 모의투자 계정 신청

---

## 📦 Step 1: 32비트 Python 설치

### 다운로드 및 설치
```
1. 다운로드: https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe
2. 설치 시 "Add Python to PATH" 체크
3. 설치 경로: C:\Python310-32
```

### 설치 확인
```cmd
C:\Python310-32\python.exe --version
```

---

## 📦 Step 2: 키움 OpenAPI+ 설치

### 다운로드 및 설치
```
1. 키움증권 홈페이지 접속: https://www3.kiwoom.com/
2. 상단 메뉴 → OpenAPI → 다운로드
3. "OpenAPI+" 다운로드
4. 관리자 권한으로 설치
5. 설치 경로: C:\OpenAPI (변경하지 말 것)
```

### 설치 확인
```cmd
dir C:\OpenAPI
```

---

## 📦 Step 3: 32비트 가상환경 설정

```cmd
# 1. 프로젝트 폴더로 이동
cd D:\Dev\auto_stock\backend

# 2. 32비트 Python으로 가상환경 생성
C:\Python310-32\python.exe -m venv venv32

# 3. 가상환경 활성화
venv32\Scripts\activate

# 4. 필수 패키지 설치
pip install --upgrade pip
pip install PyQt5==5.15.10 pywin32 python-dotenv requests
```

---

## 📦 Step 4: 모의투자 계정 설정

### 키움증권 모의투자 신청
```
1. 키움증권 홈페이지: https://www.kiwoom.com/
2. 로그인 → 모의투자 → 주식 모의투자 신청
3. 모의투자 ID/PW 생성
4. 초기 자금: 1,000만원 (기본)
```

---

## 🚀 Step 5: 테스트 실행

### 환경 테스트
```cmd
# 1. 32비트 환경 활성화
cd D:\Dev\auto_stock\backend
venv32\Scripts\activate

# 2. 아키텍처 확인
python -c "import platform; print(platform.architecture())"
# 예상: ('32bit', 'WindowsPE')

# 3. 키움 API 테스트
python test_kiwoom_mock.py
```

### 예상 결과
```
[OK] 키움 OpenAPI OCX 로드 성공
[OK] 이벤트 핸들러 연결 성공
로그인 창이 표시됩니다...
[OK] 키움증권 로그인 성공!
[OK] 계좌 정보 조회 성공!
     서버: 모의투자
     계좌: 8xxxxxxx-xx
```

---

## 🎯 전략 테스트 준비

### 생성된 파일들
```
backend/
├── test_kiwoom_mock.py      # 키움 OpenAPI 모의투자 테스트
├── test_mock_api.py         # REST API 테스트 (한투용)
├── kiwoom_openapi_bridge.py # OpenAPI 브리지 서버
├── setup_32bit_env.bat      # 32비트 환경 설정
└── venv32/                  # 32비트 가상환경
```

### 다음 단계
1. **기본 전략 구현**
   - 이동평균선 전략
   - RSI 전략
   - 볼린저밴드 전략

2. **백테스트**
   - 과거 데이터로 검증
   - 수익률 분석

3. **모의투자 실전 테스트**
   - 실시간 매매
   - 성과 모니터링

---

## ⚠️ 주의사항

1. **32비트 Python 필수**
   - 키움 OpenAPI는 32비트만 지원
   - 64비트에서는 작동 안 함

2. **관리자 권한**
   - OpenAPI 설치 시 필요
   - OCX 등록 시 필요

3. **방화벽 설정**
   - 키움 서버 접속 허용
   - 포트 9443 개방

---

## 📞 문제 해결

### OCX 로드 실패
```cmd
# OCX 재등록
regsvr32 C:\OpenAPI\bin\khopenapi.ocx
```

### 로그인 실패
```
1. 모의투자 계정 확인
2. HTS에서 먼저 로그인 테스트
3. 공인인증서 확인 (실거래용)
```

### Python 버전 문제
```cmd
# 32비트 Python 직접 실행
C:\Python310-32\python.exe test_kiwoom_mock.py
```

---

## ✅ 체크리스트

- [ ] 32비트 Python 3.10 설치
- [ ] 키움 OpenAPI+ 설치
- [ ] 모의투자 계정 신청
- [ ] 32비트 가상환경 생성
- [ ] PyQt5, pywin32 설치
- [ ] test_kiwoom_mock.py 실행 성공

모든 항목을 완료하면 모의투자 자동매매를 시작할 수 있습니다!