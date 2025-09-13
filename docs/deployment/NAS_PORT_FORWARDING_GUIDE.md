# 시놀로지 NAS 포트 포워딩 설정 가이드

## 현재 설정된 외부 접속 주소
- **NAS DSM**: https://khanyong.asuscomm.com:5001
- **N8N**: https://workflow.bll-pro.com
- **REST API (필요)**: https://khanyong.asuscomm.com:8001

## REST API 서버 외부 접속 설정

### 1. 시놀로지 NAS 포트 포워딩 설정

#### DSM에서 설정
1. **제어판** → **외부 액세스** → **라우터 구성**
2. **사용자 지정 포트** 클릭
3. 새 규칙 추가:
   - 설명: `Kiwoom REST API`
   - 프로토콜: `TCP`
   - 외부 포트: `8001`
   - 내부 포트: `8001`
   - 로컬 IP: NAS IP (192.168.50.150)

#### 공유기에서 설정 (ASUS 라우터 기준)
1. 라우터 관리자 페이지 접속
2. **WAN** → **가상 서버 / 포트 포워딩**
3. 새 규칙 추가:
   - 서비스 이름: `Kiwoom API`
   - 포트 범위: `8001`
   - 로컬 IP: `192.168.50.150`
   - 로컬 포트: `8001`
   - 프로토콜: `TCP`

### 2. 리버스 프록시 설정 (HTTPS 지원)

DSM의 리버스 프록시를 사용하여 HTTPS 지원:

1. **제어판** → **로그인 포털** → **고급** → **리버스 프록시**
2. **생성** 클릭
3. 설정 입력:
   ```
   설명: Kiwoom REST API
   원본:
     - 프로토콜: HTTPS
     - 호스트 이름: khanyong.asuscomm.com
     - 포트: 8001
   
   대상:
     - 프로토콜: HTTP
     - 호스트 이름: localhost
     - 포트: 8001
   ```
4. 사용자 지정 헤더 추가 (필요 시):
   - WebSocket 지원: `Upgrade` 및 `Connection` 헤더

### 3. Docker 컨테이너 네트워크 설정

Container Manager에서 확인:
1. **네트워크** 탭에서 컨테이너가 `bridge` 또는 `host` 모드 사용
2. 포트 매핑 확인: `0.0.0.0:8001 → 8001`

### 4. 방화벽 설정

DSM 방화벽에서 포트 허용:
1. **제어판** → **보안** → **방화벽**
2. 규칙 편집/생성
3. 포트 8001 TCP 허용

## Vercel 환경변수 설정

Vercel 대시보드에서:
1. 프로젝트 설정 → Environment Variables
2. 다음 변수 추가:
   ```
   VITE_SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJhb...
   VITE_API_URL=https://khanyong.asuscomm.com:8001
   VITE_WS_URL=wss://khanyong.asuscomm.com:8001/ws
   VITE_N8N_URL=https://workflow.bll-pro.com
   ```

## 테스트 방법

### 로컬 테스트
```bash
# 내부 네트워크에서
curl http://192.168.50.150:8001/
```

### 외부 테스트
```bash
# 외부 네트워크에서 (모바일 데이터 등)
curl https://khanyong.asuscomm.com:8001/
```

## 주의사항

1. **보안**: API 키는 절대 프론트엔드 코드에 하드코딩하지 마세요
2. **CORS**: FastAPI에서 CORS 설정이 되어 있는지 확인
3. **SSL 인증서**: Let's Encrypt 또는 자체 서명 인증서 사용
4. **백업**: 포트 포워딩 규칙 변경 전 현재 설정 백업

## 문제 해결

### 연결 실패 시
1. 포트 포워딩 규칙 확인
2. Docker 컨테이너 실행 상태 확인
3. 방화벽 규칙 확인
4. ISP의 포트 차단 여부 확인 (8001 포트)

### SSL 인증서 오류
- 자체 서명 인증서 사용 시 브라우저에서 예외 추가 필요
- Let's Encrypt 인증서 자동 갱신 설정 확인