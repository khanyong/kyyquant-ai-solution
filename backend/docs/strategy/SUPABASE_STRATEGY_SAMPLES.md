# Supabase 전략 샘플 - 분할 매수/매도 전략

생성일: 2025-10-03

이 문서는 Supabase에 저장할 수 있는 완전한 전략 샘플을 제공합니다.
각 전략은 이름, 설명, 상세 설정을 포함하며, UI에서 바로 세팅하여 백테스트할 수 있습니다.

---

## 전략 1: RSI 기반 3단계 분할 매수/매도

### 기본 정보

**전략명**: `[분할] RSI 3단계 매수매도`

**설명**: `RSI 과매도 구간을 3단계로 나누어 분할 매수하고, 목표 수익률별로 3단계 분할 매도. 동적 손절선으로 수익 보호`

**카테고리**: `분할매수`, `모멘텀`, `RSI`

**난이도**: 중급

---

### 전략 상세

#### 매수 조건 (3단계)

**1단계 매수 (50% 투자)**
- 조건: RSI < 35
- 포지션 비율: 50%
- 조건 결합: AND (모든 조건 만족 필요)
- 투자 금액 예시: 10,000,000원 → 5,000,000원 투자

**2단계 매수 (30% 추가 투자)**
- 조건: RSI < 28
- 포지션 비율: 30%
- 조건 결합: AND
- 투자 금액 예시: 남은 5,000,000원 → 1,500,000원 추가 투자
- 누적 투자: 6,500,000원 (65%)

**3단계 매수 (100% 전액 투자)**
- 조건: RSI < 22
- 포지션 비율: 100%
- 조건 결합: AND
- 투자 금액 예시: 남은 3,500,000원 → 3,500,000원 전액 투자
- 누적 투자: 10,000,000원 (100%)

#### 매도 조건 (3단계)

**1단계 매도 (50% 청산)**
- 조건: 목표수익률 3% 도달
- 청산 비율: 50%
- 동적 손절: 활성화 → 1단계 도달 시 손절선 0% (본전)

**2단계 매도 (30% 청산)**
- 조건: 목표수익률 5% 도달
- 청산 비율: 30%
- 동적 손절: 활성화 → 2단계 도달 시 손절선 3% (1단계가)

**3단계 매도 (20% 청산)**
- 조건: 목표수익률 10% 도달
- 청산 비율: 20%
- 동적 손절: 활성화 → 3단계 도달 시 손절선 5% (2단계가)

#### 손절 설정

- 손절 활성화: ✅
- 기본 손절선: -5%
- 동적 손절: ✅ (각 단계별 활성화)

---

### Supabase JSON 설정

```json
{
  "name": "[분할] RSI 3단계 매수매도",
  "description": "RSI 과매도 구간을 3단계로 나누어 분할 매수하고, 목표 수익률별로 3단계 분할 매도. 동적 손절선으로 수익 보호",
  "config": {
    "indicators": [
      {
        "name": "rsi",
        "params": {
          "period": 14
        }
      }
    ],
    "useStageBasedStrategy": true,
    "buyStages": [
      {
        "stage": 1,
        "enabled": true,
        "positionPercent": 50,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "rsi",
            "operator": "<",
            "right": 35
          }
        ]
      },
      {
        "stage": 2,
        "enabled": true,
        "positionPercent": 30,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "rsi",
            "operator": "<",
            "right": 28
          }
        ]
      },
      {
        "stage": 3,
        "enabled": true,
        "positionPercent": 100,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "rsi",
            "operator": "<",
            "right": 22
          }
        ]
      }
    ],
    "sellStages": [
      {
        "stage": 1,
        "enabled": true,
        "exitPercent": 50,
        "passAllRequired": false
      },
      {
        "stage": 2,
        "enabled": true,
        "exitPercent": 30,
        "passAllRequired": false
      },
      {
        "stage": 3,
        "enabled": true,
        "exitPercent": 20,
        "passAllRequired": false
      }
    ],
    "targetProfit": {
      "mode": "staged",
      "staged": {
        "enabled": true,
        "stages": [
          {
            "stage": 1,
            "targetProfit": 3,
            "exitPercent": 50,
            "dynamicStopLoss": true
          },
          {
            "stage": 2,
            "targetProfit": 5,
            "exitPercent": 30,
            "dynamicStopLoss": true
          },
          {
            "stage": 3,
            "targetProfit": 10,
            "exitPercent": 20,
            "dynamicStopLoss": true
          }
        ]
      }
    },
    "stopLoss": {
      "enabled": true,
      "lossPercent": 5
    }
  },
  "is_active": true,
  "user_id": null
}
```

---

## 전략 2: 볼린저 밴드 + RSI 2단계 분할 매수

### 기본 정보

**전략명**: `[분할] 볼린저밴드 2단계 매수`

**설명**: `볼린저 밴드 하단에서 RSI 확인 후 2단계 분할 매수. 밴드 상단 도달 시 전량 매도`

**카테고리**: `분할매수`, `변동성`, `볼린저밴드`

**난이도**: 초급

---

### 전략 상세

#### 매수 조건 (2단계)

**1단계 매수 (60% 투자)**
- 조건 1: close < bollinger_lower
- 조건 2: rsi < 45
- 포지션 비율: 60%
- 조건 결합: AND (모든 조건 만족)
- 투자 금액 예시: 10,000,000원 → 6,000,000원 투자

**2단계 매수 (50% 추가 투자)**
- 조건 1: close < bollinger_lower
- 조건 2: rsi < 35
- 포지션 비율: 50%
- 조건 결합: AND
- 투자 금액 예시: 남은 4,000,000원 → 2,000,000원 추가 투자
- 누적 투자: 8,000,000원 (80%)

#### 매도 조건 (단일)

**전량 매도**
- 조건 1: close > bollinger_upper
- 조건 2 (OR): rsi > 75
- 조건 결합: OR (하나만 만족해도 매도)
- 청산 비율: 100%

#### 손절 설정

- 손절 활성화: ✅
- 손절선: -3%
- 동적 손절: ❌

---

### Supabase JSON 설정

```json
{
  "name": "[분할] 볼린저밴드 2단계 매수",
  "description": "볼린저 밴드 하단에서 RSI 확인 후 2단계 분할 매수. 밴드 상단 도달 시 전량 매도",
  "config": {
    "indicators": [
      {
        "name": "bollinger",
        "params": {
          "period": 20,
          "std": 2
        }
      },
      {
        "name": "rsi",
        "params": {
          "period": 14
        }
      }
    ],
    "useStageBasedStrategy": true,
    "buyStages": [
      {
        "stage": 1,
        "enabled": true,
        "positionPercent": 60,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "close",
            "operator": "<",
            "right": "bollinger_lower"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 45
          }
        ]
      },
      {
        "stage": 2,
        "enabled": true,
        "positionPercent": 50,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "close",
            "operator": "<",
            "right": "bollinger_lower"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 35
          }
        ]
      }
    ],
    "buyConditions": [],
    "sellConditions": [
      {
        "left": "close",
        "operator": ">",
        "right": "bollinger_upper"
      },
      {
        "left": "rsi",
        "operator": ">",
        "right": 75
      }
    ],
    "combineWith": "OR",
    "stopLoss": {
      "enabled": true,
      "lossPercent": 3
    }
  },
  "is_active": true,
  "user_id": null
}
```

---

## 전략 3: MACD + RSI 복합 3단계 분할 매수/매도

### 기본 정보

**전략명**: `[분할] MACD+RSI 복합 전략`

**설명**: `MACD와 RSI를 결합하여 강한 매수 신호 포착. 3단계 진입/청산으로 리스크 분산`

**카테고리**: `분할매수`, `모멘텀`, `복합전략`

**난이도**: 고급

---

### 전략 상세

#### 매수 조건 (3단계)

**1단계 매수 (40% 투자)**
- 조건 1: macd_line > macd_signal
- 조건 2: rsi < 50
- 포지션 비율: 40%
- 조건 결합: AND
- 투자 금액 예시: 10,000,000원 → 4,000,000원 투자

**2단계 매수 (40% 추가 투자)**
- 조건 1: macd_line > macd_signal
- 조건 2: rsi < 40
- 조건 3: macd_hist > 0
- 포지션 비율: 40%
- 조건 결합: AND
- 투자 금액 예시: 남은 6,000,000원 → 2,400,000원 추가 투자
- 누적 투자: 6,400,000원 (64%)

**3단계 매수 (50% 추가 투자)**
- 조건 1: macd_line > macd_signal
- 조건 2: rsi < 30
- 조건 3: macd_hist > 0
- 포지션 비율: 50%
- 조건 결합: AND
- 투자 금액 예시: 남은 3,600,000원 → 1,800,000원 추가 투자
- 누적 투자: 8,200,000원 (82%)

#### 매도 조건 (3단계)

**1단계 매도 (40% 청산)**
- 조건: 목표수익률 4% 도달
- 청산 비율: 40%
- 동적 손절: 활성화 → 본전

**2단계 매도 (40% 청산)**
- 조건: 목표수익률 7% 도달
- 청산 비율: 40%
- 동적 손절: 활성화 → 4%

**3단계 매도 (20% 청산)**
- 조건: 목표수익률 12% 도달
- 청산 비율: 20%
- 동적 손절: 활성화 → 7%

#### 손절 설정

- 손절 활성화: ✅
- 기본 손절선: -6%
- 동적 손절: ✅

---

### Supabase JSON 설정

```json
{
  "name": "[분할] MACD+RSI 복합 전략",
  "description": "MACD와 RSI를 결합하여 강한 매수 신호 포착. 3단계 진입/청산으로 리스크 분산",
  "config": {
    "indicators": [
      {
        "name": "macd",
        "params": {
          "fast": 12,
          "slow": 26,
          "signal": 9
        }
      },
      {
        "name": "rsi",
        "params": {
          "period": 14
        }
      }
    ],
    "useStageBasedStrategy": true,
    "buyStages": [
      {
        "stage": 1,
        "enabled": true,
        "positionPercent": 40,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "macd_line",
            "operator": ">",
            "right": "macd_signal"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 50
          }
        ]
      },
      {
        "stage": 2,
        "enabled": true,
        "positionPercent": 40,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "macd_line",
            "operator": ">",
            "right": "macd_signal"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 40
          },
          {
            "left": "macd_hist",
            "operator": ">",
            "right": 0
          }
        ]
      },
      {
        "stage": 3,
        "enabled": true,
        "positionPercent": 50,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "macd_line",
            "operator": ">",
            "right": "macd_signal"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 30
          },
          {
            "left": "macd_hist",
            "operator": ">",
            "right": 0
          }
        ]
      }
    ],
    "sellStages": [
      {
        "stage": 1,
        "enabled": true,
        "exitPercent": 40,
        "passAllRequired": false
      },
      {
        "stage": 2,
        "enabled": true,
        "exitPercent": 40,
        "passAllRequired": false
      },
      {
        "stage": 3,
        "enabled": true,
        "exitPercent": 20,
        "passAllRequired": false
      }
    ],
    "targetProfit": {
      "mode": "staged",
      "staged": {
        "enabled": true,
        "stages": [
          {
            "stage": 1,
            "targetProfit": 4,
            "exitPercent": 40,
            "dynamicStopLoss": true
          },
          {
            "stage": 2,
            "targetProfit": 7,
            "exitPercent": 40,
            "dynamicStopLoss": true
          },
          {
            "stage": 3,
            "targetProfit": 12,
            "exitPercent": 20,
            "dynamicStopLoss": true
          }
        ]
      }
    },
    "stopLoss": {
      "enabled": true,
      "lossPercent": 6
    }
  },
  "is_active": true,
  "user_id": null
}
```

---

## 전략 4: 골든크로스 2단계 진입

### 기본 정보

**전략명**: `[분할] 골든크로스 2단계`

**설명**: `SMA 골든크로스 확인 후 RSI로 2단계 분할 진입. 데드크로스 시 전량 청산`

**카테고리**: `분할매수`, `추세추종`, `이동평균`

**난이도**: 초급

---

### 전략 상세

#### 매수 조건 (2단계)

**1단계 매수 (50% 투자)**
- 조건 1: sma_20 > sma_60 (골든크로스 유지)
- 조건 2: rsi < 60
- 포지션 비율: 50%
- 조건 결합: AND
- 투자 금액 예시: 10,000,000원 → 5,000,000원 투자

**2단계 매수 (60% 추가 투자)**
- 조건 1: sma_20 > sma_60
- 조건 2: rsi < 50
- 포지션 비율: 60%
- 조건 결합: AND
- 투자 금액 예시: 남은 5,000,000원 → 3,000,000원 추가 투자
- 누적 투자: 8,000,000원 (80%)

#### 매도 조건 (단일)

**전량 매도**
- 조건: sma_20 < sma_60 (데드크로스)
- 청산 비율: 100%

#### 손절 설정

- 손절 활성화: ✅
- 손절선: -4%
- 동적 손절: ❌

---

### Supabase JSON 설정

```json
{
  "name": "[분할] 골든크로스 2단계",
  "description": "SMA 골든크로스 확인 후 RSI로 2단계 분할 진입. 데드크로스 시 전량 청산",
  "config": {
    "indicators": [
      {
        "name": "sma",
        "params": {
          "period": 20
        }
      },
      {
        "name": "sma",
        "params": {
          "period": 60
        }
      },
      {
        "name": "rsi",
        "params": {
          "period": 14
        }
      }
    ],
    "useStageBasedStrategy": true,
    "buyStages": [
      {
        "stage": 1,
        "enabled": true,
        "positionPercent": 50,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "sma_20",
            "operator": ">",
            "right": "sma_60"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 60
          }
        ]
      },
      {
        "stage": 2,
        "enabled": true,
        "positionPercent": 60,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "sma_20",
            "operator": ">",
            "right": "sma_60"
          },
          {
            "left": "rsi",
            "operator": "<",
            "right": 50
          }
        ]
      }
    ],
    "buyConditions": [],
    "sellConditions": [
      {
        "left": "sma_20",
        "operator": "<",
        "right": "sma_60"
      }
    ],
    "stopLoss": {
      "enabled": true,
      "lossPercent": 4
    }
  },
  "is_active": true,
  "user_id": null
}
```

---

## 전략 5: 검증용 간단 전략 (테스트용)

### 기본 정보

**전략명**: `[테스트] 간단한 분할매수 검증`

**설명**: `RSI 완화 조건으로 빠른 검증. 분할 매수/매도 로직 테스트용`

**카테고리**: `테스트`, `검증용`

**난이도**: 테스트

---

### 전략 상세

#### 매수 조건 (2단계)

**1단계 매수 (50% 투자)**
- 조건: rsi < 55
- 포지션 비율: 50%
- 투자 금액 예시: 10,000,000원 → 5,000,000원 투자

**2단계 매수 (30% 추가 투자)**
- 조건: rsi < 48
- 포지션 비율: 30%
- 투자 금액 예시: 남은 5,000,000원 → 1,500,000원 추가 투자
- 누적 투자: 6,500,000원 (65%)

#### 매도 조건 (2단계)

**1단계 매도 (60% 청산)**
- 조건: 목표수익률 2% 도달
- 청산 비율: 60%
- 동적 손절: ✅ → 본전

**2단계 매도 (40% 청산)**
- 조건: 목표수익률 4% 도달
- 청산 비율: 40%
- 동적 손절: ✅ → 2%

#### 손절 설정

- 손절 활성화: ✅
- 손절선: -3%
- 동적 손절: ✅

---

### Supabase JSON 설정

```json
{
  "name": "[테스트] 간단한 분할매수 검증",
  "description": "RSI 완화 조건으로 빠른 검증. 분할 매수/매도 로직 테스트용",
  "config": {
    "indicators": [
      {
        "name": "rsi",
        "params": {
          "period": 14
        }
      }
    ],
    "useStageBasedStrategy": true,
    "buyStages": [
      {
        "stage": 1,
        "enabled": true,
        "positionPercent": 50,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "rsi",
            "operator": "<",
            "right": 55
          }
        ]
      },
      {
        "stage": 2,
        "enabled": true,
        "positionPercent": 30,
        "passAllRequired": true,
        "conditions": [
          {
            "left": "rsi",
            "operator": "<",
            "right": 48
          }
        ]
      }
    ],
    "sellStages": [
      {
        "stage": 1,
        "enabled": true,
        "exitPercent": 60,
        "passAllRequired": false
      },
      {
        "stage": 2,
        "enabled": true,
        "exitPercent": 40,
        "passAllRequired": false
      }
    ],
    "targetProfit": {
      "mode": "staged",
      "staged": {
        "enabled": true,
        "stages": [
          {
            "stage": 1,
            "targetProfit": 2,
            "exitPercent": 60,
            "dynamicStopLoss": true
          },
          {
            "stage": 2,
            "targetProfit": 4,
            "exitPercent": 40,
            "dynamicStopLoss": true
          }
        ]
      }
    },
    "stopLoss": {
      "enabled": true,
      "lossPercent": 3
    }
  },
  "is_active": true,
  "user_id": null
}
```

---

## UI 세팅 가이드

### 공통 설정 순서

1. **전략 생성**
   - 전략 관리 → 새 전략 만들기
   - 전략명과 설명 입력

2. **지표 추가**
   - 각 전략의 `indicators` 배열 참조
   - 지표 추가 버튼으로 필요한 지표 설정

3. **매수 조건 설정**
   - "단계별 매수 사용" 체크 ✅
   - 각 단계별로:
     - 단계 활성화 ✅
     - 포지션 비율(%) 입력
     - 조건 추가 (left, operator, right)
     - "모든 조건 만족" 또는 "하나만 만족" 선택

4. **매도 조건 설정**
   - **단계별 매도인 경우**:
     - 목표수익률 → 단계별 설정 선택
     - 각 단계별 목표(%), 청산(%), 동적손절 체크
   - **단일 매도인 경우**:
     - 일반 매도 조건 추가

5. **손절 설정**
   - 손절 사용 ✅
   - 손절(%) 입력

6. **저장 및 백테스트**
   - 전략 저장
   - 백테스트 실행

---

## 예상 결과

### 전략 1: RSI 3단계
- 예상 승률: 60-70%
- 평균 수익률: 5-7%
- 최대 낙폭: -5%
- 거래 빈도: 중간

### 전략 2: 볼린저 밴드 2단계
- 예상 승률: 55-65%
- 평균 수익률: 4-6%
- 최대 낙폭: -3%
- 거래 빈도: 높음

### 전략 3: MACD+RSI 복합
- 예상 승률: 65-75%
- 평균 수익률: 7-9%
- 최대 낙폭: -6%
- 거래 빈도: 낮음

### 전략 4: 골든크로스 2단계
- 예상 승률: 55-65%
- 평균 수익률: 5-8%
- 최대 낙폭: -4%
- 거래 빈도: 낮음

### 전략 5: 테스트용
- 예상 승률: 70-80% (완화된 조건)
- 평균 수익률: 2-3%
- 최대 낙폭: -3%
- 거래 빈도: 매우 높음

---

## Supabase 삽입 SQL 예시

```sql
-- 전략 1 삽입
INSERT INTO strategies (name, description, config, is_active, user_id, created_at)
VALUES (
  '[분할] RSI 3단계 매수매도',
  'RSI 과매도 구간을 3단계로 나누어 분할 매수하고, 목표 수익률별로 3단계 분할 매도. 동적 손절선으로 수익 보호',
  '{...JSON...}'::jsonb,
  true,
  NULL,
  NOW()
);

-- 여러 전략 한번에 삽입
INSERT INTO strategies (name, description, config, is_active, user_id, created_at)
SELECT * FROM (VALUES
  ('[분할] RSI 3단계 매수매도', '...', '{...}'::jsonb, true, NULL, NOW()),
  ('[분할] 볼린저밴드 2단계 매수', '...', '{...}'::jsonb, true, NULL, NOW()),
  ('[분할] MACD+RSI 복합 전략', '...', '{...}'::jsonb, true, NULL, NOW()),
  ('[분할] 골든크로스 2단계', '...', '{...}'::jsonb, true, NULL, NOW()),
  ('[테스트] 간단한 분할매수 검증', '...', '{...}'::jsonb, true, NULL, NOW())
) AS t(name, description, config, is_active, user_id, created_at);
```

---

## 검증 체크리스트

백테스트 실행 후 다음 항목들을 확인하세요:

- [ ] 분할 매수가 단계별로 실행되었는가?
- [ ] 투자 금액 비율이 정확한가? (남은 금액의 N%)
- [ ] 평균 매수가가 올바르게 계산되었는가?
- [ ] 단계별 매도가 목표 수익률에서 실행되었는가?
- [ ] 동적 손절선이 단계별로 조정되었는가?
- [ ] 거래 내역에 매수/매도 이유가 표시되는가?
- [ ] 최종 수익률이 합리적인가?

---

## 주의사항

1. **user_id NULL**: 템플릿 전략은 `user_id`를 NULL로 설정하여 모든 사용자가 사용 가능
2. **동적 컬럼명**: `sma_20`, `sma_60` 등은 period에 따라 자동 생성
3. **combineWith**: 단계별 전략에서는 사용 안 함 (각 단계의 `passAllRequired` 사용)
4. **useStageBasedStrategy**: 분할 매수/매도 사용 시 반드시 `true`
5. **백테스트 기간**: 최소 1년 이상 권장

---

**생성일**: 2025-10-03
**버전**: 1.0
**작성자**: Auto Stock Backend System
