"""
Ichimoku 지표 코드 수정 - 가독성 개선 및 줄바꿈 추가
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# 개선된 Ichimoku 코드
new_code = """tenkan_p = int(params.get('tenkan', 9))
kijun_p = int(params.get('kijun', 26))
senkou_p = int(params.get('senkou', 52))
chikou_p = int(params.get('chikou', 26))
tenkan_p = 1 if tenkan_p < 1 else tenkan_p
kijun_p = 1 if kijun_p < 1 else kijun_p
senkou_p = 1 if senkou_p < 1 else senkou_p
chikou_p = 0 if chikou_p < 0 else chikou_p
disp = params.get('displacement', None)
disp = int(disp) if disp is not None else kijun_p
rt = str(params.get('realtime', False)).lower() in ('1','true','yes')
h = df['high'].shift(1) if rt else df['high']
l = df['low'].shift(1) if rt else df['low']
c = df['close'].shift(1) if rt else df['close']
th = h.rolling(window=tenkan_p, min_periods=tenkan_p).max()
tl = l.rolling(window=tenkan_p, min_periods=tenkan_p).min()
tenkan = (th + tl) / 2.0
kh = h.rolling(window=kijun_p, min_periods=kijun_p).max()
kl = l.rolling(window=kijun_p, min_periods=kijun_p).min()
kijun = (kh + kl) / 2.0
senkou_a = ((tenkan + kijun) / 2.0).shift(disp)
sh = h.rolling(window=senkou_p, min_periods=senkou_p).max()
sl = l.rolling(window=senkou_p, min_periods=senkou_p).min()
senkou_b = ((sh + sl) / 2.0).shift(disp)
chikou_span = c.shift(-chikou_p)
result = {'ichimoku_tenkan': tenkan, 'ichimoku_kijun': kijun, 'ichimoku_senkou_a': senkou_a, 'ichimoku_senkou_b': senkou_b, 'ichimoku_chikou': chikou_span}
"""

# Supabase 업데이트
result = client.table('indicators').update({
    'formula': {'code': new_code}
}).eq('name', 'ichimoku').execute()

print(f"[OK] Ichimoku 지표 업데이트 완료")
print(f"수정된 행: {len(result.data)}")
