// Vercel Serverless Function - Backtest Proxy
// Vercel Node.js 18+ has native fetch support

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // Handle preflight
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const NAS_API_URL = 'http://khanyong.asuscomm.com:8080';

  try {
    console.log('Proxying request to:', `${NAS_API_URL}/api/backtest/run`);
    console.log('Request body:', JSON.stringify(req.body));

    // Use native fetch (available in Node.js 18+)
    const response = await fetch(`${NAS_API_URL}/api/backtest/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.text();
    console.log('Response status:', response.status);
    console.log('Response data (first 200 chars):', data.substring(0, 200));

    try {
      const jsonData = JSON.parse(data);
      return res.status(response.status).json(jsonData);
    } catch (e) {
      console.error('JSON parse error:', e);
      // If not JSON, return as is
      return res.status(response.status).send(data);
    }
  } catch (error) {
    console.error('Proxy error:', error);
    return res.status(500).json({
      error: 'Failed to connect to backtest server',
      details: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}