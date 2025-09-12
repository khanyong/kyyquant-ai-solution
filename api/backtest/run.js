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

  // Cloudflare + 시놀로지 리버스 프록시를 통한 HTTPS 접근
  const targetUrl = process.env.BACKTEST_API_URL 
    ? `${process.env.BACKTEST_API_URL}/api/backtest/run`
    : `https://api.bll-pro.com/api/backtest/run`;
  
  try {
    console.log('Proxying request to:', targetUrl);
    console.log('Request body:', JSON.stringify(req.body));
    
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