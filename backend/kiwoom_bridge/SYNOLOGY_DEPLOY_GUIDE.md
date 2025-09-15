# Synology NAS 배포 가이드 (Container Manager)

## 🔴 중요: 컨테이너가 0 거래를 보이는 문제 해결

### 문제 원인
Docker 컨테이너가 빌드 시점의 코드만 사용하고, 최신 코드 변경사항을 반영하지 못함.

### 해결 방법

## 방법 1: 개발용 docker-compose 사용 (권장) 🟢

1. **docker-compose.dev.yml 사용**
   ```bash
   # Container Manager에서 프로젝트 생성 시
   # docker-compose.yml 대신 docker-compose.dev.yml 업로드
   ```

2. **프로젝트 생성**
   - Container Manager → 프로젝트 → 생성
   - 이름: `kiwoom-bridge-dev`
   - 경로: `/docker/kiwoom_bridge/`
   - 소스: `docker-compose.dev.yml` 업로드

3. **빌드 및 실행**
   - 프로젝트 선택 → 빌드
   - 빌드 완료 후 자동 시작

## 방법 2: 기존 docker-compose.yml 수정

1. **볼륨 마운트 추가** (이미 수정됨)
   ```yaml
   volumes:
     - ./:/app  # 전체 코드 디렉토리 마운트
     - ./logs:/app/logs
     - ./.env:/app/.env
   ```

2. **재빌드**
   - Container Manager → 프로젝트 선택
   - 액션 → 중지
   - 액션 → 빌드 (캐시 없이)
   - 액션 → 시작

## 방법 3: SSH로 직접 실행

```bash
# SSH 접속
ssh admin@[NAS_IP] -p [SSH_PORT]

# 프로젝트 디렉토리로 이동
cd /volume1/docker/kiwoom_bridge

# 기존 컨테이너 정리
docker-compose down
docker system prune -f

# 캐시 없이 재빌드
docker-compose build --no-cache

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 📋 배포 체크리스트

### 1. 파일 업로드
- [ ] 모든 Python 파일 업로드 완료
- [ ] core/ 디렉토리 업로드 완료
- [ ] docker-compose.yml 또는 docker-compose.dev.yml 업로드
- [ ] .env 파일 업로드
- [ ] requirements.txt 업로드

### 2. 컨테이너 빌드
- [ ] Container Manager에서 프로젝트 생성
- [ ] 빌드 실행 (캐시 없이)
- [ ] 컨테이너 시작

### 3. 검증
```bash
# 로컬에서 실행
python test_container.py [NAS_IP] 8080

# 또는 상세 검증
python verify_container.py http://[NAS_IP]:8080
```

### 4. 확인 사항
- [ ] 헬스체크 통과 (`http://[NAS_IP]:8080/`)
- [ ] 버전 확인 (`http://[NAS_IP]:8080/api/backtest/version`)
- [ ] 백테스트 실행 (거래 발생 확인)

## 🔍 디버깅

### 컨테이너 로그 확인
```bash
# Container Manager GUI
프로젝트 → 로그

# SSH
docker-compose logs -f kiwoom-bridge
```

### 버전 확인
```bash
# 버전 엔드포인트 호출
curl http://[NAS_IP]:8080/api/backtest/version
```

### 파일 동기화 확인
```bash
# 컨테이너 내부 파일 확인
docker exec -it kiwoom-bridge ls -la /app/
docker exec -it kiwoom-bridge cat /app/backtest_api.py | head -20
```

## ⚠️ 주의사항

1. **볼륨 마운트**: 개발 중에만 사용, 프로덕션에서는 보안상 제거
2. **캐시 문제**: 항상 `--no-cache` 옵션으로 빌드
3. **권한 문제**: NAS 공유 폴더 권한 확인
4. **네트워크**: 방화벽에서 8080 포트 열기

## 🚀 빠른 시작 (권장)

1. 모든 파일을 `/volume1/docker/kiwoom_bridge/`에 업로드
2. Container Manager에서 `docker-compose.dev.yml`로 프로젝트 생성
3. 빌드 및 실행
4. `python test_container.py [NAS_IP] 8080` 실행하여 확인

## 📞 문제 해결

거래가 여전히 0회인 경우:

1. **코드 버전 확인**
   ```bash
   python verify_container.py http://[NAS_IP]:8080
   ```

2. **전략 데이터 확인**
   - Supabase에서 전략 config 확인
   - 지표와 조건이 올바른지 확인

3. **주가 데이터 확인**
   - Supabase에 해당 기간 데이터가 있는지 확인

4. **완전 재설치**
   ```bash
   # 모든 것 삭제
   docker-compose down -v
   docker system prune -af

   # 새로 빌드
   docker-compose -f docker-compose.dev.yml build --no-cache
   docker-compose -f docker-compose.dev.yml up -d
   ```