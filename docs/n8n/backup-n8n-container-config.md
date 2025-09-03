# 📋 기존 N8N 컨테이너 설정 백업 방법

## 방법 1: Container Manager에서 내보내기 (가장 쉬움) ✅

### Container Manager GUI:
1. **컨테이너** 탭
2. `n8n` 컨테이너 선택
3. **작업** → **내보내기** (Export)
4. 설정 파일 다운로드 (`.json` 형식)

이 파일에는 모든 설정이 포함됩니다:
- 환경변수
- 볼륨 매핑
- 포트 설정
- 네트워크 설정

---

## 방법 2: SSH로 설정 추출 📝

### SSH 접속 후 실행:

```bash
# 1. 전체 설정을 JSON 파일로 저장
docker inspect n8n > /volume1/docker/n8n_backup_config.json

# 2. 환경변수만 추출
docker inspect n8n --format '{{range .Config.Env}}{{println .}}{{end}}' > /volume1/docker/n8n_env.txt

# 3. 볼륨 매핑 추출
docker inspect n8n --format '{{range .Mounts}}{{.Source}}:{{.Destination}}{{println}}{{end}}' > /volume1/docker/n8n_volumes.txt

# 4. 포트 매핑 추출
docker inspect n8n --format '{{json .NetworkSettings.Ports}}' > /volume1/docker/n8n_ports.txt

# 5. 전체 실행 명령어 생성
docker inspect n8n --format 'docker run -d \
  --name {{.Name}} \
  --restart {{.HostConfig.RestartPolicy.Name}} \
  {{range .HostConfig.PortBindings}}-p {{range .}}{{.HostPort}}:{{end}}{{end}} \
  {{range .Mounts}}-v {{.Source}}:{{.Destination}} {{end}} \
  {{range .Config.Env}}-e {{.}} {{end}} \
  {{.Config.Image}}' > /volume1/docker/n8n_run_command.sh
```

---

## 방법 3: 설정 복사 스크립트 🔧

### 자동 백업 스크립트 생성:

```bash
#!/bin/bash
# 파일명: backup_n8n_config.sh

BACKUP_DIR="/volume1/docker/n8n_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "=== N8N 컨테이너 설정 백업 ==="

# 1. 전체 설정 백업
docker inspect n8n > $BACKUP_DIR/full_config.json
echo "✓ 전체 설정 저장됨"

# 2. 환경변수 추출
echo "=== 환경변수 ===" > $BACKUP_DIR/environment.txt
docker inspect n8n --format '{{range .Config.Env}}{{println .}}{{end}}' >> $BACKUP_DIR/environment.txt
echo "✓ 환경변수 저장됨"

# 3. 볼륨 설정 추출
echo "=== 볼륨 매핑 ===" > $BACKUP_DIR/volumes.txt
docker inspect n8n --format '{{range .Mounts}}{{.Source}}:{{.Destination}}{{println}}{{end}}' >> $BACKUP_DIR/volumes.txt
echo "✓ 볼륨 설정 저장됨"

# 4. 실행 명령어 생성
echo "#!/bin/bash" > $BACKUP_DIR/recreate_container.sh
echo "# N8N 컨테이너 재생성 스크립트" >> $BACKUP_DIR/recreate_container.sh
echo "" >> $BACKUP_DIR/recreate_container.sh

# Docker run 명령 생성
echo "docker run -d \\" >> $BACKUP_DIR/recreate_container.sh
echo "  --name n8n \\" >> $BACKUP_DIR/recreate_container.sh
echo "  --restart unless-stopped \\" >> $BACKUP_DIR/recreate_container.sh

# 포트 추출
docker inspect n8n --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}  -p {{(index $conf 0).HostPort}}:{{$p}} \{{println}}{{end}}{{end}}' >> $BACKUP_DIR/recreate_container.sh

# 볼륨 추출
docker inspect n8n --format '{{range .Mounts}}  -v {{.Source}}:{{.Destination}} \{{println}}{{end}}' >> $BACKUP_DIR/recreate_container.sh

# 환경변수 추출
docker inspect n8n --format '{{range .Config.Env}}  -e "{{.}}" \{{println}}{{end}}' >> $BACKUP_DIR/recreate_container.sh

# 이미지 추가
echo "  n8nio/n8n:latest" >> $BACKUP_DIR/recreate_container.sh

chmod +x $BACKUP_DIR/recreate_container.sh

echo ""
echo "✅ 백업 완료!"
echo "📁 백업 위치: $BACKUP_DIR"
echo ""
echo "파일 목록:"
ls -la $BACKUP_DIR
```

---

## 방법 4: Container Manager 스크린샷 📸

가장 간단한 방법:
1. Container Manager 열기
2. `n8n` 컨테이너 → **편집**
3. 각 탭 스크린샷:
   - **일반 설정** 탭
   - **볼륨** 탭  
   - **포트 설정** 탭
   - **환경** 탭
   - **네트워크** 탭
4. **취소** 클릭 (변경하지 않음)

---

## 방법 5: Docker Compose 파일로 변환 📄

```bash
# SSH에서 실행
cat > /volume1/docker/n8n_docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    volumes:
      - /volume1/docker/n8n:/home/node/.n8n
    environment:
EOF

# 환경변수 추가
docker inspect n8n --format '{{range .Config.Env}}      - {{.}}{{println}}{{end}}' >> /volume1/docker/n8n_docker-compose.yml

echo "✅ docker-compose.yml 생성 완료"
```

---

## 🔄 설정 복원 방법

### 백업한 설정으로 새 컨테이너 생성:

```bash
# 1. 기존 컨테이너 중지/삭제
docker stop n8n
docker rm n8n

# 2. 백업한 스크립트 실행
bash /volume1/docker/n8n_backup_[날짜]/recreate_container.sh

# 또는 docker-compose 사용
docker-compose -f /volume1/docker/n8n_docker-compose.yml up -d
```

---

## 💡 추천 방법

**지금 바로 실행:**
```bash
# SSH 접속 후
docker inspect n8n > /volume1/docker/n8n_config_backup.json
echo "설정이 /volume1/docker/n8n_config_backup.json에 저장되었습니다"
```

이 파일만 있으면 모든 설정을 복원할 수 있습니다!