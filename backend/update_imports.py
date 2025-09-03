#!/usr/bin/env python
"""
Import 경로 업데이트 스크립트
폴더 구조 변경에 따른 import 문 자동 수정
"""

import os
import re
from pathlib import Path

# 파일 이동 매핑
FILE_MAPPINGS = {
    # API 모듈
    'api_server': 'api.api_server',
    'api_strategy_routes': 'api.api_strategy_routes',
    'backend_api': 'api.backend_api',
    'main': 'api.main',
    'main_dev': 'api.main_dev',
    
    # Core 모듈
    'strategy_manager': 'core.strategy_manager',
    'strategy_config_manager': 'core.strategy_config_manager',
    'strategy_config_schema': 'core.strategy_config_schema',
    'strategy_execution_manager': 'core.strategy_execution_manager',
    'risk_manager': 'core.risk_manager',
    'trading_engine': 'core.trading_engine',
    'dynamic_indicator_system': 'core.dynamic_indicator_system',
    'data_pipeline': 'core.data_pipeline',
    'cloud_executor': 'core.cloud_executor',
    
    # Database 모듈
    'database': 'database.database',
    'database_supabase': 'database.database_supabase',
    'models': 'database.models',
    
    # Config 모듈
    'config': 'config.config',
    'save_complex_indicators': 'config.save_complex_indicators',
    
    # Kiwoom 스크립트
    'kiwoom_api': 'scripts.kiwoom.kiwoom_api',
    'kiwoom_bridge_server': 'scripts.kiwoom.kiwoom_bridge_server',
    'kiwoom_hybrid_api': 'scripts.kiwoom.kiwoom_hybrid_api',
    'kiwoom_data_saver': 'scripts.kiwoom.kiwoom_data_saver',
    'kiwoom_supabase_bridge': 'scripts.kiwoom.kiwoom_supabase_bridge',
    'kiwoom_trading_api': 'scripts.kiwoom.kiwoom_trading_api',
}

def update_imports_in_file(filepath):
    """파일 내의 import 문 업데이트"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    
    # from X import Y 형식 업데이트
    for old_module, new_module in FILE_MAPPINGS.items():
        # from module import something
        pattern1 = rf'from {old_module} import'
        replacement1 = f'from {new_module} import'
        content = re.sub(pattern1, replacement1, content)
        
        # import module
        pattern2 = rf'^import {old_module}$'
        replacement2 = f'import {new_module}'
        content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
        
        # import module as alias
        pattern3 = rf'import {old_module} as'
        replacement3 = f'import {new_module} as'
        content = re.sub(pattern3, replacement3, content)
    
    # 변경사항이 있으면 파일 저장
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            return True
        except:
            print(f"Failed to update: {filepath}")
            return False
    
    return False

def main():
    """메인 실행 함수"""
    backend_dir = Path(__file__).parent
    
    # 업데이트할 파이썬 파일들 찾기
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        # venv 폴더는 제외
        if 'venv' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    print("Updating import statements...")
    
    updated_count = 0
    for filepath in python_files:
        if update_imports_in_file(filepath):
            updated_count += 1
    
    print(f"\nComplete! Updated {updated_count} files")

if __name__ == "__main__":
    main()