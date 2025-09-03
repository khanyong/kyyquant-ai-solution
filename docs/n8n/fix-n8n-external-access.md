# 🔧 N8N 외부 접속 문제 해결 가이드

## 1️⃣ Container 설정 확인

### Container Manager에서 확인:
1. **컨테이너** 탭 → n8n 선택
2. **세부 정보** 클릭
3. **포트 설정** 확인:
   - 로컬 포트: 5678
   - 컨테이너 포트: 5678
   - 프로토콜: TCP

### 환경변수 확인/수정:
```
N8N_HOST=0.0.0.0  # 중요! localhost가 아닌 0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://[NAS_외부IP]:5678/
N8N_EDITOR_BASE_URL=http://[NAS_외부IP]:5678/
```

---

## 2️⃣ 시놀로지 방화벽 설정

### DSM 방화벽:
1. **제어판** → **보안** → **방화벽**
2. **규칙 편집**
3. **생성** 클릭
4. 설정:
   - 포트: **사용자 정의**
   - 프로토콜: **TCP**
   - 포트: **5678**
   - 소스 IP: **모두** (또는 특정 IP)
   - 동작: **허용**

---

## 3️⃣ 공유기 포트포워딩

### 공유기 관리 페이지:
1. 192.168.1.1 또는 192.168.0.1 접속
2. **포트포워딩** 메뉴
3. 규칙 추가:
   ```
   외부 포트: 5678
   내부 IP: [NAS 내부 IP]
   내부 포트: 5678
   프로토콜: TCP
   ```

---

## 4️⃣ Docker 명령어로 재시작

SSH로 접속 후:

```bash
# 현재 컨테이너 확인
docker ps -a | grep n8n

# 컨테이너 중지 및 제거
docker stop n8n
docker rm n8n

# 외부 접속 가능한 설정으로 재실행
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /volume1/docker/n8n:/home/node/.n8n \
  -e N8N_HOST=0.0.0.0 \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  -e NODE_ENV=production \
  -e WEBHOOK_URL=http://$(curl -s ifconfig.me):5678/ \
  -e N8N_EDITOR_BASE_URL=http://$(curl -s ifconfig.me):5678/ \
  n8nio/n8n:latest
```

---

## 5️⃣ 접속 테스트

### 내부 접속:
```
http://[NAS_내부IP]:5678
예: http://192.168.1.100:5678
```

### 외부 접속:
```
http://[공인IP]:5678
```

### 공인 IP 확인:
```bash
curl ifconfig.me
```

---

## 6️⃣ 보안 설정 (권장)

### Basic Auth 설정:
```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /volume1/docker/n8n:/home/node/.n8n \
  -e N8N_HOST=0.0.0.0 \
  -e N8N_PORT=5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=your_secure_password \
  n8nio/n8n:latest
```

### HTTPS 설정 (선택):
Synology 리버스 프록시 사용:
1. **제어판** → **응용 프로그램 포털** → **역방향 프록시**
2. **생성**:
   - 소스: HTTPS, 포트 443, n8n.yourdomain.com
   - 대상: HTTP, localhost, 5678

---

## 7️⃣ 문제 해결

### 로그 확인:
```bash
docker logs n8n --tail 100
```

### 포트 사용 확인:
```bash
netstat -tulpn | grep 5678
```

### 방화벽 상태:
```bash
sudo iptables -L -n | grep 5678
```

### Container 네트워크 확인:
```bash
docker port n8n
docker inspect n8n | grep -A 10 "NetworkSettings"
```

---

## 🆘 빠른 해결법

Container Manager에서 컨테이너 편집:
1. **중지** → **편집**
2. **네트워크** 탭:
   - ✅ "호스트 네트워크 사용" 체크
3. **환경** 탭:
   - N8N_HOST = 0.0.0.0 추가
4. **적용** → **실행**

이렇게 하면 외부 접속이 가능해집니다!