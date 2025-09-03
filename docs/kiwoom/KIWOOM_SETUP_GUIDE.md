# 키움 OpenAPI+ 및 KOA Studio 설치 가이드

## 1. OpenAPI+ 설치

### 필수 요구사항
- Windows 10/11 (64bit)
- Internet Explorer 11 이상
- .NET Framework 4.5 이상
- **관리자 권한 필수**

### 설치 순서
1. **관리자 권한으로 설치**
   ```cmd
   # OpenAPI+ 설치파일 우클릭 → "관리자 권한으로 실행"
   ```

2. **설치 경로 확인**
   - 기본 경로: `C:\OpenAPI`
   - 경로 변경 금지 (하드코딩된 경로 참조)

3. **설치 후 확인사항**
   - `C:\OpenAPI\bin` 폴더 생성 확인
   - OCX 파일 등록 확인: `khopenapi.ocx`, `khoapicomm.ocx`

## 2. KOA Studio 설치

### 설치 방법
1. **OpenAPI+ 설치 완료 후 진행**
2. **파일 복사 위치**
   ```
   C:\OpenAPI\
   ├── KOAStudioSA.exe  (KOA Studio 실행파일)
   ├── KOALoader.dll    (필수 DLL)
   └── bin\             (OpenAPI+ 기본 파일들)
   ```

## 3. 계좌 접속 문제 해결

### 문제 진단 체크리스트

#### A. 버전 호환성 확인
1. OpenAPI+ 최신 버전 확인
2. KOA Studio 버전과 OpenAPI+ 버전 호환성

#### B. 로그인 설정 확인
1. **KOA Studio 실행 전 확인사항**
   - 키움증권 홈페이지에서 OpenAPI 사용 신청 완료
   - 모의투자 신청 (모의투자 계좌 사용 시)
   - API 접속 비밀번호 설정

2. **로그인 정보**
   - 아이디: 키움증권 아이디
   - 비밀번호: 일반 로그인 비밀번호
   - 인증서 비밀번호: 공인인증서 비밀번호
   - 계좌 비밀번호: 계좌 비밀번호 (별도 설정)

#### C. 방화벽/백신 설정
```cmd
# Windows Defender 방화벽 예외 추가
netsh advfirewall firewall add rule name="KOA Studio" dir=in action=allow program="C:\OpenAPI\KOAStudioSA.exe" enable=yes
netsh advfirewall firewall add rule name="OpenAPI" dir=in action=allow program="C:\OpenAPI\bin\khoapicomm.exe" enable=yes
```

#### D. 레지스트리 확인
```cmd
# 관리자 권한 CMD에서 실행
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\KHOpenAPI"
```

## 4. 일반적인 오류 해결

### 오류: "계좌 확인 불가"
1. **OCX 재등록**
   ```cmd
   # 관리자 권한 CMD에서 실행
   cd C:\OpenAPI
   regsvr32 /u khopenapi.ocx
   regsvr32 khopenapi.ocx
   regsvr32 /u khoapicomm.ocx
   regsvr32 khoapicomm.ocx
   ```

2. **버전 관리자 실행**
   - `C:\OpenAPI\VersionAgent.exe` 실행
   - 최신 버전 업데이트

3. **호환성 모드 설정**
   - KOAStudioSA.exe 우클릭 → 속성
   - 호환성 탭 → "Windows 7 호환 모드" 체크
   - "관리자 권한으로 실행" 체크

### 오류: "로그인 실패"
1. **인터넷 옵션 설정**
   - Internet Explorer 실행
   - 도구 → 인터넷 옵션 → 보안 탭
   - "신뢰할 수 있는 사이트" 선택
   - 사이트 추가: `https://*.kiwoom.com`

2. **TLS 설정**
   - 인터넷 옵션 → 고급 탭
   - TLS 1.2 사용 체크

## 5. 추가 확인사항

### 모의투자 계좌 사용 시
1. [키움증권 홈페이지](https://www.kiwoom.com) 로그인
2. 모의투자 신청 메뉴
3. 모의투자 계좌번호 확인
4. KOA Studio에서 모의투자 서버 선택

### 실계좌 사용 시
1. OpenAPI 사용 신청 완료 확인
2. API 전용 계좌비밀번호 설정
3. 공인인증서 유효기간 확인

## 6. 테스트 절차

1. **KOA Studio 실행**
   ```cmd
   # 관리자 권한으로 실행
   C:\OpenAPI\KOAStudioSA.exe
   ```

2. **로그인 테스트**
   - 파일 → 로그인
   - 서버 구분 선택 (모의/실제)
   - 로그인 정보 입력

3. **계좌 조회 테스트**
   - 조회 → 계좌 → 계좌평가잔고내역
   - 계좌번호 선택
   - 조회 실행

## 문제 지속 시 점검사항

1. **Windows 이벤트 로그 확인**
   - 이벤트 뷰어 → Windows 로그 → 응용 프로그램
   - KOA 또는 OpenAPI 관련 오류 확인

2. **프로세스 확인**
   ```cmd
   tasklist | findstr "khoa"
   ```

3. **네트워크 연결 확인**
   ```cmd
   ping www.kiwoom.com
   nslookup www.kiwoom.com
   ```

## 지원 연락처
- 키움증권 OpenAPI 고객센터: 1544-9000
- OpenAPI 전용 상담: 평일 08:00-17:00