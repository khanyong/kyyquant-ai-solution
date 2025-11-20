"""
Supabase indicators 테이블에 지표 설정 추가
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

# 환경변수 로드
load_dotenv()

def setup_indicators():
    """Supabase에 기본 지표 설정"""

    # Supabase 연결
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        return

    supabase = create_client(url, key)

    # 기본 지표 정의
    indicators = [
        {
            'name': 'sma_5',
            'display_name': '5일 단순이동평균',
            'description': '5일간 종가의 단순 이동평균',
            'category': 'moving_average',
            'calculation_type': 'custom_formula',
            'formula': json.dumps({
                'expression': 'df["close"].rolling(window=5).mean()',
                'output_column': 'sma_5'
            }),
            'default_params': json.dumps({
                'period': 5
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['sma_5']),
            'is_active': True
        },
        {
            'name': 'sma_20',
            'display_name': '20일 단순이동평균',
            'description': '20일간 종가의 단순 이동평균',
            'category': 'moving_average',
            'calculation_type': 'custom_formula',
            'formula': json.dumps({
                'expression': 'df["close"].rolling(window=20).mean()',
                'output_column': 'sma_20'
            }),
            'default_params': json.dumps({
                'period': 20
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['sma_20']),
            'is_active': True
        },
        {
            'name': 'ema_12',
            'display_name': '12일 지수이동평균',
            'description': '12일간 종가의 지수 이동평균',
            'category': 'moving_average',
            'calculation_type': 'custom_formula',
            'formula': json.dumps({
                'expression': 'df["close"].ewm(span=12, adjust=False).mean()',
                'output_column': 'ema_12'
            }),
            'default_params': json.dumps({
                'period': 12
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['ema_12']),
            'is_active': True
        },
        {
            'name': 'ema_26',
            'display_name': '26일 지수이동평균',
            'description': '26일간 종가의 지수 이동평균',
            'category': 'moving_average',
            'calculation_type': 'custom_formula',
            'formula': json.dumps({
                'expression': 'df["close"].ewm(span=26, adjust=False).mean()',
                'output_column': 'ema_26'
            }),
            'default_params': json.dumps({
                'period': 26
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['ema_26']),
            'is_active': True
        },
        {
            'name': 'rsi_14',
            'display_name': 'RSI (14일)',
            'description': '14일 기준 RSI (Relative Strength Index)',
            'category': 'oscillator',
            'calculation_type': 'python_code',
            'code': '''
delta = df['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
rs = avg_gain / avg_loss.replace(0, np.nan)
result = {'rsi_14': 100 - (100 / (1 + rs))}
''',
            'default_params': json.dumps({
                'period': 14
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['rsi_14']),
            'is_active': True
        },
        {
            'name': 'macd',
            'display_name': 'MACD',
            'description': 'MACD 지표 (12-26-9)',
            'category': 'trend',
            'calculation_type': 'python_code',
            'code': '''
ema_fast = df['close'].ewm(span=12, adjust=False).mean()
ema_slow = df['close'].ewm(span=26, adjust=False).mean()
macd_line = ema_fast - ema_slow
macd_signal = macd_line.ewm(span=9, adjust=False).mean()
macd_hist = macd_line - macd_signal
result = {
    'macd_line': macd_line,
    'macd_signal': macd_signal,
    'macd_hist': macd_hist
}
''',
            'default_params': json.dumps({
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['macd_line', 'macd_signal', 'macd_hist']),
            'is_active': True
        },
        {
            'name': 'bb',
            'display_name': 'Bollinger Bands',
            'description': '볼린저 밴드 (20일, 2 표준편차)',
            'category': 'volatility',
            'calculation_type': 'python_code',
            'code': '''
middle = df['close'].rolling(window=20).mean()
std = df['close'].rolling(window=20).std()
upper = middle + (std * 2)
lower = middle - (std * 2)
result = {
    'bb_upper': upper,
    'bb_middle': middle,
    'bb_lower': lower
}
''',
            'default_params': json.dumps({
                'period': 20,
                'std_mult': 2
            }),
            'required_data': json.dumps(['close']),
            'output_columns': json.dumps(['bb_upper', 'bb_middle', 'bb_lower']),
            'is_active': True
        },
        {
            'name': 'volume_ma_20',
            'display_name': '20일 거래량 이동평균',
            'description': '20일간 거래량의 이동평균',
            'category': 'volume',
            'calculation_type': 'custom_formula',
            'formula': json.dumps({
                'expression': 'df["volume"].rolling(window=20).mean()',
                'output_column': 'volume_ma_20'
            }),
            'default_params': json.dumps({
                'period': 20
            }),
            'required_data': json.dumps(['volume']),
            'output_columns': json.dumps(['volume_ma_20']),
            'is_active': True
        }
    ]

    # 기존 지표 삭제 (선택사항)
    print("Clearing existing indicators...")
    try:
        supabase.table('indicators').delete().neq('id', 0).execute()
    except Exception as e:
        print(f"Warning: Could not clear existing indicators: {e}")

    # 지표 추가
    print("Adding indicators to Supabase...")
    for indicator in indicators:
        try:
            result = supabase.table('indicators').insert(indicator).execute()
            print(f"Added {indicator['name']}: {indicator['display_name']}")
        except Exception as e:
            print(f"Failed to add {indicator['name']}: {e}")

    # 확인
    print("\nVerifying indicators in database...")
    response = supabase.table('indicators').select('*').eq('is_active', True).execute()
    print(f"Total active indicators: {len(response.data)}")
    for ind in response.data:
        print(f"  - {ind['name']}: {ind['display_name']}")

if __name__ == "__main__":
    setup_indicators()