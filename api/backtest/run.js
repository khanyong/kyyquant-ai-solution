// Vercel Edge Function - Backtest API Proxy
export default async function handler(req, res) {
  // CORS 설정
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

  // POST 요청만 허용
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  // 환경변수 또는 기본값 사용
  // Vercel 환경변수: BACKTEST_API_URL = https://api.bll-pro.com
  const targetUrl = process.env.BACKTEST_API_URL 
    ? `${process.env.BACKTEST_API_URL}/api/backtest/run`
    : `https://api.bll-pro.com/api/backtest/run`;
  
  try {
    console.log('Proxying request to:', targetUrl);
    console.log('Request body:', JSON.stringify(req.body));
    
    // process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0" 설정이 필요할 수 있음
    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();
    console.log('Response from NAS:', data);
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ 
      error: 'Failed to connect to backtest server',
      details: error.message 
    });
  }
}