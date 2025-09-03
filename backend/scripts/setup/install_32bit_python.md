# 32비트 Python 설치 가이드

## 1. 32비트 Python 다운로드

### 다운로드 링크
- **Python 3.10.11 (32-bit)**: https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe
- 또는 Python 공식 사이트: https://www.python.org/downloads/windows/
  - "Windows installer (32-bit)" 선택

## 2. 설치 방법

1. **다운로드한 설치 파일 실행**
2. **"Add Python 3.10 to PATH" 체크** ✅
3. **"Install Now" 클릭**
4. **설치 경로**: `C:\Python310-32` (기본값)

## 3. 설치 확인

```cmd
# CMD 창에서 실행
C:\Python310-32\python.exe --version
```

예상 출력:
```
Python 3.10.11
```

## 4. 32비트 가상환경 생성

```cmd
cd D:\Dev\auto_stock\backend

# 32비트 Python으로 가상환경 생성
C:\Python310-32\python.exe -m venv venv32

# 가상환경 활성화
venv32\Scripts\activate

# 아키텍처 확인
python -c "import platform; print(platform.architecture())"
# 출력: ('32bit', 'WindowsPE')
```

## 5. 필수 패키지 설치

```cmd
# 가상환경이 활성화된 상태에서
pip install --upgrade pip
pip install PyQt5==5.15.10
pip install pywin32
pip install python-dotenv
pip install requests
```

## 6. 키움 OpenAPI 테스트

```cmd
# 32비트 환경에서 실행
python test_kiwoom_mock.py
```

---

## 자동 설치 스크립트

PowerShell에서 실행:

```powershell
# 1. Chocolatey 설치 (관리자 권한 필요)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. 32비트 Python 설치
choco install python310 --x86 -y

# 3. 확인
py -3.10-32 --version
```

## 주의사항

- 키움 OpenAPI는 **반드시 32비트 Python** 필요
- 64비트 Windows에서도 32비트 Python 설치 가능
- 여러 Python 버전 공존 가능