// Vercel Serverless Function - Backtest Proxy
import https from 'https';
import http from 'http';

export default async function handler(req, res) {
  // CORS 설정
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // NAS API URL (HTTP) - 환경변수 또는 하드코딩
  const NAS_API_URL = process.env.NAS_API_URL || 'http://khanyong.asuscomm.com:8080';

  try {
    console.log('Proxying backtest request to:', `${NAS_API_URL}/api/backtest/run`);
    console.log('Request body:', req.body);

    // Node.js 내장 http 모듈 사용
    const url = new URL(`${NAS_API_URL}/api/backtest/run`);
    const postData = JSON.stringify(req.body);

    return new Promise((resolve, reject) => {
      const request = http.request({
        hostname: url.hostname,
        port: url.port || 80,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        }
      }, (response) => {
        let data = '';

        response.on('data', (chunk) => {
          data += chunk;
        });

        response.on('end', () => {
          try {
            const jsonData = JSON.parse(data);

            if (response.statusCode >= 200 && response.statusCode < 300) {
              console.log('Backtest successful');
              res.status(200).json(jsonData);
            } else {
              console.error('NAS API error:', jsonData);
              res.status(response.statusCode).json(jsonData);
            }
            resolve();
          } catch (error) {
            console.error('JSON parse error:', error);
            res.status(500).json({
              error: 'Invalid response from backtest server',
              details: error.message
            });
            resolve();
          }
        });
      });

      request.on('error', (error) => {
        console.error('Request error:', error);
        res.status(500).json({
          error: 'Failed to connect to backtest server',
          details: error.message,
          nas_url: NAS_API_URL
        });
        resolve();
      });

      request.write(postData);
      request.end();
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return res.status(500).json({
      error: 'Failed to process request',
      details: error.message,
      nas_url: NAS_API_URL
    });
  }
}