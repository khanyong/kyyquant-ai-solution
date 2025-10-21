import type { VercelRequest, VercelResponse } from '@vercel/node'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { path = '', method = 'GET' } = req.query
  const n8nUrl = process.env.VITE_N8N_URL || 'https://workflow.bll-pro.com'
  const apiKey = process.env.VITE_N8N_API_KEY || ''

  try {
    const targetUrl = `${n8nUrl}/api/v1/${path}`

    const response = await fetch(targetUrl, {
      method: method as string,
      headers: {
        'X-N8N-API-KEY': apiKey,
        'Content-Type': 'application/json',
      },
      body: req.method === 'POST' ? JSON.stringify(req.body) : undefined,
    })

    const data = await response.json()

    res.status(response.status).json(data)
  } catch (error) {
    res.status(500).json({
      error: 'Proxy failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
