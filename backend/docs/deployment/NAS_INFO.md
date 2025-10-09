# 나스 서버 정보

## 🌐 네트워크 정보
- **내부 IP**: `192.168.50.150`
- **외부 DDNS**: `khanyong.asuscomm.com`
- **Cloudflared**: `api.bll-pro.com`

## 🔌 포트 정보
- **외부 포트**: `8080`
- **내부 포트**: `8001`
- **Docker 매핑**: `8080:8001`

## 📍 접속 방법

### 1. 로컬 네트워크에서
```
http://192.168.50.150:8080
http://192.168.50.150:8080/docs
```

### 2. 외부에서 (DDNS)
```
http://khanyong.asuscomm.com:8080
http://khanyong.asuscomm.com:8080/docs
```

### 3. Cloudflared (HTTPS)
```
https://api.bll-pro.com
https://api.bll-pro.com/docs
```

## 🐳 Docker 명령어

### 빌드
```bash
docker-compose build
```

### 실행
```bash
docker-compose up -d
```

### 로그 확인
```bash
docker-compose logs -f
```

### 중지
```bash
docker-compose down
```

## 📁 나스 경로
- **Docker 경로**: `/volume1/docker/auto_stock`
- **로그 경로**: `/volume1/docker/auto_stock/logs`

## 🔐 SSH 접속
```bash
ssh khanyong@192.168.50.150
```
**Note**: admin 계정은 비활성화되어 있음

## ⚙️ 환경 변수
`.env` 파일에 다음 설정 필요:
- SUPABASE_URL
- SUPABASE_KEY
- KIWOOM_APP_KEY (선택)
- KIWOOM_APP_SECRET (선택)