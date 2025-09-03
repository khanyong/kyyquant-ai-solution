# Scripts Directory

## 📁 Directory Structure

### 📂 kiwoom/
키움 OpenAPI 설치 및 설정 관련 스크립트
- **check_and_fix_ocx.bat** - OCX 파일 확인 및 수정
- **check_openapi_install.bat** - OpenAPI 설치 확인
- **diagnose_openapi.bat** - OpenAPI 진단
- **download_khoapicomm.bat** - KHOpenAPI 컴포넌트 다운로드
- **download_missing_files.ps1** - 누락된 파일 다운로드 (PowerShell)
- **fix_koa_studio.bat** - KOA Studio 문제 해결
- **fix_ocx_registration.bat** - OCX 등록 문제 해결
- **fix_openapi_final.bat** - OpenAPI 최종 수정
- **force_install_openapi.ps1** - OpenAPI 강제 설치 (PowerShell)
- **manual_fix_openapi.bat** - OpenAPI 수동 수정
- **register_ocx.bat** - OCX 파일 등록

### 📂 tests/
테스트 스크립트
- **test_api_simple.py** - 간단한 API 테스트
- **test_kiwoom_api.py** - 키움 API 테스트
- **test_kiwoom_official.py** - 키움 공식 API 테스트

## 🔧 Usage

### 키움 OpenAPI 설치
```bash
# 1. OpenAPI 설치 확인
scripts/kiwoom/check_openapi_install.bat

# 2. 문제 진단
scripts/kiwoom/diagnose_openapi.bat

# 3. OCX 등록
scripts/kiwoom/register_ocx.bat
```

### 테스트 실행
```bash
# Python 테스트 실행
python scripts/tests/test_kiwoom_api.py
```

## ⚠️ 주의사항
- 대부분의 배치 파일은 관리자 권한이 필요합니다
- Windows 환경에서만 실행 가능합니다
- 키움 OpenAPI가 사전에 설치되어 있어야 합니다