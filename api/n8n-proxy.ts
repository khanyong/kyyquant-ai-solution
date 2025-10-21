import type { VercelRequest, VercelResponse } from '@vercel/node'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORS 헤더 추가
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  // OPTIONS 요청 처리 (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  const { path = '', method = 'GET' } = req.query
  const n8nUrl = process.env.VITE_N8N_URL || 'https://workflow.bll-pro.com'
  const apiKey = process.env.VITE_N8N_API_KEY || ''

  // API 키 확인
  if (!apiKey) {
    return res.status(500).json({
      error: 'Configuration error',
      message: 'VITE_N8N_API_KEY is not set in environment variables'
    })
  }

  try {
    const targetUrl = `${n8nUrl}/api/v1/${path}`

    console.log(`[n8n-proxy] Proxying ${method} ${targetUrl}`)

    const response = await fetch(targetUrl, {
      method: method as string,
      headers: {
        'X-N8N-API-KEY': apiKey,
        'Content-Type': 'application/json',
      },
      body: req.method === 'POST' ? JSON.stringify(req.body) : undefined,
    })

    if (!response.ok) {
      console.error(`[n8n-proxy] n8n API error: ${response.status} ${response.statusText}`)

      // n8n 서버가 응답하지만 에러인 경우
      const errorText = await response.text()
      return res.status(response.status).json({
        error: 'n8n API error',
        message: `${response.status} ${response.statusText}`,
        details: errorText
      })
    }

    const data = await response.json()
    res.status(response.status).json(data)
  } catch (error) {
    console.error('[n8n-proxy] Proxy failed:', error)

    res.status(500).json({
      error: 'Proxy failed',
      message: error instanceof Error ? error.message : 'Unknown error',
      details: 'Failed to connect to n8n server. Check if n8n is running and accessible.'
    })
  }
}
