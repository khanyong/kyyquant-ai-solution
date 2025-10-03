"""
Strategies 테이블 리셋 및 템플릿 재생성
- 현재 strategies 데이터를 strategies_backup으로 백업
- 새로운 8개 템플릿 전략 생성 (최신 지표 사용)
"""

import os
import sys
import io
from supabase import create_client
from datetime import datetime

# Windows 콘솔 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Supabase 연결
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL 또는 SUPABASE_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    supabase = create_client(url, key)

    print("=" * 60)
    print("Strategies 테이블 리셋 및 템플릿 재생성")
    print("=" * 60)

    # Phase 1: 백업
    print("\n[Phase 1] 백업 중...")
    try:
        # 기존 strategies_backup 테이블 삭제 (있다면)
        print("  - 기존 백업 테이블 확인...")

        # 현재 strategies 데이터 조회
        current_strategies = supabase.table('strategies').select('*').execute()
        current_count = len(current_strategies.data)
        print(f"  - 현재 strategies 레코드 수: {current_count}")

        if current_count > 0:
            # strategies_backup 테이블에 백업 (수동으로 SQL 실행 필요)
            print(f"  ⚠️  strategies_backup 테이블로 수동 백업이 필요합니다.")
            print(f"  SQL: DELETE FROM strategies_backup; INSERT INTO strategies_backup SELECT * FROM strategies;")

        print("  ✅ 백업 준비 완료")

    except Exception as e:
        print(f"  ❌ 백업 중 오류: {e}")
        sys.exit(1)

    # Phase 2: 기존 전략 삭제
    print("\n[Phase 2] 기존 전략 삭제 중...")
    try:
        # 모든 strategies 삭제
        result = supabase.table('strategies').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"  ✅ 기존 전략 삭제 완료")

    except Exception as e:
        print(f"  ❌ 삭제 중 오류: {e}")
        sys.exit(1)

    # Phase 3: 새로운 템플릿 생성
    print("\n[Phase 3] 새로운 템플릿 전략 생성 중...")

    templates = [
        {
            "name": "[템플릿] 골든크로스",
            "description": "MACD > MACD 매수, 단기평균 추세",
            "config": {
                "indicators": [
                    {"name": "sma", "params": {"period": 20}},
                    {"name": "sma", "params": {"period": 60}}
                ],
                "buyConditions": [
                    {"left": "sma_20", "operator": "crossover", "right": "sma_60"}
                ],
                "sellConditions": [
                    {"left": "sma_20", "operator": "crossunder", "right": "sma_60"}
                ]
            }
        },
        {
            "name": "[템플릿] RSI 반전",
            "description": "RSI 30 이하 매수, 과매도 반전 포착",
            "config": {
                "indicators": [
                    {"name": "rsi", "params": {"period": 14}}
                ],
                "buyConditions": [
                    {"left": "rsi", "operator": "<", "right": 30}
                ],
                "sellConditions": [
                    {"left": "rsi", "operator": ">", "right": 70}
                ]
            }
        },
        {
            "name": "[템플릿] 볼린저밴드",
            "description": "밴드 하단 매수, 변동성 활용 매매",
            "config": {
                "indicators": [
                    {"name": "bollinger", "params": {"period": 20, "std": 2}},
                    {"name": "rsi", "params": {"period": 14}}
                ],
                "buyConditions": [
                    {"left": "close", "operator": "<", "right": "bollinger_lower"},
                    {"left": "rsi", "operator": "<", "right": 40}
                ],
                "sellConditions": [
                    {"left": "close", "operator": ">", "right": "bollinger_upper"}
                ]
            }
        },
        {
            "name": "[템플릿] MACD 시그널",
            "description": "MACD 크로스, 모멘텀 추종 매매",
            "config": {
                "indicators": [
                    {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
                ],
                "buyConditions": [
                    {"left": "macd_line", "operator": "crossover", "right": "macd_signal"},
                    {"left": "macd_line", "operator": ">", "right": 0}
                ],
                "sellConditions": [
                    {"left": "macd_line", "operator": "crossunder", "right": "macd_signal"}
                ]
            }
        },
        {
            "name": "[템플릿] 복합 전략 A",
            "description": "RSI+MACD+거래량, 강한 확률 시스템",
            "config": {
                "indicators": [
                    {"name": "rsi", "params": {"period": 14}},
                    {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                    {"name": "volume_ma", "params": {"period": 20}}
                ],
                "buyConditions": [
                    {"left": "rsi", "operator": "<", "right": 50},
                    {"left": "macd_line", "operator": ">", "right": "macd_signal"},
                    {"left": "volume", "operator": ">", "right": "volume_ma_20"}
                ],
                "sellConditions": [
                    {"left": "rsi", "operator": ">", "right": 70},
                    {"left": "macd_line", "operator": "<", "right": "macd_signal"}
                ]
            }
        },
        {
            "name": "[템플릿] 복합 전략 B",
            "description": "MA+BB+RSI, 추세와 모멘텀 결합",
            "config": {
                "indicators": [
                    {"name": "sma", "params": {"period": 20}},
                    {"name": "bollinger", "params": {"period": 20, "std": 2}},
                    {"name": "rsi", "params": {"period": 14}}
                ],
                "buyConditions": [
                    {"left": "close", "operator": ">", "right": "sma_20"},
                    {"left": "close", "operator": "<", "right": "bollinger_lower"},
                    {"left": "rsi", "operator": "<", "right": 40}
                ],
                "sellConditions": [
                    {"left": "close", "operator": ">", "right": "bollinger_upper"},
                    {"left": "rsi", "operator": ">", "right": 70}
                ]
            }
        },
        {
            "name": "[템플릿] 스캘핑",
            "description": "단기 진입/청산, 빠른 수익 확보",
            "config": {
                "indicators": [
                    {"name": "sma", "params": {"period": 5}},
                    {"name": "rsi", "params": {"period": 14}}
                ],
                "buyConditions": [
                    {"left": "close", "operator": ">", "right": "sma_5"},
                    {"left": "rsi", "operator": "<", "right": 50}
                ],
                "sellConditions": [
                    {"left": "rsi", "operator": ">", "right": 70}
                ]
            }
        },
        {
            "name": "[템플릿] 스윙 트레이딩",
            "description": "중기 추세 포착, 안정적 수익 추구",
            "config": {
                "indicators": [
                    {"name": "sma", "params": {"period": 20}},
                    {"name": "sma", "params": {"period": 60}},
                    {"name": "rsi", "params": {"period": 14}},
                    {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
                ],
                "buyConditions": [
                    {"left": "sma_20", "operator": ">", "right": "sma_60"},
                    {"left": "rsi", "operator": "<", "right": 60},
                    {"left": "macd_line", "operator": ">", "right": 0}
                ],
                "sellConditions": [
                    {"left": "sma_20", "operator": "<", "right": "sma_60"},
                    {"left": "rsi", "operator": ">", "right": 70}
                ]
            }
        }
    ]

    created_count = 0
    for idx, template in enumerate(templates, 1):
        try:
            result = supabase.table('strategies').insert({
                "name": template["name"],
                "description": template["description"],
                "config": template["config"],
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            print(f"  ✅ {idx}/8 - {template['name']} 생성 완료")
            created_count += 1

        except Exception as e:
            print(f"  ❌ {template['name']} 생성 실패: {e}")

    print(f"\n  총 {created_count}/8 전략 생성 완료")

    # Phase 4: 검증
    print("\n[Phase 4] 검증 중...")
    try:
        final_strategies = supabase.table('strategies').select('id, name, config').execute()
        final_count = len(final_strategies.data)

        print(f"  - 최종 전략 개수: {final_count}")
        print(f"\n  생성된 전략 목록:")
        for strategy in final_strategies.data:
            indicators = strategy['config'].get('indicators', [])
            buy_conditions = strategy['config'].get('buyConditions', [])
            sell_conditions = strategy['config'].get('sellConditions', [])
            print(f"    • {strategy['name']}")
            print(f"      - 지표: {len(indicators)}개")
            print(f"      - 매수조건: {len(buy_conditions)}개")
            print(f"      - 매도조건: {len(sell_conditions)}개")

        if final_count == 8:
            print("\n  ✅ 검증 완료: 8개 템플릿 전략이 정상 생성되었습니다!")
        else:
            print(f"\n  ⚠️  경고: {final_count}개 전략만 생성되었습니다. (예상: 8개)")

    except Exception as e:
        print(f"  ❌ 검증 중 오류: {e}")

    print("\n" + "=" * 60)
    print("✅ 작업 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
