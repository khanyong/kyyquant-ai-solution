# n8n 워크플로우 필드명 수정 안내

## 🔧 수정 사항

### account_balance 테이블 필드명 변경
- **기존**: `account_number` 
- **수정**: `account_no`

### 수정된 필드 매핑
```json
{
  "user_id": "n8n-auto",
  "account_no": "81101350-01",              // account_number → account_no
  "total_evaluation": 10000000,             // total_assets → total_evaluation  
  "available_cash": 5000000,
  "total_profit_loss": 0,
  "total_profit_loss_rate": 0
}
```

## 📝 실제 테이블 스키마

```sql
CREATE TABLE account_balance (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    account_no varchar(20) NOT NULL,           -- 올바른 필드명
    total_evaluation numeric,                  -- 총평가금액
    total_buy_amount numeric,                  -- 총매입금액
    available_cash numeric,                    -- 주문가능현금
    total_profit_loss numeric,                 -- 총손익금액
    total_profit_loss_rate numeric(6,2),       -- 총손익률
    stock_value numeric,                       -- 유가증권평가금액
    cash_balance numeric,                      -- 예수금
    receivable_amount numeric,                 -- 미수금
    invested_amount numeric,                   -- 투자원금
    withdrawn_amount numeric,                  -- 출금가능금액
    updated_at timestamp with time zone DEFAULT now()
)
```

## ✅ 적용 방법

### n8n에서 직접 수정
1. n8n 워크플로우 열기
2. **"💾 잔고 저장"** 노드 더블클릭
3. Body JSON 내용 수정:
   - `account_number` → `account_no`
   - `total_assets` → `total_evaluation`
4. Save 클릭

### 또는 새 워크플로우 임포트
1. 수정된 `simplest-workflow.json` 다시 임포트
2. 기존 워크플로우 비활성화
3. 새 워크플로우 활성화

## 🎯 테스트 확인 포인트

1. **Execute Workflow** 실행
2. 모든 노드가 녹색 체크 표시
3. Supabase Dashboard에서 `account_balance` 테이블 확인
4. 새 레코드가 정상적으로 저장되었는지 확인

## 📌 참고사항

- Kiwoom API 응답 필드와 Supabase 테이블 필드명이 다를 수 있음
- 매핑 시 항상 실제 테이블 스키마 확인 필요
- 필드명은 대소문자 구분됨 (PostgreSQL)