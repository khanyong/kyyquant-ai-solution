# NAS 서버 배포 가이드

## 업로드 필요 파일

### 1. 필수 업로드 파일
```
backend/
├── indicators/
│   └── calculator.py          # ⭐ 핵심 변경
├── backtest/
│   └── engine.py              # ⭐ 중요 변경
└── api/
    └── backtest.py            # 변경 없음 (호환성 확인)
```

### 2. 파일별 변경 내용

#### `indicators/calculator.py`
- **DB 전용 모드**: `ENFORCE_DB_INDICATORS` 환경변수로 제어
- **기본값 변경**: true (운영 안전)
- **Fail-fast**: Supabase 미연결 시 즉시 에러
- **캐시 개선**: 종목코드별 독립 캐싱
- **보안 강화**: AST 레벨 검증

#### `backtest/engine.py`
- **하드코딩 제거**: `volume_ma_20` 직접 계산 삭제
- **슬리피지 적용**: 매수/매도 시 불리한 가격 반영
- **포지션 사이즈**: `strategy_config['position_size']` 지원
- **캐시 지원**: stock_code를 calculator에 전달

### 3. 환경변수 설정 (필수)

```bash
# .env.production 또는 docker-compose.yml

# Supabase 연결 (필수)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# 지표 모드 (운영 필수)
ENFORCE_DB_INDICATORS=true  # 운영: true, 개발: false
```

### 4. 배포 스크립트

```bash
#!/bin/bash
# deploy_to_nas.sh

# 1. 백업
echo "Backing up current version..."
ssh nas "cd /path/to/app && cp -r backend backend.backup.$(date +%Y%m%d_%H%M%S)"

# 2. 파일 업로드
echo "Uploading modified files..."
scp indicators/calculator.py nas:/path/to/app/backend/indicators/
scp backtest/engine.py nas:/path/to/app/backend/backtest/

# 3. 환경변수 확인
echo "Checking environment variables..."
ssh nas "cd /path/to/app && grep ENFORCE_DB_INDICATORS .env"

# 4. 서비스 재시작
echo "Restarting services..."
ssh nas "cd /path/to/app && docker-compose restart backend"

echo "Deployment complete!"
```

### 5. 배포 전 체크리스트

- [ ] Supabase 연결 정보 확인
- [ ] `ENFORCE_DB_INDICATORS=true` 설정
- [ ] 기존 백업 생성
- [ ] 테스트 환경에서 검증 완료
- [ ] indicators 테이블 데이터 확인

### 6. 롤백 절차

```bash
# 문제 발생 시
ssh nas "cd /path/to/app && cp -r backend.backup.YYYYMMDD_HHMMSS/* backend/"
ssh nas "cd /path/to/app && docker-compose restart backend"
```

### 7. 검증 방법

```python
# test_nas_deployment.py
import os
os.environ['ENFORCE_DB_INDICATORS'] = 'true'

from indicators.calculator import IndicatorCalculator

# 1. DB 모드 확인
calc = IndicatorCalculator()
assert calc.enforce_db_only == True

# 2. Supabase 지표 테스트
result = calc.calculate(df, {'name': 'sma', 'params': {'period': 20}})
assert 'sma' in result.columns

# 3. 내장 지표 차단 확인
try:
    result = calc.calculate(df, {'name': 'unknown_indicator'})
    assert False, "Should have raised error"
except ValueError as e:
    assert "Supabase" in str(e)

print("All checks passed!")
```

## 주의사항

1. **운영 환경에서는 반드시 `ENFORCE_DB_INDICATORS=true`**
2. **Supabase 연결 정보가 없으면 서버가 시작되지 않음**
3. **기존 전략들이 Supabase indicators 테이블의 지표만 사용하는지 확인**
4. **백업은 필수**

## 배포 후 모니터링

```bash
# 로그 확인
docker logs backend_container | grep "INDICATOR CALCULATOR"
# "DB-ONLY MODE ACTIVE" 메시지 확인

# 에러 로그
docker logs backend_container | grep ERROR
```