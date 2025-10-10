# 역할별 기능 차이 (Role-Based Features)

## 역할 계층 구조 (Role Hierarchy)

```
admin (5) > premium (4) > standard (3) > trial (2) > user (1)
```

- 상위 역할은 하위 역할의 모든 기능에 접근 가능
- 예: `premium` 회원은 `standard`, `trial`, `user` 기능 모두 사용 가능

---

## 역할별 정의 (Role Definitions)

### 1. **user** (일반 회원)
- **설명**: 기본 무료 회원
- **레벨**: 1
- **비용**: 무료
- **가입 방법**: 이메일 회원가입

### 2. **trial** (체험판 회원)
- **설명**: 프리미엄 기능을 제한된 기간 동안 체험
- **레벨**: 2
- **비용**: 무료 (기간 제한)
- **가입 방법**: 프로모션 또는 이벤트

### 3. **standard** (표준 유료 회원)
- **설명**: 기본 유료 서비스
- **레벨**: 3
- **비용**: 유료 (기본 요금제)
- **가입 방법**: 구독 결제

### 4. **premium** (프리미엄 회원)
- **설명**: 모든 고급 기능 이용 가능
- **레벨**: 4
- **비용**: 유료 (프리미엄 요금제)
- **가입 방법**: 구독 결제

### 5. **admin** (관리자)
- **설명**: 시스템 관리자
- **레벨**: 5
- **비용**: N/A
- **가입 방법**: 시스템 관리자 지정

---

## 역할별 기능 목록 (Features by Role)

### 기본 기능 (모든 회원)

| 기능 | user | trial | standard | premium | admin |
|------|:----:|:-----:|:--------:|:-------:|:-----:|
| 커뮤니티 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 전략 구성 (Strategy Builder) | ✅ | ✅ | ✅ | ✅ | ✅ |
| 백테스팅 실행 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 백테스팅 결과 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 실시간 신호 모니터링 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 투자 흐름 관리 | ✅ | ✅ | ✅ | ✅ | ✅ |

### Premium 전용 기능

| 기능 | user | trial | standard | premium | admin | 구현 위치 |
|------|:----:|:-----:|:--------:|:-------:|:-----:|-----------|
| **전략 분석 탭** | 🔒 | 🔒 | 🔒 | ✅ | ✅ | `StrategyBuilder.tsx:1232-1243` |
| **백테스트 결과 다운로드** | 🔒 | 🔒 | 🔒 | ✅ | ✅ | `BacktestResultViewer.tsx:979-1043` |
| **거래내역 매매 이유 조회** | 🔒 | 🔒 | 🔒 | ✅ | ✅ | `BacktestResultViewer.tsx:615-693` |

**범례**:
- ✅ : 사용 가능
- 🔒 : 잠금 (업그레이드 필요)

---

## Premium 전용 기능 상세 설명

### 1. 전략 분석 탭 (Strategy Analysis Tab)

**위치**: 전략 빌더 > 전략 분석 탭

**설명**:
- 전략의 성과를 심층 분석하는 고급 도구
- 다양한 리스크 지표 및 성과 메트릭 제공

**제한 사항**:
- `user`, `trial`, `standard` 회원: 탭 클릭 시 프리미엄 업그레이드 안내 화면 표시
- 탭 레이블에 🔒 아이콘 표시

**UI 요소**:
```tsx
// 탭에 자물쇠 아이콘 표시 (non-premium)
<Tab
  icon={<Assessment />}
  label={
    <Stack direction="row" alignItems="center" spacing={0.5}>
      <span>전략 분석</span>
      {!hasRole(['premium', 'admin']) && <Lock />}
    </Stack>
  }
/>
```

---

### 2. 백테스트 결과 다운로드 (CSV Export)

**위치**: 백테스트 결과 화면 > 결과 다운로드 버튼

**설명**:
- 백테스트 거래내역을 CSV 파일로 다운로드
- 모든 지표 및 거래 상세 정보 포함
- Excel에서 바로 열람 가능 (UTF-8 BOM 포함)

**제한 사항**:
- `user`, `trial`, `standard` 회원: 버튼 클릭 시 프리미엄 업그레이드 안내 다이얼로그 표시
- 버튼에 🔒 아이콘 및 warning 색상 표시

**UI 요소**:
```tsx
// 다운로드 버튼 (non-premium은 자물쇠 아이콘)
<Button
  variant="contained"
  startIcon={hasRole(['premium', 'admin']) ? <Download /> : <Lock />}
  color={hasRole(['premium', 'admin']) ? 'primary' : 'warning'}
  onClick={handleDownload}
>
  결과 다운로드
</Button>
```

**다운로드 파일 형식**:
- 파일명: `backtest_result_{id}.csv`
- 인코딩: UTF-8 with BOM
- 포함 정보: 날짜, 종목코드, 종목명, 구분, 수량, 단가, 금액, 손익, 수익률, 단계, 매수이유, 각종 지표

---

### 3. 거래내역 매매 이유 조회 (Trade Reason Column)

**위치**: 백테스트 결과 화면 > 거래내역 탭 > 매매 이유 컬럼

**설명**:
- 각 거래의 매수/매도 이유 상세 표시
- 신호 타입 (목표달성, 손절, 신호, 청산) 표시
- 매매 근거가 된 지표 값 제공

**제한 사항**:
- `user`, `trial`, `standard` 회원: "프리미엄 전용" 칩 표시, 클릭 시 업그레이드 안내
- 컬럼 헤더에 🔒 아이콘 표시

**UI 요소**:
```tsx
// 테이블 헤더 (non-premium은 자물쇠 아이콘)
<TableCell>
  <Stack direction="row" alignItems="center" spacing={0.5}>
    <span>매매 이유</span>
    {!hasRole(['premium', 'admin']) && <Lock />}
  </Stack>
</TableCell>

// 테이블 셀 (non-premium은 프리미엄 전용 칩)
{hasRole(['premium', 'admin']) ? (
  <Typography>{trade.reason}</Typography>
) : (
  <Chip icon={<Lock />} label="프리미엄 전용" color="warning" />
)}
```

**표시 정보** (Premium/Admin):
- 매매 이유 텍스트
- 신호 타입 배지 (목표달성/손절/신호/청산)
- 관련 지표 값

---

## 코드 구현 위치

### 역할 관리
- **타입 정의**: `src/contexts/AuthContext.tsx:5`
- **역할 확인 함수**: `src/contexts/AuthContext.tsx:39-61`
- **역할 계층**: `src/contexts/AuthContext.tsx:50-56`

### Premium 기능 구현
1. **전략 분석 탭**
   - 파일: `src/components/StrategyBuilder.tsx`
   - 탭 레이블: 1232-1243 라인
   - 탭 컨텐츠: 1873-1894 라인

2. **백테스트 결과 다운로드**
   - 파일: `src/components/backtest/BacktestResultViewer.tsx`
   - 다운로드 버튼: 979-1043 라인
   - 프리미엄 다이얼로그: 1047-1065 라인

3. **거래내역 매매 이유**
   - 파일: `src/components/backtest/BacktestResultViewer.tsx`
   - 테이블 헤더: 615-627 라인
   - 테이블 셀: 649-693 라인

---

## 향후 확장 계획

### 추가 가능한 Premium 기능
- [ ] 고급 기술 지표 사용
- [ ] 무제한 백테스트 저장
- [ ] 전략 비교 분석
- [ ] AI 기반 전략 추천
- [ ] 실시간 알림 설정
- [ ] 포트폴리오 최적화

### 역할 확장
- 현재 구조는 추가 역할을 쉽게 지원
- 새로운 역할 추가 시 `AuthContext.tsx`의 `UserRole` 타입만 수정
- 계층 구조는 `roleHierarchy` 객체에서 관리

---

## 업그레이드 안내

### Premium 업그레이드 방법
1. 마이페이지 접속
2. 구독 관리 메뉴 선택
3. Premium 요금제 선택
4. 결제 진행

### 혜택
- 모든 고급 분석 도구 사용
- 백테스트 결과 무제한 다운로드
- 상세한 매매 이유 및 지표 조회
- 우선 고객 지원

---

## 문의

역할 및 권한 관련 문의사항은 관리자에게 문의해주세요.

**최종 수정일**: 2025-01-11
