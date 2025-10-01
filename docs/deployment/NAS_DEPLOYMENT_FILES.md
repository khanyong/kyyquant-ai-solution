# NAS 서버 배포 파일 목록

## 🎯 이번 수정으로 업데이트해야 할 파일

### 1. 백테스트 엔진 (핵심)
```
backend/backtest/engine.py
```
**변경 사항:**
- `_resolve_indicator_name()` 메서드 추가 (지표 이름 자동 매핑)
- `_resolve_operand()` 메서드 추가 (피연산자 해석)
- `_validate_strategy_conditions()` 메서드 추가 (Preflight 검증)
- `_check_condition()` 메서드 개선 (매핑 로직 적용)
- `Tuple` import 추가

**중요도:** ⭐⭐⭐⭐⭐ (필수)

### 2. 문서 파일들 (선택)
```
backend/INDICATOR_NAMING_FIX_GUIDE.md
backend/sql_comparison.md
backend/fix_all_strategy_conditions.sql
backend/fix_all_strategy_conditions_improved.sql
```
**중요도:** ⭐⭐ (참고용)

## 📦 전체 배포 권장 파일 목록

### 백엔드 핵심 파일

```
backend/
├── backtest/
│   ├── __init__.py
│   ├── engine.py                    ⭐⭐⭐⭐⭐ (수정됨)
│   └── models.py
├── indicators/
│   └── calculator.py                ⭐⭐⭐⭐
├── strategies/
│   └── manager.py                   ⭐⭐⭐
├── data/
│   └── provider.py                  ⭐⭐⭐
├── api/
│   └── backtest.py                  ⭐⭐⭐
├── main.py                          ⭐⭐⭐⭐
├── requirements.txt                 ⭐⭐⭐
└── .env                            ⭐⭐⭐⭐⭐
```

## 🚀 배포 방법

### 방법 1: 수정된 파일만 업로드 (빠름)

```bash
# 로컬에서
cd D:\Dev\auto_stock

# NAS로 복사 (SCP/SFTP 사용)
scp backend/backtest/engine.py user@nas-ip:/volume1/docker/auto_stock/backend/backtest/

# 또는 WinSCP/FileZilla 사용
```

### 방법 2: 전체 백엔드 재배포 (안전)

```bash
# 1. 백엔드 폴더 압축
cd D:\Dev\auto_stock
tar -czf backend_update.tar.gz backend/

# 2. NAS로 전송
scp backend_update.tar.gz user@nas-ip:/volume1/docker/auto_stock/

# 3. NAS에서 압축 해제
ssh user@nas-ip
cd /volume1/docker/auto_stock/
tar -xzf backend_update.tar.gz

# 4. Docker 컨테이너 재시작
docker-compose restart backend
```

### 방법 3: Git 사용 (권장)

```bash
# 로컬에서 커밋
cd D:\Dev\auto_stock
git add backend/backtest/engine.py
git commit -m "fix: 백테스트 지표 컬럼명 매핑 로직 추가

- 지표 이름 자동 해석 (macd_12_26 -> macd)
- Preflight 검증 추가
- 숫자 문자열 자동 변환 ('0' -> 0)
"
git push

# NAS에서 풀
ssh user@nas-ip
cd /volume1/docker/auto_stock/
git pull
docker-compose restart backend
```

## 📋 배포 체크리스트

### 배포 전

- [ ] 로컬에서 테스트 완료
- [ ] `.env` 파일 백업
- [ ] 데이터베이스 백업 (선택)
- [ ] 현재 실행 중인 백테스트 없음 확인

### 배포 중

- [ ] `backend/backtest/engine.py` 업로드
- [ ] 파일 권한 확인 (`chmod 644`)
- [ ] 소유자 확인 (`chown`)

### 배포 후

- [ ] Docker 컨테이너 재시작
  ```bash
  docker-compose restart backend
  # 또는
  docker restart auto_stock_backend
  ```

- [ ] 로그 확인
  ```bash
  docker logs -f auto_stock_backend
  ```

- [ ] 헬스체크
  ```bash
  curl http://nas-ip:8000/health
  curl http://nas-ip:8000/api/backtest/version
  ```

- [ ] 백테스트 테스트
  - 프론트엔드에서 [템플릿] MACD 시그널 선택
  - 종목: 005930
  - 기간: 2024-01-01 ~ 2024-12-31
  - 실행 후 거래 횟수 확인

## 🔧 NAS 서버 경로

### Synology NAS (일반적)
```
/volume1/docker/auto_stock/
├── backend/
│   ├── backtest/
│   │   └── engine.py          ← 이 파일 교체
│   └── ...
├── docker-compose.yml
└── ...
```

### Docker 컨테이너 내부
```
/app/
├── backtest/
│   └── engine.py
└── ...
```

## 🐳 Docker 관련 명령어

### 컨테이너 재시작
```bash
# 특정 서비스만
docker-compose restart backend

# 전체 재시작
docker-compose restart

# 강제 재빌드
docker-compose up -d --build backend
```

### 로그 확인
```bash
# 실시간 로그
docker-compose logs -f backend

# 최근 100줄
docker-compose logs --tail=100 backend

# 에러만
docker-compose logs backend | grep -i error
```

### 컨테이너 접속
```bash
# 쉘 접속
docker exec -it auto_stock_backend bash

# 파일 확인
docker exec -it auto_stock_backend ls -la /app/backtest/

# Python 실행
docker exec -it auto_stock_backend python -c "from backtest.engine import BacktestEngine; print('OK')"
```

## 🔐 권한 설정

### 파일 권한
```bash
# NAS에서
cd /volume1/docker/auto_stock/backend
chmod 644 backtest/engine.py
chown admin:users backtest/engine.py
```

### Docker 볼륨 권한
```bash
# docker-compose.yml 확인
volumes:
  - ./backend:/app:rw  # 읽기/쓰기 권한
```

## 📊 배포 후 검증

### 1. 백엔드 로그 확인
```bash
docker logs auto_stock_backend 2>&1 | grep -i "engine"
```

**기대 출력:**
```
INFO:     Application startup complete.
[Engine] Initialized successfully
```

### 2. API 테스트
```bash
# 버전 확인
curl http://nas-ip:8000/api/backtest/version

# 간단한 백테스트
curl -X POST http://nas-ip:8000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "82b9e26e-e115-4d43-a81b-1fa1f444acd0",
    "stock_codes": ["005930"],
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "initial_capital": 10000000
  }'
```

### 3. 지표 매핑 검증
```bash
# 로그에서 확인
docker logs auto_stock_backend 2>&1 | grep "\[Engine\]"
```

**기대 로그:**
```
[Engine] [OK] Strategy validation PASSED
[Engine] Signal evaluation complete: X buy signals, Y sell signals
```

## 🚨 트러블슈팅

### 문제 1: 파일이 업데이트되지 않음

**원인:** Docker 볼륨 마운트 문제

**해결:**
```bash
# 컨테이너 완전히 재시작
docker-compose down
docker-compose up -d

# 또는 볼륨 확인
docker-compose config | grep volumes
```

### 문제 2: Import 에러

**증상:**
```
ModuleNotFoundError: No module named 'backtest.engine'
```

**해결:**
```bash
# Python 경로 확인
docker exec -it auto_stock_backend python -c "import sys; print(sys.path)"

# __init__.py 존재 확인
docker exec -it auto_stock_backend ls -la /app/backtest/__init__.py
```

### 문제 3: 권한 에러

**증상:**
```
PermissionError: [Errno 13] Permission denied
```

**해결:**
```bash
# NAS에서
cd /volume1/docker/auto_stock
chmod -R 755 backend/
chown -R admin:users backend/
```

## 📝 배포 기록 템플릿

```markdown
# 배포 기록

**날짜:** 2025-09-30
**담당자:** [이름]
**버전:** v1.1.0

## 변경 사항
- 백테스트 엔진 지표 컬럼명 매핑 로직 추가
- Preflight 검증 기능 추가

## 배포된 파일
- backend/backtest/engine.py

## 테스트 결과
- [템플릿] MACD 시그널: ✅ 거래 15회
- [템플릿] RSI 반전: ✅ 거래 12회
- [템플릿] 골든크로스: ✅ 거래 3회

## 이슈
- 없음

## 롤백 방법
```bash
git checkout HEAD~1 backend/backtest/engine.py
docker-compose restart backend
```
```

## 📌 요약

**최소 필수 파일:**
- ✅ `backend/backtest/engine.py` (수정됨)

**권장 배포 방법:**
1. Git push/pull (가장 안전)
2. SCP로 파일 복사 (빠름)
3. Docker 이미지 재빌드 (완전)

**배포 후 필수 작업:**
```bash
docker-compose restart backend
docker logs -f auto_stock_backend
# 백테스트 테스트 실행
```