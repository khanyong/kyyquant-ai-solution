"""
Fix indicator names to lowercase
"""

# Read the file
with open('create_template_strategies.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all uppercase indicator names with lowercase
replacements = [
    ('SMA_20', 'sma_20'),
    ('SMA_60', 'sma_60'),
    ('SMA_120', 'sma_120'),
    ('SMA_200', 'sma_200'),
    ('SMA_50', 'sma_50'),
    ('SMA_5', 'sma_5'),
    ('EMA_8', 'ema_8'),
    ('EMA_10', 'ema_10'),
    ('RSI', 'rsi'),
    ('RSI_PREV', 'rsi_prev'),
    ('RSI_9', 'rsi_9'),
    ('MACD', 'macd'),
    ('MACD_SIGNAL', 'macd_signal'),
    ('MACD_HIST', 'macd_hist'),
    ('BB_UPPER', 'bb_upper'),
    ('BB_LOWER', 'bb_lower'),
    ('BB_MIDDLE', 'bb_middle'),
    ('BB_WIDTH', 'bb_width'),
    ('VOLUME', 'volume'),
    ('VOLUME_MA', 'volume_ma'),
    ('STOCH_K', 'stoch_k'),
    ('STOCH_D', 'stoch_d'),
    ('ADX', 'adx'),
    ('ATR', 'atr'),
    ('CLOSE', 'close'),
]

for old, new in replacements:
    content = content.replace(f'"{old}"', f'"{new}"')

# Write back
with open('create_template_strategies.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Fixed all indicator names to lowercase")