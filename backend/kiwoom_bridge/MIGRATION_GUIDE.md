# Supabase 전략 마이그레이션 가이드

## 문제 상황
- **증상**: 백테스트 실행 시 거래가 0회로 표시됨
- **원인**: Supabase에 저장된 전략의 `indicators` 배열이 비어있음
- **추가 문제**: 대문자 지표명, operator 형식 불일치

## 해결 방법

### 1. 로컬에서 실행 (권장)

```bash
# 1. backend/kiwoom_bridge 디렉토리로 이동
cd backend/kiwoom_bridge

# 2. Python 환경 활성화 (있는 경우)
# conda activate auto_stock 또는 venv 활성화

# 3. 마이그레이션 스크립트 실행
python fix_all_strategies.py
```

### 2. Docker 컨테이너에서 실행

```bash
# 1. 스크립트를 컨테이너에 복사
docker cp fix_all_strategies.py kiwoom-bridge:/app/

# 2. 컨테이너에서 실행
docker exec -it kiwoom-bridge python /app/fix_all_strategies.py
```

### 3. Synology NAS에서 실행

```bash
# 1. SSH로 NAS 접속
ssh your_nas_user@nas_ip

# 2. Docker 디렉토리로 이동
cd /volume1/docker/auto_stock/backend/kiwoom_bridge

# 3. 스크립트 실행
docker exec -it kiwoom-bridge python fix_all_strategies.py
```

## 스크립트 동작

### 자동 수정 항목

1. **빈 indicators 배열 채우기**
   - templateId가 있으면 해당 템플릿의 기본 지표 추가
   - Stage 전략이면 stage 설정에서 지표 추출
   - 조건문에서 사용된 지표명으로부터 추론

2. **대소문자 변환**
   - `MA_20` → `ma_20`
   - `RSI_14` → `rsi_14`
   - `CROSS_ABOVE` → `cross_above`

3. **params 구조 추가**
   ```javascript
   // 변경 전
   {"type": "ma", "period": 20}

   // 변경 후
   {"type": "ma", "params": {"period": 20}}
   ```

4. **operator 형식 수정**
   - MA 교차: `>` → `cross_above`, `<` → `cross_below`
   - 기타: 소문자로 변환

## 실행 결과 확인

스크립트 실행 후 다음과 같은 출력을 확인할 수 있습니다:

```
📊 전략 로드 중...
✅ 총 10개 전략 발견

🔍 수정이 필요한 전략 확인 중...
⚠️  5개 전략이 수정 필요

수정할 전략 목록:
  1. 골든크로스 전략 (ID: xxx)
  2. RSI 반전 전략 (ID: yyy)
  ...

위 전략들을 수정하시겠습니까? (y/n): y

🔧 전략 수정 시작...

전략: 골든크로스 전략
변경사항:
  • 템플릿 'golden-cross'에서 2개 지표 추가
  • 매수 operator: > → cross_above
  • 매도 operator: < → cross_below
✅ 성공적으로 업데이트됨
```

## 백테스트 재실행

마이그레이션 완료 후:

1. **프론트엔드에서 백테스트 실행**
   - 전략 선택
   - 백테스트 실행
   - 거래 횟수 확인

2. **로그 확인**
   ```bash
   # Docker 로그 확인
   docker logs kiwoom-bridge -f --tail 100
   ```

## 문제 해결

### 여전히 거래가 0회인 경우

1. **백테스트 로그 확인**
   - `[FIX]` 메시지 확인
   - 지표 계산 여부 확인
   - 신호 생성 여부 확인

2. **Supabase 데이터 직접 확인**
   - Supabase 대시보드에서 strategies 테이블 확인
   - config 필드의 indicators 배열 확인

3. **수동 수정**
   ```python
   # check_supabase_strategy.py 실행
   python check_supabase_strategy.py
   ```

## 주의사항

- ⚠️ 마이그레이션 전 백업 권장
- ⚠️ 프로덕션 환경에서는 먼저 테스트 환경에서 확인
- ⚠️ 대량의 전략이 있는 경우 배치로 나누어 실행

## 지원

문제가 계속되는 경우:
1. Docker 컨테이너 재시작
2. 프론트엔드 캐시 삭제
3. 백엔드 로그 상세 분석