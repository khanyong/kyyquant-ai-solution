# 🔧 중복 N8N 컨테이너 정리 가이드

## 📋 현재 상황
- **기존 컨테이너**: n8n (설정 완료, 데이터 있음)
- **새 컨테이너**: n8nio-n8n (새로 생성됨, 설정 없음)

---

## 방법 1: 기존 컨테이너 유지 (권장) ✅

### 1. 새 컨테이너 제거
```bash
# Container Manager에서:
1. n8nio-n8n 컨테이너 중지
2. n8nio-n8n 컨테이너 삭제
```

### 2. 기존 컨테이너 업데이트
```bash
# SSH 접속
ssh admin@[NAS_IP]

# 기존 컨테이너 확인
docker ps -a | grep n8n

# 기존 컨테이너 설정 백업
docker inspect n8n > n8n_config_backup.json

# 기존 컨테이너 중지
docker stop n8n

# 최신 이미지로 업데이트
docker pull n8nio/n8n:latest

# 기존 컨테이너 제거 (데이터는 안전!)
docker rm n8n

# 기존 설정으로 새 버전 실행
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /volume1/docker/n8n:/home/node/.n8n \
  -e N8N_HOST=0.0.0.0 \
  [기존 환경변수들] \
  n8nio/n8n:latest
```

---

## 방법 2: 기존 설정 확인 후 복사

### 1. 기존 컨테이너 설정 확인
```bash
# Container Manager에서:
1. n8n (기존) 컨테이너 선택
2. 세부정보 → 환경변수 메모
3. 세부정보 → 볼륨 경로 메모
```

### 2. 설정 내보내기 (SSH)
```bash
# 기존 컨테이너 환경변수 확인
docker inspect n8n | grep -A 20 "Env"

# 기존 볼륨 경로 확인  
docker inspect n8n | grep -A 10 "Mounts"

# 포트 설정 확인
docker inspect n8n | grep -A 5 "PortBindings"
```

### 3. 통합 스크립트
```bash
#!/bin/bash
# 파일명: migrate_n8n.sh

# 기존 설정 추출
OLD_ENV=$(docker inspect n8n --format '{{range .Config.Env}}{{println .}}{{end}}')
OLD_VOLUME=$(docker inspect n8n --format '{{range .Mounts}}{{.Source}}:{{.Destination}}{{end}}')

echo "기존 설정:"
echo "환경변수: $OLD_ENV"
echo "볼륨: $OLD_VOLUME"

# 새 컨테이너로 마이그레이션 확인
read -p "계속하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 기존 컨테이너 중지 및 제거
    docker stop n8n
    docker rm n8n
    
    # 새 컨테이너 중지 및 제거
    docker stop n8nio-n8n
    docker rm n8nio-n8n
    
    # 최신 이미지로 실행
    docker run -d \
      --name n8n \
      --restart unless-stopped \
      -p 5678:5678 \
      -v /volume1/docker/n8n:/home/node/.n8n \
      -e N8N_HOST=0.0.0.0 \
      -e N8N_PORT=5678 \
      n8nio/n8n:latest
fi
```

---

## 방법 3: Container Manager GUI 사용 (가장 쉬움)

### 1. 기존 컨테이너 설정 메모
Container Manager에서:
- **n8n** (기존) → **편집**
- 모든 탭의 설정 스크린샷 또는 메모:
  - 볼륨 탭
  - 포트 설정 탭  
  - 환경 탭
  - 네트워크 탭
- **취소** (저장하지 않음)

### 2. 새 컨테이너 정리
- **n8nio-n8n** → **중지** → **삭제**

### 3. 기존 컨테이너 업데이트
- **n8n** → **중지**
- **작업** → **재설정** (Reset)
- **이미지** 탭 → **n8nio/n8n:latest** 선택
- **실행** → 메모한 설정 적용

---

## ✅ 권장 최종 설정

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /volume1/docker/n8n:/home/node/.n8n \
  -v /volume1/docker/n8n/files:/files \
  -e N8N_HOST=0.0.0.0 \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  -e NODE_ENV=production \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=[기존비밀번호] \
  -e KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk \
  -e KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA \
  -e KIWOOM_ACCOUNT_NO=81101350-01 \
  -e KIWOOM_API_URL=https://mockapi.kiwoom.com \
  n8nio/n8n:latest
```

---

## 🔍 확인 명령어

```bash
# 실행 중인 컨테이너 확인
docker ps | grep n8n

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a | grep n8n

# 컨테이너 로그 확인
docker logs n8n --tail 50

# 접속 테스트
curl -I http://localhost:5678
```

어떤 방법을 선택하시겠습니까?