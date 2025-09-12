# 모의투자/실전투자 계좌 시스템 구현 계획

## 1. 시스템 아키텍처

```
사용자 로그인 (Supabase Auth)
    ↓
키움 계좌 연동
    ├─ 모의투자 계좌
    └─ 실전투자 계좌
         ↓
    OAuth 2.0 인증
         ↓
    계좌 정보 저장
         ↓
    실시간 매매 실행
```

## 2. 데이터베이스 스키마

### 2.1 user_trading_accounts 테이블
```sql
CREATE TABLE user_trading_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  account_type VARCHAR(20) CHECK (account_type IN ('mock', 'real')), -- 모의/실전
  account_number VARCHAR(20) NOT NULL,
  account_name VARCHAR(100),
  broker VARCHAR(20) DEFAULT 'kiwoom',
  
  -- OAuth 인증 정보
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  
  -- 계좌 상태
  is_active BOOLEAN DEFAULT false,
  is_connected BOOLEAN DEFAULT false,
  last_sync_at TIMESTAMP WITH TIME ZONE,
  
  -- 계좌 정보
  initial_balance DECIMAL(15, 2),
  current_balance DECIMAL(15, 2),
  available_balance DECIMAL(15, 2),
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, account_number)
);

-- RLS 정책
ALTER TABLE user_trading_accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own accounts" 
  ON user_trading_accounts FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own accounts" 
  ON user_trading_accounts FOR ALL 
  USING (auth.uid() = user_id);
```

### 2.2 trading_sessions 테이블
```sql
CREATE TABLE trading_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES user_trading_accounts(id),
  session_type VARCHAR(20) CHECK (session_type IN ('manual', 'auto')),
  
  -- 세션 상태
  status VARCHAR(20) DEFAULT 'active',
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ended_at TIMESTAMP WITH TIME ZONE,
  
  -- 세션 통계
  total_trades INTEGER DEFAULT 0,
  profitable_trades INTEGER DEFAULT 0,
  total_profit DECIMAL(15, 2) DEFAULT 0,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 3. 키움 REST API 통합

### 3.1 OAuth 2.0 인증 플로우
```typescript
// src/services/kiwoomAuth.ts
export class KiwoomAuthService {
  private readonly CLIENT_ID = process.env.KIWOOM_CLIENT_ID
  private readonly CLIENT_SECRET = process.env.KIWOOM_CLIENT_SECRET
  private readonly REDIRECT_URI = process.env.KIWOOM_REDIRECT_URI
  
  // 1. 인증 URL 생성
  getAuthorizationUrl(accountType: 'mock' | 'real'): string {
    const baseUrl = accountType === 'mock' 
      ? 'https://openapi.kiwoom.com/oauth2/mock/authorize'
      : 'https://openapi.kiwoom.com/oauth2/authorize'
    
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: this.CLIENT_ID,
      redirect_uri: this.REDIRECT_URI,
      scope: 'account trading'
    })
    
    return `${baseUrl}?${params}`
  }
  
  // 2. Access Token 획득
  async getAccessToken(code: string): Promise<TokenResponse> {
    const response = await fetch('https://openapi.kiwoom.com/oauth2/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: this.CLIENT_ID,
        client_secret: this.CLIENT_SECRET,
        code,
        redirect_uri: this.REDIRECT_URI
      })
    })
    
    return response.json()
  }
  
  // 3. Token 갱신
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch('https://openapi.kiwoom.com/oauth2/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        client_id: this.CLIENT_ID,
        client_secret: this.CLIENT_SECRET,
        refresh_token: refreshToken
      })
    })
    
    return response.json()
  }
}
```

### 3.2 계좌 정보 조회
```typescript
// src/services/kiwoomAccount.ts
export class KiwoomAccountService {
  private accessToken: string
  
  // 계좌 목록 조회
  async getAccounts(): Promise<Account[]> {
    const response = await fetch('https://openapi.kiwoom.com/v1/accounts', {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    return response.json()
  }
  
  // 계좌 잔고 조회
  async getBalance(accountNumber: string): Promise<Balance> {
    const response = await fetch(
      `https://openapi.kiwoom.com/v1/accounts/${accountNumber}/balance`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    return response.json()
  }
  
  // 보유 종목 조회
  async getPositions(accountNumber: string): Promise<Position[]> {
    const response = await fetch(
      `https://openapi.kiwoom.com/v1/accounts/${accountNumber}/positions`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    return response.json()
  }
}
```

## 4. 주문 실행 시스템

### 4.1 주문 API
```typescript
// src/services/kiwoomTrading.ts
export class KiwoomTradingService {
  private accessToken: string
  
  // 매수 주문
  async buyOrder(params: BuyOrderParams): Promise<OrderResponse> {
    const response = await fetch('https://openapi.kiwoom.com/v1/orders', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        account_number: params.accountNumber,
        symbol: params.symbol,
        order_type: params.orderType, // 'market' | 'limit'
        side: 'buy',
        quantity: params.quantity,
        price: params.price // limit order인 경우
      })
    })
    
    return response.json()
  }
  
  // 매도 주문
  async sellOrder(params: SellOrderParams): Promise<OrderResponse> {
    const response = await fetch('https://openapi.kiwoom.com/v1/orders', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        account_number: params.accountNumber,
        symbol: params.symbol,
        order_type: params.orderType,
        side: 'sell',
        quantity: params.quantity,
        price: params.price
      })
    })
    
    return response.json()
  }
  
  // 주문 취소
  async cancelOrder(orderId: string): Promise<void> {
    await fetch(`https://openapi.kiwoom.com/v1/orders/${orderId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
  }
}
```

## 5. React 컴포넌트 구조

### 5.1 계좌 연동 컴포넌트
```typescript
// src/components/AccountConnect.tsx
const AccountConnect: React.FC = () => {
  const [accountType, setAccountType] = useState<'mock' | 'real'>('mock')
  const [isConnecting, setIsConnecting] = useState(false)
  
  const handleConnect = async () => {
    setIsConnecting(true)
    
    // OAuth 인증 창 열기
    const authUrl = kiwoomAuth.getAuthorizationUrl(accountType)
    window.open(authUrl, 'kiwoom-auth', 'width=500,height=600')
    
    // 콜백 처리 대기
    window.addEventListener('message', async (event) => {
      if (event.data.type === 'kiwoom-auth-callback') {
        const { code } = event.data
        
        // Access Token 획득
        const tokenResponse = await kiwoomAuth.getAccessToken(code)
        
        // 계좌 정보 저장
        await saveAccountInfo({
          accountType,
          accessToken: tokenResponse.access_token,
          refreshToken: tokenResponse.refresh_token
        })
        
        setIsConnecting(false)
      }
    })
  }
  
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">키움증권 계좌 연동</Typography>
        
        <RadioGroup value={accountType} onChange={(e) => setAccountType(e.target.value)}>
          <FormControlLabel value="mock" control={<Radio />} label="모의투자" />
          <FormControlLabel value="real" control={<Radio />} label="실전투자" />
        </RadioGroup>
        
        <Button 
          variant="contained" 
          onClick={handleConnect}
          disabled={isConnecting}
        >
          {isConnecting ? '연동 중...' : '계좌 연동하기'}
        </Button>
      </CardContent>
    </Card>
  )
}
```

### 5.2 계좌 대시보드
```typescript
// src/components/TradingDashboard.tsx
const TradingDashboard: React.FC = () => {
  const [account, setAccount] = useState<Account | null>(null)
  const [positions, setPositions] = useState<Position[]>([])
  const [balance, setBalance] = useState<Balance | null>(null)
  
  return (
    <Grid container spacing={3}>
      {/* 계좌 선택 */}
      <Grid item xs={12}>
        <AccountSelector onSelect={setAccount} />
      </Grid>
      
      {/* 계좌 정보 */}
      <Grid item xs={12} md={4}>
        <AccountInfo account={account} balance={balance} />
      </Grid>
      
      {/* 보유 종목 */}
      <Grid item xs={12} md={8}>
        <PositionList positions={positions} />
      </Grid>
      
      {/* 주문 패널 */}
      <Grid item xs={12} md={6}>
        <OrderPanel account={account} />
      </Grid>
      
      {/* 실시간 체결 */}
      <Grid item xs={12} md={6}>
        <RealtimeTrades account={account} />
      </Grid>
    </Grid>
  )
}
```

## 6. 실시간 데이터 스트리밍

### 6.1 WebSocket 연결
```typescript
// src/services/kiwoomWebSocket.ts
export class KiwoomWebSocketService {
  private ws: WebSocket | null = null
  private accessToken: string
  
  connect(): void {
    this.ws = new WebSocket('wss://openapi.kiwoom.com/v1/stream')
    
    this.ws.onopen = () => {
      // 인증
      this.send({
        type: 'auth',
        access_token: this.accessToken
      })
    }
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleMessage(data)
    }
  }
  
  // 실시간 시세 구독
  subscribePrice(symbols: string[]): void {
    this.send({
      type: 'subscribe',
      channel: 'price',
      symbols
    })
  }
  
  // 실시간 체결 구독
  subscribeTrades(symbols: string[]): void {
    this.send({
      type: 'subscribe',
      channel: 'trades',
      symbols
    })
  }
  
  // 실시간 호가 구독
  subscribeOrderbook(symbols: string[]): void {
    this.send({
      type: 'subscribe',
      channel: 'orderbook',
      symbols
    })
  }
}
```

## 7. 구현 우선순위

### Phase 1: 기본 인프라 (1주)
1. ✅ Supabase 테이블 생성
2. ✅ OAuth 2.0 인증 구현
3. ✅ 계좌 연동 UI

### Phase 2: 계좌 관리 (1주)
1. ✅ 계좌 정보 조회
2. ✅ 잔고 조회
3. ✅ 보유 종목 조회

### Phase 3: 주문 시스템 (2주)
1. ✅ 매수/매도 주문
2. ✅ 주문 취소/정정
3. ✅ 주문 내역 조회

### Phase 4: 실시간 연동 (1주)
1. ✅ WebSocket 연결
2. ✅ 실시간 시세
3. ✅ 실시간 체결

### Phase 5: 자동매매 (2주)
1. ✅ 전략 실행 엔진
2. ✅ 신호 → 주문 변환
3. ✅ 포지션 관리

## 8. 보안 고려사항

1. **Token 관리**
   - Access Token은 메모리에만 저장
   - Refresh Token은 암호화하여 DB 저장
   - Token 만료 시 자동 갱신

2. **API Key 보호**
   - 환경변수로 관리
   - 클라이언트에 노출 금지
   - Proxy 서버 경유

3. **권한 관리**
   - 사용자별 계좌 격리
   - RLS로 데이터 보호
   - 실전투자 2차 인증

4. **거래 제한**
   - 일일 거래 한도
   - 종목당 최대 주문
   - 긴급 정지 기능

## 9. 테스트 계획

1. **모의투자 테스트**
   - 전체 플로우 검증
   - 주문 실행 테스트
   - 오류 처리 확인

2. **실전투자 검증**
   - 소액 테스트
   - 단계적 한도 증가
   - 모니터링 강화

## 10. 다음 단계

1. 키움증권 개발자 센터 앱 등록
2. OAuth 2.0 Redirect URI 설정
3. Supabase 테이블 생성
4. 인증 플로우 구현
5. 계좌 연동 UI 개발