#!/bin/bash
# Docker 컨테이너 내부 파일 확인

echo "=== Checking Core Module Files ==="

# naming.py 확인
echo "1. Checking naming.py..."
docker exec kiwoom-bridge grep -n "isinstance(c, dict)" /app/core/naming.py

# indicators.py 확인
echo "2. Checking indicators.py..."
docker exec kiwoom-bridge grep -n "params.get('period') or indicator.get" /app/core/indicators.py

# backtest_engine_advanced.py 확인
echo "3. Checking backtest_engine_advanced.py..."
docker exec kiwoom-bridge grep -n "data_with_signals = evaluate_conditions" /app/backtest_engine_advanced.py

echo "=== Check Complete ==="