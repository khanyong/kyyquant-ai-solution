# 📦 시놀로지 Container Manager GUI 배포 가이드

## 🚀 SSH 없이 시놀로지 GUI로 직접 배포하기

---

## 📋 Step 1: 파일 업로드 (File Station 사용)

### 1.1 File Station 열기
1. DSM 로그인
2. **File Station** 실행
3. `docker` 공유 폴더로 이동

### 1.2 폴더 생성
1. `docker` 폴더 내에 `kiwoom_bridge` 폴더 생성
2. `kiwoom_bridge` 폴더 내에 하위 폴더 생성:
   - `logs` (로그 저장용)
   - `n8n_workflows` (워크플로우 파일용)

### 1.3 파일 업로드
**File Station**으로 다음 파일들을 `/docker/kiwoom_bridge/`에 업로드:

#### 필수 파일:
- `main.py`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `.env` (아래 내용으로 새로 생성)

#### N8N 워크플로우:
- `n8n_workflows/auto_trading_workflow.json`

### 1.4 .env 파일 생성
1. File Station에서 **텍스트 편집기** 열기
2. 새 파일 생성하고 다음 내용 입력:

```env
# Supabase Configuration
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=실제_SUPABASE_ANON_KEY_입력

# Frontend URL (CORS 설정)
FRONTEND_URL=https://your-app.vercel.app

# 로깅
LOG_LEVEL=INFO
```

3. 파일명을 `.env`로 저장

---

## 📋 Step 2: Container Manager에서 프로젝트 생성

### 2.1 Container Manager 열기
1. DSM 메인 메뉴에서 **Container Manager** 실행
2. 왼쪽 메뉴에서 **프로젝트** 클릭

### 2.2 새 프로젝트 생성
1. **생성** 버튼 클릭
2. 생성 방법 선택: **docker-compose.yml 파일에서 생성**
3. 설정:
   - **프로젝트 이름**: `kiwoom-bridge`
   - **경로**: `/docker/kiwoom_bridge` 선택 (찾아보기 버튼 사용)
   - **소스**: `docker-compose.yml 사용` 선택

### 2.3 docker-compose.yml 수정 (선택사항)
Container Manager에서 직접 편집 가능:

```yaml
version: '3.8'

services:
  kiwoom-bridge:
    build: .
    container_name: kiwoom-bridge
    ports:
      - "8001:8001"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - FRONTEND_URL=${FRONTEND_URL}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 2.4 웹 포털 설정
1. **웹 포털** 탭에서 설정 확인:
   - 로컬 포트: `8001`
   - 컨테이너 포트: `8001`
   - 유형: `http`

2. **다음** 클릭

### 2.5 요약 확인 및 빌드
1. 설정 내용 확인
2. **완료** 버튼 클릭
3. 자동으로 이미지 빌드 시작 (5-10분 소요)

---

## 📋 Step 3: 컨테이너 실행 및 관리

### 3.1 프로젝트 상태 확인
**Container Manager** → **프로젝트**에서:
- 상태가 **실행 중**인지 확인
- 빌드 로그 보기: 프로젝트 선택 → **로그** 버튼

### 3.2 컨테이너 상세 설정
**Container Manager** → **컨테이너**에서:

1. `kiwoom-bridge` 컨테이너 선택
2. **세부 정보** 클릭
3. 확인 사항:
   - 상태: 실행 중
   - 포트 매핑: 8001:8001
   - 자동 재시작: 활성화

### 3.3 리소스 제한 설정 (선택사항)
1. 컨테이너 선택 → **설정** → **리소스 제한**
2. 권장 설정:
   - CPU 제한: 50%
   - 메모리 제한: 512MB

---

## 📋 Step 4: N8N 워크플로우 연결

### 4.1 기존 N8N 접속
```
http://나스IP:5678
```

### 4.2 워크플로우 가져오기
1. **Workflows** → **Import from File**
2. `auto_trading_workflow.json` 선택
3. 워크플로우 수정:
   - HTTP Request 노드의 URL을 `http://localhost:8001`로 변경
   - 또는 `http://kiwoom-bridge:8001` (같은 Docker 네트워크인 경우)

### 4.3 환경 변수 설정
N8N 설정에서:
1. **Settings** → **Variables**
2. 추가:
   - `USER_ID`: Supabase 사용자 ID
   - `DISCORD_WEBHOOK_URL`: 디스코드 웹훅 URL (선택)

---

## 📋 Step 5: 테스트

### 5.1 웹 브라우저에서 테스트
1. 브라우저 열기
2. 주소 입력: `http://나스IP:8001`
3. 응답 확인:
```json
{
  "status": "healthy",
  "message": "Kiwoom REST API Bridge Server",
  "timestamp": "2025-01-12T10:00:00"
}
```

### 5.2 Container Manager에서 로그 확인
1. **Container Manager** → **컨테이너**
2. `kiwoom-bridge` 선택
3. **로그** 버튼 클릭
4. 실시간 로그 확인

### 5.3 프론트엔드 연결 테스트
`src/services/kiwoomApiService.ts` 수정:
```typescript
const baseUrl = 'http://나스IP:8001'
```

---

## 🔧 문제 해결

### 포트 충돌 시
Container Manager에서:
1. 프로젝트 중지
2. **설정** → **웹 포털**
3. 로컬 포트를 `8002`로 변경
4. 프로젝트 재시작

### 빌드 실패 시
1. **프로젝트** → **로그** 확인
2. 일반적인 원인:
   - 메모리 부족: DSM 리소스 모니터 확인
   - 네트워크 문제: pip 패키지 다운로드 실패
   - 파일 누락: File Station에서 파일 확인

### 컨테이너가 계속 재시작되는 경우
1. 컨테이너 로그 확인
2. `.env` 파일 설정 확인
3. healthcheck 비활성화 (테스트용):
   ```yaml
   # healthcheck: 부분을 주석 처리
   ```

---

## 📊 모니터링

### DSM 리소스 모니터
1. **리소스 모니터** 실행
2. **Docker** 탭에서 컨테이너별 리소스 사용량 확인

### Container Manager 대시보드
- CPU 사용률
- 메모리 사용량
- 네트워크 I/O
- 디스크 I/O

---

## ✅ 완료 체크리스트

- [ ] File Station으로 파일 업로드 완료
- [ ] `.env` 파일 생성 및 API 키 입력
- [ ] Container Manager에서 프로젝트 생성
- [ ] 컨테이너 정상 실행 확인
- [ ] 웹 브라우저에서 API 테스트
- [ ] N8N 워크플로우 연결
- [ ] 프론트엔드 연결 설정
- [ ] 모의투자 테스트

---

## 💡 팁

### 백업
1. **Container Manager** → **프로젝트**
2. 프로젝트 선택 → **내보내기**
3. 백업 파일 저장

### 업데이트
1. File Station에서 `main.py` 수정
2. Container Manager에서 프로젝트 재빌드:
   - 프로젝트 선택 → **작업** → **빌드**
   - 또는 **재구성** 선택

### 자동 시작
1. **Container Manager** → **컨테이너**
2. 컨테이너 선택 → **설정**
3. **자동 재시작** 활성화

---

## 🎯 다음 단계

1. **실전 투자 전환**:
   - `.env`에서 실전 API 키 설정
   - N8N 워크플로우에서 `is_test_mode: false`로 변경

2. **보안 강화**:
   - DSM 방화벽에서 8001 포트 제한
   - HTTPS 리버스 프록시 설정

3. **모니터링 강화**:
   - Synology 알림 설정
   - 로그 자동 백업 설정