# Edge Function 배포 가이드

## 🔧 수정 내용

### 문제 발견
sync-kiwoom-balance/index.ts에서 `available_cash`를 항상 `'0'`으로 하드코딩하고 있었습니다.

**수정 전** (line 181-187):
```typescript
balanceData = {
  dnca_tot_amt: portfolioResult.prsm_dpst_aset_amt || '0',  // 예수금 총액
  nxdy_excc_amt: '0',  // ← 문제! 항상 0
  ord_psbl_cash: portfolioResult.prsm_dpst_aset_amt || '0',
  prvs_rcdl_excc_amt: '0',
  pchs_amt_smtl_amt: portfolioResult.tot_pur_amt || '0',
}
```

**수정 후** (line 181-188):
```typescript
const totalCash = portfolioResult.prsm_dpst_aset_amt || '0'
balanceData = {
  dnca_tot_amt: totalCash,  // 예수금 총액
  nxdy_excc_amt: totalCash,  // 사용가능 현금 ← 수정!
  ord_psbl_cash: totalCash,  // 주문가능 현금
  prvs_rcdl_excc_amt: totalCash,  // 전일정산금액
  pchs_amt_smtl_amt: portfolioResult.tot_pur_amt || '0',
}
```

## 📦 배포 방법

### 옵션 1: Supabase CLI로 배포 (권장)

```bash
# 1. Supabase 로그인 (브라우저 열림)
npx supabase login

# 2. Edge Function 배포
npx supabase functions deploy sync-kiwoom-balance --project-ref hznkyaomtrpzcayayayh
```

### 옵션 2: Supabase Dashboard에서 직접 수정

1. https://supabase.com/dashboard/project/hznkyaomtrpzcayayayh/functions 접속
2. **Edge Functions** → **sync-kiwoom-balance** 선택
3. **Edit function** 클릭
4. Line 179-188 부분을 아래 코드로 교체:

```typescript
      if (portfolioResult.return_code === 0) {
        // 잔고 정보 구성
        const totalCash = portfolioResult.prsm_dpst_aset_amt || '0'
        balanceData = {
          dnca_tot_amt: totalCash,  // 예수금 총액
          nxdy_excc_amt: totalCash,  // 사용가능 현금 (초기값: 전체 현금)
          ord_psbl_cash: totalCash,  // 주문가능 현금
          prvs_rcdl_excc_amt: totalCash,  // 전일정산금액
          pchs_amt_smtl_amt: portfolioResult.tot_pur_amt || '0',  // 매입금액합계
        }
        console.log('✅ 잔고 정보 조회 성공')
```

5. **Deploy** 버튼 클릭

## ✅ 배포 후 테스트

### 1. UI에서 계좌 동기화 실행

1. 프론트엔드 실행: `npm run dev`
2. 포트폴리오 패널로 이동
3. **"키움 계좌 동기화"** 버튼 클릭
4. 브라우저 콘솔에서 확인:
   ```
   ✅ 키움 계좌 동기화 완료
   ```

### 2. DB에서 결과 확인

Supabase Dashboard → Table Editor → kw_account_balance:

**예상 결과**:
```
account_number: 81126100
total_cash: 9782702
available_cash: 9782702  ← 이제 0이 아닌 값!
```

### 3. 전략 할당/회수 테스트

#### 테스트 1: 전략 할당
1. UI에서 전략 수정 → 50% 할당
2. DB 확인: `available_cash = 4,891,351원` (50% 차감)

#### 테스트 2: 전략 중지
1. UI에서 전략 중지 버튼 클릭
2. DB 확인: `available_cash = 9,782,702원` (100% 회수)

## 🎯 전체 수정 요약

### 1. Frontend 수정 ✅ (완료)
- **EditStrategyDialog.tsx**: 할당 시 available_cash 차감 로직 추가
- **AutoTradingPanelV2.tsx**: 중지 시 available_cash 회수 로직 추가

### 2. Edge Function 수정 ✅ (완료)
- **sync-kiwoom-balance/index.ts**: available_cash 초기화 버그 수정

### 3. 배포 필요 ⏳ (사용자 작업)
- Edge Function을 Supabase에 배포

## 📝 배포 후 동작 흐름

```
1. UI "계좌 동기화" 버튼 클릭
   ↓
2. Edge Function: sync-kiwoom-balance 호출
   ↓
3. 키움 API에서 계좌 정보 조회
   ↓
4. available_cash = total_cash로 설정 (수정된 부분!)
   ↓
5. DB kw_account_balance 테이블 업데이트
   ↓
6. UI 새로고침 → available_cash 표시

7. 사용자가 전략 50% 할당
   ↓
8. Frontend: available_cash 차감 (새로 추가한 로직)
   ↓
9. DB: available_cash = 4,891,351원

10. 사용자가 전략 중지
    ↓
11. Frontend: available_cash 회수 (새로 추가한 로직)
    ↓
12. DB: available_cash = 9,782,702원 (원상복구)
```

## ⚠️ 중요 사항

- Edge Function 배포 후에는 **즉시 적용**됩니다 (재시작 불필요)
- 배포 전 로컬 파일이 최신인지 확인
- 배포 후 **반드시 계좌 동기화 테스트** 필수!
- 문제 발생 시 Git으로 롤백 가능

## 🚀 다음 단계

1. Edge Function 배포
2. UI에서 "계좌 동기화" 버튼 클릭
3. available_cash가 제대로 설정되는지 확인
4. 전략 활성화 → 할당 금액 테스트
5. 전략 비활성화 → 회수 금액 테스트
6. 자동매매 테스트 진행
