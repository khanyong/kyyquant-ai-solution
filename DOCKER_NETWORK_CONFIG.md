# Docker 네트워크 구성 가이드

## 시놀로지 NAS Docker 네트워크 설정

### 네트워크 정보
- **Bridge Network**: `trading-network`
- **Gateway IP**: `172.20.0.1`
- **Subnet**: `172.20.0.0/16`

### 서비스 접속 정보

#### 1. kiwoom-bridge (REST API)
- **컨테이너 내부**: `http://kiwoom-bridge:8001`
- **호스트에서**: `http://172.20.0.1:8001`
- **외부에서**: `http://[NAS_IP]:8001`

#### 2. n8n (워크플로우 자동화)
- **컨테이너 내부**: `http://n8n:5678`
- **호스트에서**: `http://172.20.0.1:5678`
- **외부에서**: `http://[NAS_IP]:5678`

### n8n에서 kiwoom-bridge API 호출

n8n 워크플로우에서 HTTP Request 노드 설정:
```
URL: http://172.20.0.1:8001/api/market/current-price
Method: POST
Headers:
  Content-Type: application/json
Body:
  {
    "stock_code": "005930"
  }
```

### 네트워크 연결 확인

```bash
# SSH로 NAS 접속 후
# 1. 네트워크 목록 확인
sudo docker network ls

# 2. trading-network 상세 정보
sudo docker network inspect trading-network

# 3. 컨테이너 네트워크 연결 상태
sudo docker inspect kiwoom-bridge | grep NetworkMode
sudo docker inspect n8n | grep NetworkMode

# 4. n8n을 trading-network에 연결 (필요시)
sudo docker network connect trading-network n8n
```

### 트러블슈팅

#### 연결 실패 시
1. 방화벽 확인
   ```bash
   sudo iptables -L
   ```

2. 포트 리스닝 확인
   ```bash
   sudo netstat -tulpn | grep 8001
   sudo netstat -tulpn | grep 5678
   ```

3. 컨테이너 간 통신 테스트
   ```bash
   # n8n에서 kiwoom-bridge로
   sudo docker exec n8n ping 172.20.0.1
   sudo docker exec n8n curl http://172.20.0.1:8001/
   
   # kiwoom-bridge에서 n8n으로
   sudo docker exec kiwoom-bridge curl http://172.20.0.1:5678/
   ```

### 환경 변수 설정

`.env` 파일:
```env
# API 접속 설정
VITE_API_URL=http://172.20.0.1:8001
VITE_WS_URL=ws://172.20.0.1:8001/ws

# NAS 설정
NAS_IP=192.168.1.100  # 실제 NAS IP로 변경
N8N_URL=http://172.20.0.1:5678
```

### 보안 고려사항

1. **내부 네트워크만 사용**: 172.20.0.1은 Docker 내부 네트워크
2. **외부 접근 제한**: 필요시 NAS 방화벽에서 특정 IP만 허용
3. **HTTPS 적용**: 프로덕션 환경에서는 SSL/TLS 인증서 적용 권장

## 참고 사항

- Docker 브리지 네트워크의 기본 게이트웨이는 보통 `172.17.0.1`이지만, 
  커스텀 네트워크 생성 시 `172.18.0.1`, `172.19.0.1`, `172.20.0.1` 등으로 증가
- 시놀로지 Container Manager에서 네트워크 설정 확인 가능
- 재부팅 후에도 IP가 유지되도록 docker-compose.yml에 네트워크 설정 명시