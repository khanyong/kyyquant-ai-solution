# 변경 이력 - 2025년 10월 4일 (최종)

## 📋 개요
1. 볼린저 밴드 조건 설정 UI 개선
2. Supabase 지표 동적 로드 시스템 구축  
3. **SMA 동적 컬럼 생성 및 custom_params 우선순위 버그 수정** ⭐

## 🎯 주요 변경사항

### ⭐ SMA 동적 컬럼 생성 및 파라미터 버그 수정 (신규)

#### 문제 상황
- 골든크로스 전략: SMA(20), SMA(60) 중 sma_60 컬럼 생성 실패 → 거래 0회
- 스윙 트레이딩 전략: MACD 컬럼명 불일치 → Preflight 검증 실패

#### 해결 내용

**1. Preflight f-string 파싱 개선** (`backend/backtest/preflight.py`)
```python
# Before (버그)
match = re.search(r"result\s*=\s*\{([^}]+)\}", formula_code)
# [^}]+ 패턴이 f"sma_{period}"의 {period}에서 멈춤

# After (수정)
match = re.search(r"result\s*=\s*\{(.+)\}", formula_code, re.DOTALL)
# 중첩 중괄호 처리, 멀티라인 지원
```

**2. 캐시 키에 params 포함** (`backend/indicators/calculator.py:605`)
```python
# Before
cache_key = self._get_cache_key(indicator_name, options, stock_code, df.index)

# After  
cache_key = self._get_cache_key(indicator_name, options, stock_code, df.index, config.get('params', {}))
```

**3. default_params 우선순위 버그 수정** (`backend/indicators/calculator.py:932-934`)
```python
# Before (버그)
if definition.get('default_params'):
    options.period = params['period']  # Supabase의 period:20이 모든 SMA 덮어씀!

# After (제거)
# default_params로 options 덮어쓰기 제거
# namespace 생성 시에만 사용
```

**4. python_code 타입 custom_params 지원** (`backend/indicators/calculator.py:784,973`)
```python
# Before
def _calculate_python_code(self, df, config, options):
    # custom_params 파라미터 없음

# After
def _calculate_python_code(self, df, config, options, custom_params: Dict = None):
    # default_params 먼저 적용
    # custom_params 나중에 적용 (우선순위!)
    if custom_params:
        namespace['params'].update(custom_params)
```

#### 테스트 결과
✅ 골든크로스: sma_20, sma_60 모두 생성, 거래 발생  
✅ 스윙 트레이딩: MACD 컬럼명 수정 후 정상 작동  
✅ 모든 템플릿 전략 백테스트 정상

### 커밋 이력
1. `347b06e` - Strategy 인터페이스 user_id/userId 추가 (Vercel 빌드 에러 수정)
2. `75b0161` - 볼린저 밴드 UI 개선 및 Supabase 지표 연동
3. `4c7990a` - **SMA 동적 컬럼 생성 및 custom_params 버그 수정** (13개 파일 +683/-61)

### 총 변경 통계
- **파일 수**: 20개 (신규 11개, 수정 9개)
- **코드**: +913줄 추가, -301줄 삭제, 순증 +612줄

---
**작성일**: 2025년 10월 4일  
**브랜치**: feature/sell-or-logic-and-ui-improvements  
**최종 커밋**: 4c7990a
