
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)

class TokenManager:
    """Kiwoom/KIS Token Manager with File-based Caching"""
    
    def __init__(self, is_demo: bool = True):
        self.is_demo = is_demo
        self.token_file = 'token_cache_demo.json' if is_demo else 'token_cache_real.json'
        
        # Determine Base URL
        if self.is_demo:
            self.base_url = "https://mockapi.kiwoom.com"
        else:
            self.base_url = "https://api.kiwoom.com"
            
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        
        if not self.app_key or not self.app_secret:
            logger.warning("[TokenManager] Missing API credentials")
            
    def get_token(self) -> str:
        """Get valid access token (from cache or new request)"""
        # 1. Try to load from cache
        cached_token = self._load_from_cache()
        if cached_token:
            return cached_token
            
        # 2. Request new token
        return self._request_new_token()
    
    def _load_from_cache(self) -> Optional[str]:
        """Load token from file and check expiration"""
        if not os.path.exists(self.token_file):
            return None
            
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            token = data.get('access_token')
            expires_at_str = data.get('expires_at')
            
            if not token or not expires_at_str:
                return None
                
            expires_at = datetime.fromisoformat(expires_at_str)
            
            # Buffer time (e.g. 5 minutes)
            if datetime.now() < expires_at - timedelta(minutes=5):
                logger.debug("[TokenManager] Loaded valid token from cache")
                return token
            else:
                logger.info("[TokenManager] Cached token expired")
                return None
                
        except Exception as e:
            logger.warning(f"[TokenManager] Failed to load cache: {e}")
            return None

    def _request_new_token(self) -> str:
        """Request new token from API"""
        url = f"{self.base_url}/oauth2/token"
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret
        }
        
        try:
            logger.info(f"[TokenManager] Requesting new token from {url}...")
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if 'error' in result:
                raise Exception(f"Token error: {result}")
                
            token = result.get('access_token')
            if not token: # Sometimes 'token' key
                token = result.get('token')
                
            if not token:
                raise Exception(f"No access token in response: {result}")
                
            expires_in = int(result.get('expires_in', 86400))
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_to_cache(token, expires_at)
            logger.info("[TokenManager] New token obtained and cached")
            
            return token
            
        except Exception as e:
            logger.error(f"[TokenManager] Failed to get token: {e}")
            raise

    def _save_to_cache(self, token: str, expires_at: datetime):
        """Save token to file"""
        try:
            data = {
                "access_token": token,
                "expires_at": expires_at.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"[TokenManager] Failed to save cache: {e}")

# Singleton instance accessor
_managers: Dict[bool, TokenManager] = {}

def get_token_manager(is_demo: bool = True) -> TokenManager:
    if is_demo not in _managers:
        _managers[is_demo] = TokenManager(is_demo)
    return _managers[is_demo]
