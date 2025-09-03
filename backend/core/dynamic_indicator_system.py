"""
동적 지표 시스템 - 새로운 지표를 스키마 변경 없이 추가
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class DynamicIndicatorSystem:
    """동적으로 확장 가능한 지표 시스템"""
    
    def __init__(self):
        # 기본 지표 템플릿 (계속 확장 가능)
        self.indicator_templates = {
            "rsi": {
                "name": "RSI",
                "category": "momentum",
                "parameters": {
                    "enabled": {"type": "boolean", "default": False},
                    "period": {"type": "integer", "default": 14, "min": 2, "max": 100},
                    "oversold": {"type": "number", "default": 30, "min": 0, "max": 100},
                    "overbought": {"type": "number", "default": 70, "min": 0, "max": 100}
                }
            },
            "macd": {
                "name": "MACD",
                "category": "trend",
                "parameters": {
                    "enabled": {"type": "boolean", "default": False},
                    "fast": {"type": "integer", "default": 12},
                    "slow": {"type": "integer", "default": 26},
                    "signal": {"type": "integer", "default": 9}
                }
            },
            # 새 지표는 여기에 계속 추가...
        }
    
    def add_new_indicator(self, indicator_key: str, indicator_config: Dict[str, Any]):
        """
        새로운 지표를 런타임에 추가
        데이터베이스 스키마 변경 없이 JSONB에 저장
        """
        self.indicator_templates[indicator_key] = indicator_config
        
        # 지표 정의를 데이터베이스에 저장 (선택사항)
        self.save_indicator_definition(indicator_key, indicator_config)
    
    def save_indicator_definition(self, key: str, config: Dict):
        """지표 정의를 별도 테이블에 저장"""
        # SQL: INSERT INTO indicator_definitions ...
        pass
    
    def validate_indicator_settings(self, indicators: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        사용자가 입력한 지표 설정 검증
        새로운 지표도 자동으로 처리
        """
        errors = []
        
        for indicator_key, settings in indicators.items():
            # 알려지지 않은 지표도 허용 (확장성)
            if indicator_key not in self.indicator_templates:
                # 새로운 지표로 간주하고 저장
                print(f"New indicator detected: {indicator_key}")
                continue
            
            template = self.indicator_templates[indicator_key]
            for param_key, param_config in template.get("parameters", {}).items():
                if param_key in settings:
                    # 타입 검증
                    if not self.validate_type(settings[param_key], param_config):
                        errors.append(f"{indicator_key}.{param_key}: Invalid type")
        
        return len(errors) == 0, errors
    
    def validate_type(self, value: Any, config: Dict) -> bool:
        """타입 검증"""
        expected_type = config.get("type")
        if expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "array":
            return isinstance(value, list)
        return True


class FlexibleStrategyStorage:
    """유연한 전략 저장 시스템"""
    
    @staticmethod
    def save_strategy_with_new_indicators(strategy_data: Dict[str, Any]) -> Dict:
        """
        새로운 지표가 포함된 전략 저장
        JSONB 필드에 모든 것을 저장하므로 스키마 변경 불필요
        """
        
        # 예시: 사용자가 새로운 지표 "custom_indicator_x" 추가
        strategy_data['indicators']['custom_indicator_x'] = {
            "enabled": True,
            "parameter_1": 50,
            "parameter_2": "advanced",
            "complex_setting": {
                "nested_value": 123,
                "array_values": [1, 2, 3]
            }
        }
        
        # 데이터베이스에 저장 (JSONB는 어떤 구조든 허용)
        sql = """
        UPDATE strategies 
        SET indicators = %s,
            custom_parameters = %s,
            updated_at = NOW()
        WHERE id = %s
        """
        
        # indicators JSONB 필드에 그대로 저장
        # 스키마 변경 없이 새 지표 추가 완료!
        
        return strategy_data


class IndicatorRegistry:
    """
    지표 레지스트리 - 사용 가능한 모든 지표 관리
    새 지표 추가 시 여기만 업데이트
    """
    
    def __init__(self):
        self.load_from_database()
    
    def load_from_database(self):
        """데이터베이스에서 지표 정의 로드"""
        # 별도 테이블에서 지표 정의를 로드
        sql = """
        SELECT * FROM indicator_definitions 
        WHERE is_active = true
        ORDER BY category, name
        """
        # 결과를 self.indicators에 저장
        
    def register_new_indicator(self, indicator: Dict[str, Any]):
        """새 지표 등록"""
        sql = """
        INSERT INTO indicator_definitions (
            key, name, category, description,
            parameters_schema, calculation_code,
            version, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (key) DO UPDATE SET
            parameters_schema = EXCLUDED.parameters_schema,
            calculation_code = EXCLUDED.calculation_code,
            version = EXCLUDED.version,
            updated_at = NOW()
        """
        # 새 지표를 데이터베이스에 등록
        
    def get_indicator_schema(self, indicator_key: str) -> Dict:
        """지표의 파라미터 스키마 반환"""
        # 프론트엔드에서 동적 폼 생성용
        return self.indicators.get(indicator_key, {})


# 사용 예시
def example_adding_new_indicator():
    """새로운 지표 추가 예시"""
    
    # 1. 새로운 지표 정의
    new_indicator = {
        "key": "super_custom_indicator",
        "name": "Super Custom Indicator",
        "category": "custom",
        "description": "사용자 정의 특수 지표",
        "parameters_schema": {
            "enabled": {"type": "boolean", "default": False},
            "sensitivity": {"type": "number", "default": 0.5, "min": 0, "max": 1},
            "mode": {"type": "string", "options": ["fast", "normal", "slow"]},
            "advanced_settings": {
                "type": "object",
                "properties": {
                    "threshold": {"type": "number"},
                    "filters": {"type": "array"}
                }
            }
        },
        "calculation_code": """
def calculate_super_custom(data, params):
    # 지표 계산 로직
    sensitivity = params.get('sensitivity', 0.5)
    # ... 계산 ...
    return signal
        """
    }
    
    # 2. 지표 등록
    registry = IndicatorRegistry()
    registry.register_new_indicator(new_indicator)
    
    # 3. 전략에서 사용
    strategy = {
        "name": "My Strategy",
        "indicators": {
            # 기존 지표
            "rsi": {"enabled": True, "period": 14},
            "macd": {"enabled": True},
            
            # 새로 추가된 지표 (스키마 변경 없이!)
            "super_custom_indicator": {
                "enabled": True,
                "sensitivity": 0.7,
                "mode": "fast",
                "advanced_settings": {
                    "threshold": 0.3,
                    "filters": ["filter1", "filter2"]
                }
            }
        }
    }
    
    # 4. 데이터베이스에 저장 (JSONB라서 자유롭게 저장)
    sql = """
    UPDATE strategies 
    SET indicators = %s 
    WHERE id = %s
    """
    # strategy['indicators']를 그대로 JSONB에 저장
    
    print("새 지표가 스키마 변경 없이 추가되었습니다!")


# 프론트엔드에서 동적 폼 생성
def generate_indicator_form_config():
    """프론트엔드용 동적 폼 설정 생성"""
    
    registry = IndicatorRegistry()
    all_indicators = registry.get_all_indicators()
    
    form_config = {
        "sections": []
    }
    
    for category in ["momentum", "trend", "volume", "volatility", "custom"]:
        section = {
            "title": category.title(),
            "indicators": []
        }
        
        for indicator in all_indicators:
            if indicator['category'] == category:
                section['indicators'].append({
                    "key": indicator['key'],
                    "name": indicator['name'],
                    "description": indicator['description'],
                    "fields": generate_fields_from_schema(indicator['parameters_schema'])
                })
        
        form_config['sections'].append(section)
    
    return form_config


def generate_fields_from_schema(schema: Dict) -> List[Dict]:
    """스키마에서 폼 필드 생성"""
    fields = []
    
    for key, config in schema.items():
        field = {
            "name": key,
            "type": config['type'],
            "default": config.get('default'),
            "label": key.replace('_', ' ').title()
        }
        
        if config['type'] == 'number' or config['type'] == 'integer':
            field['min'] = config.get('min')
            field['max'] = config.get('max')
        elif config['type'] == 'string' and 'options' in config:
            field['options'] = config['options']
        
        fields.append(field)
    
    return fields