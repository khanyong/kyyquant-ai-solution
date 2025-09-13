// Vercel Serverless Function - Backtest Proxy

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

  // Try environment variable first, fallback to direct URL
  const NAS_API_URL = process.env.NAS_API_URL || 'http://khanyong.asuscomm.com:8080';

  // Check if fetch is available
  if (typeof fetch === 'undefined') {
    return res.status(500).json({
      error: 'Fetch is not available',
      nodeVersion: process.version,
      env: process.env.NODE_ENV
    });
  }

  try {
    console.log('Proxying request to:', `${NAS_API_URL}/api/backtest/run`);
    console.log('Request body:', JSON.stringify(req.body));

    // Test with a timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 seconds timeout

    const response = await fetch(`${NAS_API_URL}/api/backtest/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    const data = await response.text();
    console.log('Response status:', response.status);
    console.log('Response data (first 200 chars):', data.substring(0, 200));

    // Try to parse as JSON
    try {
      const jsonData = JSON.parse(data);
      return res.status(response.status).json(jsonData);
    } catch (e) {
      // If not JSON, check if it's an error page
      if (data.includes('<!DOCTYPE') || data.includes('<html')) {
        return res.status(502).json({
          error: 'Received HTML instead of JSON',
          details: 'The backend server returned an HTML page instead of JSON data',
          htmlPreview: data.substring(0, 500)
        });
      }
      // Return raw data
      return res.status(response.status).send(data);
    }
  } catch (error) {
    console.error('Proxy error:', error);

    // Handle different error types
    if (error.name === 'AbortError') {
      return res.status(504).json({
        error: 'Request timeout',
        details: 'The request to the backend server timed out after 30 seconds'
      });
    }

    if (error.cause?.code === 'ECONNREFUSED') {
      return res.status(503).json({
        error: 'Backend server unreachable',
        details: 'Could not connect to the backend server',
        server: NAS_API_URL
      });
    }

    // Generic error
    return res.status(500).json({
      error: 'Failed to connect to backtest server',
      details: error.message,
      type: error.name,
      nodeVersion: process.version
    });
  }
}