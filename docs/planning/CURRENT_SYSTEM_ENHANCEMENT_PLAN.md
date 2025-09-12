# 현재 운영 중인 시스템 개선 계획

## 📊 현재 운영 상태

### 🟢 현재 가능한 기능 (Vercel + Supabase)
- ✅ **전략 빌더**: 사용자가 투자 전략 구성
- ✅ **백테스팅**: 과거 데이터로 전략 검증
- ✅ **투자 설정**: 투자 유니버스, 필터 설정
- ✅ **데이터 저장**: Supabase에 전략/결과 저장
- ✅ **사용자 인증**: Supabase Auth
- ✅ **실시간 업데이트**: Supabase Realtime

### 🔴 현재 불가능한 기능
- ❌ **실제 주문 실행**: 증권사 API 연동 필요
- ❌ **실시간 시세 수집**: Windows 기반 API 제약
- ❌ **자동 매매**: 24/7 실행 환경 필요
- ❌ **대용량 백테스트**: 연산 리소스 제한

---

## 🏗️ 현재 아키텍처와 개선안

### 현재 구조
```
┌────────────────────────────────────────┐
│         사용자 (웹 브라우저)              │
└────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────┐
│      Vercel (현재 운영 중)               │
│  - React Frontend                      │
│  - 전략 빌더 UI                         │
│  - 백테스트 결과 시각화                   │
│  - 투자 설정 관리                       │
└────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────┐
│      Supabase (현재 운영 중)             │
│  - PostgreSQL DB                       │
│  - 사용자 인증                          │
│  - 전략/백테스트 데이터 저장              │
│  - Realtime 구독                       │
└────────────────────────────────────────┘
                    ↓
        ⚠️ 실제 거래 불가능 (API 연동 X)
```

### 개선된 구조 (NAS 추가)
```
┌────────────────────────────────────────┐
│         사용자 (웹/모바일)               │
└────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────┐
│      Vercel (기존 유지 + 확장)           │
│  - React Frontend ✅                   │
│  - 전략 빌더 UI ✅                      │
│  - 백테스트 결과 시각화 ✅               │
│  - 투자 설정 관리 ✅                    │
│  + API Routes (신규)                   │
│  + 주문 관리 UI (신규)                  │
└────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────┐
│      Supabase (기존 유지 + 확장)         │
│  - PostgreSQL DB ✅                    │
│  - 사용자 인증 ✅                       │
│  - 전략/백테스트 데이터 ✅               │
│  - Realtime 구독 ✅                    │
│  + Edge Functions (신규)               │
│  + 주문/포지션 테이블 (신규)             │
└────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────┐
│    Synology NAS (신규 추가)             │
│  - 증권사 API 브릿지                    │
│  - 실시간 시세 수집                     │
│  - 자동 매매 실행                      │
│  - 대용량 백테스트 엔진                 │
└────────────────────────────────────────┘
```

---

## 🚀 단계별 개선 계획

### Phase 0: 현재 시스템 최적화 (1주)
기존 운영 중인 기능을 유지하면서 준비 작업

#### 0.1 데이터베이스 스키마 확장
```sql
-- 새로운 테이블 추가 (Supabase)

-- 증권사 계정 정보
CREATE TABLE broker_accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  broker_type TEXT NOT NULL, -- 'kis', 'ebest', 'ls'
  account_number TEXT,
  encrypted_credentials JSONB, -- 암호화된 API 키
  is_paper_account BOOLEAN DEFAULT true,
  is_active BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 실제 주문 내역
CREATE TABLE real_orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  broker_account_id UUID REFERENCES broker_accounts(id),
  stock_code TEXT NOT NULL,
  order_type TEXT NOT NULL, -- 'buy', 'sell'
  order_status TEXT NOT NULL, -- 'pending', 'executed', 'cancelled'
  quantity INTEGER NOT NULL,
  price DECIMAL(10,2),
  executed_price DECIMAL(10,2),
  broker_order_id TEXT, -- 증권사 주문번호
  strategy_id UUID REFERENCES strategies(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  executed_at TIMESTAMPTZ
);

-- 실시간 포지션
CREATE TABLE real_positions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  broker_account_id UUID REFERENCES broker_accounts(id),
  stock_code TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  avg_price DECIMAL(10,2),
  current_price DECIMAL(10,2),
  profit_loss DECIMAL(10,2),
  profit_loss_rate DECIMAL(5,2),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(broker_account_id, stock_code)
);

-- RLS 정책 추가
ALTER TABLE broker_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_positions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own broker accounts" ON broker_accounts
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own orders" ON real_orders
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own positions" ON real_positions
  FOR ALL USING (auth.uid() = user_id);
```

#### 0.2 Vercel API Routes 준비
```typescript
// app/api/trading/route.ts (새로 추가)
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function POST(request: NextRequest) {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )
  
  // 사용자 인증 확인
  const token = request.headers.get('authorization')?.replace('Bearer ', '')
  const { data: { user } } = await supabase.auth.getUser(token)
  
  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  const { action, stockCode, quantity, price } = await request.json()
  
  // NAS 서버로 주문 전달 (Phase 1에서 구현)
  // 현재는 주문을 DB에만 저장
  const { data, error } = await supabase
    .from('real_orders')
    .insert({
      user_id: user.id,
      stock_code: stockCode,
      order_type: action,
      order_status: 'pending',
      quantity,
      price
    })
    .select()
    .single()
  
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 400 })
  }
  
  return NextResponse.json(data)
}
```

---

### Phase 1: NAS 서버 구축 (2주)
기존 시스템은 그대로 운영하면서 NAS 추가

#### 1.1 NAS Docker 환경 설정
```yaml
# docker-compose.yml
version: '3.8'

services:
  # API 게이트웨이
  api-gateway:
    build: ./gateway
    ports:
      - "8080:8080"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    depends_on:
      - trading-service
      - market-service

  # 거래 서비스
  trading-service:
    build: ./services/trading
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    volumes:
      - ./credentials:/app/credentials
    ports:
      - "8081:8081"

  # 시장 데이터 서비스
  market-service:
    build: ./services/market
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    volumes:
      - market-data:/app/data
    ports:
      - "8082:8082"

  # 백테스트 워커
  backtest-worker:
    build: ./services/backtest
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    deploy:
      replicas: 3

volumes:
  market-data:
  credentials:
```

#### 1.2 증권사 API 브릿지
```python
# services/trading/broker_manager.py
from typing import Dict, Any
import asyncio
from supabase import create_client
import os

class BrokerManager:
    def __init__(self):
        self.supabase = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY']
        )
        self.brokers = {}
    
    async def initialize_broker(self, user_id: str, broker_type: str):
        """사용자의 브로커 연결 초기화"""
        # Supabase에서 암호화된 인증정보 조회
        response = self.supabase.table('broker_accounts')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('broker_type', broker_type)\
            .single()\
            .execute()
        
        if not response.data:
            raise Exception("Broker account not found")
        
        account = response.data
        
        # 브로커별 API 초기화
        if broker_type == 'kis':
            from .brokers.kis import KISBroker
            broker = KISBroker(account['encrypted_credentials'])
        elif broker_type == 'ebest':
            from .brokers.ebest import EbestBroker
            broker = EbestBroker(account['encrypted_credentials'])
        else:
            raise Exception(f"Unknown broker type: {broker_type}")
        
        self.brokers[user_id] = broker
        return broker
    
    async def execute_order(self, user_id: str, order: Dict[str, Any]):
        """주문 실행"""
        if user_id not in self.brokers:
            await self.initialize_broker(
                user_id, 
                order.get('broker_type', 'kis')
            )
        
        broker = self.brokers[user_id]
        
        # 주문 실행
        result = await broker.place_order(order)
        
        # 결과를 Supabase에 업데이트
        await self.update_order_status(order['id'], result)
        
        # 실시간 알림 (Supabase Realtime)
        await self.notify_user(user_id, result)
        
        return result
    
    async def update_order_status(self, order_id: str, result: Dict[str, Any]):
        """주문 상태 업데이트"""
        self.supabase.table('real_orders')\
            .update({
                'order_status': result['status'],
                'broker_order_id': result.get('order_id'),
                'executed_price': result.get('executed_price'),
                'executed_at': result.get('executed_at')
            })\
            .eq('id', order_id)\
            .execute()
```

---

### Phase 2: 연동 및 테스트 (2주)
Vercel과 NAS 연동

#### 2.1 Vercel에서 NAS API 호출
```typescript
// app/api/trading/execute/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const { orderId, userId } = await request.json()
  
  // NAS 서버로 주문 실행 요청
  const nasResponse = await fetch(
    `${process.env.NAS_API_URL}/api/v1/trading/execute`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.NAS_API_KEY!
      },
      body: JSON.stringify({ orderId, userId })
    }
  )
  
  if (!nasResponse.ok) {
    return NextResponse.json(
      { error: 'Failed to execute order' },
      { status: 500 }
    )
  }
  
  const result = await nasResponse.json()
  return NextResponse.json(result)
}
```

#### 2.2 프론트엔드 업데이트
```typescript
// src/components/RealTrading.tsx
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export function RealTrading() {
  const [orders, setOrders] = useState([])
  const [positions, setPositions] = useState([])
  
  useEffect(() => {
    // 실시간 주문 상태 구독
    const ordersChannel = supabase
      .channel('orders-changes')
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'real_orders',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          if (payload.eventType === 'UPDATE') {
            setOrders(prev => 
              prev.map(o => o.id === payload.new.id ? payload.new : o)
            )
          } else if (payload.eventType === 'INSERT') {
            setOrders(prev => [...prev, payload.new])
          }
        }
      )
      .subscribe()
    
    // 실시간 포지션 업데이트
    const positionsChannel = supabase
      .channel('positions-changes')
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'real_positions',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          setPositions(prev => 
            prev.map(p => p.stock_code === payload.new.stock_code 
              ? payload.new 
              : p
            )
          )
        }
      )
      .subscribe()
    
    return () => {
      supabase.removeChannel(ordersChannel)
      supabase.removeChannel(positionsChannel)
    }
  }, [userId])
  
  const executeOrder = async (stockCode: string, quantity: number) => {
    const response = await fetch('/api/trading/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify({
        stockCode,
        quantity,
        orderType: 'market'
      })
    })
    
    const result = await response.json()
    console.log('Order executed:', result)
  }
  
  return (
    <div>
      {/* 실시간 주문/포지션 UI */}
    </div>
  )
}
```

---

### Phase 3: 점진적 기능 확장 (2-3주)

#### 3.1 모의투자 → 실전투자 전환
```typescript
// 사용자 권한 관리
interface UserTradingPermission {
  userId: string
  canPaperTrade: boolean  // 모의투자
  canRealTrade: boolean   // 실전투자
  dailyTradeLimit: number
  maxPositionSize: number
  verifiedAt: Date | null
}

// 권한 체크 미들웨어
export async function checkTradingPermission(
  userId: string, 
  isRealTrade: boolean
): Promise<boolean> {
  const { data } = await supabase
    .from('trading_permissions')
    .select('*')
    .eq('user_id', userId)
    .single()
  
  if (!data) return false
  
  if (isRealTrade && !data.can_real_trade) {
    throw new Error('Real trading not allowed for this user')
  }
  
  return true
}
```

#### 3.2 자동매매 스케줄러
```python
# services/scheduler/auto_trader.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

class AutoTrader:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.active_strategies = {}
    
    async def start(self):
        """자동매매 스케줄러 시작"""
        # 장 시작 전 준비
        self.scheduler.add_job(
            self.prepare_market_open,
            'cron',
            hour=8,
            minute=30
        )
        
        # 장중 전략 실행 (1분마다)
        self.scheduler.add_job(
            self.execute_strategies,
            'cron',
            hour='9-15',
            minute='*',
            second=0
        )
        
        # 장 마감 정리
        self.scheduler.add_job(
            self.market_close_cleanup,
            'cron',
            hour=15,
            minute=35
        )
        
        self.scheduler.start()
    
    async def execute_strategies(self):
        """활성화된 전략 실행"""
        # Supabase에서 활성 전략 조회
        active = await self.get_active_strategies()
        
        for strategy in active:
            try:
                # 전략 조건 체크
                signals = await self.check_strategy_conditions(strategy)
                
                if signals:
                    # 주문 실행
                    await self.execute_orders(strategy, signals)
            except Exception as e:
                await self.log_error(strategy['id'], str(e))
```

---

## 📊 성능 및 확장성

### 현재 vs 개선 후 비교

| 항목 | 현재 (Vercel+Supabase) | 개선 후 (+NAS) |
|------|------------------------|----------------|
| **전략 빌더** | ✅ 가능 | ✅ 유지 |
| **백테스트** | ✅ 제한적 (브라우저) | ✅ 대용량 가능 |
| **모의투자** | ⚠️ 수동 | ✅ 자동 |
| **실전투자** | ❌ 불가 | ✅ 가능 |
| **실시간 시세** | ❌ 불가 | ✅ 가능 |
| **자동매매** | ❌ 불가 | ✅ 24/7 |
| **동시 사용자** | 100명 | 1,000명+ |
| **응답 속도** | 200ms | 100ms |

### 비용 분석

#### 현재 비용 (월)
- Vercel: $0 (무료 티어)
- Supabase: $0-25 (무료/Pro)
- **합계**: $0-25

#### 개선 후 비용 (월)
- Vercel: $0-20 (무료/Pro)
- Supabase: $25 (Pro)
- NAS 전력: ~$10
- 증권사 API: $0
- **합계**: $35-55

---

## 🎯 핵심 이점

### 1. **기존 시스템 유지**
- 운영 중인 서비스 중단 없음
- 점진적 기능 추가
- 사용자 경험 연속성

### 2. **실전 거래 가능**
- 증권사 API 연동
- 실시간 주문 실행
- 포지션 관리

### 3. **확장성**
- 다중 사용자 지원
- 자동 스케일링
- 병렬 백테스트

### 4. **24/7 운영**
- NAS 상시 가동
- 자동매매 스케줄러
- 실시간 모니터링

---

## 🚦 즉시 시작 가능한 작업

### Week 1: 준비
- [ ] Supabase 스키마 업데이트
- [ ] Vercel API Routes 추가
- [ ] NAS Docker 환경 설정

### Week 2: 개발
- [ ] 증권사 API 브릿지 구현
- [ ] 주문 실행 로직
- [ ] 실시간 업데이트

### Week 3: 테스트
- [ ] 모의투자 테스트
- [ ] 부하 테스트
- [ ] 보안 점검

### Week 4: 배포
- [ ] 단계적 롤아웃
- [ ] 모니터링 설정
- [ ] 사용자 가이드

이렇게 하면 현재 운영 중인 시스템을 중단하지 않고 실전 거래 기능을 추가할 수 있습니다.