"""
자동매매 시스템 설정 관리
"""
import os
from typing import Dict, Any
from pathlib import Path
import json
from datetime import time

class Config:
    """시스템 전체 설정 관리 클래스"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정값"""
        return {
            "api": {
                "mode": "demo",  # demo or real
                "server_url": "https://openapi.koreainvestment.com:9443",
                "demo_server_url": "https://openapivts.koreainvestment.com:29443",
                "app_key": "",
                "app_secret": "",
                "account_no": "",
                "account_product_code": "01"
            },
            "trading": {
                "auto_trading_enabled": False,
                "market_open": "09:00",
                "market_close": "15:30",
                "max_position_size": 0.1,  # 전체 자산의 10%
                "max_positions": 5,  # 최대 보유 종목 수
                "stop_loss_rate": 0.05,  # 5% 손절
                "take_profit_rate": 0.1,  # 10% 익절
                "min_order_amount": 5000,  # 최소 주문 금액
                "commission_rate": 0.00015  # 거래 수수료
            },
            "strategy": {
                "default": "momentum",
                "parameters": {
                    "momentum": {
                        "period": 20,
                        "threshold": 0.05
                    },
                    "ma_cross": {
                        "short_period": 5,
                        "long_period": 20
                    },
                    "bollinger": {
                        "period": 20,
                        "std_dev": 2
                    }
                }
            },
            "monitoring": {
                "refresh_interval": 1,  # 실시간 데이터 갱신 주기 (초)
                "log_level": "INFO",
                "enable_notifications": True,
                "notification_channels": ["console", "file"]
            },
            "database": {
                "type": "sqlite",
                "path": "data/trading.db",
                "backup_enabled": True,
                "backup_interval": 24  # hours
            },
            "risk_management": {
                "daily_loss_limit": 0.03,  # 일일 최대 손실 3%
                "daily_trade_limit": 10,  # 일일 최대 거래 횟수
                "margin_ratio": 0.3,  # 증거금 비율
                "volatility_filter": True,
                "volatility_threshold": 0.05
            }
        }
    
    def save(self):
        """설정 저장"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """중첩된 키 값 가져오기 (예: 'api.mode')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """중첩된 키 값 설정"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()
    
    def is_market_open(self) -> bool:
        """현재 시장 개장 시간인지 확인"""
        from datetime import datetime
        now = datetime.now().time()
        market_open = time.fromisoformat(self.get('trading.market_open'))
        market_close = time.fromisoformat(self.get('trading.market_close'))
        return market_open <= now <= market_close

# 전역 설정 인스턴스
config = Config()