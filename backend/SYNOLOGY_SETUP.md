# 시놀로지 Container Manager 설정 가이드

## 📋 사전 준비사항

1. **Container Manager** 설치 (구 Docker 패키지)
2. **SSH 활성화** (제어판 > 터미널 및 SNMP)
3. **공유 폴더 생성**: `/volume1/docker/auto_stock`

## 🚀 Container Manager GUI 설정 방법

### 1단계: 파일 업로드
1. File Station 열기
2. `/docker/auto_stock` 폴더로 이동
3. backend_new 폴더의 모든 파일 업로드

### 2단계: 프로젝트 생성

1. **Container Manager** 실행
2. 왼쪽 메뉴에서 **프로젝트** 클릭
3. **생성** 버튼 클릭
4. 프로젝트 설정:
   - **프로젝트 이름**: `auto-stock`
   - **경로**: `/docker/auto_stock` 선택
   - **소스**: `docker-compose.synology.yml 파일 업로드` 선택

### 3단계: 환경 변수 설정

Container Manager에서 직접 설정하거나 .env 파일 사용:

```env
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
KIWOOM_ACCOUNT_NO=81101350
KIWOOM_IS_DEMO=true
```

### 4단계: 빌드 및 실행

1. **빌드** 버튼 클릭
2. 빌드 완료 후 **실행** 버튼 클릭
3. 컨테이너 상태 확인

## 🖥️ SSH를 통한 설정 방법

```bash
# 1. SSH 접속
ssh khanyong@192.168.50.150

# 2. 폴더 이동
cd /volume1/docker/auto_stock

# 3. 권한 설정
sudo chown -R $(whoami):users .
chmod 755 .

# 4. Docker Compose 실행
sudo docker-compose -f docker-compose.synology.yml up -d --build

# 5. 로그 확인
sudo docker-compose -f docker-compose.synology.yml logs -f

# 6. 컨테이너 상태 확인
sudo docker ps
```

## 🔧 문제 해결

### 포트 충돌
```bash
# 사용 중인 포트 확인
sudo netstat -tulpn | grep 8080

# 컨테이너 중지
sudo docker stop auto-stock-backend
```

### 권한 문제
```bash
# Docker 그룹에 사용자 추가
sudo synogroup --member docker khanyong

# 로그아웃 후 재접속
```

### 빌드 실패
```bash
# 캐시 삭제 후 재빌드
sudo docker system prune -a
sudo docker-compose -f docker-compose.synology.yml build --no-cache
```

## 📡 접속 확인

### 로컬 네트워크
- http://192.168.50.150:8080
- http://192.168.50.150:8080/docs

### 외부 접속 (Cloudflared)
- https://api.bll-pro.com
- https://api.bll-pro.com/docs

## 📝 Container Manager 팁

1. **자동 시작**: 컨테이너 설정에서 "자동 재시작" 활성화
2. **리소스 제한**: CPU/메모리 제한 설정 가능
3. **로그 확인**: 컨테이너 우클릭 > 세부정보 > 로그
4. **터미널 접속**: 컨테이너 우클릭 > 세부정보 > 터미널

## ⚠️ 주의사항

1. **방화벽**: DSM 방화벽에서 8080 포트 허용
2. **리버스 프록시**: 필요시 Control Panel > Application Portal > Reverse Proxy
3. **백업**: Container Manager > 설정 > 내보내기/가져오기