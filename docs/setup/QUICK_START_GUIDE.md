# 🚀 자동매매 시스템 빠른 시작 가이드

## 📋 시작 체크리스트

### Step 1: 키움증권 API 서비스 확인 ✅
```
□ https://openapi.kiwoom.com 접속
□ 로그인 (키움증권 계좌 필요)
□ My Page → 서비스 관리 확인
  □ OpenAPI+ (이미 있음)
  □ REST API (없으면 신청)
  □ WebSocket (선택사항)
□ My Page → APP 관리
  □ APP Key 확인
  □ APP Secret 확인 (없으면 재발급)
```

### Step 2: 환경 설정 파일 생성 🔧
```bash
# 1. .env 파일 생성 (프로젝트 루트)
```

`.env` 파일 내용:
```env
# 키움증권 API (필수)
KIWOOM_APP_KEY=여기에_APP_KEY_입력
KIWOOM_APP_SECRET=여기에_APP_SECRET_입력
KIWOOM_ACCOUNT_NO=계좌번호-01
KIWOOM_IS_DEMO=true  # 모의투자: true, 실전: false

# API URLs
KIWOOM_API_URL=https://openapi.kiwoom.com:9443
KIWOOM_WS_URL=ws://openapi.kiwoom.com:9443

# Supabase (나중에 추가)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# N8N (나중에 추가)
N8N_WEBHOOK_URL=
```

### Step 3: API 연결 테스트 🧪
```bash
# Python 패키지 설치
pip install requests python-dotenv

# 테스트 실행
python test_kiwoom_api.py
```

성공시 출력:
```
✅ 토큰 발급 성공!
✅ 시세 조회 성공!
   삼성전자: 70,000원
```

### Step 4: Supabase 설정 (5분) ☁️
1. https://supabase.com 접속
2. 무료 프로젝트 생성
3. SQL Editor에서 실행:
```bash
# 파일 순서대로 실행
supabase/migrations/create_trading_system_tables.sql
```
4. Settings → API → Keys 복사
5. `.env` 파일에 추가

### Step 5: 로컬 테스트 (선택) 💻
```bash
# 프론트엔드 실행
npm install
npm run dev
# http://localhost:3000 접속
```

### Step 6: N8N 설치 (10분) 🔄
```bash
# Docker 방식 (추천)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 또는 npm 설치
npm install n8n -g
n8n start
```

1. http://localhost:5678 접속
2. 워크플로우 임포트:
   - `n8n-workflows/main-trading-workflow.json`
3. Credentials 설정:
   - Supabase 연결
   - 환경변수 설정

### Step 7: 첫 전략 생성 📈
웹사이트에서:
1. 전략 생성 → 새 전략
2. 간단한 RSI 전략:
```json
{
  "name": "RSI 과매도 매수",
  "conditions": {
    "entry": {
      "rsi": {"operator": "<", "value": 30}
    },
    "exit": {
      "profit_target": 5
    }
  }
}
```
3. 저장 → 활성화

---

## ⚡ 빠른 실행 명령어

### 전체 시스템 시작
```bash
# 터미널 1: 프론트엔드
npm run dev

# 터미널 2: N8N
n8n start

# 터미널 3: API 테스트
python test_kiwoom_api.py
```

### 상태 확인
```bash
# API 상태
python -c "from backend.kiwoom_hybrid_api import KiwoomHybridAPI; api = KiwoomHybridAPI(); print(api.get_status())"

# Supabase 연결
python -c "from backend.database_supabase import SupabaseDatabase; db = SupabaseDatabase(); print('Connected' if db.client else 'Failed')"
```

---

## 🎯 다음 단계별 목표

### Day 1: 기본 설정 ✅
- [x] API 키 발급
- [x] 환경 설정
- [x] 연결 테스트

### Day 2: 데이터베이스
- [ ] Supabase 테이블 생성
- [ ] 샘플 데이터 입력
- [ ] 연결 테스트

### Day 3: 자동화
- [ ] N8N 워크플로우 설정
- [ ] 첫 자동 실행
- [ ] 알림 설정

### Day 4: 전략
- [ ] 첫 전략 생성
- [ ] 백테스트 실행
- [ ] 모의투자 시작

### Day 5: 운영
- [ ] 실시간 모니터링
- [ ] 성과 분석
- [ ] 최적화

---

## 🆘 문제 해결

### ❌ 토큰 발급 실패
```bash
# 1. API 서비스 확인
https://openapi.kiwoom.com → My Page → 서비스 관리

# 2. REST API 신청 여부 확인
# 3. APP Key/Secret 재확인
```

### ❌ 시세 조회 실패
```bash
# 1. 장 운영시간 확인 (09:00~15:30)
# 2. 종목코드 확인 (6자리)
# 3. 모의/실전 구분 확인
```

### ❌ Supabase 연결 실패
```bash
# 1. URL 형식 확인: https://xxx.supabase.co
# 2. Anon Key 확인
# 3. 테이블 생성 여부 확인
```

---

## 📞 도움말

- 키움증권: 1544-9000
- 문서 위치: `docs/`
- 테스트 스크립트: `test_kiwoom_api.py`
- 하이브리드 API: `backend/kiwoom_hybrid_api.py`

---

## 🎉 준비 완료!

모든 설정이 완료되면:
1. 전략이 자동 실행됩니다
2. 결과가 Supabase에 저장됩니다
3. 웹사이트에서 실시간 확인 가능합니다

**화이팅! 성공적인 자동매매를 시작하세요!** 🚀