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
    const NAS_API_URL = process.env.NAS_API_URL || 'https://api.bll-pro.com';

    try {
      // First test if the host is reachable
      testInfo.nasUrl = NAS_API_URL;

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
      // Try a simpler request
      let alternativeTest = null;
      try {
        // Try just accessing the root
        const simpleResponse = await fetch(`${NAS_API_URL}/`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        });
        alternativeTest = {
          rootAccessible: true,
          status: simpleResponse.status
        };
      } catch (altError) {
        alternativeTest = {
          rootAccessible: false,
          error: altError.message
        };
      }

      testInfo.nasTest = {
        success: false,
        error: error.message,
        errorCause: error.cause,
        errorCode: error.cause?.code,
        alternativeTest,
        stack: error.stack.split('\n').slice(0, 5).join('\n')
      };
    }
  }

  return res.status(200).json(testInfo);
}