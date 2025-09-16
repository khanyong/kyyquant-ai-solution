// Vercel Functions - Backtest Run Proxy
// api.bll-pro.com으로 요청을 프록시

export default async function handler(req, res) {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // OPTIONS 요청 처리
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // POST 요청만 처리
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('[Vercel Function] Proxying to api.bll-pro.com');

    // api.bll-pro.com으로 요청 전달
    const response = await fetch('https://api.bll-pro.com/api/backtest-run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    // 응답 처리
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Vercel Function] Error from api.bll-pro.com:', errorText);
      return res.status(response.status).json({
        error: errorText || 'Proxy request failed',
        details: 'Failed to reach api.bll-pro.com'
      });
    }

    const data = await response.json();

    console.log('[Vercel Function] Success, returning data');
    return res.status(200).json(data);

  } catch (error) {
    console.error('[Vercel Function] Proxy error:', error);
    return res.status(500).json({
      error: 'Internal Server Error',
      message: error.message,
      details: 'Vercel Function proxy failed'
    });
  }
}