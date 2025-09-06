# 투자설정 데이터 수집 가이드

## 개요
키움 OpenAPI+를 통해 투자설정에 필요한 재무 데이터를 수집하고 Supabase에 저장하는 시스템입니다.

## 데이터 수집 항목

### 1. 가격 정보 (kw_price_current)
- 현재가, 변동률
- 52주 최고/최저가
- **시가총액** (키움에서 직접 제공, 계산하지 않음)
- 거래량, 거래대금
- 외인소진률

### 2. 재무비율 (kw_financial_ratio)
- PER, PBR, EPS, BPS
- ROE, ROA
- 부채비율, 유동비율, 당좌비율
- 배당수익률

### 3. 시계열 스냅샷 (kw_financial_snapshot)
- 모든 데이터를 날짜/시간별로 누적 저장
- 데이터 변화 추적 가능
- 과거 시점 데이터 조회 가능

## 실행 방법

### 사전 준비
1. **키움 OpenAPI+ 실행 및 로그인**
   ```
   - KOA Studio 실행
   - 계정 로그인 확인
   ```

2. **환경 변수 설정** (.env 파일)
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

### 데이터 수집 실행

#### 방법 1: 배치 파일 사용 (권장)
```batch
cd backend
run_investment_data_collection.bat
```

메뉴 옵션:
- [1] 전체 종목 데이터 수집 (2000+ 종목, 1-2시간 소요)
- [2] 테스트 모드 (10개 종목만)
- [3] 최신 데이터 정보 확인
- [4] 주요 종목만 수집 (삼성전자, SK하이닉스 등 10개)

#### 방법 2: Python 직접 실행
```python
# 전체 종목 수집
python collect_investment_data.py --all

# 테스트 (10개만)
python collect_investment_data.py --all --limit 10

# 주요 종목만
python collect_investment_data.py --major

# 데이터 정보 확인
python collect_investment_data.py --info
```

## 데이터 확인

### Supabase에서 확인
1. **최신 데이터 조회**
   ```sql
   SELECT * FROM kw_latest_financial;
   ```

2. **데이터 신선도 확인**
   ```sql
   SELECT * FROM get_data_freshness();
   ```

3. **특정 종목 이력 조회**
   ```sql
   SELECT * FROM kw_financial_snapshot 
   WHERE stock_code = '005930' 
   ORDER BY snapshot_date DESC;
   ```

### UI에서 확인
- 투자설정 화면 우측 상단에 "데이터 수집일" 표시
- 실시간 투자유니버스에서 필터링된 종목 수 확인

## 데이터 수집 주기

### 권장 수집 주기
- **일일**: 주요 종목 (--major 옵션)
- **주간**: 전체 종목 (--all 옵션)
- **장 종료 후**: 30분 후 수집 권장

### 자동화 (Windows 작업 스케줄러)
1. 작업 스케줄러 열기
2. "기본 작업 만들기" 선택
3. 트리거: 매일 오후 4시
4. 동작: run_investment_data_collection.bat 실행

## 주의사항

1. **API 제한**
   - TR 요청 간 0.5초 대기
   - 연속 조회 시 3.6초 대기
   - 1시간당 1000회 제한

2. **데이터 정합성**
   - 시가총액은 억원 단위로 저장
   - 재무제표는 최신 연간 데이터
   - 모든 데이터에 timestamp 포함

3. **오류 처리**
   - 네트워크 오류 시 자동 재시도
   - 진행상황 json 파일로 저장
   - 중단된 작업 재개 가능

## 트러블슈팅

### "키움 OpenAPI+ 연결 실패"
- KOA Studio가 실행 중인지 확인
- 로그인 상태 확인
- 방화벽 설정 확인

### "Supabase 저장 실패"
- 인터넷 연결 확인
- .env 파일의 SUPABASE_URL, KEY 확인
- Supabase 대시보드에서 테이블 존재 확인

### "데이터가 표시되지 않음"
- collect_investment_data.py --info로 데이터 확인
- Supabase에서 kw_financial_snapshot 테이블 확인
- UI 새로고침 (F5)

## 데이터 구조

```
kw_financial_snapshot (시계열 누적)
├── snapshot_date: 수집 날짜
├── snapshot_time: 수집 시간
├── market_cap: 시가총액 (억원)
├── per, pbr, eps, bps: 가치평가 지표
├── roe: 수익성 지표
└── created_at: DB 저장 시간

kw_price_current (최신 가격)
├── current_price: 현재가
├── market_cap: 시가총액 (원)
└── updated_at: 업데이트 시간

kw_financial_ratio (최신 재무비율)
├── per, pbr, roe, roa: 재무비율
├── debt_ratio: 부채비율
└── current_ratio: 유동비율
```