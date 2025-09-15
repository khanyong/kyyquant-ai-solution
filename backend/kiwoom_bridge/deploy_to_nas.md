# 시놀로지 NAS 배포 가이드

## 1. 사전 준비사항

### 필요한 파일들
- `core/` 디렉터리 (새로 생성된 핵심 모듈)
- `backtest_engine_advanced.py` (수정됨)
- `migrate_templates.py` (신규)
- `test_regression.py` (신규)
- 기존 파일들 (strategy_engine.py, backtest_api.py 등)

## 2. NAS 접속 및 백업

### SSH 접속
```bash
ssh admin@NAS_IP
# 또는 DSM 웹 인터페이스에서 File Station 사용
```

### 기존 코드 백업
```bash
# Docker 컨테이너가 있는 디렉터리로 이동
cd /volume1/docker/auto_stock/backend/kiwoom_bridge

# 백업 생성
cp -r . ../kiwoom_bridge_backup_$(date +%Y%m%d)

# 또는 tar로 압축 백업
tar -czf ../kiwoom_bridge_backup_$(date +%Y%m%d).tar.gz .
```

## 3. 새 코드 업로드

### 방법 1: File Station 사용 (권장)
1. DSM 웹 인터페이스 로그인
2. File Station 열기
3. `/docker/auto_stock/backend/kiwoom_bridge` 경로로 이동
4. 다음 파일/폴더 업로드:
   - `core` 폴더 전체 (드래그 앤 드롭)
   - `backtest_engine_advanced.py` (덮어쓰기)
   - `migrate_templates.py` (신규)
   - `test_regression.py` (신규)

### 방법 2: SCP 사용
```bash
# 로컬 PC에서 실행
scp -r D:\Dev\auto_stock\backend\kiwoom_bridge\core admin@NAS_IP:/volume1/docker/auto_stock/backend/kiwoom_bridge/
scp D:\Dev\auto_stock\backend\kiwoom_bridge\backtest_engine_advanced.py admin@NAS_IP:/volume1/docker/auto_stock/backend/kiwoom_bridge/
scp D:\Dev\auto_stock\backend\kiwoom_bridge\migrate_templates.py admin@NAS_IP:/volume1/docker/auto_stock/backend/kiwoom_bridge/
scp D:\Dev\auto_stock\backend\kiwoom_bridge\test_regression.py admin@NAS_IP:/volume1/docker/auto_stock/backend/kiwoom_bridge/
```

### 방법 3: Git 사용 (버전 관리가 되어 있는 경우)
```bash
cd /volume1/docker/auto_stock/backend/kiwoom_bridge
git pull origin main
```

## 4. Docker 이미지 재빌드

### Dockerfile 수정 (필요한 경우)
```dockerfile
# Dockerfile에 core 모듈 복사 추가 확인
COPY ./core /app/core
COPY ./backtest_engine_advanced.py /app/
COPY ./migrate_templates.py /app/
COPY ./test_regression.py /app/
```

### Docker Compose로 재배포
```bash
cd /volume1/docker/auto_stock/backend/kiwoom_bridge

# 기존 컨테이너 중지
docker-compose down

# 이미지 재빌드
docker-compose build --no-cache kiwoom-bridge

# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f kiwoom-bridge
```

## 5. 기존 전략 템플릿 마이그레이션

### 컨테이너 내부에서 실행
```bash
# 컨테이너 접속
docker exec -it kiwoom-bridge /bin/bash

# Python 환경에서 마이그레이션 실행
python migrate_templates.py

# 또는 특정 파일 마이그레이션
python -c "
from migrate_templates import migrate_file
migrate_file('/app/strategies/old_strategy.json', '/app/strategies/new_strategy.json')
"
```

### Supabase 데이터 마이그레이션
```python
# 컨테이너 내부에서 실행
python -c "
import os
from supabase import create_client
from migrate_templates import migrate_strategy_template
import json

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# 전략 조회
strategies = supabase.table('strategies').select('*').execute()

# 각 전략 마이그레이션
for strategy in strategies.data:
    config = strategy.get('config', {})
    if config:
        migrated = migrate_strategy_template(config)

        # 업데이트
        supabase.table('strategies').update({
            'config': migrated,
            'updated_at': 'now()'
        }).eq('id', strategy['id']).execute()

        print(f'마이그레이션 완료: {strategy['name']}')
"
```

## 6. 테스트 및 검증

### 회귀 테스트 실행
```bash
# 컨테이너 내부에서
docker exec -it kiwoom-bridge python test_regression.py

# 또는 호스트에서 직접
docker exec kiwoom-bridge python test_regression.py
```

### API 엔드포인트 테스트
```bash
# 헬스체크
curl http://localhost:8080/

# 백테스트 API 테스트
curl -X POST http://localhost:8080/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "test",
    "stock_codes": ["005930"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

## 7. 롤백 방법 (문제 발생 시)

```bash
# Docker 컨테이너 중지
docker-compose down

# 백업에서 복원
cd /volume1/docker/auto_stock/backend
rm -rf kiwoom_bridge
mv kiwoom_bridge_backup_$(date +%Y%m%d) kiwoom_bridge

# 또는 tar 백업에서 복원
tar -xzf kiwoom_bridge_backup_$(date +%Y%m%d).tar.gz -C kiwoom_bridge

# 컨테이너 재시작
cd kiwoom_bridge
docker-compose up -d
```

## 8. 환경 변수 확인

`.env` 파일에 필요한 환경 변수가 모두 설정되어 있는지 확인:
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# 키움 API
KIWOOM_APP_KEY=your_app_key
KIWOOM_APP_SECRET=your_app_secret
KIWOOM_ACCOUNT_NO=your_account
KIWOOM_IS_DEMO=true

# 기타
FRONTEND_URL=http://localhost:3000
NAS_IP=192.168.1.100
```

## 9. 모니터링

### 로그 확인
```bash
# 실시간 로그
docker-compose logs -f kiwoom-bridge

# 최근 100줄
docker-compose logs --tail=100 kiwoom-bridge

# 로그 파일 직접 확인
tail -f /volume1/docker/auto_stock/backend/kiwoom_bridge/logs/app.log
```

### 컨테이너 상태 확인
```bash
docker ps | grep kiwoom-bridge
docker stats kiwoom-bridge
```

## 10. 주의사항

1. **백업 필수**: 코드 변경 전 반드시 백업
2. **단계별 테스트**: 각 단계마다 동작 확인
3. **로그 모니터링**: 에러 발생 시 즉시 확인
4. **버전 호환성**: Python 패키지 버전 확인
5. **메모리 사용량**: NAS 리소스 모니터링

## 문제 해결

### ImportError 발생 시
```bash
# 컨테이너 내부에서
pip install --upgrade pandas numpy

# requirements.txt 업데이트
pip freeze > requirements.txt
```

### 권한 문제
```bash
# 파일 권한 설정
chmod -R 755 /volume1/docker/auto_stock/backend/kiwoom_bridge/core
chown -R docker:docker /volume1/docker/auto_stock/backend/kiwoom_bridge
```

### Docker 빌드 캐시 문제
```bash
# 모든 캐시 삭제 후 재빌드
docker system prune -a
docker-compose build --no-cache
```