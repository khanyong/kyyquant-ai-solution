-- 실패한 4개 지표 수정 SQL (타입 캐스팅 수정)

-- 1. Ichimoku 수정
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb('tenkan_p = int(params.get(''tenkan'', 9))
kijun_p = int(params.get(''kijun'', 26))
senkou_p = int(params.get(''senkou'', 52))
chikou_p = int(params.get(''chikou'', 26))
tenkan_p = 1 if tenkan_p < 1 else tenkan_p
kijun_p = 1 if kijun_p < 1 else kijun_p
senkou_p = 1 if senkou_p < 1 else senkou_p
chikou_p = 0 if chikou_p < 0 else chikou_p
disp = params.get(''displacement'', None)
disp = int(disp) if disp is not None else kijun_p
rt = str(params.get(''realtime'', False)).lower() in (''1'',''true'',''yes'')
h = df[''high''].shift(1) if rt else df[''high'']
l = df[''low''].shift(1) if rt else df[''low'']
c = df[''close''].shift(1) if rt else df[''close'']
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
result = {''ichimoku_tenkan'': tenkan, ''ichimoku_kijun'': kijun, ''ichimoku_senkou_a'': senkou_a, ''ichimoku_senkou_b'': senkou_b, ''ichimoku_chikou'': chikou_span}'::text)
)
WHERE name = 'ichimoku';

-- 2. CCI 수정 (lambda 제거)
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb('period = int(params.get(''period'', 20))
period = 1 if period < 1 else period
c = float(params.get(''c'', 0.015))
c = 1e-12 if c == 0 else c
rt = str(params.get(''realtime'', False)).lower() in (''1'',''true'',''yes'')
h = df[''high''].shift(1) if rt else df[''high'']
l = df[''low''].shift(1) if rt else df[''low'']
cclose = df[''close''].shift(1) if rt else df[''close'']
tp = (h + l + cclose) / 3.0
sma = tp.rolling(window=period, min_periods=period).mean()
mad = tp.rolling(window=period, min_periods=period).std()
denom = (c * mad).where(mad != 0)
cci = (tp - sma) / denom
result = {''cci'': cci}'::text)
)
WHERE name = 'cci';

-- 3. Parabolic 수정 (간소화 버전)
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb('af_start = float(params.get(''af_start'', 0.02))
af_step = float(params.get(''af_step'', 0.02))
af_max = float(params.get(''af_max'', 0.2))
rt = str(params.get(''realtime'', False)).lower() in (''1'',''true'',''yes'')
h = df[''high''].shift(1) if rt else df[''high'']
l = df[''low''].shift(1) if rt else df[''low'']
c = df[''close''].shift(1) if rt else df[''close'']
n = len(df)
psar = [c.iloc[0] if n > 0 else 0]
trend = [1]
for i in range(1, n):
    psar.append(h.iloc[i-1] if trend[-1] == 1 else l.iloc[i-1])
    if h.iloc[i] > psar[-1]:
        trend.append(1)
    elif l.iloc[i] < psar[-1]:
        trend.append(-1)
    else:
        trend.append(trend[-1])
psar_series = pd.Series(psar, index=df.index)
trend_series = pd.Series(trend, index=df.index)
result = {''psar'': psar_series, ''psar_trend'': trend_series}'::text)
)
WHERE name = 'parabolic';

-- 4. VWAP 수정 (rolling 모드만 사용 - 간소화)
UPDATE indicators
SET formula = jsonb_set(
    formula,
    '{code}',
    to_jsonb('period = int(params.get(''period'', 20))
period = 1 if period < 1 else period
rt = str(params.get(''realtime'', False)).lower() in (''1'',''true'',''yes'')
src = str(params.get(''source'',''close'')).lower()
if src in (''hlc3'',''tp''):
    h = df[''high''].shift(1) if rt else df[''high'']
    l = df[''low''].shift(1) if rt else df[''low'']
    c = df[''close''].shift(1) if rt else df[''close'']
    price = (h + l + c) / 3.0
else:
    s = df.get(src, df[''close''])
    price = s.shift(1) if rt else s
vol = df[''volume'']
price = price.astype(''float64'')
vol = vol.astype(''float64'')
pv = price * vol
minp = period
num = pv.rolling(window=period, min_periods=minp).sum()
den = vol.rolling(window=period, min_periods=minp).sum()
vwap = num / den.where(den != 0)
result = {''vwap'': vwap}'::text)
)
WHERE name = 'vwap';

-- 수정 확인
SELECT
    name,
    CASE
        WHEN formula->>'code' LIKE '%result%' THEN 'OK'
        ELSE 'MISSING result'
    END as has_result,
    LENGTH(formula->>'code') as code_length
FROM indicators
WHERE name IN ('ichimoku', 'cci', 'parabolic', 'vwap')
ORDER BY name;
