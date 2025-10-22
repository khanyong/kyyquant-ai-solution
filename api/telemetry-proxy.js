module.exports = async function handler(req, res) {
  // CORS 헤더 추가
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  // OPTIONS 요청 처리 (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  try {
    // 텔레메트리 요청을 그냥 200 OK로 응답 (실제로는 저장하지 않음)
    // 또는 실제 n8n 텔레메트리 서버로 포워딩 가능
    res.status(200).json({ success: true })
  } catch (error) {
    console.error('[telemetry-proxy] Error:', error)
    res.status(500).json({ error: 'Telemetry proxy failed' })
  }
}
