# 📚 n8n + 키움 REST API + Supabase 자동매매 시스템 설정 가이드

## 🎯 시스템 개요

```
[웹사이트] → [Supabase] ← [n8n] → [키움 REST API]
                ↑                      ↓
            [실행결과]            [매매주문]
```

## 📋 설정 단계

### 1️⃣ 키움증권 REST API 설정

#### 1.1 API 신청
1. 키움증권 OpenAPI 사이트 접속
2. REST API 신청
3. APP Key/Secret 발급받기

#### 1.2 계좌 설정
- 실전투자/모의투자 계좌 선택
- 계좌번호 확인

### 2️⃣ Supabase 데이터베이스 설정

#### 2.1 테이블 생성
```bash
# Supabase Dashboard > SQL Editor에서 실행
# 파일: supabase/migrations/create_trading_system_tables.sql
```

#### 2.2 RLS 정책 확인
- 각 테이블의 Row Level Security 활성화 확인
- 사용자별 데이터 격리 확인

### 3️⃣ n8n 설정

#### 3.1 환경변수 설정
```bash
# n8n 환경변수 (.env)
KIWOOM_APP_KEY=your_app_key
KIWOOM_APP_SECRET=your_app_secret
KIWOOM_ACCOUNT_NO=your_account_number
KIWOOM_API_URL=https://openapi.kiwoom.com:9443

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

ADMIN_EMAIL=your-email@domain.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

#### 3.2 Credentials 생성

**Supabase Credentials:**
1. n8n > Settings > Credentials
2. New > Supabase
3. 입력:
   - Host: `https://your-project.supabase.co`
   - Service Role Key: `your_service_key`

**SMTP Credentials (이메일 알림용):**
1. New > SMTP
2. Gmail 예시:
   - Host: `smtp.gmail.com`
   - Port: `587`
   - User: `your-email@gmail.com`
   - Password: `앱 비밀번호`

#### 3.3 워크플로우 임포트
1. n8n > Workflows > Import
2. 파일 선택:
   - `n8n-workflows/main-trading-workflow.json`
   - `n8n-workflows/monitoring-workflow.json`

### 4️⃣ 전략 생성 (웹사이트)

#### 4.1 전략 예시
```javascript
{
  "name": "RSI 과매도 매수 전략",
  "conditions": {
    "entry": {
      "rsi": {"operator": "<", "value": 30},
      "volume": {"operator": ">", "value": "avg_volume * 2"}
    },
    "exit": {
      "profit_target": 5,  // 5% 수익
      "stop_loss": -3      // 3% 손절
    }
  },
  "position_size": 10,      // 자산의 10%씩 투자
  "max_positions": 5,       // 최대 5종목
  "target_stocks": ["005930", "000660", "035720"]  // 삼성전자, SK하이닉스, 카카오
}
```

### 5️⃣ 실행 및 모니터링

#### 5.1 워크플로우 활성화
1. Main Trading Workflow → Active 토글 ON
2. Monitoring Workflow → Active 토글 ON

#### 5.2 실행 확인
- n8n > Executions에서 실행 로그 확인
- Supabase Dashboard에서 데이터 확인
- 이메일/Slack 알림 수신 확인

## 🔧 고급 설정

### 기술적 지표 추가
```python
# n8n 워크플로우 > 전략 실행 로직 노드 수정

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """MACD 계산"""
    # 구현...
    
def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """볼린저밴드 계산"""
    # 구현...
```

### 리스크 관리
```python
# 포지션 크기 계산
def calculate_position_size(capital, risk_per_trade, stop_loss_pct):
    """켈리 공식 기반 포지션 사이징"""
    return (capital * risk_per_trade) / stop_loss_pct
```

### 백테스팅 연동
```javascript
// 별도 워크플로우로 백테스팅 실행
{
  "name": "백테스팅 워크플로우",
  "trigger": "Manual",
  "nodes": [
    "과거 데이터 조회",
    "전략 시뮬레이션",
    "성과 분석",
    "리포트 생성"
  ]
}
```

## 📊 모니터링 대시보드

### Supabase 뷰 활용
```sql
-- 오늘의 거래 현황
SELECT * FROM v_todays_trades;

-- 활성 전략 상태
SELECT * FROM v_active_strategies;
```

### Grafana 연동 (선택사항)
1. Grafana 설치
2. PostgreSQL 데이터소스 추가 (Supabase)
3. 대시보드 생성:
   - 실시간 손익
   - 전략별 성과
   - 거래 히스토리

## ⚠️ 주의사항

1. **API 호출 제한**
   - 키움 REST API: 초당 10회
   - 적절한 딜레이 설정 필요

2. **실전/모의 구분**
   - 테스트는 반드시 모의투자로
   - 실전 전환시 계좌번호 변경

3. **에러 처리**
   - 네트워크 오류 재시도 로직
   - 주문 실패시 알림

4. **보안**
   - API Key는 환경변수로 관리
   - Supabase RLS 활성화 필수
   - n8n 접근 권한 제한

## 🚀 운영 팁

1. **점진적 시작**
   - 소액으로 시작
   - 1-2개 전략으로 테스트
   - 안정화 후 확대

2. **로그 분석**
   - 매일 실행 로그 검토
   - 실패 패턴 분석
   - 전략 개선

3. **성과 측정**
   - 승률, MDD, 샤프지수
   - 월별 리포트 생성
   - 전략 비교 분석

## 📞 문제 해결

### 자주 발생하는 문제

1. **인증 실패**
   - API Key/Secret 확인
   - 유효기간 확인

2. **주문 실패**
   - 계좌 잔고 확인
   - 거래 가능 시간 확인
   - 종목 코드 유효성

3. **데이터 조회 실패**
   - API 호출 제한 확인
   - 네트워크 상태
   - Supabase 연결

### 지원
- n8n 커뮤니티: https://community.n8n.io
- Supabase Discord: https://discord.supabase.com
- 키움 OpenAPI 포럼: https://openapi.kiwoom.com