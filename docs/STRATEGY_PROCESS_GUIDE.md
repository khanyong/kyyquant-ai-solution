# 전략 생성 및 저장 프로세스 가이드

## 📊 시스템 아키텍처

```
프론트엔드 (React)
    ↓
전략 생성 UI (StrategyCreator)
    ↓
strategyService.ts
    ↓
Supabase Client
    ↓
Supabase Database (PostgreSQL)
    ↑
백엔드 API (FastAPI) - 선택적
    ↑
키움 API 브릿지 - 실거래용
```

## 🚀 전략 생성 프로세스

### 1. 프론트엔드에서 전략 생성

#### 1.1 사용자가 전략 정보 입력
```typescript
// StrategyCreator.tsx
const strategy = {
  name: 'RSI 과매도 전략',
  description: 'RSI 30 이하에서 매수',
  conditions: {
    entry: {
      rsi: { operator: '<', value: 30 }
    },
    exit: {
      profit_target: 5,
      stop_loss: -3
    }
  },
  position_size: 10,
  max_positions: 5,
  target_stocks: ['005930', '000660']
}
```

#### 1.2 strategyService를 통해 저장
```typescript
// strategyService.ts - createStrategy 함수
const savedStrategy = await strategyService.createStrategy(strategy)
```

### 2. Supabase 저장 과정

#### 2.1 사용자 인증 확인
```typescript
const user = await supabase.auth.getUser()
if (!user.data.user) throw new Error('로그인 필요')
```

#### 2.2 데이터베이스에 저장
```typescript
const { data, error } = await supabase
  .from('strategies')
  .insert({
    ...strategy,
    user_id: user.data.user.id,
    is_active: false,
    created_at: new Date().toISOString()
  })
  .select()
  .single()
```

#### 2.3 실시간 업데이트 전파
- Supabase Realtime이 자동으로 구독자들에게 알림
- 대시보드가 자동으로 새 전략 표시

## 🔍 테스트 방법

### 방법 1: 자동 테스트 스크립트
```bash
# 백엔드 폴더에서 실행
D:\Dev\auto_stock\backend\test_strategy.bat
```

테스트 항목:
- ✅ Supabase 테이블 존재 확인
- ✅ 전략 CRUD 작업
- ✅ 실시간 구독
- ✅ API 서버 연결

### 방법 2: 수동 테스트 (프론트엔드)

#### Step 1: API 서버 실행
```bash
D:\Dev\auto_stock\backend\run_trading_system.bat
# 옵션 2 선택 (전략 관리 API 서버)
```

#### Step 2: 프론트엔드 실행
```bash
cd D:\Dev\auto_stock
npm run dev
```

#### Step 3: 전략 생성 테스트
1. http://localhost:5173 접속
2. 로그인 (Supabase 계정)
3. 전략 메뉴 클릭
4. "새 전략" 버튼 클릭
5. 정보 입력:
   - 전략 이름: "테스트 전략"
   - 설명: "Supabase 저장 테스트"
   - RSI 지표 선택
   - 진입 조건: RSI < 30
   - 목표 수익: 5%
   - 손절선: -3%
6. "전략 저장" 클릭

#### Step 4: 저장 확인

**Supabase 대시보드에서 확인:**
1. https://app.supabase.com 접속
2. 프로젝트 선택
3. Table Editor → strategies 테이블
4. 새로 생성된 전략 확인

**SQL로 직접 확인:**
```sql
-- Supabase SQL Editor에서 실행
SELECT * FROM strategies 
ORDER BY created_at DESC 
LIMIT 5;
```

## 📝 데이터베이스 스키마

### strategies 테이블
```sql
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT false,
    conditions JSONB NOT NULL,
    position_size DECIMAL(5,2) DEFAULT 10.00,
    max_positions INTEGER DEFAULT 5,
    target_stocks JSONB DEFAULT '[]',
    execution_time JSONB DEFAULT '{"start": "09:00", "end": "15:20"}',
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    total_profit DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🛠️ 문제 해결

### 1. 테이블이 없다는 오류
```bash
# Supabase SQL Editor에서 실행
-- 파일: supabase/migrations/create_trading_system_tables.sql
-- 전체 내용을 복사하여 실행
```

### 2. 인증 오류
```javascript
// .env 파일 확인
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### 3. CORS 오류
```javascript
// API 서버가 실행 중인지 확인
// backend/api_strategy_routes.py의 CORS 설정 확인
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. 실시간 업데이트 안 됨
```javascript
// Supabase 대시보드에서 Realtime 활성화 확인
// Database → Replication → strategies 테이블 활성화
```

## 📊 모니터링

### 실시간 로그 확인
```javascript
// 브라우저 개발자 도구 콘솔에서
localStorage.debug = 'supabase:*'
```

### 네트워크 요청 확인
1. 개발자 도구 → Network 탭
2. "strategies" 필터링
3. 요청/응답 확인

### Supabase 로그
1. Supabase 대시보드 → Logs
2. API logs 또는 Postgres logs 선택
3. 에러 메시지 확인

## ✅ 검증 체크리스트

- [ ] Supabase 프로젝트 생성
- [ ] 환경 변수 설정 (.env)
- [ ] 테이블 생성 (SQL 실행)
- [ ] RLS 정책 설정
- [ ] Realtime 활성화
- [ ] 프론트엔드 로그인 기능
- [ ] 전략 생성 UI 작동
- [ ] Supabase에 데이터 저장
- [ ] 실시간 업데이트 수신
- [ ] API 서버 연동 (선택)

## 📚 참고 자료

- [Supabase 문서](https://supabase.com/docs)
- [전략 API 문서](http://localhost:8001/docs) (FastAPI 자동 문서)
- 프로젝트 파일 구조:
  - `/src/services/strategyService.ts` - Supabase 연동
  - `/src/components/StrategyCreator.tsx` - 전략 생성 UI
  - `/backend/api_strategy_routes.py` - API 엔드포인트
  - `/supabase/migrations/` - 데이터베이스 스키마