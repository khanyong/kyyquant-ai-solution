"""
복잡한 지표 저장 예시 - 일목균형표, 엘리어트 파동 등
"""
import json
from typing import Dict, Any

def save_ichimoku_strategy():
    """일목균형표 전략을 데이터베이스에 저장하는 예시"""
    
    # 1. 일목균형표 설정
    ichimoku_config = {
        "enabled": True,
        "parameters": {
            "tenkan_period": 9,      # 전환선
            "kijun_period": 26,      # 기준선
            "senkou_b_period": 52,   # 선행스팬B
            "chikou_period": 26,     # 후행스팬
            "displacement": 26       # 구름 이동
        },
        "entry_rules": {
            "buy_when": [
                "tenkan_above_kijun",    # 전환선 > 기준선
                "price_above_kumo",      # 가격 > 구름
                "chikou_above_price"     # 후행스팬 > 과거가격
            ]
        }
    }
    
    # 2. 전체 전략 설정
    strategy = {
        "name": "일목균형표 + RSI 복합 전략",
        "indicators": {
            # 일목균형표
            "ichimoku": ichimoku_config,
            
            # RSI (보조 지표)
            "rsi": {
                "enabled": True,
                "period": 14,
                "oversold": 30,
                "overbought": 70
            },
            
            # 새로운 지표 추가 가능 (스키마 변경 없이!)
            "new_custom_indicator": {
                "enabled": False,
                "custom_param_1": 100,
                "nested_config": {
                    "level_1": {
                        "level_2": {
                            "deep_value": 42
                        }
                    }
                }
            }
        }
    }
    
    # 3. 데이터베이스에 저장 (Python)
    import psycopg2
    import json
    
    # Supabase 연결
    conn = psycopg2.connect("postgresql://...")
    cursor = conn.cursor()
    
    # JSONB로 저장 - 어떤 구조든 가능!
    cursor.execute("""
        UPDATE strategies 
        SET indicators = %s
        WHERE id = %s
    """, (json.dumps(strategy['indicators']), strategy_id))
    
    conn.commit()
    
    print("일목균형표 설정이 저장되었습니다!")


def calculate_ichimoku(price_data, config):
    """일목균형표 계산 로직"""
    
    params = config['parameters']
    
    # 전환선 (Tenkan-sen) = (9일 최고가 + 9일 최저가) / 2
    high_9 = price_data['high'].rolling(params['tenkan_period']).max()
    low_9 = price_data['low'].rolling(params['tenkan_period']).min()
    tenkan = (high_9 + low_9) / 2
    
    # 기준선 (Kijun-sen) = (26일 최고가 + 26일 최저가) / 2
    high_26 = price_data['high'].rolling(params['kijun_period']).max()
    low_26 = price_data['low'].rolling(params['kijun_period']).min()
    kijun = (high_26 + low_26) / 2
    
    # 선행스팬A (Senkou Span A) = (전환선 + 기준선) / 2, 26일 앞으로
    senkou_a = ((tenkan + kijun) / 2).shift(params['displacement'])
    
    # 선행스팬B (Senkou Span B) = (52일 최고가 + 52일 최저가) / 2, 26일 앞으로
    high_52 = price_data['high'].rolling(params['senkou_b_period']).max()
    low_52 = price_data['low'].rolling(params['senkou_b_period']).min()
    senkou_b = ((high_52 + low_52) / 2).shift(params['displacement'])
    
    # 후행스팬 (Chikou Span) = 현재 가격, 26일 뒤로
    chikou = price_data['close'].shift(-params['chikou_period'])
    
    return {
        'tenkan': tenkan,
        'kijun': kijun,
        'senkou_a': senkou_a,
        'senkou_b': senkou_b,
        'chikou': chikou
    }


def load_and_execute_strategy(strategy_id):
    """저장된 전략 로드 및 실행"""
    
    # 1. 데이터베이스에서 전략 로드
    cursor.execute("""
        SELECT indicators FROM strategies WHERE id = %s
    """, (strategy_id,))
    
    indicators_json = cursor.fetchone()[0]
    indicators = json.loads(indicators_json)
    
    # 2. 일목균형표가 있는지 확인
    if 'ichimoku' in indicators and indicators['ichimoku']['enabled']:
        ichimoku_config = indicators['ichimoku']
        
        # 계산 실행
        ichimoku_values = calculate_ichimoku(price_data, ichimoku_config)
        
        # 신호 생성
        if check_ichimoku_buy_signal(ichimoku_values, ichimoku_config):
            return {"signal": "BUY", "indicator": "ichimoku"}
    
    # 3. 다른 지표들도 처리
    for indicator_name, indicator_config in indicators.items():
        if indicator_config.get('enabled'):
            # 동적으로 지표 처리
            process_indicator(indicator_name, indicator_config)
    
    return {"signal": "HOLD"}


# SQL로 직접 조회도 가능
def get_ichimoku_strategies():
    """일목균형표를 사용하는 모든 전략 조회"""
    
    sql = """
    SELECT 
        id,
        name,
        indicators->'ichimoku' as ichimoku_config,
        indicators->'ichimoku'->'parameters'->'tenkan_period' as tenkan_period
    FROM strategies
    WHERE 
        indicators->'ichimoku'->>'enabled' = 'true'
        AND is_active = true
    """
    
    # JSONB는 SQL에서도 직접 조회 가능!
    return cursor.execute(sql).fetchall()


# 새로운 지표 추가 예시
def add_new_indicator_type():
    """완전히 새로운 지표 타입 추가"""
    
    new_indicator = {
        "super_new_indicator_2025": {
            "enabled": True,
            "version": "1.0.0",
            "created_by": "user123",
            "parameters": {
                "anything": "가능",
                "nested": {
                    "deep": {
                        "very_deep": {
                            "unlimited": "JSONB는 제한 없음"
                        }
                    }
                },
                "array_example": [1, 2, 3, 4, 5],
                "mixed_types": {
                    "number": 123,
                    "string": "text",
                    "boolean": True,
                    "null_value": None
                }
            }
        }
    }
    
    # 스키마 변경 없이 바로 저장!
    cursor.execute("""
        UPDATE strategies 
        SET 
            indicators = indicators || %s,
            custom_parameters = custom_parameters || %s
        WHERE id = %s
    """, (
        json.dumps(new_indicator),
        json.dumps({"last_indicator_added": "super_new_indicator_2025"}),
        strategy_id
    ))
    
    print("새 지표가 추가되었습니다. 테이블 스키마 변경 없음!")


if __name__ == "__main__":
    # 예시 실행
    save_ichimoku_strategy()
    
    # 결과 확인
    print("""
    일목균형표와 같은 복잡한 지표도 JSONB 타입 덕분에:
    1. 스키마 변경 없이 저장
    2. 중첩된 구조 제한 없음
    3. 새 버전/파라미터 자유롭게 추가
    4. SQL로 직접 조회 가능
    """)