# 포트폴리오 업데이트 문제 해결 가이드

## 문제 상황

모의투자 계좌에서 buy 시그널이 들어가 체결이 완료되었으나, 프론트엔드의 포트폴리오 패널에서 계좌 현황이 자동으로 업데이트되지 않는 문제가 발생했습니다.

## 원인 분석

1. **n8n 워크플로우**: 주문 생성 시 `orders` 테이블에만 INSERT하고, 키움 API를 통해 실제 주문을 전송합니다.
2. **키움 API**: 주문이 체결되면 키움 서버에서 체결 정보가 업데이트됩니다.
3. **데이터베이스**: `orders` 테이블의 status는 업데이트되지만, **`kw_account_balance`와 `kw_portfolio` 테이블은 자동으로 업데이트되지 않습니다.**
4. **프론트엔드**: `PortfolioPanel`은 `kw_account_balance`와 `kw_portfolio` 테이블을 조회하므로, 수동으로 "키움 계좌 동기화" 버튼을 눌러야만 최신 데이터를 볼 수 있습니다.

## 해결 방법

### ✅ Phase 1: 프론트엔드 Realtime 구독 (완료)

[PortfolioPanel.tsx:143-208](src/components/trading/PortfolioPanel.tsx#L143-L208)에 다음 기능을 추가했습니다:

1. **`orders` 테이블 변경 감지**: 주문 상태가 `EXECUTED` 또는 `PARTIAL`로 변경되면 포트폴리오 자동 새로고침
2. **`kw_account_balance` 테이블 변경 감지**: 계좌 잔고가 업데이트되면 자동 새로고침
3. **`kw_portfolio` 테이블 변경 감지**: 보유 종목이 업데이트되면 자동 새로고침

```typescript
useEffect(() => {
  if (user) {
    fetchPortfolio()

    // Realtime 구독: orders 테이블 변경 감지
    const ordersChannel = supabase
      .channel('orders_changes_portfolio')
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'orders'
      }, (payload) => {
        if (payload.new && (payload.new.status === 'EXECUTED' || payload.new.status === 'PARTIAL')) {
          console.log('✅ Order executed, refreshing portfolio...')
          fetchPortfolio()
        }
      })
      .subscribe()

    // ... (다른 채널도 구독)

    return () => {
      supabase.removeChannel(ordersChannel)
      // ...
    }
  }
}, [user])
```

**효과**: 이제 주문이 체결되면 **즉시** 포트폴리오 패널이 자동으로 새로고침됩니다. 단, `kw_account_balance`와 `kw_portfolio` 테이블이 실제로 업데이트되어야 합니다.

### ⚠️ Phase 2: 자동 동기화 메커니즘 (미완료)

**문제**: `orders` 테이블의 status가 `EXECUTED`로 변경되어도, `kw_account_balance`와 `kw_portfolio` 테이블은 **키움 API를 호출해야만** 업데이트됩니다.

**해결 방법 옵션**:

#### 옵션 A: n8n 워크플로우 수정 (권장)

**주문 생성 워크플로우 (workflow-v7-2-buy-order-creation.json)**에 다음 단계를 추가:

1. 키움 API로 주문 전송
2. 주문 번호를 `orders` 테이블에 저장
3. **5분마다 체결 확인**
4. 체결 완료 시:
   - `orders.status` → `'EXECUTED'` 업데이트
   - **Supabase Edge Function `sync-kiwoom-balance` 호출**
   - 또는 **직접 `kw_account_balance`와 `kw_portfolio` 테이블 업데이트**

**장점**:
- n8n에서 주기적으로 체결 여부를 확인하므로 가장 안정적
- Edge Function을 재사용 가능

**단점**:
- n8n 워크플로우 수정 필요

#### 옵션 B: Database Trigger + Edge Function (복잡)

[supabase/migrations/05_create_auto_sync_trigger.sql](supabase/migrations/05_create_auto_sync_trigger.sql)을 생성했지만, Supabase에서는 Database Trigger로 HTTP 요청을 보내는 것이 쉽지 않습니다.

**대안**: `pg_net` 확장을 사용하거나, Supabase의 `pg_cron` + `http` 확장을 사용할 수 있지만, 설정이 복잡합니다.

#### 옵션 C: 프론트엔드에서 Polling (임시 방편)

프론트엔드에서 주문이 `PENDING` 상태일 때 1분마다 "키움 계좌 동기화" 버튼을 자동으로 호출하는 방법입니다.

**장점**:
- 간단하게 구현 가능

**단점**:
- 불필요한 API 호출이 많아짐
- 네트워크 부하 증가

## 권장 솔루션

### 🎯 최종 권장: n8n 워크플로우 + Realtime 구독

1. **n8n 워크플로우 수정**:
   - 주문 체결 확인 후 `sync-kiwoom-balance` Edge Function 호출
   - 또는 직접 `kw_account_balance`와 `kw_portfolio` 테이블 업데이트

2. **프론트엔드 Realtime 구독 (이미 완료)**:
   - `orders` 테이블 변경 → 포트폴리오 새로고침
   - `kw_account_balance`, `kw_portfolio` 테이블 변경 → 포트폴리오 새로고침

### 워크플로우 수정 예시

**workflow-v7-2-buy-order-creation.json**에 다음 노드 추가:

```json
{
  "name": "체결 확인 및 동기화",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://your-project.supabase.co/functions/v1/sync-kiwoom-balance",
    "authentication": "genericCredentialType",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "Bearer YOUR_SUPABASE_ANON_KEY"
        }
      ]
    }
  }
}
```

또는 **직접 DB 업데이트**:

```json
{
  "name": "포트폴리오 업데이트",
  "type": "n8n-nodes-base.postgres",
  "parameters": {
    "operation": "executeQuery",
    "query": "SELECT sync_kiwoom_account_balance($1, $2, $3)",
    "additionalFields": {}
  }
}
```

## 현재 상태

### ✅ 완료
- [x] 프론트엔드 Realtime 구독 추가
- [x] `orders` 테이블 변경 감지 및 자동 새로고침
- [x] `kw_account_balance`, `kw_portfolio` 테이블 변경 감지

### ⏳ 진행 필요
- [ ] n8n 워크플로우에 체결 확인 로직 추가
- [ ] 체결 완료 시 자동으로 키움 계좌 동기화 호출
- [ ] 테스트 및 검증

## 즉시 사용 가능한 임시 방법

현재는 다음 방법을 사용할 수 있습니다:

1. **수동 동기화**: 포트폴리오 패널에서 "키움 계좌 동기화" 버튼 클릭
2. **자동 새로고침**: 주문이 체결되면 Realtime 구독으로 인해 UI가 자동으로 업데이트되지만, **먼저 키움 계좌 동기화 버튼을 눌러야 최신 데이터가 DB에 반영됩니다.**

## 다음 단계

1. **n8n 워크플로우 확인**: 현재 어떻게 주문 체결을 확인하는지 점검
2. **체결 확인 후 동기화 로직 추가**: `sync-kiwoom-balance` Edge Function 호출 또는 직접 DB 업데이트
3. **테스트**: 실제 주문 체결 시나리오 테스트
4. **모니터링**: 로그 확인 및 에러 처리

## 관련 파일

- [src/components/trading/PortfolioPanel.tsx](src/components/trading/PortfolioPanel.tsx) - 프론트엔드 포트폴리오 패널
- [supabase/functions/sync-kiwoom-balance/index.ts](supabase/functions/sync-kiwoom-balance/index.ts) - 키움 계좌 동기화 Edge Function
- [n8n-workflows/workflow-v7-2-buy-order-creation.json](n8n-workflows/workflow-v7-2-buy-order-creation.json) - 매수 주문 생성 워크플로우
- [supabase/migrations/05_create_auto_sync_trigger.sql](supabase/migrations/05_create_auto_sync_trigger.sql) - 자동 동기화 트리거 (참고용)
