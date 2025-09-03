# 📦 시놀로지 NAS Container N8N 업그레이드 가이드

## 🔍 현재 버전 확인

### 1. Container Manager 접속
- DSM → Container Manager (구 Docker)
- 컨테이너 탭 → n8n 컨테이너 확인

### 2. 현재 버전 확인
```bash
# SSH 접속 후
docker ps | grep n8n
docker exec -it [컨테이너명] n8n --version
```

---

## 📋 업그레이드 전 백업 (중요!)

### 1. N8N 데이터 백업
```bash
# SSH로 NAS 접속
ssh admin@[NAS_IP]

# n8n 데이터 위치 확인
docker inspect n8n | grep -A 5 Mounts

# 백업 생성
sudo cp -r /volume1/docker/n8n /volume1/docker/n8n_backup_$(date +%Y%m%d)
```

### 2. 워크플로우 내보내기
- N8N 웹 UI 접속
- Settings → Download all workflows
- 백업 파일 저장

---

## 🚀 업그레이드 방법

### 방법 1: Container Manager GUI 사용 (권장)

1. **Container Manager 열기**
2. **레지스트리** 탭
3. **n8nio/n8n** 검색
4. **다운로드** → latest 태그 선택
5. **이미지** 탭 → 새 이미지 다운로드 확인
6. **컨테이너** 탭 → n8n 컨테이너 선택
7. **작업** → **중지**
8. **작업** → **지우기** (설정은 유지됨)
9. **이미지** 탭 → n8nio/n8n:latest 선택
10. **실행** → 이전과 동일한 설정 적용

### 방법 2: Docker Compose 사용 (고급)

`docker-compose.yml` 파일:
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - '5678:5678'
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_password
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=http://[NAS_IP]:5678/
      - N8N_ENCRYPTION_KEY=your_encryption_key
    volumes:
      - /volume1/docker/n8n:/home/node/.n8n
      - /volume1/docker/n8n/files:/files
    networks:
      - n8n-network

networks:
  n8n-network:
    driver: bridge
```

실행 명령:
```bash
# 기존 컨테이너 중지 및 제거
docker stop n8n
docker rm n8n

# 새 버전으로 실행
docker-compose pull
docker-compose up -d
```

### 방법 3: Docker 명령어 직접 사용

```bash
# 1. 새 이미지 다운로드
docker pull n8nio/n8n:latest

# 2. 기존 컨테이너 중지 및 제거
docker stop n8n
docker rm n8n

# 3. 새 컨테이너 실행
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /volume1/docker/n8n:/home/node/.n8n \
  -v /volume1/docker/n8n/files:/files \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=your_password \
  -e N8N_HOST=0.0.0.0 \
  -e N8N_PORT=5678 \
  -e NODE_ENV=production \
  n8nio/n8n:latest
```

---

## ✅ 업그레이드 후 확인

### 1. 컨테이너 상태 확인
```bash
docker ps | grep n8n
docker logs n8n --tail 50
```

### 2. 웹 UI 접속
```
http://[NAS_IP]:5678
```

### 3. 버전 확인
- Settings → Version info
- 또는 SSH: `docker exec -it n8n n8n --version`

### 4. 워크플로우 테스트
- 기존 워크플로우 실행 테스트
- 문제 발생시 로그 확인

---

## 🔧 문제 해결

### 컨테이너 시작 안됨
```bash
# 로그 확인
docker logs n8n

# 권한 문제시
sudo chown -R 1000:1000 /volume1/docker/n8n
```

### 데이터 손실시
```bash
# 백업에서 복구
sudo rm -rf /volume1/docker/n8n
sudo cp -r /volume1/docker/n8n_backup_[날짜] /volume1/docker/n8n
```

### 포트 충돌
```bash
# 사용 중인 포트 확인
netstat -tulpn | grep 5678

# 다른 포트로 변경
docker run ... -p 5679:5678 ...
```

---

## 📌 환경변수 추가 (키움 API용)

Container 설정에 추가:
```
KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
KIWOOM_ACCOUNT_NO=81101350-01
KIWOOM_API_URL=https://mockapi.kiwoom.com
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_ANON_KEY=[Supabase 키]
```

---

## 🎯 권장 버전
- **최신 안정 버전**: n8nio/n8n:latest
- **특정 버전 고정**: n8nio/n8n:1.20.0 (예시)

업그레이드 완료 후 워크플로우 임포트하시면 됩니다!