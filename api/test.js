// Simple test endpoint to verify Vercel functions are working

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Test basic functionality
  const testInfo = {
    message: 'Vercel function is working',
    method: req.method,
    url: req.url,
    headers: req.headers,
    body: req.body,
    nodeVersion: process.version,
    timestamp: new Date().toISOString()
  };

  // Test if fetch is available
  let fetchAvailable = false;
  let fetchError = null;

  try {
    if (typeof fetch !== 'undefined') {
      fetchAvailable = true;

      // Try to actually fetch something
      const testResponse = await fetch('https://jsonplaceholder.typicode.com/posts/1');
      const testData = await testResponse.json();
      testInfo.fetchTest = {
        success: true,
        data: testData
      };
    }
  } catch (error) {
    fetchError = error.message;
    testInfo.fetchTest = {
      success: false,
      error: fetchError
    };
  }

  testInfo.fetchAvailable = fetchAvailable;

  // Now test actual NAS connection
  if (req.method === 'POST') {
    const NAS_API_URL = 'http://khanyong.asuscomm.com:8080';

    try {
      const response = await fetch(`${NAS_API_URL}/api/backtest/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body || {}),
      });

      const responseText = await response.text();

      testInfo.nasTest = {
        success: response.ok,
        status: response.status,
        statusText: response.statusText,
        responseData: responseText.substring(0, 500)
      };
    } catch (error) {
      testInfo.nasTest = {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  }

  return res.status(200).json(testInfo);
}